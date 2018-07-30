import random

from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import models

def current_game():
    return models.Game.objects.last()

def current_game_with_question():
    try:
        with transaction.atomic():
            game = current_game()
            if game.current is None:
                game.current = random.choice(
                    models.Question.objects.filter(topic=game.topic))
            game.save()
    except IntegrityError:
        game = current_game()
        assert game.current is not None
    return game

def cur_answers(game):
    return models.Answer.objects.filter(game=game, question=game.current)

def index(request):
    player = request.session.get('player')
    if player is None:
        return render(request, 'welcome.html')
    game = current_game_with_question()
    answers = cur_answers(game)
    if len(answers) >= game.num_psych_answers:
        if models.Vote.objects.filter(
            voter__id=player, game=game, question=game.current
            ).exists():
            return HttpResponseRedirect('/summary/%d/' % game.current.id)
        return ask_quiz(request, game, answers)
    for answer in answers:
        if answer.author.id == player:
            return render(request, 'wait_for_answers.html')
    return render(request, 'open_question.html', {
        'question': game.current.question_text,
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

def get_player(request):
    return models.Player.objects.select_related(
        'game', 'game__current').get(
        id=request.session.get('player'))

@require_POST
def answer_quiz(request):
    answer = request.POST['answer']
    player = get_player(request)
    game = current_game_with_question()
    vote = models.Vote(voter=player, question=game.current, game=game)
    for x in cur_answers(player.game):
        if answer != x.permutation_order:
            continue
        vote.answer = x
        if player == x.author:
            player.score -= 3
            break
        x.author += 1
        break
    else:
        # Correct answer!
        player.score += 3
    with transaction.atomic():
        player.save()
        vote.save()
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

def summary(request, question_id):
    game = current_game_with_question()
    if question_id == game.current.id:
        return render(request, 'wait_for_answers.html')
    todo
