import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin


class Question(models.Model):
    """A class to represents each question in the poll,
    allowing to store questions, manage their start dates,
    and determine when they are published."""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        """determines if the question was published within the last day."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        """returns a string representation of the question."""
        return self.question_text


class Choice(models.Model):
    """A class to represents each choice in the poll"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """returns a string representation of the choice."""
        return self.choice_text
