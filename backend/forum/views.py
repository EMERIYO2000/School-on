from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Category

from .models import ForumPost, ForumThread
from .serializers import CreateForumPostSerializer, CreateForumThreadSerializer, ForumPostSerializer, ForumThreadSerializer


class ThreadListCreateView(generics.ListCreateAPIView):
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		queryset = ForumThread.objects.select_related('author', 'category').prefetch_related('posts__author').annotate(replies_total=Count('posts')).order_by('-created_at')
		category = self.request.query_params.get('category')
		if category:
			queryset = queryset.filter(Q(category__slug=category) | Q(category__name__iexact=category))
		return queryset

	def list(self, request, *args, **kwargs):
		serializer = ForumThreadSerializer(self.get_queryset(), many=True, context={'request': request})
		return Response(serializer.data)

	def create(self, request, *args, **kwargs):
		serializer = CreateForumThreadSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		category_value = serializer.validated_data.get('category', '').strip()
		category = None
		if category_value:
			category = Category.objects.filter(Q(slug=category_value) | Q(name__iexact=category_value)).first()
			if not category:
				return Response({'category': 'Catégorie introuvable.'}, status=status.HTTP_400_BAD_REQUEST)
		thread = ForumThread.objects.create(author=request.user, category=category, **{
			'title': serializer.validated_data['title'],
			'content': serializer.validated_data['content'],
		})
		return Response(ForumThreadSerializer(thread, context={'request': request}).data, status=status.HTTP_201_CREATED)


class ThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [permissions.IsAuthenticated]
	queryset = ForumThread.objects.select_related('author', 'category').prefetch_related('posts__author')
	serializer_class = ForumThreadSerializer

	def perform_update(self, serializer):
		if serializer.instance.author_id != self.request.user.id and not self.request.user.is_staff:
			from rest_framework.exceptions import PermissionDenied
			raise PermissionDenied('Seul l’auteur ou un administrateur peut modifier cette publication.')
		serializer.save()

	def perform_destroy(self, instance):
		if instance.author_id != self.request.user.id and not self.request.user.is_staff:
			from rest_framework.exceptions import PermissionDenied
			raise PermissionDenied('Seul l’auteur ou un administrateur peut supprimer cette publication.')
		instance.delete()


class ThreadReplyView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, thread_id):
		thread = get_object_or_404(ForumThread, pk=thread_id)
		if thread.is_closed:
			return Response({'detail': 'Cette discussion est fermée.'}, status=status.HTTP_400_BAD_REQUEST)
		serializer = CreateForumPostSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		post = ForumPost.objects.create(thread=thread, author=request.user, content=serializer.validated_data['content'])
		return Response(ForumPostSerializer(post, context={'request': request}).data, status=status.HTTP_201_CREATED)


class ThreadCloseView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, thread_id):
		thread = get_object_or_404(ForumThread, pk=thread_id)
		if thread.author_id != request.user.id and not request.user.is_staff:
			return Response({'detail': 'Seul l’auteur ou un administrateur peut fermer la discussion.'}, status=status.HTTP_403_FORBIDDEN)
		thread.is_closed = True
		thread.save(update_fields=['is_closed'])
		return Response(ForumThreadSerializer(thread, context={'request': request}).data)
