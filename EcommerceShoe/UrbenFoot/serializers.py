from rest_framework import serializers
from UrbenFoot.models import CategoryModel, ProductModel, CartModel, WishListModel
from payments.models import OrderItemModel,OrderModel


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CategoryModel
        fields = ["id", "name"]

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image1 = serializers.SerializerMethodField()
    image2 = serializers.SerializerMethodField()
    image3 = serializers.SerializerMethodField()
   
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
   
    def get_image1(self, obj):
        request = self.context.get('request')
        if obj.image1:
            return request.build_absolute_uri(obj.image1.url)
        return None
   
    def get_image2(self, obj):
        request = self.context.get('request')
        if obj.image2:
            return request.build_absolute_uri(obj.image2.url)
        return None
   
    def get_image3(self, obj):
        request = self.context.get('request')
        if obj.image3:
            return request.build_absolute_uri(obj.image3.url)
        return None
   
   

    category = serializers.SlugRelatedField(
        slug_field="name",  # field from Category to show
        queryset=CategoryModel.objects.all(),
    )

    class Meta:
        model = ProductModel
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product=ProductSerializer()
    class Meta:
        model = CartModel
        fields = ["id", "user", "product", "quantity", "total_price"]
        read_only_fields = ["user", "total_price"]

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )
    product=ProductSerializer(read_only=True)
    class Meta:
        model = WishListModel
        fields = ["id", "product", "product_name", "product_price", "added_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItemModel
        fields = ['id', 'product', 'quantity', 'price', 'get_subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            'id',
            'user',
            'total_amount',
            'status',
            'razorpay_order_id',
            'razorpay_payment_id',
            'razorpay_signature',
            'created_at',
            'updated_at',
            'address',
            'city',
            'state',
            'pincode',
            'landmark',
            'phone',
            'items',
        ]
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']


