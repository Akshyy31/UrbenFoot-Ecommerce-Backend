from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path(
        "create_order/",
        csrf_exempt(views.CreateOrderView.as_view()),
        name="create_order",
    ),
    path(
        "verify_payment/",
        csrf_exempt(views.VerifyPaymentView.as_view()),
        name="verify_payment",
    ),
]
