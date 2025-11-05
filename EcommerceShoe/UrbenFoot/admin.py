from django.contrib import admin
from .models import ProductModel,CategoryModel,CartModel,WishListModel

# Register your models here.


admin.site.register(ProductModel)
admin.site.register(CategoryModel)
admin.site.register(WishListModel)
admin.site.register(CartModel)
