from django.db import models
from utilisateurs.models.user_models import CustomUser


class TutorProfile(models.Model):
    """
    Profil professionnel complet pour les enseignants et mentors (Section 3.2 & 8.1).
    """
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='tutor_profile'
    )
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    location = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Burundi")
    
    # Documents de vérification pour devenir mentor certifié (Section 3.2)
    identity_card = models.FileField(upload_to='tutors/id_cards/', blank=True, null=True)
    diploma = models.FileField(upload_to='tutors/diplomas/', blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Profil Pro de {self.user.username}"


class ParentProfile(models.Model):
    """
    Profil tuteur / parent pour le suivi de la progression et le paiement de frais (Section 3.3 & 8.1).
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    children = models.ManyToManyField(
        CustomUser,
        related_name='parents',
        blank=True
    )

    def __str__(self):
        return f"Profil Parent de {self.user.username}"


class ParentChildRelation(models.Model):
    """
    Demandes de rattachement Parent/Tuteur -> Enfant.
    """
    STATUS_CHOICES = (
        ('PENDING', 'En attente'),
        ('ACCEPTED', 'Accepté'),
        ('REJECTED', 'Refusé'),
    )
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='child_requests_sent')
    child = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='parent_requests_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('parent', 'child')


class TeacherApplication(models.Model):
    """
    Formulaire permettant à un apprenant de postuler pour devenir mentor (Section 3.2).
    """
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='teacher_applications')
    bio = models.TextField()
    skills = models.TextField()
    certificates = models.FileField(upload_to='certificates/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candidature de {self.user.username} [{self.status}]"