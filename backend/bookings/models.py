from django.db import models
from django.conf import settings

# Create your models here.
class Booking(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'En attente de confirmation'),
        ('pending_payment', 'En attente de paiement'),
        ('accepted', 'Accepté par le professeur'),
        ('confirmed', 'Paiement confirmé'),
        ('in_progress', 'Session en cours'),
        ('rejected', 'Rejeté par le professeur'),
        ('completed', 'Session terminée'),
        ('disputed', 'Litige'),
        ('cancelled', 'Annulée'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    tutor = models.ForeignKey('utilisateurs.TutorProfile', on_delete=models.CASCADE, related_name='tutor_bookings')
    date_requested = models.DateField() # Date du cours demandé
    time_requested = models.TimeField() # Heure d'enseignement du cours
    adress = models.CharField(max_length=255) # Adresse du quartier d'un etudition
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    student_confirmed = models.BooleanField(default=False)
    mentor_confirmed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Réservation de {self.student.username} chez {self.tutor.user.username}"


class BookingReview(models.Model):
    """Avis d'un apprenant après une session réellement terminée."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis #{self.pk} pour la réservation #{self.booking_id}"
    
