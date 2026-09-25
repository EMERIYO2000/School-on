from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    
    USER_TYPE_CHOICES = (
        ('STUDENT', 'Élève / Étudiant'),
        ('TEACHER', 'Enseignant / Mentor'),
        ('PARENT', 'Parent / Tuteur'),
    )
    email = models.EmailField(unique=True, verbose_name='Adresse Email')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_premium_subscriber = models.BooleanField(default=False)
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='STUDENT')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    avatar = models.ImageField(upload_to="media/profiles/avatars/", blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fcm = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

        
class TutorRelationship(models.Model):
    """Permet à un tuteur de prendre en charge plusieurs apprenants et de payer leurs frais."""
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='managed_students')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tutors')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'student')
