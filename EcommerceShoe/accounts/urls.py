from django.urls import path
from accounts import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.views.decorators.csrf import csrf_exempt

urlpatterns=[
    path('register/', views.UserRegistrationView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path ('token/refresh/',csrf_exempt(TokenRefreshView.as_view()),name='refresh-token'),
    path('user_profile/',views.UserProfileView.as_view(),name='user_profile'),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', views.ResetPasswordView.as_view(), name='reset-password'),
     path('google/', views.GoogleAuthView.as_view(), name='google_auth'),
]