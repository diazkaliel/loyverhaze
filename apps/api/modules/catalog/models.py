import uuid
from django.core.validators import MinValueValidator
from django.db import models

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    color = models.CharField(max_length=7, default="#64748b")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, related_name="items")
    sku = models.CharField(max_length=40, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    cost = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    available_for_sale = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="item_price_nonnegative"),
            models.CheckConstraint(condition=models.Q(cost__gte=0), name="item_cost_nonnegative"),
        ]
