from django.shortcuts import render
from rest_framework.views import APIView
from accounts.serializers import RegisterSerializer,LoginSerializer,UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from rest_framework.permissions import IsAuthenticated

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
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response(
                {"message": "Profile not found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)
    

        