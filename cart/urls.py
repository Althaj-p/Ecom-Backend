from django.urls import path
from . views import *

urlpatterns = [
    path('', view_cart, name='view-cart'),
    path('add/', add_to_cart, name='add-to-cart'),
    path('delete/<int:item_id>/', delete_from_cart, name='delete-from-cart'),
    path('clear/', clear_cart, name='clear-cart'),
    path('wishlist/', wishlists, name='wishlists'),
    path('wishlist/add', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/delete', delete_from_wishlist, name='delete_from_wishlist'),
]