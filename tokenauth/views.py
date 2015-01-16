from django.shortcuts import render
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required

@login_required
def ping(request):

	return HttpResponse("pong")
