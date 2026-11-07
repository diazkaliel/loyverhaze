import uuid
from django.conf import settings
from django.db import models


class Sale(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Efectivo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organization.Organization", on_delete=models.PROTECT)
    store = models.ForeignKey("organization.Store", on_delete=models.PROTECT)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    cash_shift = models.ForeignKey("cash.CashShift", on_delete=models.PROTECT, null=True, blank=True, related_name="sales")
    idempotency_key = models.UUIDField()
    total = models.DecimalField(max_digits=14, decimal_places=2)
    cash_received = models.DecimalField(max_digits=14, decimal_places=2)
    change_due = models.DecimalField(max_digits=14, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "idempotency_key"], name="unique_sale_request_per_org"),
            models.CheckConstraint(condition=models.Q(total__gte=0), name="sale_total_nonnegative"),
            models.CheckConstraint(condition=models.Q(change_due__gte=0), name="sale_change_nonnegative"),
        ]


class SaleLine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="lines")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT)
    item_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=40)
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gt=0), name="sale_line_quantity_positive")]
