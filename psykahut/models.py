from django.conf import settings
from django.db import models

# One topic for testing without revealing answers,
# other used in actual game.
class Topic(models.Model):
    name = models.CharField(max_length=200)

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    # The real answer for the question
    answer_text = models.CharField(max_length=200)

class Game(models.Model):
    started = models.DateTimeField('date created', auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    questions_asked = models.ManyToManyField(Question)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    permutation_order = models.IntegerField()

class Vote(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

class Participant(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
