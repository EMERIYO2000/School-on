from django.db import models
from utilisateurs.models.user_models import CustomUser


class LearnerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='learner_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Burundi')
    city = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=100, blank=True, help_text='Niveau scolaire, ex. 9ème année, Terminale, Licence 1…')
    school_name = models.CharField(max_length=150, blank=True)
    interests = models.JSONField(default=list, blank=True, help_text="Domaines d'intérêt choisis par l'apprenant (liste de chaînes).")
    learning_goal = models.TextField(blank=True)
    profile_completion = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil apprenant'
        verbose_name_plural = 'Profils apprenants'


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
    # Keep legacy profile columns in sync with deployed databases/migrations.
    education = models.TextField(blank=True, default='')
    experience = models.CharField(max_length=100, blank=True, default='')
    headline = models.CharField(max_length=200, blank=True, default='')
    id_document = models.CharField(max_length=500, blank=True, default='')
    mentor_status = models.CharField(max_length=30, default='DRAFT')
    public_location = models.CharField(max_length=150, blank=True, default='')
    session_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    specialties = models.JSONField(default=list, blank=True)
    title = models.CharField(max_length=200, blank=True, default='')
    verified_at = models.DateTimeField(null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
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

    def is_public(self):
        return self.is_verified and self.is_available and self.user.is_active and self.user.is_teacher


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
