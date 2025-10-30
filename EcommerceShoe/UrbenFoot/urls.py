from django.urls import path
from UrbenFoot import views

urlpatterns = [
    path("productview/", views.ProductListView.as_view(), name="productview"),
    path(
        "product_detail/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("cart_view/", views.CartView.as_view(), name="cart_view"),
    # path('add_to_cart/',views.AddToCartView.as_view(),name='add_to_cart'),
    path("wishlist_view/", views.WishlistView.as_view(), name="wishlist_view"),
    path("orders/", views.UserOrderListView.as_view(), name="user-orders"),
    path(
        "orders/<int:order_id>/",
        views.UserOrderDetailView.as_view(),
        name="order-detail",
    ),
]
