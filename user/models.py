from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import admin

# Create your models here.

class User(AbstractUser):
    email = models.EmailField('email address', unique=True, blank=False)
