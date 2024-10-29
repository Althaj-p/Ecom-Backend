from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from .models import Cart, CartItem,Wishlist
from products.models import ProductVariant
from .serializers import CartSerializer, CartItemSerializer,WishlistSerializer
from decimal import Decimal

# View Cart
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    """
    Retrieve the user's cart details including all cart items.
    Caching is used to store cart data for faster repeated requests.
    """
    user = request.user
    cache_key = f"cart_{user.id}"

    cached_cart = cache.get(cache_key)
    # if cached_cart:
    #     return Response(cached_cart, status=status.HTTP_200_OK)

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CartSerializer(cart)
    cache.set(cache_key, serializer.data, timeout=60 * 15)  # Cache for 15 minutes
    return Response(serializer.data, status=status.HTTP_200_OK)

# Add to Cart
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Add an item to the user's cart. If the item already exists, update the quantity.
    """
    user = request.user
    variant_id = request.data.get('variant_id')
    quantity = int(request.data.get('quantity', 1))

    if not variant_id:
        return Response({"error": "Variant ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        variant = ProductVariant.objects.get(id=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Product variant not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get or create cart for the user
    cart, _ = Cart.objects.get_or_create(user=user)

    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

    # Update the quantity and price
    if not created:
        cart_item.quantity += quantity
    cart_item.price = variant.price
    cart_item.cart_total = cart_item.quantity * Decimal(variant.price)
    cart_item.save()

    # Invalidate the cache
    cache.delete(f"cart_{user.id}")

    return Response({"success": "Item added to cart."}, status=status.HTTP_200_OK)

# Delete from Cart
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_from_cart(request, item_id):
    """
    Remove an item from the cart by item ID.
    """
    user = request.user

    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=user)
        cart_item.delete()

        # Invalidate the cache
        cache.delete(f"cart_{user.id}")
        return Response({"success": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)

    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
    
# update cart quantity
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_quantity(request):
    """
    Remove an item from the cart by item ID.
    """
    user = request.user
    item_id = request.data.get('item_id')
    quantity = request.data.get('quantity')

    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=user)
        cart_item.quantity=quantity
        cart_item.save()

        # Invalidate the cache
        return Response({"success": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)

    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

# Clear Cart
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """
    Clear all items in the user's cart.
    """
    user = request.user

    try:
        cart = Cart.objects.get(user=user)
        cart.items.all().delete()

        # Invalidate the cache
        cache.delete(f"cart_{user.id}")
        return Response({"success": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)

    except Cart.DoesNotExist:
        return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wishlists(request):
    user = request.user
    cache_key = f'wishlist_{user.id}'
    cached_wishlist = cache.get(cache_key)
    if cached_wishlist:
        return Response(cached_wishlist, status=status.HTTP_200_OK)
    try:
        user_wishlist = Wishlist.objects.prefetch_related('products').get(user=user)
    except Wishlist.DoesNotExist:
        return Response({'status': 0, 'error': 'Wishlist not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # serializer = WishlistSerializer(user_wishlist)
    response_data = {
        'user':user_wishlist.user.email,
        'items':[],
        'status':1
    }
    for i in user_wishlist.products.all():
        product_data = {
            'product_varient_id':i.id,
            'product':i.product.name,
        }
        response_data['items'].append(product_data)
    cache.set(cache_key, response_data, timeout=60 * 15)
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    user = request.user
    product_id = request.data.get('product_id')

    try:
        product_variant = ProductVariant.objects.get(id=product_id)
    except ProductVariant.DoesNotExist:
        return Response({'status': 0, 'error': "Product not found"}, status=404)

    wishlist_obj, created = Wishlist.objects.get_or_create(user=user)

    if product_variant in wishlist_obj.products.all():
        return Response({'status': 0, 'error': "Product already in wishlist"})

    wishlist_obj.products.add(product_variant)

    return Response({'status': 1, 'message': 'Product added to wishlist'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_from_wishlist(request):
    user = request.user
    product_id = request.query_params.get('product_id')

    if not product_id:
        return Response({'status': 0, 'error': 'Product ID is required'}, status=400)

    try:
        product_variant = ProductVariant.objects.get(id=product_id)
    except ProductVariant.DoesNotExist:
        return Response({'status': 0, 'error': 'Product not found'}, status=404)

    try:
        wishlist_obj = Wishlist.objects.get(user=user)
    except Wishlist.DoesNotExist:
        return Response({'status': 0, 'error': 'Wishlist not found'}, status=404)

    wishlist_obj.products.remove(product_variant)
    return Response({'status': 1, 'message': 'Product deleted from wishlist'})
