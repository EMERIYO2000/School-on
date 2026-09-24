from django.conf import settings
from django.db import models
from django.utils.timezone import now

class CommunityCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class ForumThread(models.Model):
    CONTENT_TYPES = [
        ('QUESTION', 'Question'),
        ('DISCUSSION', 'Discussion éducative'),
        ('EXERCISE_HELP', "Aide sur un exercice"),
        ('RESOURCE', 'Ressource'),
        ('ORIENTATION', 'Orientation'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('PENDING_MODERATION', 'En attente de modération'),
        ('PUBLISHED', 'Publié'),
        ('HIDDEN', 'Masqué'),
        ('LOCKED', 'Verrouillé'),
        ('ARCHIVED', 'Archivé'),
        ('REMOVED', 'Retiré'),
    ]
    title = models.CharField(max_length=250)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_threads')
    category = models.ForeignKey(CommunityCategory, on_delete=models.PROTECT, null=True, related_name='threads')
    content = models.TextField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='QUESTION')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_MODERATION')
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_threads')
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_threads')
    quiz = models.ForeignKey('courses.Quiz', on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_threads')
    quiz_question = models.ForeignKey('courses.Question', on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_threads')
    accepted_post = models.ForeignKey('ForumPost', on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_for_threads')
    views_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(default=now)
    is_closed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
class ForumPost(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    status = models.CharField(max_length=25, choices=ForumThread.STATUS_CHOICES, default='PUBLISHED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_accepted_solution = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Réponse de {self.author.username} sur le fil {self.thread.id}"


class CommunityReport(models.Model):
    REASONS = [
        ('OFF_TOPIC', 'Hors sujet'),
        ('HARASSMENT', 'Harcèlement'),
        ('HATE_OR_ABUSE', 'Haine ou abus'),
        ('VIOLENCE', 'Violence ou menace'),
        ('SEXUAL_CONTENT', 'Contenu sexuel'),
        ('ILLEGAL_ACTIVITY', 'Activité illégale'),
        ('SPAM', 'Spam'),
        ('PERSONAL_DATA', 'Données personnelles'),
        ('MISINFORMATION', 'Désinformation'),
        ('OTHER', 'Autre'),
    ]
    STATUSES = [('OPEN', 'Ouvert'), ('UNDER_REVIEW', 'En cours'), ('RESOLVED', 'Résolu'), ('DISMISSED', 'Classé')]
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_reports')
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reason = models.CharField(max_length=30, choices=REASONS)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='OPEN')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_community_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    moderation_action = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class CommunityModerationAction(models.Model):
    ACTIONS = [('APPROVE', 'Approuver'), ('HIDE', 'Masquer'), ('REMOVE', 'Retirer'), ('RESTORE', 'Restaurer'), ('LOCK_THREAD', 'Verrouiller')]
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='community_moderation_actions')
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, null=True, blank=True, related_name='moderation_actions')
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, null=True, blank=True, related_name='moderation_actions')
    action_type = models.CharField(max_length=20, choices=ACTIONS)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)