from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    #context = {}
    #return HttpResponse("...")
    return render(request, 'frontend/home.html')

def talk_view(request):
    #context = {}
    return render(request, 'frontend/talk.html')

def survey_view(request):
    #context = {}
    return render(request, 'frontend/survey.html')

def suggest_view(request):
    #context = {}
    return render(request, 'frontend/suggest.html')