from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('usd', views.usd, name='usd'),
    path('quote', views.quote, name='quote'),
    path('history', views.history, name='history'),
    path('challenges', views.challenges, name='challenges'),
    path('spotify/authorize', views.spotify_auth, name='spotify_auth'),
    path('spotify/token', views.spotify_token, name='spotify_token'),
    path('spotify/add-songs', views.spotify_add_songs, name='spotify_add_songs'),
    path('chatbot', views.chatbot, name='chatbot'),
]
