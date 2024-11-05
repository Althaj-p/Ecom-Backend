from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from . models import *
from django.core.paginator import Paginator
from rest_framework import status
from django.core.cache import cache
from rest_framework import generics
# Create your views here.


class BannerListView(generics.ListAPIView):
    queryset = Banner.objects.filter(is_active=True).order_by('-created_on')
    serializer_class = BannerSerializer

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
    

@api_view(['GET'])
def variant_list(request):
    """
    Fetch a list of product variants. Supports filtering by category (via category slug),
    pagination, and caching. Each variant includes associated product details, images, 
    primary and secondary variant values.

    Caching Mechanism:
    - Caches variant listings by category and page number for efficient repeated requests.
    - Cache is invalidated if variants or products are updated.

    Query Parameters:
    - category: (string) Optional. Filter variants by the category of their parent product (category slug).
    - page: (int) Optional. The page number for paginated results. Default is 1.

    Response:
    - Returns a paginated list of product variants including associated product details, images, and variant values.
    
    Status Codes:
    - 200: Success, with paginated variant data.
    - 404: Category not found if the provided category slug is invalid.
    """
    category_slug = request.query_params.get('category', None)
    page = request.query_params.get('page', 1)

    # Cache key for specific category and page
    cache_key = f"variants_{category_slug or 'all'}_page_{page}"
    
    # Check if data is cached
    cached_data = cache.get(cache_key)
    # if cached_data:
    #     return Response(cached_data, status=status.HTTP_200_OK)

    try:
        variants = ProductVariant.objects.all().select_related('product', 'primary_varient', 'secondary_varient', 'product__category') \
                                              .prefetch_related('variant_images', 'product__tags')
        
        if category_slug:
            category = Category.objects.get(slug=category_slug)
            variants = variants.filter(product__category=category)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    # Paginate variants
    paginator = Paginator(variants, 10)
    try:
        paginated_variants = paginator.page(page)
    except:
        paginated_variants = paginator.page(1)
    
    # Serialize paginated variant data
    serializer = ProductVariantSerializer(paginated_variants, many=True)
    
    # Prepare response data
    response_data = {
        'variants': serializer.data,
        'page': paginated_variants.number,
        'pages': paginated_variants.paginator.num_pages,
        'status': 1,
    }

    # Cache the response data
    cache.set(cache_key, response_data, timeout=60*15)  # Cache for 15 minutes

    return Response(response_data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def product_variant_detail(request, slug):
    """
    Fetch detailed information about a specific product variant by its ID.
    This includes variant details, product information, primary and secondary variant values, and images.

    Caching Mechanism:
    - The variant detail is cached based on the variant ID to avoid repeated DB hits.
    - Cache is invalidated if variant data is updated.

    URL Parameters:
    - variant_id: (int) Required. The ID of the product variant to retrieve details for.

    Response:
    - Returns a detailed variant object including product details, variant values, and images.
    
    Status Codes:
    - 200: Success, with variant detail data.
    - 404: Variant not found if the provided ID is invalid.
    """
    # Define cache key based on variant ID
    cache_key = f"variant_detail_{slug}"

    # Check if data is already cached
    cached_data = cache.get(cache_key)
    # if cached_data:
    #     return Response(cached_data, status=status.HTTP_200_OK)

    # Fetch variant with related data
    variant = get_object_or_404(ProductVariant.objects.prefetch_related('variant_images', 'primary_varient', 'secondary_varient', 'product'), slug=slug)

    # Serialize variant detail
    serializer = ProductVariantSerializer(variant)

    # Cache the serialized data for 15 minutes
    cache.set(cache_key, serializer.data, timeout=60 * 15)

    return Response(serializer.data, status=status.HTTP_200_OK)