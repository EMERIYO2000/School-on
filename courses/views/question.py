# courses/views/question.py
"""Question Engine — questions et réponses (spec §9, §12 et §28)."""
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from ..models import Choice, Question, Quiz
from ..permissions import user_can_edit_quiz
from ..serializers import (
    QuizChoiceLearnerSerializer,
    QuizChoiceStaffSerializer,
    QuizQuestionLearnerSerializer,
    QuizQuestionStaffSerializer,
    QuizQuestionWriteSerializer,
)
from .mixins import ReorderMixin


class QuestionViewSet(ReorderMixin, viewsets.ModelViewSet):
    """Questions du Question Engine (indépendantes du contexte d'utilisation).

    Endpoints (spec §28) :
    - ``GET/POST   /api/courses/questions/``                (filtre ``?quiz=``) ;
    - ``GET/PUT/PATCH/DELETE /api/courses/questions/{id}/`` ;
    - ``GET/POST   /api/courses/questions/{id}/answers/``   (corrigé masqué pour l'apprenant) ;
    - ``POST       /api/courses/questions/reorder/``.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _quiz_in_context(self):
        """Quiz concerné par la requête (via ``?quiz=`` ou via l'objet courant)."""
        if getattr(self, '_quiz_cache', None) is not None:
            return self._quiz_cache
        quiz = None
        instance = getattr(self, 'instance', None)
        if instance is not None:
            quiz = instance.quiz
        else:
            quiz_id = self.request.query_params.get('quiz')
            if quiz_id:
                quiz = Quiz.objects.filter(pk=quiz_id).select_related('course', 'created_by').first()
        self._quiz_cache = quiz
        return quiz

    def _can_see_answers(self):
        """Le corrigé n'est renvoyé qu'au créateur / admin, jamais à un apprenant."""
        return user_can_edit_quiz(self.request.user, self._quiz_in_context())

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return QuizQuestionWriteSerializer
        if self.action == 'answers':
            return QuizChoiceStaffSerializer if self._can_see_answers() else QuizChoiceLearnerSerializer
        # Actions de lecture : le corrigé est masqué par défaut (spec §33 règle 3).
        return QuizQuestionStaffSerializer if self._can_see_answers() else QuizQuestionLearnerSerializer

    def get_queryset(self):
        queryset = Question.objects.select_related('quiz', 'quiz__course').prefetch_related('choices')
        quiz_id = self.request.query_params.get('quiz')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)

        user = self.request.user
        if user.is_staff:
            return queryset
        if user.is_teacher:
            return queryset.filter(
                Q(quiz__created_by=user) | Q(quiz__course__teacher=user) | Q(quiz__status='PUBLISHED')
            ).distinct()
        # Côté apprenant : mêmes règles de visibilité que la page de détail du cours.
        return queryset.filter(
            Q(quiz__status='PUBLISHED') | Q(quiz__course__isnull=False)
        )

    def perform_create(self, serializer):
        quiz = serializer.validated_data['quiz']
        if not user_can_edit_quiz(self.request.user, quiz):
            raise PermissionDenied('Vous ne pouvez pas modifier ce quiz.')
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if not user_can_edit_quiz(self.request.user, serializer.instance.quiz):
            raise PermissionDenied('Vous ne pouvez pas modifier ce quiz.')
        serializer.save()

    def perform_destroy(self, instance):
        if not user_can_edit_quiz(self.request.user, instance.quiz):
            raise PermissionDenied('Vous ne pouvez pas modifier ce quiz.')
        instance.delete()

    @action(detail=True, methods=['get', 'post'], url_path='answers')
    def answers(self, request, pk=None):
        """Liste ou ajoute les réponses possibles d'une question."""
        question = self.get_object()
        is_editor = user_can_edit_quiz(request.user, question.quiz)

        if request.method == 'GET':
            serializer_class = QuizChoiceStaffSerializer if is_editor else QuizChoiceLearnerSerializer
            return Response(serializer_class(question.choices.all(), many=True).data)

        if not is_editor:
            raise PermissionDenied('Seul le créateur du quiz peut ajouter des réponses.')

        text = str(request.data.get('text', '')).strip()
        if not text:
            raise ValidationError({'text': 'Le texte de la réponse est obligatoire.'})
        is_correct = bool(request.data.get('is_correct', False))
        if question.question_type in {'SINGLE_CHOICE', 'TRUE_FALSE'} and is_correct:
            question.choices.filter(is_correct=True).update(is_correct=False)
        choice = Choice.objects.create(
            question=question,
            text=text,
            is_correct=is_correct,
            order=question.choices.count() + 1,
        )
        return Response(QuizChoiceStaffSerializer(choice).data, status=status.HTTP_201_CREATED)
