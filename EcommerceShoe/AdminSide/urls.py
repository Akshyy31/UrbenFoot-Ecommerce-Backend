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
    path('dash_details/',views.AdminDashboardView.as_view(),name="admin_dashboard_details")
]


# pbkdf2_sha256$1000000$jDhts5HJCCHBhERK2Tah4I$bUXjCif2zdL1Gvo/u0zvjEeg53vvQqVF9WM9VT7MMME=
# pbkdf2_sha256$1000000$DKa3XhzSpKGj3K7pu2sC88$F0umEu41eux6HDVil32kmTVUz7UL+rio1CCbkB27owY=