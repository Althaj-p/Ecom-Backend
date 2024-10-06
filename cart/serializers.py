from rest_framework import serializers
from .models import Cart, CartItem
from products.models import ProductVariant

class CartItemSerializer(serializers.ModelSerializer):
    variant = serializers.StringRelatedField()

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'quantity', 'price', 'cart_total']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items']
