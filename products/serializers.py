from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant,Category,ProductTag

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'variant_name', 'variant_price', 'stock']

class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = ['name']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField() 
    tags = ProductTagSerializer(many=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)  # Include variants in the product response

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'discount_price', 'sku', 'total_stock', 'category', 'tags', 'status', 'images', 'variants','slug']
