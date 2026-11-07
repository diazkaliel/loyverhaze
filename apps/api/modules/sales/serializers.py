from rest_framework import serializers
from .models import Sale


class SaleItemInputSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3, min_value=0.001)


class CheckoutSerializer(serializers.Serializer):
    store_id = serializers.UUIDField()
    idempotency_key = serializers.UUIDField()
    lines = SaleItemInputSerializer(many=True, allow_empty=False)
    payment_method = serializers.ChoiceField(choices=Sale.PaymentMethod.choices)
    cash_received = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0)

    def validate_lines(self, value):
        ids = [x["item_id"] for x in value]
        if len(set(ids)) != len(ids):
            raise serializers.ValidationError("Cada artículo debe aparecer solo una vez.")
        if len(value) > 100:
            raise serializers.ValidationError("Máximo 100 artículos distintos por venta.")
        return value


class SaleLineSerializer(serializers.Serializer):
    item_name = serializers.CharField()
    sku = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3)
    unit_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2)


class SaleSerializer(serializers.ModelSerializer):
    lines = SaleLineSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = Sale
        fields = ("id", "store", "store_name", "cashier", "total", "cash_received",
                  "change_due", "payment_method", "created_at", "lines")
