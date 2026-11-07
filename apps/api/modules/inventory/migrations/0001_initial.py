import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog", "0002_organization_scope"),
        ("organization", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(name="StockBalance", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("quantity", models.DecimalField(decimal_places=3, default=0, max_digits=18)),
            ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="stock_balances", to="catalog.item")),
            ("store", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="stock_balances", to="organization.store")),
        ]),
        migrations.CreateModel(name="StockMovement", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("quantity_delta", models.DecimalField(decimal_places=3, max_digits=18)),
            ("resulting_quantity", models.DecimalField(decimal_places=3, max_digits=18)),
            ("reason", models.CharField(choices=[("receipt", "Entrada"), ("adjustment", "Ajuste")], max_length=20)),
            ("note", models.CharField(blank=True, max_length=300)),
            ("idempotency_key", models.UUIDField()),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.item")),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organization.organization")),
            ("performed_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ("store", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organization.store")),
        ], options={"ordering": ["-created_at", "-id"]}),
        migrations.AddConstraint(model_name="stockbalance", constraint=models.UniqueConstraint(fields=("item", "store"), name="unique_item_store_stock")),
        migrations.AddConstraint(model_name="stockbalance", constraint=models.CheckConstraint(condition=models.Q(quantity__gte=0), name="stock_cannot_be_negative")),
        migrations.AddConstraint(model_name="stockmovement", constraint=models.UniqueConstraint(fields=("organization", "idempotency_key"), name="unique_org_stock_request")),
        migrations.AddConstraint(model_name="stockmovement", constraint=models.CheckConstraint(condition=models.Q(resulting_quantity__gte=0), name="movement_result_nonnegative")),
    ]
