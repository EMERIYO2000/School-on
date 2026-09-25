from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import CommunityCategory, CommunityLike, CommunityModerationAction, CommunityReport, ForumPost, ForumThread
from .serializers import CommunityCategorySerializer, CommunityReportSerializer, ForumPostSerializer, ForumThreadSerializer


class CommunityCategoryViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = CommunityCategory.objects.filter(is_active=True)
	serializer_class = CommunityCategorySerializer
	permission_classes = [permissions.AllowAny]


class ForumThreadViewSet(viewsets.ModelViewSet):
	serializer_class = ForumThreadSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

	def get_queryset(self):
		queryset = ForumThread.objects.select_related('author', 'category', 'course', 'lesson', 'quiz', 'quiz_question').prefetch_related('posts__author').annotate(likes_count=Count('likes'))
		user = self.request.user
		if user.is_authenticated and user.is_staff:
			scoped = queryset
		elif user.is_authenticated:
			scoped = queryset.filter(Q(status__in=['PUBLISHED', 'LOCKED', 'ARCHIVED']) | Q(author=user)).distinct()
		else:
			scoped = queryset.filter(status__in=['PUBLISHED', 'LOCKED', 'ARCHIVED'])
		params = self.request.query_params
		if params.get('category'):
			scoped = scoped.filter(category__slug=params['category'])
		if params.get('content_type'):
			scoped = scoped.filter(content_type=params['content_type'].upper())
		if params.get('course'):
			scoped = scoped.filter(course_id=params['course'])
		if params.get('unresolved') == 'true':
			scoped = scoped.filter(accepted_post__isnull=True)
		if params.get('search'):
			term = params['search'].strip()
			scoped = scoped.filter(Q(title__icontains=term) | Q(content__icontains=term))
		return scoped.order_by('-last_activity_at', '-created_at')

	def perform_create(self, serializer):
		user = self.request.user
		if not user.is_active:
			raise PermissionDenied('Ce compte ne peut pas publier.')
		key = f'community-thread-rate:{user.id}'
		if cache.get(key):
			raise PermissionDenied('Attends un moment avant de publier une nouvelle question.')
		cache.set(key, True, timeout=20)
		serializer.save(author=user, status='PUBLISHED', last_activity_at=timezone.now())

	def perform_update(self, serializer):
		thread = serializer.instance
		if not self.request.user.is_staff and thread.author_id != self.request.user.id:
			raise PermissionDenied('Tu ne peux modifier que tes propres publications.')
		if thread.status in {'LOCKED', 'REMOVED'}:
			raise PermissionDenied('Cette discussion ne peut plus être modifiée.')
		serializer.save(last_activity_at=timezone.now())

	def perform_destroy(self, instance):
		if not self.request.user.is_staff and instance.author_id != self.request.user.id:
			raise PermissionDenied('Tu ne peux supprimer que tes propres publications.')
		instance.status = 'REMOVED'
		instance.save(update_fields=['status', 'updated_at'])

	def retrieve(self, request, *args, **kwargs):
		thread = self.get_object()
		ForumThread.objects.filter(pk=thread.pk).update(views_count=F('views_count') + 1)
		thread.views_count += 1
		return Response(self.get_serializer(thread).data)

	@action(detail=True, methods=['get', 'post'], url_path='replies')
	def replies(self, request, pk=None):
		thread = self.get_object()
		if request.method == 'GET':
			posts = thread.posts.filter(status='PUBLISHED').select_related('author').annotate(likes_count=Count('likes'))
			return Response(ForumPostSerializer(posts, many=True, context={'request': request}).data)
		if thread.is_closed or thread.status in {'LOCKED', 'REMOVED', 'HIDDEN'}:
			return Response({'detail': 'Cette discussion est fermée aux nouvelles réponses.'}, status=status.HTTP_400_BAD_REQUEST)
		key = f'community-post-rate:{request.user.id}'
		if cache.get(key):
			return Response({'detail': 'Attends un moment avant de répondre.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
		serializer = ForumPostSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		cache.set(key, True, timeout=10)
		post = serializer.save(thread=thread, author=request.user, status='PUBLISHED')
		ForumThread.objects.filter(pk=thread.pk).update(replies_count=F('replies_count') + 1, last_activity_at=timezone.now())
		return Response(ForumPostSerializer(post, context={'request': request}).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='like')
	def like(self, request, pk=None):
		thread = self.get_object()
		like, created = CommunityLike.objects.get_or_create(user=request.user, thread=thread)
		if not created:
			like.delete()
		return Response({'liked': created, 'likes_count': CommunityLike.objects.filter(thread=thread).count()})

	@action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='report')
	def report(self, request, pk=None):
		thread = self.get_object()
		serializer = CommunityReportSerializer(data=request.data, context={'thread': thread})
		serializer.is_valid(raise_exception=True)
		report = serializer.save(reporter=request.user, thread=thread)
		return Response(CommunityReportSerializer(report).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='moderate')
	def moderate(self, request, pk=None):
		thread = self.get_object()
		action_name = str(request.data.get('action', '')).upper()
		allowed = {'APPROVE', 'HIDE', 'REMOVE', 'RESTORE', 'LOCK_THREAD'}
		if action_name not in allowed:
			return Response({'action': 'Action de modération invalide.'}, status=status.HTTP_400_BAD_REQUEST)
		new_status = {'APPROVE': 'PUBLISHED', 'HIDE': 'HIDDEN', 'REMOVE': 'REMOVED', 'RESTORE': 'PUBLISHED', 'LOCK_THREAD': 'LOCKED'}[action_name]
		thread.status = new_status
		thread.is_closed = action_name == 'LOCK_THREAD'
		thread.save(update_fields=['status', 'is_closed', 'updated_at'])
		CommunityModerationAction.objects.create(moderator=request.user, thread=thread, action_type=action_name, reason=str(request.data.get('reason', '')).strip())
		return Response(self.get_serializer(thread).data)


class ForumPostViewSet(viewsets.ModelViewSet):
	serializer_class = ForumPostSerializer
	permission_classes = [permissions.IsAuthenticated]
	http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

	def get_queryset(self):
		queryset = ForumPost.objects.select_related('author', 'thread').annotate(likes_count=Count('likes'))
		if self.request.user.is_staff:
			return queryset
		return queryset.filter(Q(status='PUBLISHED') | Q(author=self.request.user))

	def perform_update(self, serializer):
		post = serializer.instance
		if not self.request.user.is_staff and post.author_id != self.request.user.id:
			raise PermissionDenied('Tu ne peux modifier que tes propres réponses.')
		if post.thread.is_closed or post.thread.status in {'LOCKED', 'REMOVED'}:
			raise PermissionDenied('Cette discussion est fermée.')
		serializer.save()

	def perform_destroy(self, instance):
		if not self.request.user.is_staff and instance.author_id != self.request.user.id:
			raise PermissionDenied('Tu ne peux supprimer que tes propres réponses.')
		instance.status = 'REMOVED'
		instance.save(update_fields=['status', 'updated_at'])

	@action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='like')
	def like(self, request, pk=None):
		post = self.get_object()
		like, created = CommunityLike.objects.get_or_create(user=request.user, post=post)
		if not created:
			like.delete()
		return Response({'liked': created, 'likes_count': CommunityLike.objects.filter(post=post).count()})

	@action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='accept')
	def accept(self, request, pk=None):
		post = self.get_object()
		if not request.user.is_staff and post.thread.author_id != request.user.id:
			raise PermissionDenied('Seul l’auteur de la question peut accepter une réponse.')
		with transaction.atomic():
			ForumPost.objects.filter(thread=post.thread).update(is_accepted_solution=False)
			post.is_accepted_solution = True
			post.save(update_fields=['is_accepted_solution', 'updated_at'])
			post.thread.accepted_post = post
			post.thread.save(update_fields=['accepted_post', 'updated_at'])
		return Response(ForumPostSerializer(post).data)

	@action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='report')
	def report(self, request, pk=None):
		post = self.get_object()
		serializer = CommunityReportSerializer(data=request.data, context={'post': post})
		serializer.is_valid(raise_exception=True)
		report = serializer.save(reporter=request.user, post=post)
		return Response(CommunityReportSerializer(report).data, status=status.HTTP_201_CREATED)


class CommunityReportViewSet(viewsets.GenericViewSet):
	serializer_class = CommunityReportSerializer
	permission_classes = [permissions.IsAdminUser]

	def get_queryset(self):
		queryset = CommunityReport.objects.select_related('reporter', 'thread', 'post', 'reviewed_by')
		status_filter = self.request.query_params.get('status')
		return queryset.filter(status=status_filter.upper()) if status_filter else queryset

	def list(self, request):
		return Response(CommunityReportSerializer(self.get_queryset(), many=True).data)

	@action(detail=True, methods=['post'], url_path='resolve')
	def resolve(self, request, pk=None):
		report = self.get_object()
		report.status = request.data.get('status', 'RESOLVED')
		report.moderation_action = request.data.get('action', '')
		report.reviewed_by = request.user
		report.reviewed_at = timezone.now()
		report.save(update_fields=['status', 'moderation_action', 'reviewed_by', 'reviewed_at'])
		return Response(CommunityReportSerializer(report).data)
