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
    certification_enabled = models.BooleanField(default=False)
    minimum_progress = models.PositiveIntegerField(default=100)
    minimum_quiz_score = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    all_quizzes_required = models.BooleanField(default=False)
    require_final_assessment = models.BooleanField(default=False)
    require_final_project = models.BooleanField(default=False)
    require_mentor_approval = models.BooleanField(default=False)
    
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
    """Chapitre de regroupement de leçons, de contenus dynamiques et de quiz.

    Un chapitre peut contenir :
    - des leçons historiques (`Lesson`) ;
    - des blocs de contenu dynamiques (`ContentBlock`) ;
    - un ou plusieurs quiz (`Quiz.chapter`) ;
    - les questions des apprenants (`LearnerQuestion.chapter`).
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Chapitre'
        verbose_name_plural = 'Chapitres'
        ordering = ['order', 'id']

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
    """Question posée par un apprenant à la fin d'un chapitre (spec §8)."""
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
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='answered_learner_questions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Question d'apprenant"
        verbose_name_plural = "Questions d'apprenants"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.learner_id} -> {self.chapter_id} [{self.status}]"


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
    """Quiz du Question Engine SCHOOL ON (spec Learning & Quiz Engine §25).

    Le même modèle sert :
    - aux quiz intégrés à un cours (`COURSE`) ;
    - au Quiz Game (`GAME`, autonome, sans cours obligatoire) ;
    - au Quiz Training (`TRAINING`) ;
    - à la préparation aux examens d'État (`EXAM_PREP`).
    """
    QUIZ_TYPES = [
        ('COURSE', 'Cours'),
        ('GAME', 'Quiz Game'),
        ('TRAINING', 'Quiz Training'),
        ('EXAM_PREP', 'Préparation examen'),
    ]
<<<<<<< Updated upstream:backend/courses/models/course.py
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default='COURSE')
    subject = models.CharField(max_length=100, blank=True)
    school_level = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    session = models.CharField(max_length=100, blank=True)
    series = models.CharField(max_length=100, blank=True)
    duration = models.PositiveIntegerField(default=0, help_text='Durée en secondes, 0 = illimitée')
    shuffle_questions = models.BooleanField(default=False)
    shuffle_choices = models.BooleanField(default=False)
    is_final_assessment = models.BooleanField(default=False)
=======
>>>>>>> Stashed changes:courses/models/course.py
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('SUBMITTED', 'Soumis'),
        ('REVIEW', 'En révision'),
        ('PUBLISHED', 'Publié'),
        ('ARCHIVED', 'Archivé'),
    ]

    # Un quiz de type GAME / TRAINING / EXAM_PREP est autonome : le cours est optionnel.
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True
    )
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes',
        help_text="Catégorie utilisée pour le Quiz Game et le Quiz Training",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_quizzes',
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default='COURSE')

    # Métadonnées Quiz Training (spec §15 / §16)
    subject = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=30, blank=True, help_text="Niveau de difficulté du Quiz Game")
    school_level = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    session = models.CharField(max_length=100, blank=True)
    series = models.CharField(max_length=100, blank=True)

    duration = models.PositiveIntegerField(default=0, help_text='Durée en secondes, 0 = illimitée')
    shuffle_questions = models.BooleanField(default=False)
    shuffle_choices = models.BooleanField(default=False)
    random_question_count = models.PositiveIntegerField(
        default=0, help_text='0 = toutes les questions, sinon nombre de questions tirées au hasard'
    )

    allow_multiple_attempts = models.BooleanField(default=True)
    max_attempts = models.PositiveIntegerField(default=0, help_text='0 = tentatives illimitées')
    passing_score = models.PositiveIntegerField(default=70, help_text='Seuil de réussite en pourcentage')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    review_note = models.TextField(blank=True)
    xp_reward = models.PositiveIntegerField(default=10, verbose_name="Points XP d'apprentissage")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at', 'id']

    def __str__(self):
        support = self.course.title if self.course_id else (self.category.name if self.category_id else 'Quiz autonome')
        return f"Quiz: {self.title} ({support})"

    @property
    def max_score(self):
        """Somme des points de toutes les questions (spec §18)."""
        return sum((question.points for question in self.questions.all()), 0)

    @property
    def questions_count(self):
        return self.questions.count()


class Question(models.Model):
    """Question du Question Engine — indépendante du contexte d'utilisation (spec §9)."""
    QUESTION_TYPES = [
        ('SINGLE_CHOICE', 'Choix unique'),
        ('MULTIPLE_CHOICE', 'Choix multiple'),
        ('TRUE_FALSE', 'Vrai / Faux'),
        ('NUMERIC', 'Réponse numérique'),
        ('FREE_TEXT', 'Réponse libre'),
    ]
    # Types corrigés automatiquement en V1 (spec §10 et §17)
    AUTO_GRADED_TYPES = {'SINGLE_CHOICE', 'MULTIPLE_CHOICE', 'TRUE_FALSE', 'NUMERIC'}

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='SINGLE_CHOICE')
    points = models.PositiveIntegerField(default=1)
    correct_numeric = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_questions')
    explanation = models.TextField(blank=True, null=True, help_text="Explication affichée après la réponse")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"

    @property
    def is_auto_graded(self):
        return self.question_type in self.AUTO_GRADED_TYPES

    def correct_choice_ids(self):
        return set(self.choices.filter(is_correct=True).values_list('id', flat=True))


class Choice(models.Model):
    """Réponse possible pour une question — le concepteur définit le corrigé (spec §36)."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Choix de réponse'
        verbose_name_plural = 'Choix de réponses'
        ordering = ['order', 'id']

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
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.email} -> {self.course.title} [{self.status}]"


class CourseReview(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['course', 'student'], name='unique_course_student_review')]


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
    """Une tentative d'apprenant sur un quiz (spec §21 et §22).

    Le backend reste l'autorité : score, points et statut sont toujours
    calculés côté serveur (spec §33, règles 1 et 2).
    """
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'En cours'),
        ('SUBMITTED', 'Soumise'),
        ('EXPIRED', 'Expirée'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(help_text="Score en pourcentage (0-100)")
    started_at = models.DateTimeField(default=now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    raw_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    selected_question_ids = models.JSONField(
        default=list,
        blank=True,
        help_text='Questions présentées dans cette tentative, dans leur ordre.',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    duration_seconds = models.PositiveIntegerField(
        default=0, help_text="Temps réellement passé sur la tentative"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tentative de quiz'
        verbose_name_plural = 'Tentatives de quiz'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}%)"

    @property
    def percentage(self):
        """Alias explicite utilisé par l'API (spec §25)."""
        return self.score

    @property
    def total_answers(self):
        return self.correct_answers + self.wrong_answers

    def is_passed(self):
        """Une tentative est réussie si elle atteint le seuil de réussite du quiz."""
        return self.score >= float(self.quiz.passing_score or 0)


class AttemptAnswer(models.Model):
    """Trace exacte de ce que l'apprenant a répondu (spec §25 et §33 règle 4)."""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempt_answers')
    selected_choices = models.JSONField(default=list, blank=True)
    answer_text = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    points_awarded = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('attempt', 'question')
        verbose_name = 'Réponse de tentative'
        verbose_name_plural = 'Réponses de tentative'

    def __str__(self):
        return f"Attempt {self.attempt_id} / Q{self.question_id} -> {'OK' if self.is_correct else 'KO'}"