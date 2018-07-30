from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import models

def current_game():
    return models.Game.objects.last()

def index(request):
    player = request.session.get('player')
    if player is None:
        return render(request, 'welcome.html')
    return HttpResponse("Hello, world. You're at the psykahut index.")

@require_POST
def register(request):
    name = request.POST['name']
    if name:
        player, created = models.Player.objects.get_or_create(
            name=name, game=current_game())
        request.session["player"] = player.id
    return HttpResponseRedirect('/')
