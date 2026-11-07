from rest_framework import serializers
from .models import Category, Item


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "color", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_name(self, value):
        org = self.context["organization"]
        existing = Category.objects.filter(organization=org, name=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError("Esta categoría ya existe en la organización.")
        return value


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(), allow_null=True, required=False
    )

    class Meta:
        model = Item
        fields = ("id", "name", "category", "sku", "barcode", "description", "price", "cost", "available_for_sale", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def get_fields(self):
        fields = super().get_fields()
        if "organization" in self.context:
            fields["category"].queryset = Category.objects.filter(organization=self.context["organization"])
        return fields

    def validate_sku(self, value):
        existing = Item.objects.filter(organization=self.context["organization"], sku=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError("Esta referencia ya existe en la organización.")
        return value

    def validate(self, attrs):
        org = self.context["organization"]
        cat = attrs.get("category", self.instance.category if self.instance else None)
        if cat is not None and cat.organization_id != org.pk:
            raise serializers.ValidationError({"category": "La categoría pertenece a otra organización."})
        return attrs
