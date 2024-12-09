from django.urls import path
from .views import *


urlpatterns = [
    path('banners', BannerListView.as_view(), name='banner-list'),
    path('categories',categories_list,name='categories_list'),
    path('products',variant_list,name='product_list'),
    path('products/<slug:slug>/', product_variant_detail, name='product_detail'),
    path('popular-varients', popular_variants, name='popular_variants'),
    path('recently-viewed-variants', RecentlyViewedProductVariantView.as_view(), name='recently-viewed-variants'),
    path('top-offer-product-variants', TopOfferProductVariantsView.as_view(), name='top-offer-product-variants'),
]