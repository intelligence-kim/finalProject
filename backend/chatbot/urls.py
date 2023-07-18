from django.urls import path
from . import views
from chatbot.views import hello_rest_api
#from django.chatbot.views import web_hook

urlpatterns = [
    #home
    path('', views.home, name='home'),
    path('talk/', views.talk_view, name='talk-button'),
    path('survey/', views.survey_view, name='survey-button'),
    path('suggest/', views.suggest_view, name='suggest-button'),

    #chatbot
    path('api/hello/', hello_rest_api, name='hello_rest_api'),

]