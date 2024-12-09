from rest_framework import serializers
from .models import Product, ProductVarientImage, ProductVariant,Category,ProductTag
from .models import *
from django.db.models import Avg


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'link_url', 'description', 'is_active']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVarientImage
        fields = ['id', 'image', 'alt_text']

class VariantValuesSerializer(serializers.ModelSerializer):
    varient_type = serializers.StringRelatedField()  # Display the name of the variant type

    class Meta:
        model = Varient_values
        fields = ['id', 'varient_type', 'value']

class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for basic product details to be included in the variant response."""
    category = serializers.StringRelatedField()  # Display the name of the category
    tags = serializers.StringRelatedField(many=True)  # Display the names of tags
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'tags', 'price', 'discount_price','average_rating','review_count']
    
    def get_average_rating(self, obj):
        """Method to return the average rating for a product."""
        reviews = obj.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            return round(avg_rating, 1)
        return 0
    
    def get_review_count(self,obj):
        return obj.reviews.count()

class ProductVariantSerializer(serializers.ModelSerializer):
    primary_varient = VariantValuesSerializer(read_only=True)
    secondary_varient = VariantValuesSerializer(read_only=True)
    variant_images = ProductImageSerializer(many=True, read_only=True)
    product = ProductDetailSerializer(read_only=True)  # Include selective product details

    class Meta:
        model = ProductVariant
        fields = ['id', 'variant_name', 'price', 'discount_price', 'sku', 'total_stock', 'primary_varient', 'secondary_varient', 'variant_images', 'product','slug']
