from rest_framework import serializers
from .models import Category, Item

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "color", "created_at")
        read_only_fields = ("id", "created_at")

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ("id", "name", "category", "sku", "barcode", "description", "price", "cost", "available_for_sale", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
