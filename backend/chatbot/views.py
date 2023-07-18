from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Create your views here.

# home.html
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


# rest api
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def hello_rest_api(request):
    data = {'message': 'Hello, REST API!'}
    return Response(data)
    # -> urls.py 열고 import function


'''# chatbot
def keyboard(request):

    return JsonResponse({
        'type':'buttons',
        'buttons':['안녕', '날씨']
    })

def message'''