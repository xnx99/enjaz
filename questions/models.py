# -*- coding: utf-8  -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

question_type_choices = (
    ('F', u'أربع صور'),
    ('Q', u'سؤال'),
    ('S', u'لقطة'),
)

class Booth(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Question(models.Model):
    booth = models.ForeignKey(Booth, null=True)
    question_type = models.CharField(max_length=1, choices=question_type_choices,
                                    verbose_name=u"نوع السؤال", default="S")
    text = models.CharField(max_length=200)

    def __unicode__(self):
        return self.text

class QuestionFigure (models.Model):
    question = models.ForeignKey(Question)
    figure = models.FileField(upload_to="questions/question_image", blank=True, null=True)

class Choice(models.Model):
    is_answer = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __unicode__(self):
        return self.text

class Game (models.Model):
    user = models.ForeignKey(User)
    choices = models.ForeignKey(Choice, null=True )
    right_answers = models.IntegerField(default=0)
    submission_date = models.DateTimeField(auto_now_add=True, verbose_name=u"تاريخ الإرسال")

    def __unicode__(self):
        return self.user.username
