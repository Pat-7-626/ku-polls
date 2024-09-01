import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('end date', null=True, blank=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published?',
    )
    def is_published(self):
        now = timezone.localtime()
        return self.pub_date <= now

    @admin.display(
        boolean=True,
        ordering='end_date',
        description='Closed?',
    )
    def is_closed(self):
        now = timezone.localtime()
        return self.end_date is not None and self.end_date <= now

    def can_vote(self):
        return self.is_published() and not self.is_closed()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
