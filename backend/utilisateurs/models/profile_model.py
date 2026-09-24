from django.db import models
from utilisateurs.models.user_models import CustomUser


class TutorProfile(models.Model):
    """
    Profil professionnel complet pour les enseignants et mentors (Section 3.2 & 8.1).

    C'est le profil public du mentor : il porte le statut du parcours de
    vérification (`mentor_status`) et les informations affichables dans
    l'annuaire. Les documents sensibles et les décisions de vérification sont
    stockés séparément (`Qualification`, `VerificationRecord`) pour rester privés.
    """
    MENTOR_STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('PENDING_VERIFICATION', 'Vérification en attente'),
        ('UNDER_REVIEW', 'En cours de révision'),
        ('NEEDS_INFORMATION', 'Informations requises'),
        ('VERIFIED', 'Vérifié'),
        ('REJECTED', 'Rejeté'),
        ('SUSPENDED', 'Suspendu'),
    ]

    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='tutor_profile'
    )
    title = models.CharField(max_length=200, blank=True, help_text="Titre professionnel affiché")
    bio = models.TextField(blank=True, null=True)
    headline = models.CharField(max_length=200, blank=True, help_text="Slogan du profil mentor")
    skills = models.TextField(blank=True, null=True)
    # Spécialités saisies librement dans l'écran de vérification.
    specialties = models.JSONField(default=list, blank=True)
    experience = models.CharField(max_length=100, blank=True, help_text="Tranche d'expérience déclarée")
    education = models.TextField(blank=True, help_text="Diplômes et formations")
    certifications = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    session_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    id_document = models.CharField(
        max_length=500, blank=True,
        help_text="Référence CNI / passeport ou URL du document d'identité",
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Burundi")
    public_location = models.CharField(
        max_length=150, blank=True,
        help_text="Localisation publique volontairement imprécise (« Gitega, Burundi »).",
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Documents de vérification pour devenir mentor certifié (Section 3.2)
    identity_card = models.FileField(upload_to='tutors/id_cards/', blank=True, null=True)
    diploma = models.FileField(upload_to='tutors/diplomas/', blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    mentor_status = models.CharField(
        max_length=30, choices=MENTOR_STATUS_CHOICES, default='DRAFT',
        help_text="Statut du parcours de vérification mentor (spec User & Mentor Journey).",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Profil mentor'
        verbose_name_plural = 'Profils mentors'
        # Les noms de permissions générés restent `tutorprofile.*` : on garde
        # la compatibilité avec les migrations et l'admin Django existants.
        ordering = ['-is_verified', 'id']

    def __str__(self):
        return f"Profil Pro de {self.user.username}"

    def is_public(self):
        """Un mentor n'apparaît dans l'annuaire public que s'il est vérifié."""
        return self.mentor_status == 'VERIFIED' and self.is_verified


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
    Les documents d’identité et de diplôme sont requis pour une validation stricte du mentor.
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
    identity_card = models.FileField(upload_to='tutors/id_cards/', blank=True, null=True)
    diploma = models.FileField(upload_to='tutors/diplomas/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    review_note = models.TextField(blank=True, default='')
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentor_application_reviews',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candidature de {self.user.username} [{self.status}]"