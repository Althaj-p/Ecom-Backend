from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status,generics
from decimal import Decimal
from django.db import transaction
from . models import *
from cart.models import *
from .serializers import OrderSerializer,ShippingAddressSerializer
from django.core.paginator import Paginator
from accounts.models import ShippingAddress
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    """
    Handle checkout process by creating an order based on the cart items.
    """
    user = request.user
    shipping_address_id = request.data.get('shipping_address_id')
    payment_method = request.data.get('payment_method')

    # Check if cart exists for the user
    try:
        cart = Cart.objects.get(user=user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if shipping address is provided
    try:
        shipping_address = ShippingAddress.objects.get(id=shipping_address_id, user=user)
    except ShippingAddress.DoesNotExist:
        return Response({'error': 'Shipping address not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Create the order and its items
    with transaction.atomic():
        total_price = Decimal(0)
        
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            status='Pending',
            payment_method=payment_method,
            total_price=0  # We will calculate this below
        )
        
        for cart_item in cart.items.all():
            variant_price = cart_item.variant.price
            item_total_price = variant_price * cart_item.quantity
            total_price += item_total_price
            
            # Create OrderItem for each item in the cart
            OrderItem.objects.create(
                order=order,
                product=cart_item.variant.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=variant_price
            )
        
        # Update the total price for the order
        order.total_price = total_price
        order.save()

        # Clear the cart after order creation
        cart.items.all().delete()

    return Response({'order_id': order.id, 'message': 'Order created successfully.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    Create a Stripe Checkout session for an order.
    """
    try:
        user = request.user
        order_id = request.data.get('order_id')

        # Get the order by ID and check if it belongs to the current user
        try:
            order = Order.objects.get(id=order_id, user=user, status='Pending')
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or already processed.'}, status=status.HTTP_404_NOT_FOUND)

        # Create the line items for the Stripe session from the order items
        line_items = [
            {
                'price_data': {
                    'currency': 'INR',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.price * 100),  # Amount in cents
                },
                'quantity': item.quantity,
            } for item in order.items.all()
        ]

        try:
            # Create the Stripe Checkout session
            customer=stripe.Customer.create(
            name='Muhammed Althaj',
            email='muhammedalthaj371@gmail.com',
             address={
                "line1":'Pukkunnummal House pandikkad',
                "postal_code": '676521',
                "city": 'malappuram',
                "state": 'Kerala',
                "country": 'in',
            },
            )
            customer_id=customer.id
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=settings.FRONTEND_URL + '/order-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.FRONTEND_URL + '/order-cancel',
                client_reference_id=order.id,
            )

            # Save the session ID in the order for reference
            # order.payment_intent_id = checkout_session['id']
            # order.save()

            return Response({'checkout_url': checkout_session.url}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(str(e),'eroro')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    """
    Process the payment for an order and update the payment status.
    """
    user = request.user
    order_id = request.data.get('order_id')
    payment_method = request.data.get('payment_method')
    transaction_id = request.data.get('transaction_id')
    amount = Decimal(request.data.get('amount'))

    try:
        order = Order.objects.get(id=order_id, user=user)
        if order.payment_status == 'Completed':
            return Response({'error': 'Payment has already been completed for this order.'}, status=status.HTTP_400_BAD_REQUEST)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Process payment
    if amount != order.total_price:
        return Response({'error': 'Amount does not match the order total price.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Record the payment
    Payment.objects.create(
        order=order,
        payment_method=payment_method,
        amount=amount,
        status='Completed',
        transaction_id=transaction_id
    )

    # Update the order status
    order.payment_status = 'Completed'
    order.status = 'Processing'
    order.save()

    return Response({'message': 'Payment processed successfully.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Fetch details of a specific order by its ID.
    """
    user = request.user
    
    try:
        order = Order.objects.prefetch_related('items__variant', 'items__product').get(id=order_id, user=user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    order_items = [
        {
            'product': item.product.name,
            'variant': item.variant.variant_name,
            'quantity': item.quantity,
            'price': item.price,
            'total_price': item.quantity * item.price,
        }
        for item in order.items.all()
    ]

    order_data = {
        'order_id': order.id,
        'total_price': order.total_price,
        'status': order.status,
        'payment_status': order.payment_status,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'shipping_address': {
            'address 1':order.shipping_address.address_line_1 if order.shipping_address else None,
            'address 2': order.shipping_address.address_line_2 if order.shipping_address else None,
            'city': order.shipping_address.city if order.shipping_address.city else None,
            'state': order.shipping_address.state if order.shipping_address.state else None,
            'country': order.shipping_address.country if order.shipping_address.country else None,
            'postal code': order.shipping_address.postal_code if order.shipping_address.postal_code else None,
        },
        'items': order_items
    }

    return Response(order_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def shipping_methods(request):
    """
    List all available shipping methods.
    """
    shipping_methods = ShippingMethod.objects.all()

    methods = [
        {
            'id': method.id,
            'name': method.name,
            'price': method.price,
            'estimated_delivery_days': method.estimated_delivery_days
        }
        for method in shipping_methods
    ]

    return Response({'shipping_methods': methods}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_orders(request):
    """
    Fetch a list of all orders for the authenticated user. Supports pagination.
    
    Query Parameters:
    - page: (int) Optional. The page number for paginated results. Default is 1.
    
    Response:
    - Returns a paginated list of orders, including items and payment details.
    
    Status Codes:
    - 200: Success, with paginated order data.
    """
    user = request.user
    page = request.query_params.get('page', 1)

    # Fetch all orders for the authenticated user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # Paginate the orders (10 per page)
    paginator = Paginator(orders, 10)
    try:
        paginated_orders = paginator.page(page)
    except:
        paginated_orders = paginator.page(1)

    # Serialize the paginated orders
    serializer = OrderSerializer(paginated_orders, many=True)

    response_data = {
        'orders': serializer.data,
        'page': paginated_orders.number,
        'total_pages': paginated_orders.paginator.num_pages,
    }

    return Response(response_data, status=status.HTTP_200_OK)

class ShippingAddressListCreate(generics.ListCreateAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ShippingAddressRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]