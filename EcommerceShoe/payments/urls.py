from django.urls import path
from . import views

urlpatterns=[
     path('create_order/', views.CreateOrderView.as_view(), name='create_order'),
    path('verify_payment/', views.VerifyPaymentView.as_view(), name='verify_payment'),
]