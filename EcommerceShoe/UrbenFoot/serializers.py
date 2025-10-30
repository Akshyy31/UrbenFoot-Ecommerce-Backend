from rest_framework import serializers
from UrbenFoot.models import CategoryModel,ProductModel,CartModel,WishListModel

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',                        #field from Category to show
        queryset=CategoryModel.objects.all()
    )
    
    class Meta:
        model = ProductModel
        fields = "__all__"
        
class CartSerializer(serializers.ModelSerializer):  
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartModel
        fields = ['id', 'user', 'product', 'quantity', 'total_price']
        read_only_fields = ['user', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity
    
class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = WishListModel
        fields = ['id', 'product', 'product_name', 'product_price', 'added_at']