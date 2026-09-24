from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    """Matières ou domaines (ex: Mathématiques, Physique, Examen d'État)[cite: 13, 17, 18]"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='subjects/icons/', blank=True, null=True)

    class Meta:
        verbose_name = 'Catégorie / Matière'
        verbose_name_plural = 'Catégories / Matières'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StateExam(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('SUBMITTED', 'Soumis'),
        ('PUBLISHED', 'Publié'),
        ('ARCHIVED', 'Archivé'),
    ]
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    subject = models.CharField(max_length=100)
    session = models.CharField(max_length=100, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='state_exams')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'subject', 'title']


class ExamQuestion(models.Model):
    exam = models.ForeignKey(StateExam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)


class ExamChoice(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class ArchiveResource(models.Model):
    RESOURCE_TYPES = [
        ('DOCUMENT', 'Document'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Vidéo'),
        ('OTHER', 'Autre fichier'),
    ]
    exam = models.ForeignKey(StateExam, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='DOCUMENT')
    file = models.FileField(upload_to='exam_archives/%Y/%m/')
    description = models.TextField(blank=True)
    downloadable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Course(models.Model):
    """Un cours complet rédigé par un enseignant/mentor[cite: 13, 17, 18]"""
    LEVEL_CHOICES = [
        ('DEBUTANT', 'Débutant'),
        ('INTERMEDIAIRE', 'Intermédiaire'),
        ('AVANCE', 'Avancé'),
    ]

    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    learning_objectives = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='taught_courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='DEBUTANT')
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    estimated_duration = models.PositiveIntegerField(default=0, help_text='Durée estimée en minutes')
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('SUBMITTED', 'Soumis'),
        ('REVIEW', 'En révision'),
        ('PUBLISHED', 'Publié'),
        ('ARCHIVED', 'Archivé'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PUBLISHED')
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_courses')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_state_exam_prep = models.BooleanField(default=False, verbose_name="Préparation Examen d'État")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"


class Chapter(models.Model):
    """Chapitre de regroupement de leçons"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Chapitre'
        verbose_name_plural = 'Chapitres'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Ch.{self.order}: {self.title}"


class ContentBlock(models.Model):
    TYPE_CHOICES = [
        ('TEXT', 'Texte'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Vidéo'),
        ('DOCUMENT', 'Document'),
        ('CODE', 'Code'),
        ('RESOURCE', 'Ressource externe'),
    ]
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='content_blocks')
    content_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    text_content = models.TextField(blank=True)
    file = models.FileField(upload_to='courses/content/', blank=True, null=True)
    url = models.URLField(blank=True)
    language = models.CharField(max_length=50, blank=True)
    caption = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']


class LearnerQuestion(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('ANSWERED', 'Répondue'),
        ('ARCHIVED', 'Archivée'),
    ]
    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learner_questions')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='learner_questions')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='learner_questions')
    content_block = models.ForeignKey(ContentBlock, on_delete=models.SET_NULL, null=True, blank=True, related_name='learner_questions')
    question = models.TextField()
    answer = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)


class Lesson(models.Model):
    """Leçon multi-support (Vidéo, PDF ou Texte/Markdown)[cite: 13, 17, 18]"""
    TYPE_CHOICES = [
        ('VIDEO', 'Vidéo'),
        ('PDF', 'Document PDF'),
        ('TEXT', 'Article / Texte'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='TEXT')
    
    text_content = models.TextField(blank=True, null=True, help_text="Contenu texte ou Markdown")
    file = models.FileField(upload_to='courses/lessons/files/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    
    order = models.PositiveIntegerField(default=1)
    is_free_preview = models.BooleanField(default=False, help_text="Aperçu gratuit sans inscription")

    class Meta:
        verbose_name = 'Leçon'
        verbose_name_plural = 'Leçons'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Leçon {self.order}: {self.title}"


class Quiz(models.Model):
    """Quiz interactif avec récompense en points d'expérience (XP)[cite: 13, 18]"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    QUIZ_TYPES = [
        ('COURSE', 'Cours'),
        ('GAME', 'Quiz Game'),
        ('TRAINING', 'Quiz Training'),
        ('EXAM_PREP', 'Préparation examen'),
    ]
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default='COURSE')
    subject = models.CharField(max_length=100, blank=True)
    school_level = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    session = models.CharField(max_length=100, blank=True)
    series = models.CharField(max_length=100, blank=True)
    duration = models.PositiveIntegerField(default=0, help_text='Durée en secondes, 0 = illimitée')
    shuffle_questions = models.BooleanField(default=False)
    shuffle_choices = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('SUBMITTED', 'Soumis'),
        ('REVIEW', 'En révision'),
        ('PUBLISHED', 'Publié'),
        ('ARCHIVED', 'Archivé'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    xp_reward = models.PositiveIntegerField(default=10, verbose_name="Points XP d'apprentissage")

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"Quiz: {self.title} ({self.course.title})"


class Question(models.Model):
    """Question d'un quiz[cite: 13, 18]"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    QUESTION_TYPES = [
        ('SINGLE_CHOICE', 'Choix unique'),
        ('MULTIPLE_CHOICE', 'Choix multiple'),
        ('TRUE_FALSE', 'Vrai / Faux'),
        ('NUMERIC', 'Réponse numérique'),
        ('FREE_TEXT', 'Réponse libre'),
    ]
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='SINGLE_CHOICE')
    points = models.PositiveIntegerField(default=1)
    correct_numeric = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_questions')
    explanation = models.TextField(blank=True, null=True, help_text="Explication affichée après la réponse")

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"


class Choice(models.Model):
    """Choix de réponse pour une question[cite: 13, 18]"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Choix de réponse'
        verbose_name_plural = 'Choix de réponses'

    def __str__(self):
        return f"{self.question.text[:30]} -> {self.text}"


class Enrollment(models.Model):
    """Inscription de l'apprenant à un cours[cite: 13, 18]"""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('pending', 'En attente de paiement'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.email} -> {self.course.title} [{self.status}]"


class LessonProgress(models.Model):
    """Suivi individuel de complétion des leçons[cite: 13, 18]"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Progression de leçon'
        verbose_name_plural = 'Progressions des leçons'
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"


class QuizAttempt(models.Model):
    """Historique des tentatives de quiz et score obtenu[cite: 13, 18]"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(help_text="Score en pourcentage (0-100)")
    started_at = models.DateTimeField(default=now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    raw_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'En cours'),
        ('SUBMITTED', 'Soumise'),
        ('EXPIRED', 'Expirée'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tentative de quiz'
        verbose_name_plural = 'Tentatives de quiz'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}%)"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempt_answers')
    selected_choices = models.JSONField(default=list, blank=True)
    answer_text = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    points_awarded = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('attempt', 'question')