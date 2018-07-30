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

def index(request):
    player = request.session.get('player')
    if player is None:
        return render(request, 'welcome.html')
    game = current_game_with_question()
    answers = models.Answer.objects.filter(game=game, question=game.current)
    if len(answers) < game.num_psych_answers:
        return render(request, 'open_question.html', {
            'question': game.current.question_text
        })
    return HttpResponse("Hello, world. You're at the psykahut index.")

@require_POST
def register(request):
    name = request.POST['name']
    if name:
        player, created = models.Player.objects.get_or_create(
            name=name, game=current_game())
        request.session["player"] = player.id
    return HttpResponseRedirect('/')
