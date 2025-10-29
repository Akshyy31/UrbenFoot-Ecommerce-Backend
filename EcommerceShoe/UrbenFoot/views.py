from django.shortcuts import render
from rest_framework.views import APIView
from UrbenFoot.models import ProductModel
from rest_framework.response import Response
from .serializers import ProductSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class ProductListView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        category_name=request.query_params.get('category')
        if category_name:
            products=ProductModel.objects.filter(category__name__iexact=category_name)
        else:
            products=ProductModel.objects.all()
            
        serilizer=ProductSerializer(products,many=True)
        return Response({"products":serilizer.data})
    
class ProductDetailView(APIView):
    def get(self, request, pk):
        try:
            product = ProductModel.objects.get(id=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except ProductModel.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

            
            
        
        
