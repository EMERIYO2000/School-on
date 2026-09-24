# courses/views/quiz_attempt.py
"""Historique, correction détaillée et progression des tentatives (spec §22, §23)."""
from django.db.models import Count, Max, Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..models import QuizAttempt
from ..serializers import QuizAttemptDetailSerializer, QuizAttemptSerializer


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """Tentatives de quiz.

    - ``GET /api/courses/quiz-attempts/``            : mes résultats
      (filtres : ``quiz``, ``quiz_type``, ``status`` ; mentor : ``as_mentor=true``) ;
    - ``GET /api/courses/quiz-attempts/{id}/``       : correction détaillée (spec §33 règle 4) ;
    - ``GET /api/courses/quiz-attempts/stats/``      : progression par matière (spec §23).

    Une tentative ne peut être lue que par son auteur, le créateur du quiz
    concerné ou l'administration.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizAttemptDetailSerializer
        return QuizAttemptSerializer

    def get_queryset(self):
        queryset = QuizAttempt.objects.select_related('quiz', 'quiz__category').prefetch_related(
            'answers__question__choices', 'answers__question__quiz',
        )
        user = self.request.user
        if not user.is_staff:
            if user.is_teacher and self.request.query_params.get('as_mentor') == 'true':
                queryset = queryset.filter(
                    Q(quiz__created_by=user) | Q(quiz__course__teacher=user)
                ).distinct()
            else:
                queryset = queryset.filter(student=user)

        quiz_id = self.request.query_params.get('quiz')
        quiz_type = self.request.query_params.get('quiz_type')
        status_filter = self.request.query_params.get('status')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        if quiz_type:
            queryset = queryset.filter(quiz__quiz_type=quiz_type.upper())
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        return queryset

    def get_object(self):
        attempt = super().get_object()
        user = self.request.user
        if user.is_staff or attempt.student_id == user.id:
            return attempt
        quiz = attempt.quiz
        if quiz.created_by_id == user.id or (quiz.course_id and quiz.course.teacher_id == user.id):
            return attempt
        raise PermissionDenied('Cette tentative ne vous appartient pas.')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Progression de l'apprenant par matière et type de quiz (spec §23)."""
        attempts = self.get_queryset().filter(status='SUBMITTED')
        by_subject = (
            attempts.values('quiz__subject', 'quiz__quiz_type')
            .annotate(attempts_count=Count('id'), best_score=Max('score'))
            .order_by('-attempts_count')
        )
        summary = attempts.aggregate(best_score=Max('score'))
        latest = attempts.order_by('-completed_at').values_list('score', flat=True).first()
        return Response({
            'attempts_count': attempts.count(),
            'best_score': summary['best_score'] or 0,
            'latest_score': latest or 0,
            'by_subject': [
                {
                    'subject': row['quiz__subject'] or row['quiz__quiz_type'],
                    'quiz_type': row['quiz__quiz_type'],
                    'attempts_count': row['attempts_count'],
                    'best_score': row['best_score'] or 0,
                }
                for row in by_subject
            ],
        })
