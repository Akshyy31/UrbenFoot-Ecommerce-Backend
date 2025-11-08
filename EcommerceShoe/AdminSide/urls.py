from django.urls import path
from . import views

urlpatterns = [
    path("userlist/", views.UserListView.as_view(), name="userlist"),
    path("userdetail/<int:id>/", views.UserDetailView.as_view(), name="userdetail"),
    path("productslist/", views.ProductListViewForAdmin.as_view(), name="productslist"),
    path(
        "productdetail/byadmin/<int:id>/",
        views.ProducDetailViewForAdmin.as_view(),
        name="productslist",
    ),
    path(
        "product/add/management/",
        views.ProductManagementViewForAdd.as_view(),
        name="product_add_management",
    ),
    path(
        "product/management/<int:id>/",
        views.ProductManagement.as_view(),
        name="product_management",
    ),
    path(
        "dash_details/",
        views.AdminDashboardView.as_view(),
        name="admin_dashboard_details",
    ),
    path('update/orders/<int:order_id>/status/', views.UpdateOrderStatus.as_view(), name='update-order-status'),
    path('order/status/summeryview/', views.OrderStatusSummaryView.as_view(), name='orderstatus-summeryview'),
    path('category/',views.CategoryListView.as_view(),name='category-view'),
    path("block-user/<int:user_id>/", views.BlockUnblockUserView.as_view(), name="block-unblock-user"),

]

