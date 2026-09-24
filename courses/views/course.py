from decimal import Decimal, InvalidOperation
import random

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import (
    Category, StateExam, ArchiveResource, Course, Lesson, Quiz,
    Question, Choice, Enrollment, LessonProgress, QuizAttempt,
    AttemptAnswer, ContentBlock, LearnerQuestion
)
from ..serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    LessonSerializer, QuizSerializer, QuizCreateSerializer, QuizSubmitSerializer,
    EnrollmentSerializer, ContentBlockSerializer, LearnerQuestionSerializer, StateExamSerializer, ArchiveResourceSerializer,
    LearnerQuestionAnswerSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Consultation des catégories et matières disponibles."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class StateExamViewSet(viewsets.ModelViewSet):
    queryset = StateExam.objects.select_related('creator').prefetch_related('questions__choices')
    serializer_class = StateExamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated and self.request.user.is_teacher:
            return queryset.filter(Q(status='PUBLISHED') | Q(creator=self.request.user)).distinct()
        return queryset.filter(status='PUBLISHED')

    def perform_create(self, serializer):
        if not self.request.user.is_teacher:
            raise PermissionDenied('Seuls les enseignants peuvent créer une archive.')
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit_review(self, request, pk=None):
        exam = self.get_object()
        if exam.creator_id != request.user.id:
            raise PermissionDenied('Seul le créateur peut soumettre cette archive.')
        exam.status = 'SUBMITTED'
        exam.review_note = ''
        exam.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(StateExamSerializer(exam).data)


class ArchiveResourceViewSet(viewsets.ModelViewSet):
    queryset = ArchiveResource.objects.select_related('exam', 'exam__creator')
    serializer_class = ArchiveResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated and self.request.user.is_teacher:
            return queryset.filter(Q(exam__status='PUBLISHED') | Q(exam__creator=self.request.user)).distinct()
        return queryset.filter(exam__status='PUBLISHED', downloadable=True)

    def perform_create(self, serializer):
        if not self.request.user.is_teacher:
            raise PermissionDenied('Seuls les enseignants peuvent ajouter une ressource.')
        exam = serializer.validated_data['exam']
        if exam.creator_id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied('Vous ne pouvez modifier que vos propres archives.')
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        exam = self.get_object()
        exam.status = 'PUBLISHED'
        exam.review_note = ''
        exam.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(StateExamSerializer(exam).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        exam = self.get_object()
        note = str(request.data.get('review_note', '')).strip()
        if len(note) < 10:
            return Response({'review_note': 'Le motif doit contenir au moins 10 caractères.'}, status=status.HTTP_400_BAD_REQUEST)
        exam.status = 'DRAFT'
        exam.review_note = note
        exam.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(StateExamSerializer(exam).data)


class CourseViewSet(viewsets.ModelViewSet):
    """Gestion et consultation des cours et examens d'État[cite: 13, 18]."""
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            pass
        elif self.request.user.is_authenticated and self.request.user.is_teacher:
            queryset = queryset.filter(Q(status='PUBLISHED') | Q(teacher=self.request.user)).distinct()
        else:
            queryset = queryset.filter(status='PUBLISHED')
        category_slug = self.request.query_params.get('category')
        is_state_exam = self.request.query_params.get('state_exam')
        level = self.request.query_params.get('level')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if is_state_exam is not None:
            queryset = queryset.filter(is_state_exam_prep=is_state_exam.lower() == 'true')
        if level:
            queryset = queryset.filter(level=level)

        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated or not self.request.user.is_teacher:
            raise PermissionDenied('Seuls les comptes mentor peuvent créer un cours.')
        serializer.save(teacher=self.request.user, status='DRAFT')

    def _review_rules(self, course):
        errors = []
        if len(course.title.strip()) < 5:
            errors.append('Le titre doit contenir au moins 5 caractères.')
        if len(course.summary.strip()) < 20:
            errors.append('Le résumé doit contenir au moins 20 caractères.')
        if not course.description or len(course.description.strip()) < 80:
            errors.append('La description doit contenir au moins 80 caractères.')
        if not course.category_id:
            errors.append('Une catégorie doit être sélectionnée.')
        if not course.chapters.exists():
            errors.append('Le cours doit contenir au moins un chapitre.')
        elif not course.lessons.exists() and not course.quizzes.exists() and not course.chapters.filter(content_blocks__isnull=False).exists():
            errors.append('Ajoutez au moins une leçon, un quiz ou un contenu pédagogique.')
        return errors

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit_review(self, request, pk=None):
        course = self.get_object()
        if course.teacher_id != request.user.id:
            raise PermissionDenied('Seul le mentor propriétaire peut soumettre ce cours.')
        if course.status not in {'DRAFT', 'REVIEW'}:
            return Response({'detail': 'Seul un brouillon peut être soumis.'}, status=status.HTTP_400_BAD_REQUEST)
        errors = self._review_rules(course)
        if errors:
            return Response({'detail': 'Le cours ne respecte pas encore les règles.', 'rules': errors}, status=status.HTTP_400_BAD_REQUEST)
        course.status = 'SUBMITTED'
        course.review_note = ''
        course.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(CourseDetailSerializer(course, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        course = self.get_object()
        if course.status != 'SUBMITTED':
            return Response({'detail': 'Seul un cours soumis peut être accepté.'}, status=status.HTTP_400_BAD_REQUEST)
        errors = self._review_rules(course)
        if errors:
            return Response({'detail': 'Le cours échoue aux règles de publication.', 'rules': errors}, status=status.HTTP_400_BAD_REQUEST)
        course.status = 'PUBLISHED'
        course.is_published = True
        course.review_note = ''
        course.reviewed_by = request.user
        course.reviewed_at = timezone.now()
        course.save(update_fields=['status', 'is_published', 'review_note', 'reviewed_by', 'reviewed_at', 'updated_at'])
        return Response(CourseDetailSerializer(course, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        course = self.get_object()
        if course.status != 'SUBMITTED':
            return Response({'detail': 'Seul un cours soumis peut être rejeté.'}, status=status.HTTP_400_BAD_REQUEST)
        note = str(request.data.get('review_note', '')).strip()
        if len(note) < 10:
            return Response({'review_note': 'Le motif du rejet doit contenir au moins 10 caractères.'}, status=status.HTTP_400_BAD_REQUEST)
        course.status = 'DRAFT'
        course.is_published = False
        course.review_note = note
        course.reviewed_by = request.user
        course.reviewed_at = timezone.now()
        course.save(update_fields=['status', 'is_published', 'review_note', 'reviewed_by', 'reviewed_at', 'updated_at'])
        return Response(CourseDetailSerializer(course, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        """S'inscrire à un cours gratuit ou initié (Section 8.3)[cite: 13, 18]."""
        course = self.get_object()
        if course.price > 0 or course.is_premium:
            from payments.services import create_payment

            try:
                payment = create_payment(
                    payer=request.user,
                    course_id=course.id,
                    payment_method=request.data.get('payment_method', 'TEST'),
                    idempotency_key=request.data.get('idempotency_key') or f'enroll-{request.user.id}-{course.id}',
                )
            except (ValueError, RuntimeError) as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            enrollment, _ = Enrollment.objects.get_or_create(
                student=request.user,
                course=course,
                defaults={'status': 'active' if payment.status == 'PAID' else 'pending'},
            )
            if payment.status == 'PAID' and enrollment.status != 'active':
                enrollment.status = 'active'
                enrollment.save(update_fields=['status'])
            return Response({
                'enrollment': EnrollmentSerializer(enrollment).data,
                'payment': {'transaction_id': payment.transaction_id, 'status': payment.status},
            }, status=status.HTTP_201_CREATED)
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'status': 'active' if not course.is_premium else 'pending'}
        )
        serializer = EnrollmentSerializer(enrollment)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_courses(self, request):
        """Liste des cours auxquels l'utilisateur courant est inscrit[cite: 18]."""
        enrollments = Enrollment.objects.filter(student=request.user, status='active')
        courses = [e.course for e in enrollments]
        serializer = CourseListSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture des leçons et enregistrement de la progression[cite: 13, 18]."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()
        if user.is_teacher:
            return Lesson.objects.filter(course__teacher=user).distinct()
        return Lesson.objects.filter(
            Q(course__enrollments__student=user, course__enrollments__status='active')
        ).distinct()

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Marquer une leçon comme terminée par l'apprenant[cite: 13, 18]."""
        lesson = self.get_object()
        progress, _ = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )
        progress.is_completed = True
        progress.save()
        return Response({'status': 'Leçon marquée comme terminée'}, status=status.HTTP_200_OK)


class ContentBlockViewSet(viewsets.ModelViewSet):
    queryset = ContentBlock.objects.select_related('chapter__course')
    serializer_class = ContentBlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        chapter_id = self.request.query_params.get('chapter')
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        if self.request.user.is_teacher and not self.request.user.is_staff:
            queryset = queryset.filter(chapter__course__teacher=self.request.user)
        return queryset

    def perform_create(self, serializer):
        chapter = serializer.validated_data['chapter']
        if not self.request.user.is_staff and chapter.course.teacher_id != self.request.user.id:
            raise PermissionDenied('Vous ne pouvez modifier que votre propre cours.')
        serializer.save()


class LearnerQuestionViewSet(viewsets.ModelViewSet):
    queryset = LearnerQuestion.objects.select_related('course', 'chapter', 'learner')
    serializer_class = LearnerQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_teacher and not self.request.user.is_staff:
            return queryset.filter(course__teacher=self.request.user)
        return queryset.filter(learner=self.request.user)

    def perform_create(self, serializer):
        chapter = serializer.validated_data['chapter']
        if chapter.course_id != serializer.validated_data['course'].id:
            raise serializers.ValidationError({'chapter': 'Ce chapitre n’appartient pas au cours indiqué.'})
        serializer.save(learner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def answer(self, request, pk=None):
        learner_question = self.get_object()
        if not request.user.is_staff and learner_question.course.teacher_id != request.user.id:
            raise PermissionDenied('Seul le mentor du cours peut répondre.')
        serializer = LearnerQuestionAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        learner_question.answer = serializer.validated_data['answer']
        learner_question.status = 'ANSWERED'
        learner_question.answered_at = timezone.now()
        learner_question.save(update_fields=['answer', 'status', 'answered_at'])
        return Response(LearnerQuestionSerializer(learner_question).data)


class QuizViewSet(viewsets.ModelViewSet):
    """Évaluation interactive et attribution de points XP (Section 5)[cite: 13, 18]."""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return QuizCreateSerializer
        return QuizSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_teacher:
            raise PermissionDenied('Seuls les enseignants peuvent créer un quiz.')
        course = serializer.validated_data['course']
        if course.teacher_id != self.request.user.id:
            raise PermissionDenied('Vous ne pouvez créer un quiz que dans votre propre cours.')
        serializer.save()

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        quiz = self.get_object()
        attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz, score=0, status='IN_PROGRESS')
        return Response({'attempt_id': attempt.id, 'started_at': attempt.started_at, 'duration': quiz.duration}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='submit/(?P<pk>[^/.]+)', serializer_class=QuizSubmitSerializer)
    def submit(self, request, pk=None):
        """Soumettre les réponses à un quiz et calculer le score obtenu[cite: 13, 18]."""
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_answers = serializer.validated_data['answers']
        questions = list(quiz.questions.prefetch_related('choices').order_by('order', 'id'))

        if not questions:
            return Response({'error': 'Ce quiz ne contient aucune question.'}, status=status.HTTP_400_BAD_REQUEST)

        attempt = None
        attempt_id = request.data.get('attempt_id')
        if attempt_id:
            attempt = get_object_or_404(QuizAttempt, id=attempt_id, quiz=quiz, student=request.user)
            if attempt.status != 'IN_PROGRESS':
                return Response({'error': 'Cette tentative est déjà terminée.'}, status=status.HTTP_400_BAD_REQUEST)
            if quiz.duration and (timezone.now() - attempt.started_at).total_seconds() > quiz.duration:
                attempt.status = 'EXPIRED'
                attempt.submitted_at = timezone.now()
                attempt.save(update_fields=['status', 'submitted_at'])
                return Response({'error': 'Le temps du quiz est dépassé.', 'attempt_id': attempt.id}, status=status.HTTP_400_BAD_REQUEST)

        if quiz.shuffle_questions:
            random.shuffle(questions)

        raw_score = Decimal('0')
        max_score = sum((question.points for question in questions), 0)
        correct_count = 0
        details = []

        for question in questions:
            submitted = user_answers.get(str(question.id), user_answers.get(question.id))
            correct_ids = {choice.id for choice in question.choices.all() if choice.is_correct}
            selected_ids = set(submitted if isinstance(submitted, list) else [submitted]) if submitted is not None else set()
            is_correct = False
            answer_text = ''
            if question.question_type in {'SINGLE_CHOICE', 'TRUE_FALSE', 'MULTIPLE_CHOICE'}:
                try:
                    selected_ids = {int(choice_id) for choice_id in selected_ids}
                except (TypeError, ValueError):
                    selected_ids = set()
                is_correct = selected_ids == correct_ids
            elif question.question_type == 'NUMERIC':
                answer_text = str(submitted or '')
                try:
                    is_correct = Decimal(answer_text) == question.correct_numeric
                except (InvalidOperation, TypeError, ValueError):
                    is_correct = False
            if is_correct:
                correct_count += 1
                raw_score += question.points

            details.append({
                'question_id': question.id,
                'is_correct': is_correct,
                'points_awarded': question.points if is_correct else 0,
                'explanation': question.explanation,
            })

        score_percentage = round((float(raw_score) / max_score) * 100, 2) if max_score else 0
        with transaction.atomic():
            if attempt is None:
                attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz, score=score_percentage)
            attempt.score = score_percentage
            attempt.raw_score = raw_score
            attempt.max_score = max_score
            attempt.correct_answers = correct_count
            attempt.wrong_answers = len(questions) - correct_count
            attempt.status = 'SUBMITTED'
            attempt.submitted_at = timezone.now()
            attempt.save(update_fields=['score', 'raw_score', 'max_score', 'correct_answers', 'wrong_answers', 'status', 'submitted_at'])
            AttemptAnswer.objects.filter(attempt=attempt).delete()
            AttemptAnswer.objects.bulk_create([
                AttemptAnswer(
                    attempt=attempt,
                    question=question,
                    selected_choices=list(user_answers.get(str(question.id), user_answers.get(question.id, []))) if isinstance(user_answers.get(str(question.id), user_answers.get(question.id, [])), list) else [user_answers.get(str(question.id), user_answers.get(question.id))],
                    answer_text=str(user_answers.get(str(question.id), user_answers.get(question.id, ''))),
                    is_correct=detail['is_correct'],
                    points_awarded=detail['points_awarded'],
                )
                for question, detail in zip(questions, details)
            ])

        return Response({
            'attempt_id': attempt.id,
            'score': score_percentage,
            'xp_earned': quiz.xp_reward if score_percentage >= 70.0 else 0,
            'details': details
        }, status=status.HTTP_201_CREATED)
