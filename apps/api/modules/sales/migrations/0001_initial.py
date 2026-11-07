import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organization", "0001_initial"),
        ("catalog", "0002_organization_scope"),
    ]
    operations = [
        migrations.CreateModel(name="Sale", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("idempotency_key", models.UUIDField()),
            ("total", models.DecimalField(max_digits=14, decimal_places=2)),
            ("cash_received", models.DecimalField(max_digits=14, decimal_places=2)),
            ("change_due", models.DecimalField(max_digits=14, decimal_places=2)),
            ("payment_method", models.CharField(choices=[("cash", "Efectivo")], default="cash", max_length=15)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("cashier", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organization.organization")),
            ("store", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organization.store")),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="SaleLine", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("item_name", models.CharField(max_length=200)),
            ("sku", models.CharField(max_length=40)),
            ("quantity", models.DecimalField(max_digits=14, decimal_places=3)),
            ("unit_price", models.DecimalField(max_digits=14, decimal_places=2)),
            ("line_total", models.DecimalField(max_digits=14, decimal_places=2)),
            ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.item")),
            ("sale", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lines", to="sales.sale")),
        ]),
        migrations.AddConstraint(model_name="sale", constraint=models.UniqueConstraint(fields=("organization", "idempotency_key"), name="unique_sale_request_per_org")),
        migrations.AddConstraint(model_name="sale", constraint=models.CheckConstraint(condition=models.Q(total__gte=0), name="sale_total_nonnegative")),
        migrations.AddConstraint(model_name="sale", constraint=models.CheckConstraint(condition=models.Q(change_due__gte=0), name="sale_change_nonnegative")),
        migrations.AddConstraint(model_name="saleline", constraint=models.CheckConstraint(condition=models.Q(quantity__gt=0), name="sale_line_quantity_positive")),
    ]
