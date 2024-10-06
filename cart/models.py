from django.db import models
from accounts.models import User
from products.models import Product,ProductVariant
from core.utils import Base_content

# Create your models here.
class Cart(Base_content):
    user = models.OneToOneField(User, related_name='cart', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

class CartItem(Base_content):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='cart_items', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    cart_total = models.DecimalField(max_digits=20,decimal_places=2,null=True)

    def __str__(self):
        return f"{self.quantity} x {self.variant}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discount percentage")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Discount(models.Model):
    product = models.ForeignKey(Product, related_name='discounts', on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return f"{self.discount_percentage}% off on {self.product.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlists', on_delete=models.CASCADE)
    products = models.ManyToManyField(ProductVariant, related_name='wishlists')

    def __str__(self):
        return f"Wishlist of {self.user.email}"
