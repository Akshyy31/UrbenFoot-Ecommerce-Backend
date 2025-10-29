from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class CustomeUser(AbstractUser):
    ROLE_CHOICES=(
        ('user','user'),
       ( 'admin','admin')
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_pic= models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    email = models.EmailField(unique=True)
    role= models.CharField(max_length=20,choices=ROLE_CHOICES,default='user')
    status=models.CharField(max_length=100,default='active')
    blocked=models.BooleanField(default=False)
    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username}'s Profile" 
    
@receiver(post_save, sender=CustomeUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomeUser)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
