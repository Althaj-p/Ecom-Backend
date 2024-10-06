from django.urls import path
from . views import *

urlpatterns = [
    path('', view_cart, name='view-cart'),
    path('add/', add_to_cart, name='add-to-cart'),
    path('delete/<int:item_id>/', delete_from_cart, name='delete-from-cart'),
    path('clear/', clear_cart, name='clear-cart'),
]