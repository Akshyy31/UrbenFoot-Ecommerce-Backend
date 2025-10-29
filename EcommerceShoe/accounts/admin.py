from django.contrib import admin
from accounts.models import CustomeUser,UserProfile
# Register your models here.

admin.site.register(CustomeUser)
admin.site.register(UserProfile)
