from rest_framework import serializers
from .models import Order, OrderItem, Payment

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.variant_name', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product_name', 'variant_name', 'quantity', 'price']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount', 'status', 'payment_date', 'transaction_id']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'created_at', 'updated_at', 'shipping_address', 'payment_status', 'payment_method', 'items', 'payments']
