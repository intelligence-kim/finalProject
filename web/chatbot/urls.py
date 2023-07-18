from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('talk/', views.talk_view, name='talk-button'),
    path('survey/', views.survey_view, name='survey-button'),
    path('suggest/', views.suggest_view, name='suggest-button'),

]