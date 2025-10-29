from rest_framework import serializers
from accounts.models import CustomeUser
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomeUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
        ]

    def validate_password(self, val):
        length = len(val)
        if length < 8:
            raise serializers.ValidationError("password character must be 8 characters")
        return val

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        # Remove password2 before creating the user
        validated_data.pop("password2")
        user = CustomeUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                }
            else:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError(
                "Both username and password are required."
            )
