from django.db import models
from accounts.models import CustomeUser
from django.conf import settings
# Create your models here.

class CategoryModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class ProductModel(models.Model):
    STOCK_CHOICES = (
        ("available", "Available"),
        ("not_available", "Not Available"),
    )
    # IS_NEW_CHOICES = (
    #     ("new", "New"),
    #     (" ", " "),
    # )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="product_images/")
    image1 = models.ImageField(upload_to="product_images/")
    image2 = models.ImageField(upload_to="product_images/")
    image3 = models.ImageField(upload_to="product_images/")
    price = models.PositiveIntegerField()
    category = models.ForeignKey(CategoryModel,related_name='products', on_delete=models.CASCADE)
    stock = models.CharField(max_length=50, choices=STOCK_CHOICES)
    quantity = models.PositiveIntegerField()
    is_new = models.BooleanField(default=False)
    brand = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class CartModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"

    @property
    def total_price(self):
        return self.product.price * self.quantity
       
class WishListModel(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='wishlist_items')
    product=models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=('user','product')    
    def __str__(self):
        return f"{self.user.first_name} - {self.product.name}"
    
 
