from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def my_view(request):
    #context = {}
    #return HttpResponse("...")
    return render(request, 'frontend/home.html')