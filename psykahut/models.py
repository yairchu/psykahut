from django.db import models

# One topic for testing without revealing answers,
# other used in actual game.
class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    # The real answer for the question
    answer_text = models.CharField(max_length=200)
    def __str__(self):
        return '%s: %s (%s)' % (self.topic, self.question_text, self.answer_text)

class Game(models.Model):
    started = models.DateTimeField('date created', auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    questions_asked = models.ManyToManyField(Question, blank=True)
    current = models.ForeignKey(Question, null=True, on_delete=models.CASCADE, related_name='current')
    num_psych_answers = models.IntegerField(default=4)
    def __str__(self):
        return 'Game(%s, %s)' % (self.current or self.topic, self.started)

class Player(models.Model):
    name = models.CharField(max_length=200)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    def __str__(self):
        return '%s: %s' % (self.name, self.score)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    permutation_order = models.IntegerField()

    # game is redundat to author.game, but repeats for
    # query optimization (guessing here)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return '%s: %s (%s)' % (
            self.question.question_text, self.text, self.game.started)

class Vote(models.Model):
    voter = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, on_delete=models.CASCADE)

    # game is redundat to voter.game, but repeats for
    # query optimization (guessing here)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
