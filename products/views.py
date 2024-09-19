from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from . models import *
# Create your views here.

@api_view(['GET'])
def categories_list(request):
    categories = Category.objects.filter(status=True)
    category_serializer = CategorySerializer(categories,many=True)
    response_data = {
        'status':1,
        'message':"",
        'data':category_serializer.data
    }
    return Response(response_data)
    