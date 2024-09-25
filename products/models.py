from django.db import models
from accounts.models import User
from .utils import Category_image_renamer
from uuid import uuid4
from django.utils.text import slugify 
from core.utils import Base_content
from django.core.cache import cache

# Create your models here.
class Category(Base_content):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=Category_image_renamer,null=True,blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name+str(uuid4())[:10])
        return super().save(*args,**kwargs)

class SubCategory(Base_content):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='categories')
    name = models.CharField(max_length=500)
    image = models.ImageField(upload_to=Category_image_renamer,null=True,blank=True)
    
    def __str__(self):
        return self.name
    
class ProductTag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    total_stock = models.IntegerField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    tags = models.ManyToManyField(ProductTag, related_name='products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50,choices=(('Active','Active'),('Inactive','Inactive')),default='Active')
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Clear the product detail cache when a product is saved
        cache_key = f"product_detail_{self.slug}"
        cache.delete(cache_key)
        
        if not self.slug:
            self.slug = slugify(self.name+str(uuid4())[:10])
            
        return super().save(*args,**kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} Image"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=100)
    variant_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.variant_name}"

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Stock(models.Model):
    product = models.ForeignKey(Product, related_name='stock', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, related_name='stock', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"


class Review(models.Model):
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review by {self.user.email} on {self.product.name}"
