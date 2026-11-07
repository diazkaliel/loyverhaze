from rest_framework import serializers
from .models import StockMovement


class StockMovementCreateSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    store_id = serializers.UUIDField()
    quantity_delta = serializers.DecimalField(max_digits=18, decimal_places=3)
    reason = serializers.ChoiceField(choices=[StockMovement.Reason.RECEIPT, StockMovement.Reason.ADJUSTMENT])
    note = serializers.CharField(required=False, allow_blank=True, max_length=300)
    idempotency_key = serializers.UUIDField()

    def validate(self, data):
        if data["quantity_delta"] == 0:
            raise serializers.ValidationError({"quantity_delta": "La cantidad no puede ser cero."})
        if data["reason"] == StockMovement.Reason.RECEIPT and data["quantity_delta"] < 0:
            raise serializers.ValidationError({"quantity_delta": "Las entradas deben ser positivas."})
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    username = serializers.CharField(source="performed_by.username", read_only=True)

    class Meta:
        model = StockMovement
        fields = ("id", "item", "item_name", "store", "store_name",
                  "quantity_delta", "resulting_quantity", "reason", "note", "username", "created_at")
