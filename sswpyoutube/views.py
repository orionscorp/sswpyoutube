from django.shortcuts import render, HttpResponse
from django.contrib.auth import get_user_model

# Create your views here.

def index(request):
    return HttpResponse("Logged in status: {} <p>Username: {}".format(request.user.is_authenticated, request.user.username))
