from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('payments', '0006_deposit_payment_request')]

    operations = [
        migrations.AddField(
            model_name='transaction', name='provider_payment_request',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='withdrawal', name='provider_response',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='transaction', name='payment_method',
            field=models.CharField(choices=[('TEST', 'Faux provider'), ('lumicash', 'Lumicash'), ('eco_cash', 'EcoCash'), ('bank_transfer', 'Virement bancaire'), ('bitcoin', 'Bitcoin via Blink Lightning')], default='TEST', max_length=20),
        ),
    ]
