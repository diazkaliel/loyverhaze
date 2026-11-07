import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("organization", "0001_initial")]
    operations = [
        migrations.CreateModel(name="CashShift", fields=[
            ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ("status", models.CharField(max_length=10, default="open", choices=[("open", "Abierto"), ("closed", "Cerrado")])),
            ("opening_amount", models.DecimalField(max_digits=14, decimal_places=2)),
            ("expected_amount", models.DecimalField(max_digits=14, decimal_places=2)),
            ("counted_amount", models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)),
            ("difference", models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)),
            ("opened_at", models.DateTimeField(auto_now_add=True)),
            ("closed_at", models.DateTimeField(blank=True, null=True)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="organization.organization")),
            ("store", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="cash_shifts", to="organization.store")),
            ("opened_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="opened_cash_shifts", to=settings.AUTH_USER_MODEL)),
            ("closed_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="closed_cash_shifts", to=settings.AUTH_USER_MODEL, blank=True, null=True)),
        ], options={"ordering": ["-opened_at"]}),
        migrations.CreateModel(name="CashMovement", fields=[
            ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ("kind", models.CharField(max_length=3, choices=[("in", "Entrada de efectivo"), ("out", "Salida de efectivo")])),
            ("amount", models.DecimalField(max_digits=14, decimal_places=2)),
            ("note", models.CharField(max_length=300)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("shift", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movements", to="cash.cashshift")),
            ("performed_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ["-created_at"]}),
        migrations.AddConstraint(model_name="cashshift", constraint=models.UniqueConstraint(fields=("store",), condition=models.Q(status="open"), name="one_open_shift_per_store")),
        migrations.AddConstraint(model_name="cashshift", constraint=models.CheckConstraint(condition=models.Q(opening_amount__gte=0), name="shift_opening_nonnegative")),
        migrations.AddConstraint(model_name="cashshift", constraint=models.CheckConstraint(condition=models.Q(expected_amount__gte=0), name="shift_expected_nonnegative")),
        migrations.AddConstraint(model_name="cashmovement", constraint=models.CheckConstraint(condition=models.Q(amount__gt=0), name="cash_movement_positive")),
    ]
