import re

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import serializers

from courses.models import Course, Lesson, Question, Quiz

from .models import (
    CommunityLike,
    CommunityCategory,
    CommunityReport,
    ForumPost,
    ForumThread,
)

User = get_user_model()
PHONE_PATTERN = re.compile(r'(?<!\d)(?:\+?\d[\d .-]{7,}\d)(?!\d)')
BLOCKED_PATTERNS = re.compile(r'\b(?:porn|porno|sexuel explicite|acheter de la drogue|fabriquer une bombe)\b', re.I)


def validate_educational_text(value, field='content'):
    value = (value or '').strip()
    if not value:
        raise serializers.ValidationError({field: 'Le contenu ne peut pas être vide.'})
    if PHONE_PATTERN.search(value):
        raise serializers.ValidationError({field: 'Ne partage pas de numéro de téléphone ou de donnée personnelle.'})
    if BLOCKED_PATTERNS.search(value):
        raise serializers.ValidationError({field: 'Ce contenu ne respecte pas les règles de la communauté.'})
    return value


class CommunityAuthorSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'display_name', 'avatar', 'role']
        read_only_fields = fields

    def get_display_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_role(self, obj):
        if obj.is_staff:
            return 'ADMIN'
        if obj.is_teacher:
            return 'MENTOR'
        return 'LEARNER'


class CommunityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityCategory
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'display_order']
        read_only_fields = ['id']


class ForumPostSerializer(serializers.ModelSerializer):
    author = CommunityAuthorSerializer(read_only=True)
    accepted = serializers.BooleanField(source='is_accepted_solution', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = ['id', 'thread', 'author', 'parent_post', 'content', 'status', 'accepted', 'likes_count', 'liked_by_user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'thread', 'author', 'status', 'accepted', 'created_at', 'updated_at']

    def validate_content(self, value):
        return validate_educational_text(value)

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and CommunityLike.objects.filter(user=request.user, post=obj).exists())


class ForumThreadSerializer(serializers.ModelSerializer):
    author = CommunityAuthorSerializer(read_only=True)
    category = serializers.SlugRelatedField(slug_field='slug', queryset=CommunityCategory.objects.filter(is_active=True), required=True)
    category_detail = CommunityCategorySerializer(source='category', read_only=True)
    replies = serializers.SerializerMethodField()
    is_resolved = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = ForumThread
        fields = [
            'id', 'author', 'category', 'category_detail', 'title', 'content', 'content_type',
            'status', 'course', 'lesson', 'quiz', 'quiz_question', 'accepted_post',
            'is_resolved', 'is_closed', 'views_count', 'replies_count', 'replies',
            'likes_count', 'liked_by_user', 'created_at', 'updated_at', 'last_activity_at',
        ]
        read_only_fields = [
            'id', 'author', 'status', 'accepted_post', 'is_resolved', 'views_count',
            'replies_count', 'replies', 'created_at', 'updated_at', 'last_activity_at',
        ]

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 8:
            raise serializers.ValidationError('Le titre doit contenir au moins 8 caractères.')
        if len(value) > 250:
            raise serializers.ValidationError('Le titre est trop long.')
        return value

    def validate_content(self, value):
        value = validate_educational_text(value)
        if len(value) < 20:
            raise serializers.ValidationError('Décris suffisamment ta question pour recevoir de l’aide.')
        if len(value) > 10000:
            raise serializers.ValidationError('Le contenu est trop long.')
        return value

    def validate(self, attrs):
        course = attrs.get('course')
        lesson = attrs.get('lesson')
        quiz = attrs.get('quiz')
        question = attrs.get('quiz_question')
        if lesson and course and lesson.course_id != course.id:
            raise serializers.ValidationError({'lesson': 'Cette leçon n’appartient pas au cours indiqué.'})
        if quiz and question and question.quiz_id != quiz.id:
            raise serializers.ValidationError({'quiz_question': 'Cette question n’appartient pas au quiz indiqué.'})
        return attrs

    def get_is_resolved(self, obj):
        return bool(obj.accepted_post_id)

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and CommunityLike.objects.filter(user=request.user, thread=obj).exists())

    def get_replies(self, obj):
        posts = obj.posts.select_related('author').annotate(likes_count=Count('likes'))
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            posts = posts.filter(status='PUBLISHED')
        elif not request.user.is_staff:
            posts = posts.filter(Q(status='PUBLISHED') | Q(author=request.user))
        return ForumPostSerializer(posts, many=True, context=self.context).data


class CommunityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityReport
        fields = ['id', 'reporter', 'thread', 'post', 'reason', 'description', 'status', 'reviewed_by', 'reviewed_at', 'moderation_action', 'created_at']
        read_only_fields = ['id', 'reporter', 'thread', 'post', 'status', 'reviewed_by', 'reviewed_at', 'moderation_action', 'created_at']

    def validate_description(self, value):
        return value.strip()

    def validate(self, attrs):
        if not self.context.get('thread') and not self.context.get('post'):
            raise serializers.ValidationError('Un thread ou une réponse doit être signalé.')
        return attrs
