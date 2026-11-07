import uuid
from django.conf import settings
from django.db import models


class StockBalance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, related_name="stock_balances")
    store = models.ForeignKey("organization.Store", on_delete=models.PROTECT, related_name="stock_balances")
    quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["item", "store"], name="unique_item_store_stock"),
            models.CheckConstraint(condition=models.Q(quantity__gte=0), name="stock_cannot_be_negative"),
        ]


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        RECEIPT = "receipt", "Entrada"
        ADJUSTMENT = "adjustment", "Ajuste"
        SALE = "sale", "Venta"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organization.Organization", on_delete=models.PROTECT)
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT)
    store = models.ForeignKey("organization.Store", on_delete=models.PROTECT)
    quantity_delta = models.DecimalField(max_digits=18, decimal_places=3)
    resulting_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    reason = models.CharField(max_length=20, choices=Reason.choices)
    note = models.CharField(max_length=300, blank=True)
    idempotency_key = models.UUIDField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "idempotency_key"], name="unique_org_stock_request"),
            models.CheckConstraint(condition=models.Q(resulting_quantity__gte=0), name="movement_result_nonnegative"),
        ]
