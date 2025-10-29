from rest_framework import serializers
from UrbenFoot.models import CategoryModel,ProductModel

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