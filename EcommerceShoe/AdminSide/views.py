from django.shortcuts import render
from rest_framework.views import APIView
from accounts.permissions import IsAdminRole
from accounts.models import CustomeUser
from .serializers import UserListSerializer
from rest_framework.response import Response
from rest_framework import status
from UrbenFoot.models import ProductModel
from UrbenFoot.serializers import ProductSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, F
from payments.models import OrderModel, OrderItemModel
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


class UserListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        users = CustomeUser.objects.filter(role="user")
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, id, *args, **kwargs):
        try:
            user = CustomeUser.objects.get(id=id)
            serializer = UserListSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomeUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ProductListViewForAdmin(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        category_name = request.query_params.get("category")
        if category_name:
            products = ProductModel.objects.filter(category__name__iexact=category_name)
        else:
            products = ProductModel.objects.all()
        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response({"products": serializer.data})


class ProducDetailViewForAdmin(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, id, *args, **kwargs):
        try:
            product = ProductModel.objects.get(id=id)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductModel.DoesNotExist:
            return Response(
                {"message": "Product Not Found"}, status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name="dispatch")
class ProductManagementViewForAdd(APIView):

    permission_classes = [IsAdminRole]

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductManagement(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, id, *args, **kwargs):
        try:
            product = ProductModel.objects.get(id=id)
        except ProductModel.DoesNotExist:
            return Response({"message": "Not FOund"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "product updated succesfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, *args, **kwwargs):
        try:
            product = ProductModel.objects.get(id=id)
            product.delete()
            return Response({"message": "product deleted"})

        except ProductModel.DoesNotExist:
            return Response(
                {"message": "product Not Found"}, status=status.HTTP_404_NOT_FOUND
            )


class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]
    def get(self, request, *args, **kwargs):
        # 1 Total products purchased
        total_products = (
            OrderItemModel.objects.aggregate(total=Sum("quantity"))["total"] or 0
        )
        # 2 Total revenue generated
        total_revenue = (
            OrderItemModel.objects.aggregate(total=Sum(F("quantity") * F("price")))[
                "total"
            ]
            or 0
        )
        # 3 Order details
        orders_data = []
        orders = OrderModel.objects.all().order_by("-created_at")
        for order in orders:
            items = order.items.all()                              # related_name='items' in OrderItemModel
            products = [
                {
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.price),
                    "subtotal": float(item.get_subtotal()),
                }
                for item in items
            ]

            orders_data.append(
                {
                    "order_id": order.id,
                    "user": order.user.username,
                    "status": order.status,
                    "total_amount": float(order.total_amount),
                    "created_at": order.created_at,
                    "products": products,
                    "shipping_address": {
                        "address": order.address,
                        "city": order.city,
                        "state": order.state,
                        "pincode": order.pincode,
                        "landmark": order.landmark,
                        "phone": order.phone,
                    },
                }
            )

        return Response(
            {
                "total_products_purchased": total_products,
                "total_revenue_generated": float(total_revenue),
                "orders": orders_data,
            },
            status=status.HTTP_200_OK,
        )
