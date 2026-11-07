import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("sales", "0001_initial"), ("cash", "0001_initial")]
    operations = [
        migrations.AddField(model_name="sale", name="cash_shift", field=models.ForeignKey(
            to="cash.cashshift", related_name="sales", on_delete=django.db.models.deletion.PROTECT,
            null=True, blank=True,
        ))
    ]
