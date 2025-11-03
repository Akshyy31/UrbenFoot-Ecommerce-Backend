from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from UrbenFoot.models import ProductModel, CartModel, WishListModel
from rest_framework.response import Response
from .serializers import (
    ProductSerializer,
    CartSerializer,
    WishlistSerializer,
    OrderSerializer,
)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework import status
from django.db.models import Sum, F
from rest_framework import viewsets
from payments.models import OrderItemModel, OrderModel

# Create your views here.


class ProductListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        category_name = request.query_params.get("category")
        if category_name:
            products = ProductModel.objects.filter(category__name__iexact=category_name)
        else:
            products = ProductModel.objects.all()
        # Pass request context to serializer
        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response({"products": serializer.data})


class ProductDetailView(APIView):
    def get(self, request, pk):
        try:
            product = ProductModel.objects.get(id=pk)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(serializer.data)
        except ProductModel.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all cart items with total"""
        items = CartModel.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True, context={"request": request})
        total_cart_price = sum(item.product.price * item.quantity for item in items)

        return Response(
            {"items": serializer.data, "total_cart_price": total_cart_price},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Add a product to cart or increase quantity"""
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        try:
            product = ProductModel.objects.get(id=product_id)
        except ProductModel.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        cart_item, created = CartModel.objects.get_or_create(
            user=request.user, product=product
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        serializer = CartSerializer(cart_item, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        """Update quantity of a specific cart item"""
        cart_id = request.data.get("cart_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            cart_item = CartModel.objects.get(id=cart_id, user=request.user)
        except CartModel.DoesNotExist:
            return Response(
                {"error": "Item not found in your cart"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if quantity <= 0:
            cart_item.delete()
            return Response(
                {"message": "Item removed from cart"}, status=status.HTTP_200_OK
            )
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartSerializer(cart_item, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        """Remove a single item or clear entire cart"""
        cart_id = request.data.get("cart_id")
        if cart_id:
            try:
                cart_item = CartModel.objects.get(id=cart_id, user=request.user)
                cart_item.delete()
                return Response(
                    {"message": "Item removed from cart"}, status=status.HTTP_200_OK
                )
            except CartModel.DoesNotExist:
                return Response(
                    {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            CartModel.objects.filter(user=request.user).delete()
            return Response(
                {"message": "Cart cleared successfully"}, status=status.HTTP_200_OK
            )


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = WishListModel.objects.filter(user=request.user)
        serializer = WishlistSerializer(items, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product_id")
        product = get_object_or_404(ProductModel, id=product_id)
        wishlist_item, created = WishListModel.objects.get_or_create(
            user=request.user, product=product
        )
        if not created:
            return Response(
                {"message": "Already in wishlist"}, status=status.HTTP_200_OK
            )
        serializer = WishlistSerializer(wishlist_item, context={"request": request})
        return Response(
            {"wishlist_items": serializer.data}, status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        product_id = request.data.get("product_id")
        WishListModel.objects.filter(user=request.user, product_id=product_id).delete()
        return Response({"message": "Removed from wishlist"}, status=status.HTTP_200_OK)


class UserOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = OrderModel.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True,context={"request":request})
        return Response(serializer.data)


class UserOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = OrderModel.objects.get(id=order_id, user=request.user)
        except OrderModel.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        serializer = OrderSerializer(order,context={"request":request})
        return Response(serializer.data)
