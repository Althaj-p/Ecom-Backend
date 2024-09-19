from django.urls import path
from .views import *


urlpatterns = [
    path('categories',categories_list,name='categories_list')
]