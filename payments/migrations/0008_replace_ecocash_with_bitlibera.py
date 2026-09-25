from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('payments', '0007_blink_payment_fields')]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('TEST', 'Faux provider'),
                    ('lumicash', 'Lumicash'),
                    ('bitlibera', 'Bitlibera'),
                    ('bank_transfer', 'Virement bancaire'),
                    ('bitcoin', 'Bitcoin via Blink Lightning'),
                ],
                default='TEST',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='withdrawal',
            name='method',
            field=models.CharField(
                choices=[
                    ('lumicash', 'Lumicash'),
                    ('bitlibera', 'Bitlibera'),
                    ('bank_transfer', 'Virement bancaire'),
                    ('bitcoin', 'Bitcoin'),
                ],
                max_length=20,
            ),
        ),
    ]
