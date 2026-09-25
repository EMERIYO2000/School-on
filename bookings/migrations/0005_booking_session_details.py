from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('bookings', '0004_bookingreview')]

    operations = [
        migrations.AddField('booking', 'duration', models.PositiveSmallIntegerField(default=60)),
        migrations.AddField('booking', 'subject', models.CharField(blank=True, max_length=200)),
        migrations.AddField('booking', 'notes', models.TextField(blank=True)),
        migrations.AddField('booking', 'mode', models.CharField(blank=True, max_length=30)),
    ]
