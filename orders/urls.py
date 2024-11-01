from django.urls import path
from . import views

urlpatterns = [
    # Checkout and Order-related URLs
    path('', views.checkout, name='checkout'),
    path('payment/', views.process_payment, name='process_payment'),
    path('order-view/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.all_orders, name='all_orders'),
    
    # Shipping methods
    path('shipping-methods/', views.shipping_methods, name='shipping_methods'),
    path('shipping-addresses/', views.ShippingAddressListCreate.as_view(), name='shipping-address-list-create'),
    path('shipping-addresses/<int:pk>/', views.ShippingAddressRetrieveUpdateDelete.as_view(), name='shipping-address-detail'),
]