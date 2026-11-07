from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("inventory", "0001_initial")]
    operations = [
        migrations.AlterField(model_name="stockmovement", name="reason",
            field=models.CharField(max_length=20, choices=[("receipt", "Entrada"), ("adjustment", "Ajuste"), ("sale", "Venta")])),
    ]
