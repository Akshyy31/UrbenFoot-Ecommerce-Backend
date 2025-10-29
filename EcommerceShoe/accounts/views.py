from django.shortcuts import render
from rest_framework.views import APIView
from accounts.serializers import RegisterSerializer,LoginSerializer
from rest_framework.response import Response
from rest_framework import status

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
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
