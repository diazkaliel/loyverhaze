import uuid
from django.conf import settings
from django.db import models


class CashShift(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Abierto"
        CLOSED = "closed", "Cerrado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organization.Organization", on_delete=models.PROTECT)
    store = models.ForeignKey("organization.Store", on_delete=models.PROTECT, related_name="cash_shifts")
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="opened_cash_shifts")
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="closed_cash_shifts", null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    opening_amount = models.DecimalField(max_digits=14, decimal_places=2)
    expected_amount = models.DecimalField(max_digits=14, decimal_places=2)
    counted_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    difference = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]
        constraints = [
            models.UniqueConstraint(fields=["store"], condition=models.Q(status="open"), name="one_open_shift_per_store"),
            models.CheckConstraint(condition=models.Q(opening_amount__gte=0), name="shift_opening_nonnegative"),
            models.CheckConstraint(condition=models.Q(expected_amount__gte=0), name="shift_expected_nonnegative"),
        ]


class CashMovement(models.Model):
    class Kind(models.TextChoices):
        IN = "in", "Entrada de efectivo"
        OUT = "out", "Salida de efectivo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shift = models.ForeignKey(CashShift, on_delete=models.PROTECT, related_name="movements")
    kind = models.CharField(max_length=3, choices=Kind.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.CharField(max_length=300)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.CheckConstraint(condition=models.Q(amount__gt=0), name="cash_movement_positive")]
