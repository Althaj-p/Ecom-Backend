from rest_framework import serializers
from .models import Cart, CartItem,Wishlist
from products.models import ProductVariant
from products.serializers import ProductVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    # variant = serializers.StringRelatedField()
    variant = ProductVariantSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'quantity', 'price', 'cart_total']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items']

class WishlistSerializer(serializers.ModelSerializer):
    products = ProductVariantSerializer(many=True,read_only=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products']

