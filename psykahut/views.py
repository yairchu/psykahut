import json
import random

from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import models

def current_game():
    return models.Game.objects.last()

def cur_answers(game):
    return models.Answer.objects.filter(game=game, question=game.current)

def get_player(request):
    try:
        return models.Player.objects.select_related(
            'game', 'game__current').get(
            id=request.session.get('player'))
    except models.Player.DoesNotExist:
        return

def summary(game):
    if not game.prev:
        return
    votes = models.Vote.objects.filter(
        question=game.prev, game=game).select_related('voter')
    colors = ['red', 'green', 'blue', 'brown', 'purple']
    def votes_for(answer):
        cur = [x for x in votes if x.answer == answer]
        score_char = 'ח' if answer else '✓'
        return {
            'count':
                ''.join(
                    '<span style="color:%s">%s</span>' %
                    (colors[i % len(colors)], score_char)
                    for i in range(len(cur))),
            'voters': [x.voter.name for x in cur],
        }
    answers = models.Answer.objects.filter(
        question=game.prev, game=game)
    leading_players = models.Player.objects.filter(game=game).order_by('-score')[:5]
    return {
        'question': game.prev.question_text,
        'answers':
            [{
                'text': game.prev.answer_text,
                'author': 'תשובה אמיתית',
                'votes': votes_for(None),
            }]
            +
            [{
                'text': x.text,
                'author': x.author.name,
                'votes': votes_for(x),
            } for x in answers],
        'scores': leading_players,
        }

def wait_for_answers(request, game):
    return render(request, 'wait_for_answers.html', {
        'cur': game.current.id,
    })

def is_in_quiz(game, answers):
    return len(answers) >= game.num_psych_answers

def index(request):
    game = current_game()
    player = get_player(request)
    if player is None or player.game != game:
        return render(request, 'welcome.html')
    answers = cur_answers(game)
    if is_in_quiz(game, answers):
        if models.Vote.objects.filter(
            voter=player, game=game, question=game.current
            ).exists():
            return wait_for_answers(request, game)
        return ask_quiz(request, game, answers)
    for answer in answers:
        if answer.author == player:
            return wait_for_answers(request, game)
    return render(request, 'open_question.html', {
        'question': game.current and game.current.question_text,
        'summary': summary(game),
        'cur': game.current and game.current.id,
    })

def permutation_order_avail(game, answers):
    perm_taken = set(x.permutation_order for x in answers)
    return list(set(range(game.num_psych_answers+1))-perm_taken)

def ask_quiz(request, game, answers):
    ordered_answers = [(x.permutation_order, x.text) for x in answers]
    [real_answer_pos] = permutation_order_avail(game, answers)
    ordered_answers.append((real_answer_pos, game.current.answer_text))
    ordered_answers.sort()
    return render(request, 'quiz.html', {
        'question': game.current.question_text,
        'answers': [{'id': x, 'text': y} for x, y in ordered_answers],
        'num_answers': len(ordered_answers),
    })

@require_POST
def answer_quiz(request):
    answer = int(request.POST['answer'])
    print(answer)
    player = get_player(request)
    game = current_game()
    vote, created = models.Vote.objects.get_or_create(voter=player, question=game.current, game=game)
    if created:
        for x in cur_answers(player.game):
            if answer == x.permutation_order:
                vote.answer = x
                break
    return HttpResponseRedirect('/')

@require_POST
def register(request):
    name = request.POST['name']
    if name:
        player, created = models.Player.objects.get_or_create(
            name=name, game=current_game())
        request.session["player"] = player.id
    return HttpResponseRedirect('/')

@require_POST
def open_question(request):
    answer = request.POST['answer']
    player = get_player(request)
    if answer == player.game.current.answer_text:
        return HttpResponseRedirect('/')
    while True:
        try:
            with transaction.atomic():
                answers = cur_answers(player.game)
                for x in answers:
                    if answer == x.text:
                        break
                if len(answers) < player.game.num_psych_answers:
                    perm_avail = permutation_order_avail(player.game, answers)
                    answer, created = models.Answer.objects.get_or_create(
                        text=answer, author=player,
                        permutation_order=random.choice(perm_avail),
                        game=player.game, question=player.game.current)
        except IntegrityError:
            raise
        break
    return HttpResponseRedirect('/')

def manage(request):
    game = current_game()
    return render(request, 'manage_game.html', {
        'game': game,
        'num_questions_asked': len(game.questions_asked.all()),
        'num_answers': len(models.Answer.objects.filter(game=game, question=game.current)),
        'num_votes': len(models.Vote.objects.filter(game=game, question=game.current)),
        'summary': summary(game),
    })

@require_POST
def start_new(request):
    try:
        topic = models.Topic.objects.get(name=request.POST['topic'])
    except models.Topic.DoesNotExist:
        return HttpResponseRedirect('/manage/')
    game = models.Game(topic=topic)
    game.current = random.choice(
        models.Question.objects.filter(topic=game.topic))
    num_answers = request.POST.get('num_answers')
    if num_answers:
        game.num_psych_answers = num_answers
    game.save()
    return HttpResponseRedirect('/manage/')

@require_POST
def next_question(request):
    game = current_game()
    players_to_update = set()
    for vote in models.Vote.objects.filter(question=game.current, game=game):
        if vote.answer is None:
            # Correct answer
            vote.voter.score += 3
            players_to_update.add(vote.voter)
        elif vote.voter == vote.answer.author:
            vote.voter.score -= 3
            players_to_update.add(vote.voter)
        else:
            vote.answer.author.score += 1
            players_to_update.add(vote.answer.author)
    with transaction.atomic():
        for player in players_to_update:
            player.save()

    asked = set(game.questions_asked.all())
    asked.add(game.current)
    questions_pool = [
        x for x in models.Question.objects.filter(topic=game.topic).all()
        if x not in asked]
    with transaction.atomic():
        game.questions_asked.add(game.current)
        game.prev = game.current
        if questions_pool:
            game.current = random.choice(questions_pool)
        else:
            game.current = None
        game.save()
    return HttpResponseRedirect('/manage/')

def cur_question_id(request):
    game = current_game()
    if game.current is None:
        return HttpResponse('null', content_type="application/json")
    return HttpResponse(json.dumps({
        'cur': game.current.id,
        'is_quiz': is_in_quiz(game, cur_answers(game)),
    }), content_type="application/json")
