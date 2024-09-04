from django.shortcuts import render
from rest_framework.views import api_view
# Create your views here.

from . models import *
@api_view['GET']
def categories_list():
    