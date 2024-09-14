"""models.py for polls app."""

from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


class Question(models.Model):
    """Question model for questions."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', null=True,
                                    blank=True, default=None)

    def __str__(self):
        """Return question text."""
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published?',
    )
    def is_published(self):
        """Return true if question is published."""
        now = timezone.localtime()
        return self.pub_date <= now

    @admin.display(
        boolean=True,
        ordering='end_date',
        description='Closed?',
    )
    def is_closed(self):
        """Return true if question is closed."""
        now = timezone.localtime()
        return self.end_date is not None and self.end_date <= now

    def can_vote(self):
        """Return true if question can vote."""
        return self.is_published() and not self.is_closed()


class Choice(models.Model):
    """Choice model for choices."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self) -> int:
        """Return the total number of votes for a choice."""
        return self.vote_set.count()

    def __str__(self):
        """Return choice text."""
        return self.choice_text


class Vote(models.Model):
    """Record a choice for a question made by a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        """Return choice text."""
        return f"{self.user} voted for {self.choice}"
