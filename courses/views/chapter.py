# courses/views/chapter.py
"""Course Builder — gestion des chapitres (spec §5)."""
from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from ..models import Chapter
from ..permissions import user_can_edit_course
from ..serializers import ChapterSerializer
from .mixins import ReorderMixin


class ChapterViewSet(ReorderMixin, viewsets.ModelViewSet):
    """Chapitres d'un cours.

    - ``GET /api/courses/chapters/?course=<id>`` : liste (visibilité selon le rôle) ;
    - ``POST/PUT/PATCH/DELETE`` : réservés au mentor propriétaire ou à l'admin ;
    - ``POST /api/courses/chapters/reorder/`` : réordonnancement pédagogique.

    Un apprenant ne voit que les chapitres des cours publiés.
    """
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Chapter.objects.select_related('course').prefetch_related(
            'content_blocks', 'lessons', 'quizzes__questions',
        )
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        user = self.request.user
        if not user.is_authenticated:
            return queryset.filter(course__status='PUBLISHED')
        if user.is_staff:
            return queryset
        if user.is_teacher:
            return queryset.filter(Q(course__teacher=user) | Q(course__status='PUBLISHED')).distinct()
        return queryset.filter(course__status='PUBLISHED')

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if not user_can_edit_course(self.request.user, course):
            raise PermissionDenied('Vous ne pouvez modifier que vos propres cours.')
        serializer.save(order=serializer.validated_data.get('order') or course.chapters.count() + 1)

    def perform_update(self, serializer):
        course = serializer.validated_data.get('course', serializer.instance.course)
        if not user_can_edit_course(self.request.user, course):
            raise PermissionDenied('Vous ne pouvez modifier que vos propres cours.')
        serializer.save()

    def perform_destroy(self, instance):
        if not user_can_edit_course(self.request.user, instance.course):
            raise PermissionDenied('Vous ne pouvez modifier que vos propres cours.')
        instance.delete()
