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
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.db.models import F, ExpressionWrapper, DecimalField
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

@api_view(['GET'])
def popular_variants(request):
    """
    Fetch a list of the first variant of each product based on the average rating of the product.
    Only the first variant is listed per product, ordered by the product's average rating.

    Query Parameters:
    - page: (int) Optional. The page number for paginated results. Default is 1.

    Response:
    - Returns a paginated list of the first variant for each product, ordered by the product's average rating.
    """
    page = request.query_params.get('page', 1)
    cache_key = f"popular_variants_page_{page}"

    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)

    products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(
        avg_rating__isnull=False 
    ).order_by('-avg_rating')

    first_variants = [product.variants.first() for product in products if product.variants.exists()]

    paginator = Paginator(first_variants, 10) 
    try:
        paginated_variants = paginator.page(page)
    except:
        paginated_variants = paginator.page(1)

    serializer = ProductVariantSerializer(paginated_variants, many=True)

    response_data = {
        'variants': serializer.data,
        'page': paginated_variants.number,
        'pages': paginator.num_pages,
    }

    cache.set(cache_key, response_data, timeout=60 * 1)  # Cache for 15 minutes

    return Response(response_data, status=status.HTTP_200_OK)

class RecentlyViewedProductVariantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f"recently_viewed_variants_{user.id}"
        
        product_variants_data = cache.get(cache_key)

        if product_variants_data is None:
            recently_viewed_items = RecentlyViewedProduct.objects.filter(user=user).order_by('-viewed_at')[:10]  # Limit to 10 most recent
            # print(recently_viewed_items,'recent')
            # product_variants = ProductVariant.objects.filter(id__in=[item.product_variant.id for item in recently_viewed_items])
            # print(product_variants,'variants')
            product_variant_ids = [item.product_variant.id for item in recently_viewed_items]
            product_variants = ProductVariant.objects.filter(id__in=product_variant_ids)

            product_variants = sorted(product_variants, key=lambda pv: product_variant_ids.index(pv.id))

            
            serializer = ProductVariantSerializer(product_variants, many=True)
            product_variants_data = serializer.data

            cache.set(cache_key, product_variants_data, timeout=60 * 1)
        print(product_variants_data,'data2')
        response_data = {
            'status':1,
            'data':product_variants_data
        }
        return Response(response_data)

    def post(self, request):
        user = request.user
        product_slug = request.data.get("product_slug")

        if not product_slug:
            return Response({"error": "Product variant slug is required.",'status':0}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_variant = ProductVariant.objects.get(slug=product_slug)
        except ProductVariant.DoesNotExist:
            return Response({"error": "Product variant not found.",'status':0}, status=status.HTTP_404_NOT_FOUND)

        recently_viewed, created = RecentlyViewedProduct.objects.update_or_create(
            user=user,
            product_variant=product_variant,
            defaults={"viewed_at": datetime.now()}
        )

        cache_key = f"recently_viewed_variants_{user.id}"
        cache.delete(cache_key)

        return Response({"message": "Product variant marked as recently viewed.",'status':1}, status=status.HTTP_200_OK)

class TopOfferProductVariantsView(APIView):
    
    def get(self, request):
        offer_variants = ProductVariant.objects.filter(
            discount_price__isnull=False,
            discount_price__lt=F('price')  # Ensure there's a discount
        ).annotate(
            discount_amount=ExpressionWrapper(
                F('price') - F('discount_price'), output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).order_by('-discount_amount')[:10]  # Get top 10 by discount amount

        serializer = ProductVariantSerializer(offer_variants, many=True)
        
        return Response({
            "status": 1,
            "data": serializer.data
        }, status=status.HTTP_200_OK)