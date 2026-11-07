from rest_framework import serializers
from .models import CashMovement, CashShift


class ShiftOpenSerializer(serializers.Serializer):
    store_id = serializers.UUIDField()
    opening_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0)


class ShiftCloseSerializer(serializers.Serializer):
    counted_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0)


class MovementCreateSerializer(serializers.Serializer):
    shift_id = serializers.UUIDField()
    kind = serializers.ChoiceField(choices=CashMovement.Kind.choices)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value="0.01")
    note = serializers.CharField(max_length=300, allow_blank=False)


class CashShiftSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    opened_by_username = serializers.CharField(source="opened_by.username", read_only=True)
    closed_by_username = serializers.CharField(source="closed_by.username", read_only=True, allow_null=True)

    class Meta:
        model = CashShift
        fields = ("id", "store", "store_name", "status", "opening_amount",
                  "expected_amount", "counted_amount", "difference", "opened_at",
                  "closed_at", "opened_by_username", "closed_by_username")


class CashMovementSerializer(serializers.ModelSerializer):
    performed_by_username = serializers.CharField(source="performed_by.username", read_only=True)

    class Meta:
        model = CashMovement
        fields = ("id", "shift", "kind", "amount", "note", "performed_by_username", "created_at")
