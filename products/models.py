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

class Banner(Base_content):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    link_url = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class ProductTag(Base_content):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(Base_content):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    total_stock = models.IntegerField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, related_name='products', on_delete=models.CASCADE,null=True)
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


class Varient_Type(Base_content):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Varient_values(Base_content):
    varient_type = models.ForeignKey(Varient_Type,on_delete=models.CASCADE,related_name='varient_type_values')
    value = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.varient_type}-{self.value}'
    
class ProductVariant(Base_content):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    primary_varient = models.ForeignKey(Varient_values,on_delete=models.CASCADE,related_name='variant_primary_variant',null=True)
    secondary_varient = models.ForeignKey(Varient_values,on_delete=models.CASCADE,related_name='variant_secondary_variant',null=True,blank=True)
    variant_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True,null=True)
    total_stock = models.IntegerField(default=1)
    slug = models.SlugField(unique=True,null=True,blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.variant_name}"
    
    def save(self, *args, **kwargs):
        # Clear the product detail cache when a product is saved
        cache_key = f"variant_detail_{self.slug}"
        cache.delete(cache_key)
        
        if not self.slug:
            self.slug = slugify(self.product.name+str(uuid4())[:10])
            
        return super().save(*args,**kwargs)

class ProductVarientImage(Base_content):
    varient = models.ForeignKey(ProductVariant, related_name='variant_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.varient.product.name} Image"
    
    # def save(self, *args, **kwargs):
    #     # Clear the product detail cache when a product is saved
    #     cache_key = f"variant_detail_{self.slug}"
    #     cache.delete(cache_key)


class Warehouse(Base_content):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Stock(Base_content):
    product = models.ForeignKey(Product, related_name='stock', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, related_name='stock', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"


class Review(Base_content):
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review by {self.user.email} on {self.product.name}"
