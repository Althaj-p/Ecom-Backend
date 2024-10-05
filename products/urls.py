from django.urls import path
from .views import *


urlpatterns = [
    path('categories',categories_list,name='categories_list'),
    path('products',variant_list,name='product_list'),
    path('products/<slug:slug>/', product_variant_detail, name='product_detail'),
]