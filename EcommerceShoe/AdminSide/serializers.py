from rest_framework import serializers
from accounts.models import CustomeUser

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomeUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'role', 'status', 'blocked']