from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from . models import *
from django.core.paginator import Paginator
from rest_framework import status
from django.core.cache import cache
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
    

@api_view(['GET'])
def product_list(request):
    """
    Fetch a list of active products. Supports filtering by category (via category slug),
    pagination, and caching. Each product includes associated images, tags, and variants.

    Caching Mechanism:
    - Caches product listings by category and page number for efficient repeated requests.
    - Cache is invalidated if products are updated.

    Query Parameters:
    - category: (string) Optional. Filter products by category slug.
    - page: (int) Optional. The page number for paginated results. Default is 1.

    Response:
    - Returns a paginated list of products including associated tags, images, and variants.
    
    Status Codes:
    - 200: Success, with paginated product data.
    - 404: Category not found if the provided category slug is invalid.
    """
    category_slug = request.query_params.get('category', None)
    page = request.query_params.get('page', 1)
    
    # Cache key for specific category and page
    cache_key = f"products_{category_slug or 'all'}_page_{page}"
    
    # Check if data is cached
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)
    
    try:
        products = Product.objects.filter(status='Active') \
                                  .select_related('category') \
                                  .prefetch_related('tags', 'images', 'variants')
        if category_slug:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    # Paginate products
    paginator = Paginator(products, 10)
    try:
        paginated_products = paginator.page(page)
    except:
        paginated_products = paginator.page(1)
    
    # Serialize paginated product data
    serializer = ProductSerializer(paginated_products, many=True)
    
    # Prepare response data
    response_data = {
        'products': serializer.data,
        'page': paginated_products.number,
        'pages': paginated_products.paginator.num_pages,
        'status':1,
    }
    
    # Cache the response data
    cache.set(cache_key, response_data, timeout=60*15)  # Cache for 15 minutes

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def product_detail(request, slug):
    """
    Fetch the details of a specific product by its slug. This includes
    all related data such as images, tags, variants, and category.
    
    Caching Mechanism:
    - The product detail is cached based on the product slug to avoid repeated DB hits.
    - Cache is invalidated if product data is updated.

    URL Parameters:
    - slug: (string) Required. The slug of the product to retrieve details for.

    Response:
    - Returns a detailed product object including its category, tags, images, and variants.
    
    Status Codes:
    - 200: Success, with product detail data.
    - 404: Product not found if the provided slug is invalid.
    """

    # Define cache key based on product slug
    cache_key = f"product_detail_{slug}"

    # Check if data is already cached
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)

    try:
        # Fetch product and related data efficiently
        product = Product.objects.filter(status='Active') \
                                 .select_related('category') \
                                 .prefetch_related('tags', 'images', 'variants') \
                                 .get(slug=slug)
        print(product,'data')
        # Serialize product detail
        serializer = ProductSerializer(product)

        # Cache the serialized data for 15 minutes (900 seconds)
        cache.set(cache_key, serializer.data, timeout=60 * 15)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)