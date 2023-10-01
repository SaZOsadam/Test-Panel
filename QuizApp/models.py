# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Quiz(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='quizzes', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available.")
    cut_off_score = models.PositiveIntegerField(default=0)
    duration = models.IntegerField(default=30)  # Duration in minutes
    def __str__(self):
        return self.name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    score = models.PositiveIntegerField(default=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return self.text 

class UserResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    quiz_session = models.CharField(max_length=100)


class CustomUser(AbstractUser):
    is_instructor = models.BooleanField(default=False)
    #is_student = models.BooleanField(default=True)