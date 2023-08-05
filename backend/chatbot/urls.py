from django.urls import path
from . import views
from chatbot.views import hello_rest_api, message_rest_api, mbti_rest_api, question_rest_api
#from django.chatbot.views import web_hook

urlpatterns = [
    #home
    path('', views.home, name='home'),
    path('talk/', views.talk_view, name='talk-button'),
    path('survey/', views.survey_view, name='survey-button'),
    path('suggest/', views.suggest_view, name='suggest-button'),

    #chatbot
    path('api/hello/', hello_rest_api, name='hello_rest_api'),
    path('api/message/', message_rest_api, name='message_rest_api'),
    path('api/mbti/', mbti_rest_api, name='mbti_rest_api'),
    path('api/question/', question_rest_api, name='question_rest_api'),
    

]