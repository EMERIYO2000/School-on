from django.db import models

from .user_models import CustomUser


class LearnerProfile(models.Model):
    """Profil apprenant — « progressive profiling » (spec §12 et §13).

    Tous les champs sont optionnels : un utilisateur doit pouvoir explorer
    School On sans remplir un long formulaire d'inscription. Le pourcentage de
    complétion est recalculé automatiquement à chaque sauvegarde.
    """
    INTEREST_CHOICES = [
        ('informatique', 'Informatique'),
        ('programmation', 'Programmation'),
        ('mathematiques', 'Mathématiques'),
        ('sciences', 'Sciences'),
        ('design', 'Design'),
        ('business', 'Business'),
        ('langues', 'Langues'),
        ('ia', 'Intelligence artificielle'),
        ('sante', 'Santé'),
        ('agriculture', 'Agriculture'),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='learner_profile',
    )
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Burundi')
    city = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(
        max_length=100, blank=True,
        help_text="Niveau scolaire, ex. 9ème année, Terminale, Licence 1…",
    )
    school_name = models.CharField(max_length=150, blank=True)
    interests = models.JSONField(
        default=list, blank=True,
        help_text="Domaines d'intérêt choisis par l'apprenant (liste de chaînes).",
    )
    learning_goal = models.TextField(blank=True)
    profile_completion = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil apprenant'
        verbose_name_plural = 'Profils apprenants'

    def __str__(self):
        return f"Profil apprenant de {self.user.username}"

    #: Champs pris en compte dans la complétion, avec leur poids respectif.
    COMPLETION_FIELDS = (
        ('first_name', 10),
        ('last_name', 10),
        ('avatar', 10),
        ('phone_number', 10),
        ('date_of_birth', 10),
        ('city', 10),
        ('education_level', 10),
        ('interests', 15),
        ('learning_goal', 15),
    )

    def compute_completion(self):
        """Recalcule le pourcentage de complétion du profil (0-100)."""
        score = 0
        for field, weight in self.COMPLETION_FIELDS:
            source = self.user if field in {'first_name', 'last_name', 'avatar', 'phone_number'} else self
            value = getattr(source, field, None)
            if value not in (None, '', [], {}):
                score += weight
        return min(100, score)

    def save(self, *args, **kwargs):
        self.profile_completion = self.compute_completion()
        super().save(*args, **kwargs)
