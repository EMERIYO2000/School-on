from django.db import models

from .user_models import CustomUser


MentorStatusChoices = [
    ('DRAFT', 'Brouillon'),
    ('PENDING_VERIFICATION', 'Vérification en attente'),
    ('UNDER_REVIEW', 'En cours de révision'),
    ('NEEDS_INFORMATION', 'Informations requises'),
    ('VERIFIED', 'Vérifié'),
    ('REJECTED', 'Rejeté'),
    ('SUSPENDED', 'Suspendu'),
]


class MentorApplication(models.Model):
    """Candidature mentor (spec §15 à §26 et §39).

    Porte le statut du parcours de vérification et conserve la trace des
    décisions administratives (`reviewed_at`, `reviewed_by`, `review_note`).
    """
    STATUS_CHOICES = MentorStatusChoices

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='mentor_applications'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')

    # Informations personnelles (spec §16) — l'adresse exacte n'est jamais publique.
    legal_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Burundi')
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # Motivation et présentation (spec §19)
    motivation = models.TextField(blank=True)
    professional_bio = models.TextField(blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_mentor_applications',
    )
    review_note = models.TextField(blank=True, help_text="Motif du refus ou demande d'information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Candidature mentor'
        verbose_name_plural = 'Candidatures mentor'
        ordering = ['-created_at']

    def __str__(self):
        return f"Candidature mentor #{self.pk} de {self.user.username} [{self.status}]"

    @property
    def is_open(self):
        """Une candidature ouverte peut encore être modifiée par le candidat."""
        return self.status in {'DRAFT', 'NEEDS_INFORMATION'}

    @property
    def is_verified(self):
        return self.status == 'VERIFIED'


class MentorSkill(models.Model):
    """Compétence déclarée par un candidat / mentor (spec §19 et §40)."""
    LEVEL_CHOICES = [
        ('DEBUTANT', 'Débutant'),
        ('INTERMEDIAIRE', 'Intermédiaire'),
        ('AVANCE', 'Avancé'),
        ('EXPERT', 'Expert'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentor_skills')
    application = models.ForeignKey(
        MentorApplication, on_delete=models.CASCADE, null=True, blank=True,
        related_name='skills',
    )
    domain = models.CharField(max_length=120, help_text="Domaine principal, ex. Programmation")
    specialization = models.CharField(max_length=150, blank=True, help_text="Spécialité, ex. JavaScript / Web")
    declared_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='INTERMEDIAIRE')
    years_of_experience = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Compétence mentor'
        verbose_name_plural = 'Compétences mentor'
        ordering = ['domain', 'specialization']

    def __str__(self):
        return f"{self.user.username} — {self.domain} ({self.declared_level})"


class Qualification(models.Model):
    """Diplôme, certificat ou licence déclarée par un candidat (spec §20 et §41).

    ``verification_status`` trace la vérification éventuelle auprès de la
    source. Un document uploadé n'est jamais considéré comme une preuve
    absolue (principe 3 de la spec).
    """
    QUALIFICATION_TYPES = [
        ('DIPLOMA', 'Diplôme'),
        ('CERTIFICATE', 'Certificat'),
        ('ATTESTATION', 'Attestation'),
        ('PROFESSIONAL_LICENSE', 'Licence professionnelle'),
        ('EXPERIENCE', "Preuve d'expérience"),
        ('PORTFOLIO', 'Portfolio'),
        ('OTHER', 'Autre document'),
    ]
    VERIFICATION_STATUS = [
        ('PENDING', 'En attente'),
        ('UNDER_REVIEW', 'En cours de vérification'),
        ('VERIFIED', 'Vérifié'),
        ('REJECTED', 'Rejeté'),
        ('NOT_VERIFIABLE', 'Non vérifiable'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='qualifications')
    application = models.ForeignKey(
        MentorApplication, on_delete=models.CASCADE, null=True, blank=True,
        related_name='qualifications',
    )
    qualification_type = models.CharField(max_length=30, choices=QUALIFICATION_TYPES, default='DIPLOMA')
    title = models.CharField(max_length=200)
    institution = models.CharField(max_length=200, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    document = models.FileField(upload_to='mentors/qualifications/%Y/%m/', blank=True, null=True)
    reference = models.CharField(max_length=150, blank=True, help_text="Référence ou URL externe")
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Qualification'
        verbose_name_plural = 'Qualifications'
        ordering = ['-year', 'title']

    def __str__(self):
        return f"{self.user.username} — {self.title} ({self.get_qualification_type_display()})"


class VerificationRecord(models.Model):
    """Historique traçable des décisions de vérification (spec §31 et §42).

    On n'enregistre jamais seulement ``mentor.is_verified = True`` : chaque
    décision importante doit pouvoir être expliquée plus tard (« qui a validé,
    quand, pourquoi »).
    """
    VERIFICATION_TYPES = [
        ('IDENTITY', 'Identité'),
        ('DOCUMENT', 'Documents'),
        ('SKILL', 'Compétences'),
        ('EXPERIENCE', 'Expérience'),
        ('ASSESSMENT', 'Évaluation'),
        ('INTERVIEW', 'Entretien'),
        ('STATUS', 'Décision de statut'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('IN_PROGRESS', 'En cours'),
        ('PASSED', 'Validé'),
        ('FAILED', 'Refusé'),
        ('INFO_REQUIRED', 'Informations requises'),
    ]

    application = models.ForeignKey(
        MentorApplication, on_delete=models.CASCADE, related_name='verification_records'
    )
    mentor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='verification_records'
    )
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='performed_verifications',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    document_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Décision de vérification'
        verbose_name_plural = 'Décisions de vérification'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.application_id} {self.verification_type} -> {self.status}"



class MentorAssessment(models.Model):
    """Test de compétence d'un candidat mentor (spec §24 et §43)."""
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Non commencé'),
        ('IN_PROGRESS', 'En cours'),
        ('PASSED', 'Réussi'),
        ('FAILED', 'Échoué'),
    ]

    application = models.ForeignKey(
        MentorApplication, on_delete=models.CASCADE, related_name='assessments'
    )
    skill = models.CharField(max_length=150, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    assessed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assessments_performed',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Évaluation de compétence'
        verbose_name_plural = 'Évaluations de compétence'

    def __str__(self):
        return f"{self.application_id} — {self.skill} ({self.status})"


class MentorInterview(models.Model):
    """Entretien facultatif avec l'équipe (spec §25)."""
    STATUS_CHOICES = [
        ('SCHEDULED', 'Planifié'),
        ('COMPLETED', 'Effectué'),
        ('CANCELLED', 'Annulé'),
        ('NO_SHOW', 'Absent'),
    ]

    application = models.ForeignKey(
        MentorApplication, on_delete=models.CASCADE, related_name='interviews'
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    interviewer = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mentor_interviews',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Entretien mentor'
        verbose_name_plural = 'Entretiens mentor'

    def __str__(self):
        return f"{self.application_id} — entretien {self.status}"


class MentorReport(models.Model):
    """Signalement d'un mentor par un utilisateur (spec §32 et §33).

    Le signalement déclenche une revue admin qui peut aboutir à une
    suspension du mentor.
    """
    REASON_CHOICES = [
        ('FALSE_IDENTITY', 'Fausse identité'),
        ('FALSE_QUALIFICATION', 'Fausse qualification'),
        ('INAPPROPRIATE_BEHAVIOUR', 'Comportement inapproprié'),
        ('FRAUD', 'Fraude'),
        ('HARASSMENT', 'Harcèlement'),
        ('SESSION_ISSUE', 'Problème pendant une session'),
        ('OTHER', 'Autre'),
    ]
    STATUS_CHOICES = [
        ('OPEN', 'Ouvert'),
        ('UNDER_REVIEW', 'En cours d’investigation'),
        ('RESOLVED', 'Clôturé'),
        ('DISMISSED', 'Rejeté'),
        ('ACTION_TAKEN', 'Sanction appliquée'),
    ]

    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_received')
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_filed')
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default='OTHER')
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    reviewed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reports_reviewed',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Signalement de mentor'
        verbose_name_plural = 'Signalements de mentor'
        ordering = ['-created_at']
        unique_together = ('mentor', 'reporter', 'reason')

    def __str__(self):
        return f"{self.reporter_id} -> {self.mentor_id} [{self.reason}/{self.status}]"

