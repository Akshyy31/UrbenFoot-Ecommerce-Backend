from django.utils import timezone
from django.shortcuts import render
from rest_framework.views import APIView
from accounts.permissions import IsAdminRole
from accounts.models import CustomeUser
from .serializers import UserListSerializer
from rest_framework.response import Response
from rest_framework import status
from UrbenFoot.models import ProductModel, CategoryModel
from UrbenFoot.serializers import ProductSerializer, CategorySerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, F
from payments.models import OrderModel, OrderItemModel
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


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
        search_query = request.query_params.get("search", "")
        category_name = request.query_params.get("category", "")

        paginator = PageNumberPagination()
        paginator.page_size = 20  # Default per-page size

        # queryset
        products = ProductModel.objects.all().order_by("-created_at")

        # category filter
        if category_name:
            products = products.filter(category__name__iexact=category_name)

        #  search filter
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query)
                | Q(brand__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        # Paginate results
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(
            result_page, many=True, context={"request": request}
        )
        response = paginator.get_paginated_response(serializer.data)

        # Rename key to `products`
        response.data["products"] = response.data.pop("results")

        return response


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

    def get(self, request, id, *args, **kwargs):
        try:
            product = ProductModel.objects.get(id=id)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductModel.DoesNotExist:
            return Response(
                {"message": "Product Not Found"}, status=status.HTTP_404_NOT_FOUND
            )

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
        # 1. Total products purchased
        total_products = (
            OrderItemModel.objects.aggregate(total=Sum("quantity"))["total"] or 0
        )

        # 2. Total revenue generated
        total_revenue = (
            OrderItemModel.objects.aggregate(total=Sum(F("quantity") * F("price")))[
                "total"
            ]
            or 0
        )

        # 3. Monthly sales

        # 4. Orders Data
        orders_data = []
        orders = (
            OrderModel.objects.select_related("user")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

        for order in orders:
            items = order.items.all()
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
                    "email": order.user.email,
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


class UpdateOrderStatus(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, order_id):
        try:
            order = OrderModel.objects.get(id=order_id)
            print("order:  ", order)
        except OrderModel.DoesNotExist:
            return Response(
                {"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        status_value = request.data.get("status")
        if status_value not in dict(OrderModel.STATUS_CHOICES):
            return Response(
                {"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )
        order.status = status_value
        order.save()
        # Build product summary
        product_list = "\n".join(
            [f"- {item.product.name} (x{item.quantity})" for item in order.items.all()]
        )
        # Prepare email
        subject = f"Your Order ID #{order.id} is now {status_value.capitalize()}"
        message = f"""
Hi {order.user},

Your order #{order.id} status has been Ready to {status_value.upper()}.

Items:
{product_list}

Thank you for shopping with us!
– UrbanFoot Team
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("Email sending failed:", e)

        return Response(
            {"message": "Status updated and email sent successfully"},
            status=status.HTTP_200_OK,
        )


class OrderStatusSummaryView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        # Summary counts
        summary = {
            "delivered": OrderModel.objects.filter(status="DELIVERED").count(),
            "cancelled": OrderModel.objects.filter(status="CANCELLED").count(),
        }

        # Delivered orders with user + product details
        delivered_orders = (
            OrderModel.objects.filter(status="DELIVERED")
            .select_related("user")
            .prefetch_related("items__product")
        )

        delivered_products = []
        for order in delivered_orders:
            for item in order.items.all():
                delivered_products.append(
                    {
                        "order_id": order.id,
                        "user_id": order.user.id,
                        "username": order.user.username,
                        "user_email": order.user.email,
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.price),
                        "subtotal": float(item.get_subtotal()),
                        "delivered_at": (
                            order.updated_at
                            if hasattr(order, "updated_at")
                            else order.created_at
                        ),
                    }
                )

        # Cancelled orders with user + product details
        cancelled_orders = (
            OrderModel.objects.filter(status="CANCELLED")
            .select_related("user")
            .prefetch_related("items__product")
        )

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_sales = (
            OrderModel.objects.filter(created_at__gte=month_start).aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        cancelled_products = []
        for order in cancelled_orders:
            for item in order.items.all():
                cancelled_products.append(
                    {
                        "order_id": order.id,
                        "user_id": order.user.id,
                        "username": order.user.username,
                        "user_email": order.user.email,
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.price),
                        "subtotal": float(item.get_subtotal()),
                        "cancelled_at": (
                            order.updated_at
                            if hasattr(order, "updated_at")
                            else order.created_at
                        ),
                    }
                )

        most_ordered = (
            OrderItemModel.objects.values("product__id", "product__name")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

        top_5_products = [
            {
                "product_id": item["product__id"],
                "product_name": item["product__name"],
                "total_quantity_sold": item["total_quantity"],
            }
            for item in most_ordered
        ]

        return Response(
            {
                "summary": summary,
                "delivered_products": delivered_products,
                "cancelled_products": cancelled_products,
                "top_5_most_ordered_products": top_5_products,
                "monthly_sales": float(monthly_sales),
            },
            status=status.HTTP_200_OK,
        )


class CategoryListView(APIView):
    def get(self, request):
        categories = CategoryModel.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class BlockUnblockUserView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, user_id):
        try:
            user = CustomeUser.objects.get(id=user_id)
            action = request.data.get("action")
            if action == "block":
                user.blocked = True
                user.status = "blocked"
                user.save()
                subject = "Account Blocked Notification"
                message = (
                    f"Hi {user.username}, your account has been blocked by the admin."
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

                return Response(
                    {"message": f"{user.username} has been blocked."},
                    status=status.HTTP_200_OK,
                )

            elif action == "unblock":
                user.blocked = False
                user.status = "active"
                user.save()
                subject = "Account Unblocked Notification"
                message = f"Hi {user.username}, your account has been unblocked. You can now access your account again."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                return Response(
                    {"message": f"{user.username} has been unblocked."},
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {"error": "Invalid action. Use 'block' or 'unblock'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except CustomeUser.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
