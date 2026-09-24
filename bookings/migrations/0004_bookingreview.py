from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bookings', '0003_booking_mentor_confirmed_booking_student_confirmed_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField()),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='review', to='bookings.booking')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]