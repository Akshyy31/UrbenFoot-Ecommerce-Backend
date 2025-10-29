from django.urls import path
from UrbenFoot import views

urlpatterns=[
    path('productview/',views.ProductListView.as_view(),name='productview'),
    path('product_detail/<int:pk>/',views.ProductDetailView.as_view(),name='product_detail')
]