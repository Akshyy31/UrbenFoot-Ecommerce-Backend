from rest_framework import serializers
from UrbenFoot.models import CategoryModel, ProductModel, CartModel, WishListModel,ContactModel
from payments.models import OrderItemModel, OrderModel


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryModel
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    image1 = serializers.ImageField(required=False)
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)

    # Output URLs
    image_url = serializers.SerializerMethodField()
    image1_url = serializers.SerializerMethodField()
    image2_url = serializers.SerializerMethodField()
    image3_url = serializers.SerializerMethodField()

    

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "name",
            "price",
            "category",
            "stock",
            "quantity",
            "is_new",
            "brand",
            "image",
            "image1",
            "image2",
            "image3",
            "image_url",
            "image1_url",
            "image2_url",
            "image3_url",
            'description'
        ]

    # Output URLs for frontend
    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image else None

    def get_image1_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image1.url) if obj.image1 else None

    def get_image2_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image2.url) if obj.image2 else None

    def get_image3_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image3.url) if obj.image3 else None

    category = serializers.SlugRelatedField(
        slug_field="name",  # field from Category to show
        queryset=CategoryModel.objects.all(),
    )

    class Meta:
        model = ProductModel
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product = ProductSerializer()

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
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WishListModel
        fields = ["id", "product", "product_name", "product_price", "added_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItemModel
        fields = ["id", "product", "quantity", "price", "get_subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            "id",
            "user",
            "total_amount",
            "status",
            "razorpay_order_id",
            "razorpay_payment_id",
            "razorpay_signature",
            "created_at",
            "updated_at",
            "address",
            "city",
            "state",
            "pincode",
            "landmark",
            "phone",
            "items",
        ]
        read_only_fields = ["user", "status", "created_at", "updated_at"]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactModel
        fields = "__all__"