from django.contrib import admin
from . models import *
# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductVarientImage)
admin.site.register(ProductTag)
admin.site.register(Varient_Type)
admin.site.register(Varient_values)
admin.site.register(Banner)
admin.site.register(Review)