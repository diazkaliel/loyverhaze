import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def move_legacy_catalog(apps, schema_editor):
    Organization = apps.get_model("organization", "Organization")
    Store = apps.get_model("organization", "Store")
    Membership = apps.get_model("organization", "Membership")
    Category = apps.get_model("catalog", "Category")
    Item = apps.get_model("catalog", "Item")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    org = Organization.objects.create(name="Mi negocio")
    Store.objects.create(organization_id=org.pk, name="Sucursal principal")
    Category.objects.filter(organization__isnull=True).update(organization_id=org.pk)
    Item.objects.filter(organization__isnull=True).update(organization_id=org.pk)
    # Legacy administrators may keep managing their existing test catalog.
    for user_id in User.objects.filter(is_superuser=True, is_active=True).values_list("pk", flat=True):
        Membership.objects.get_or_create(organization_id=org.pk, user_id=user_id, defaults={"role": "owner"})


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0001_initial"),
        ("catalog", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AlterField(model_name="category", name="name", field=models.CharField(max_length=120)),
        migrations.AlterField(model_name="item", name="sku", field=models.CharField(max_length=40)),
        migrations.AddField(model_name="category", name="organization", field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="categories", to="organization.organization")),
        migrations.AddField(model_name="item", name="organization", field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="items", to="organization.organization")),
        migrations.RunPython(move_legacy_catalog, migrations.RunPython.noop),
        migrations.AlterField(model_name="category", name="organization", field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="categories", to="organization.organization")),
        migrations.AlterField(model_name="item", name="organization", field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="items", to="organization.organization")),
        migrations.AddConstraint(model_name="category", constraint=models.UniqueConstraint(fields=("organization", "name"), name="category_name_unique_in_organization")),
        migrations.AddConstraint(model_name="item", constraint=models.UniqueConstraint(fields=("organization", "sku"), name="item_sku_unique_in_organization")),
    ]
