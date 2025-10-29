from django.urls import path
from accounts import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns=[
    path('register/', views.UserRegistrationView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path ('token/refresh/',TokenRefreshView.as_view(),name='refresh-token')
]