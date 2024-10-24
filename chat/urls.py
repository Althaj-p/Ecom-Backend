from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('rooms/', chat_rooms, name='rooms'),
    path('messages/<roomId>', chat_messages, name='chat_messages'),
]