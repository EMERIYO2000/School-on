import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    STATUS_CHOICES = [
        ('VALID', 'Valide'),
        ('REVOKED', 'Révoqué'),
    ]

    certificate_id = models.CharField(max_length=40, unique=True, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey('courses.Course', on_delete=models.PROTECT, related_name='certificates')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='issued_certificates')
    student_name = models.CharField(max_length=255, blank=True, default='')
    course_title = models.CharField(max_length=255, blank=True, default='')
    mentor_name = models.CharField(max_length=255, blank=True)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    student_signature_text = models.CharField(max_length=255, blank=True, default='')
    study_started_at = models.DateTimeField(null=True, blank=True)
    study_completed_at = models.DateTimeField(null=True, blank=True)
    mentor_signature_at_issue = models.ImageField(upload_to='certificates/signatures/', null=True, blank=True)
    school_on_signature_at_issue = models.ImageField(upload_to='certificates/signatures/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='VALID')
    issued_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']
        constraints = [
            models.UniqueConstraint(fields=['student', 'course'], name='unique_student_course_certificate'),
        ]

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f'SO-CERT-{timezone.now():%Y}-{uuid.uuid4().hex[:12].upper()}'
        if not self.student_name:
            self.student_name = self.student.get_full_name() or self.student.username
        if not self.course_title:
            self.course_title = self.course.title
        if not self.mentor_id:
            self.mentor = self.course.teacher
        if not self.mentor_name and self.mentor:
            self.mentor_name = self.mentor.get_full_name() or self.mentor.username
        if not self.student_signature_text:
            self.student_signature_text = self.student_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.certificate_id} - {self.course.title}'


class FinalProject(models.Model):
    STATUS_CHOICES = [('SUBMITTED', 'Soumis'), ('APPROVED', 'Validé'), ('REJECTED', 'Refusé')]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='final_projects')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='final_projects')
    submission = models.TextField()
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_final_projects')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['student', 'course'], name='unique_student_course_final_project')]


class CertificationProgress(models.Model):
    STATUS_CHOICES = [('NOT_STARTED', 'Non commencé'), ('IN_PROGRESS', 'En cours'), ('ELIGIBLE', 'Éligible'), ('PENDING_MENTOR_APPROVAL', 'En attente du mentor'), ('CERTIFIED', 'Certifié')]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certification_progress')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='certification_progress')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='NOT_STARTED')
    mentor_approved = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'course'], name='unique_student_course_certification_progress')]
