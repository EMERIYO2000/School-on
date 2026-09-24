from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ('SYSTEM', 'Système'),
        ('COURSE', 'Cours'),
        ('QUIZ', 'Quiz'),
        ('PAYMENT', 'Paiement'),
        ('BOOKING', 'Réservation'),
        ('PROFILE', 'Profil'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SYSTEM')
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient} - {self.title}'


class DeviceToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_token')
    token = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, default='android', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Token appareil'
        verbose_name_plural = 'Tokens appareils'

    def __str__(self):
        return f'{self.user} - {self.platform}'
