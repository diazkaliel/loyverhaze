import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Organization", fields=[
            ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ("name", models.CharField(max_length=160)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name="Store", fields=[
            ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ("name", models.CharField(max_length=160)),
            ("is_active", models.BooleanField(default=True)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="stores", to="organization.organization")),
        ]),
        migrations.CreateModel(name="Membership", fields=[
            ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ("role", models.CharField(choices=[("owner", "Propietario"), ("manager", "Administrador"), ("cashier", "Cajero")], max_length=20)),
            ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="organization.organization")),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="organization_memberships", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.AddConstraint(model_name="store", constraint=models.UniqueConstraint(fields=("organization", "name"), name="store_unique_name_per_organization")),
        migrations.AddConstraint(model_name="membership", constraint=models.UniqueConstraint(fields=("organization", "user"), name="one_membership_per_organization_user")),
    ]
