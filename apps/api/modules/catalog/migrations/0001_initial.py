import uuid
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Category", fields=[
            ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ("name", models.CharField(max_length=120, unique=True)),
            ("color", models.CharField(max_length=7, default="#64748b")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ], options={"ordering": ["name"]}),
        migrations.CreateModel(name="Item", fields=[
            ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ("name", models.CharField(max_length=200)),
            ("sku", models.CharField(max_length=40, unique=True)),
            ("barcode", models.CharField(max_length=100, blank=True)),
            ("description", models.TextField(blank=True)),
            ("price", models.DecimalField(max_digits=14, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
            ("cost", models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ("available_for_sale", models.BooleanField(default=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("updated_at", models.DateTimeField(auto_now=True)),
            ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="items", to="catalog.category")),
        ], options={"ordering": ["name"]}),
        migrations.AddConstraint(model_name="item", constraint=models.CheckConstraint(condition=models.Q(price__gte=0), name="item_price_nonnegative")),
        migrations.AddConstraint(model_name="item", constraint=models.CheckConstraint(condition=models.Q(cost__gte=0), name="item_cost_nonnegative")),
    ]
