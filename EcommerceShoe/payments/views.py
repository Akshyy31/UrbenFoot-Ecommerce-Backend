# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import razorpay
from UrbenFoot.models import CartModel
from .models import OrderModel, OrderItemModel
from UrbenFoot.serializers import OrderSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name="dispatch")
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Extract address data 
        address_data = {
            "address": request.data.get("address"),
            "city": request.data.get("city"),
            "state": request.data.get("state"),
            "pincode": request.data.get("pincode"),
            "landmark": request.data.get("landmark", ""),
            "phone": request.data.get("phone"),
        }

        # Validate required fields only
        required_fields = ["address", "city", "state", "pincode", "phone"]
        missing = [f for f in required_fields if not address_data.get(f)]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=400)

        #  Get cart items
        cart_items = CartModel.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        
        total = sum(item.product.price * item.quantity for item in cart_items)

        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(total * 100), "currency": "INR", "payment_capture": 1}
        )

        # Save order in DB
        order = OrderModel.objects.create(
            user=user,
            total_amount=total,
            razorpay_order_id=razorpay_order["id"],
            **address_data
        )

        # Add order items
        for item in cart_items:
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        #  Clear cart after order
        cart_items.delete()

        return Response({
            "order_id": razorpay_order["id"],
            "order_db_id": order.id,
            "amount": float(total),
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
            "message": "Order created successfully",
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user

        # Get Razorpay details from request

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Verify payment signature
        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Invalid payment signature"}, status=400)

        # Update order details
        try:
            order = OrderModel.objects.get(
                user=user, razorpay_order_id=razorpay_order_id
            )
        except OrderModel.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.status = "PAID"
        order.save()

        return Response({"message": "Payment verified successfully ✅"})


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = OrderModel.objects.filter(user=request.user).prefetch_related(
            "items__product"
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
