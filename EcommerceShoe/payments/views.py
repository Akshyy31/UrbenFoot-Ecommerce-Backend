# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import razorpay
from UrbenFoot.models import CartModel
from .models import OrderModel, OrderItemModel


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # Get all items in the user's cart
        cart_items = CartModel.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # Calculate total amount
        total = sum(item.product.price * item.quantity for item in cart_items)

        # Create Razorpay client
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Create Razorpay order (amount must be in paise)
        razorpay_order = client.order.create(
            {"amount": int(total * 100), "currency": "INR", "payment_capture": 1}
        )

        # Create order in our database
        order = OrderModel.objects.create(
            user=user, total_amount=total, razorpay_order_id=razorpay_order["id"]
        )

        # Create OrderItems for each cart product
        for item in cart_items:
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Clear user's cart after creating order
        cart_items.delete()

        return Response(
            {
                "order_id": razorpay_order["id"],
                "total_amount": total,
                "currency": "INR",
                "key": settings.RAZORPAY_KEY_ID,
                "message": "Order created successfully",
            }
        )


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user

        # Get Razorpay details from request
        
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify payment signature
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Invalid payment signature"}, status=400)

        # Update order details
        try:
            order = OrderModel.objects.get(user=user, razorpay_order_id=razorpay_order_id)
        except OrderModel.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.status = "PAID"
        order.save()

        return Response({"message": "Payment verified successfully ✅"})
