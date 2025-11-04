from django.shortcuts import render
from rest_framework.views import APIView
from accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, CustomeUser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

# Create your views here.

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": "Registration failed!", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

class LoginView(APIView):
    def post(self, request):
        print("Incoming data:", request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer validated:", serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        print("Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    def put(self, request):
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Keep user logged in after change

        return Response(
            {"message": "Password updated successfully."}, status=status.HTTP_200_OK
        )

CustomeUser = get_user_model()
token_generator = PasswordResetTokenGenerator()

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = CustomeUser.objects.get(email=email)
        except CustomeUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # create token and uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = (
            f"http://localhost:3000/reset-password/{uid}/{token}"  # frontend link
        )
        send_mail(
            "Reset Your Password",
            f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn’t request this, ignore this email.",
            "your_email@gmail.com",
            [user.email],
            fail_silently=False,
        )
        return Response(
            {"message": "Password reset link sent to your email"},
            status=status.HTTP_200_OK,
        )

class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        password = request.data.get("password")
        if not password:
            return Response(
                {"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomeUser.objects.get(pk=uid)
        except (CustomeUser.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(
                {"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not token_generator.check_token(user, token):
            return Response(
                {"error": "Token is invalid or expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )
