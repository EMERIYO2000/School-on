from datetime import timedelta
import random

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import (
    Category, StateExam, ArchiveResource, Course, Lesson, Quiz,
    Question, Choice, Enrollment, LessonProgress, QuizAttempt,
    AttemptAnswer, ContentBlock, LearnerQuestion, CourseReview
)
<<<<<<< Updated upstream:backend/courses/views/course.py
from notifications.services import notify_course_published, notify_course_rejected, notify_quiz_result
from certificates.services import issue_certificate_if_eligible
=======
from ..permissions import user_can_edit_course, user_can_edit_quiz
from ..services import attempt_duration, build_attempt_answers, grade_attempt
from ..views.mixins import ReorderMixin
>>>>>>> Stashed changes:courses/views/course.py
from ..serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    LessonSerializer, QuizSerializer, QuizCreateSerializer, QuizSubmitSerializer,
    EnrollmentSerializer, ContentBlockSerializer, LearnerQuestionSerializer, StateExamSerializer, ArchiveResourceSerializer,
<<<<<<< Updated upstream:backend/courses/views/course.py
    LearnerQuestionAnswerSerializer, CourseReviewSerializer
=======
    LearnerQuestionAnswerSerializer, QuizQuestionLearnerSerializer, QuizQuestionStaffSerializer,
    QuizQuestionWriteSerializer,
>>>>>>> Stashed changes:courses/views/course.py
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        exam = self.get_object()
        if exam.status != 'SUBMITTED':
            return Response({'detail': 'Seul un examen soumis peut être publié.'}, status=status.HTTP_400_BAD_REQUEST)
        exam.status = 'PUBLISHED'
        exam.review_note = ''
        exam.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(StateExamSerializer(exam, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        exam = self.get_object()
        note = str(request.data.get('review_note', '')).strip()
        if len(note) < 10:
            return Response({'review_note': 'Le motif doit contenir au moins 10 caractères.'}, status=status.HTTP_400_BAD_REQUEST)
        exam.status = 'DRAFT'
        exam.review_note = note
        exam.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(StateExamSerializer(exam, context={'request': request}).data)


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
        resource = self.get_object()
        resource.exam.status = 'PUBLISHED'
        resource.exam.review_note = ''
        resource.exam.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(ArchiveResourceSerializer(resource, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        resource = self.get_object()
        note = str(request.data.get('review_note', '')).strip()
        if len(note) < 10:
            return Response({'review_note': 'Le motif doit contenir au moins 10 caractères.'}, status=status.HTTP_400_BAD_REQUEST)
        resource.exam.status = 'DRAFT'
        resource.exam.review_note = note
        resource.exam.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(ArchiveResourceSerializer(resource, context={'request': request}).data)


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

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated])
    def reviews(self, request, pk=None):
        course = self.get_object()
        if request.method == 'GET':
            reviews = list(course.reviews.select_related('student').all())
            return Response({
                'average_rating': round(sum(review.rating for review in reviews) / len(reviews), 2) if reviews else 0,
                'count': len(reviews),
                'results': CourseReviewSerializer(reviews, many=True).data,
            })
        if not Enrollment.objects.filter(student=request.user, course=course, status='active').exists():
            return Response({'detail': 'Une inscription active est requise pour laisser un avis.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CourseReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review, _ = CourseReview.objects.update_or_create(
            course=course,
            student=request.user,
            defaults={'rating': serializer.validated_data['rating'], 'comment': serializer.validated_data.get('comment', '')},
        )
        return Response(CourseReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated or not self.request.user.is_teacher:
            raise PermissionDenied('Seuls les comptes mentor peuvent créer un cours.')
        serializer.save(teacher=self.request.user, status='DRAFT')

    def perform_update(self, serializer):
        if not user_can_edit_course(self.request.user, serializer.instance):
            raise PermissionDenied('Vous ne pouvez modifier que votre propre cours.')
        serializer.save()

    def perform_destroy(self, instance):
        if not user_can_edit_course(self.request.user, instance):
            raise PermissionDenied('Vous ne pouvez supprimer que votre propre cours.')
        instance.delete()

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
        notify_course_published(course, course.teacher)
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
        notify_course_rejected(course, course.teacher, note)
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
        certificate = issue_certificate_if_eligible(request.user, lesson.course)
        return Response({'status': 'Leçon marquée comme terminée'}, status=status.HTTP_200_OK)


class ContentBlockViewSet(ReorderMixin, viewsets.ModelViewSet):
    """Blocs de contenu dynamiques d'un chapitre (spec §6).

    - ``GET/POST /api/courses/content-blocks/?chapter=<id>`` ;
    - ``POST /api/courses/content-blocks/reorder/`` ;
    - écriture réservée au mentor propriétaire du cours ou à l'admin.
    """
    queryset = ContentBlock.objects.select_related('chapter__course')
    serializer_class = ContentBlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        chapter_id = self.request.query_params.get('chapter')
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        user = self.request.user
        if user.is_staff:
            return queryset
        if user.is_teacher:
            return queryset.filter(
                Q(chapter__course__teacher=user) | Q(chapter__course__status='PUBLISHED')
            ).distinct()
        return queryset.filter(chapter__course__status='PUBLISHED')

    def perform_create(self, serializer):
        chapter = serializer.validated_data['chapter']
        if not user_can_edit_course(self.request.user, chapter.course):
            raise PermissionDenied('Vous ne pouvez modifier que votre propre cours.')
        serializer.save(order=serializer.validated_data.get('order') or chapter.content_blocks.count() + 1)

    def perform_update(self, serializer):
        if not user_can_edit_course(self.request.user, serializer.instance.chapter.course):
            raise PermissionDenied('Vous ne pouvez modifier que votre propre cours.')
        serializer.save()

    def perform_destroy(self, instance):
        if not user_can_edit_course(self.request.user, instance.chapter.course):
            raise PermissionDenied('Vous ne pouvez modifier que votre propre cours.')
        instance.delete()


class LearnerQuestionViewSet(viewsets.ModelViewSet):
    """Questions posées par les apprenants sur un chapitre (spec §8).

    - un apprenant voit et crée ses propres questions ;
    - un mentor voit les questions des cours qu'il anime et peut y répondre ;
    - l'administration voit tout.
    """
    queryset = LearnerQuestion.objects.select_related('course', 'chapter', 'learner', 'answered_by')
    serializer_class = LearnerQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            scoped = queryset
        elif user.is_teacher:
            scoped = queryset.filter(course__teacher=user)
        else:
            scoped = queryset.filter(learner=user)

        params = self.request.query_params
        if params.get('course'):
            scoped = scoped.filter(course_id=params['course'])
        if params.get('chapter'):
            scoped = scoped.filter(chapter_id=params['chapter'])
        if params.get('status'):
            scoped = scoped.filter(status=params['status'].upper())
        return scoped

    def perform_create(self, serializer):
        chapter = serializer.validated_data['chapter']
        course = serializer.validated_data.get('course') or chapter.course
        user = self.request.user
        if not user.is_staff and course.status != 'PUBLISHED':
            raise PermissionDenied('Ce cours n’est pas encore ouvert aux questions.')
        serializer.save(learner=user, course=course)

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff and instance.learner_id != user.id:
            raise PermissionDenied('Vous ne pouvez supprimer que vos propres questions.')
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def answer(self, request, pk=None):
        """Le mentor du cours répond à la question de l'apprenant (spec §8)."""
        learner_question = self.get_object()
        if not request.user.is_staff and learner_question.course.teacher_id != request.user.id:
            raise PermissionDenied('Seul le mentor du cours peut répondre.')
        serializer = LearnerQuestionAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        learner_question.answer = serializer.validated_data['answer']
        learner_question.status = 'ANSWERED'
        learner_question.answered_by = request.user
        learner_question.answered_at = timezone.now()
        learner_question.save(update_fields=['answer', 'status', 'answered_by', 'answered_at'])
        return Response(LearnerQuestionSerializer(learner_question).data)

    @action(detail=False, methods=['get'], url_path='pending-count')
    def pending_count(self, request):
        """Nombre de questions en attente pour le mentor connecté (spec §8)."""
        queryset = self.get_queryset().filter(status='PENDING')
        by_course = (
            queryset.values('course', 'course__title')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        return Response({
            'total': queryset.count(),
            'by_course': [
                {'course': row['course'], 'course_title': row['course__title'], 'total': row['total']}
                for row in by_course
            ],
        })

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive une question sans la supprimer (spec §8, statut ARCHIVED)."""
        learner_question = self.get_object()
        user = request.user
        if not user.is_staff and learner_question.course.teacher_id != user.id:
            raise PermissionDenied('Seul le mentor du cours peut archiver cette question.')
        learner_question.status = 'ARCHIVED'
        learner_question.save(update_fields=['status'])
        return Response(LearnerQuestionSerializer(learner_question).data)


class QuizViewSet(viewsets.ModelViewSet):
    """Quiz et soumission des tentatives (Learning & Assessment Engine).

    Endpoints :
    - ``GET    /api/courses/quizzes/``                    liste filtrable ;
    - ``POST   /api/courses/quizzes/``                    création (métadonnées + questions) ;
    - ``GET    /api/courses/quizzes/{id}/``               détail (corrigé masqué pour l'apprenant) ;
    - ``POST   /api/courses/quizzes/{id}/start/``         ouvre une tentative et renvoie les questions ;
    - ``POST   /api/courses/quizzes/{id}/submit/``        corrige et enregistre la tentative ;
    - ``POST   /api/courses/quizzes/{id}/questions/``     ajoute une question ;
    - ``POST   /api/courses/quizzes/{id}/publish/``       publication (admin).

    Filtres de liste : ``quiz_type``, ``course``, ``chapter``, ``category``,
    ``subject``, ``level``, ``school_level``, ``year``, ``series``, ``status``, ``search``.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return QuizCreateSerializer
        if self.action == 'submit':
            return QuizSubmitSerializer
        if self.action == 'add_question':
            return QuizQuestionWriteSerializer
        return QuizSerializer

    def get_queryset(self):
        queryset = Quiz.objects.select_related('course', 'category', 'created_by').prefetch_related(
            'questions__choices',
        )
        user = self.request.user
        params = self.request.query_params
        if params.get('id'):
            queryset = queryset.filter(id=params['id'])
        if params.get('course'):
            queryset = queryset.filter(course_id=params['course'])
        if params.get('chapter'):
            queryset = queryset.filter(chapter_id=params['chapter'])
        if params.get('category'):
            queryset = queryset.filter(category_id=params['category'])
        if params.get('quiz_type'):
            queryset = queryset.filter(quiz_type=params['quiz_type'].upper())
        if params.get('subject'):
            queryset = queryset.filter(subject__icontains=params['subject'])
        if params.get('level'):
            queryset = queryset.filter(level__iexact=params['level'])
        if params.get('school_level'):
            queryset = queryset.filter(school_level__icontains=params['school_level'])
        if params.get('year'):
            queryset = queryset.filter(year=params['year'])
        if params.get('series'):
            queryset = queryset.filter(series__icontains=params['series'])
        if params.get('status'):
            queryset = queryset.filter(status=params['status'].upper())
        if params.get('search'):
            queryset = queryset.filter(
                Q(title__icontains=params['search']) | Q(description__icontains=params['search'])
            )

        if user.is_staff:
            return queryset
        if user.is_teacher:
            owns = Q(created_by=user) | Q(course__teacher=user)
            if params.get('mine') == 'true':
                return queryset.filter(owns).distinct()
            return queryset.filter(owns | Q(status='PUBLISHED')).distinct()
        # Côté apprenant : les quiz rattachés à un cours restent visibles au même
        # titre que via la page de détail du cours (déjà le cas avant cette mise à
        # jour), tandis que les quiz autonomes (Game / Training / Examen) ne sont
        # accessibles que s'ils sont publiés.
        return queryset.filter(Q(status='PUBLISHED') | Q(course__isnull=False))

    def perform_create(self, serializer):
        if not self.request.user.is_teacher and not self.request.user.is_staff:
            raise PermissionDenied('Seuls les mentors et l’administration peuvent créer un quiz.')
        course = serializer.validated_data.get('course')
        if course is not None and not user_can_edit_course(self.request.user, course):
            raise PermissionDenied('Vous ne pouvez créer un quiz que dans votre propre cours.')
        serializer.save()

    def perform_update(self, serializer):
        if not user_can_edit_quiz(self.request.user, serializer.instance):
            raise PermissionDenied('Vous ne pouvez modifier que vos propres quiz.')
        serializer.save()

    def perform_destroy(self, instance):
        if not user_can_edit_quiz(self.request.user, instance):
            raise PermissionDenied('Vous ne pouvez supprimer que vos propres quiz.')
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit_review(self, request, pk=None):
        quiz = self.get_object()
        if not user_can_edit_quiz(request.user, quiz):
            raise PermissionDenied('Seul le créateur peut soumettre ce quiz.')
        if quiz.status not in {'DRAFT', 'REVIEW'}:
            return Response({'detail': 'Seul un brouillon peut être soumis.'}, status=status.HTTP_400_BAD_REQUEST)
        if not quiz.questions.exists():
            return Response({'detail': 'Ajoutez au moins une question avant la soumission.'}, status=status.HTTP_400_BAD_REQUEST)
        quiz.status = 'SUBMITTED'
        quiz.review_note = ''
        quiz.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(QuizSerializer(quiz, context={'request': request}).data)

    def _attempt_limit_reached(self, quiz, user):
        """Vérifie si l'apprenant a épuisé ses tentatives autorisées (spec §21)."""
        if quiz.allow_multiple_attempts is False or quiz.max_attempts:
            finished = QuizAttempt.objects.filter(quiz=quiz, student=user).exclude(
                status='IN_PROGRESS'
            ).count()
            if quiz.allow_multiple_attempts is False and finished >= 1:
                return True, 'Ce quiz n’autorise qu’une seule tentative.'
            if quiz.max_attempts and finished >= quiz.max_attempts:
                return True, f'Nombre maximal de tentatives atteint ({quiz.max_attempts}).'
        return False, ''

    def _learner_questions(self, quiz):
        """Questions présentées à l'apprenant : tirage et mélange (spec §20)."""
        questions = list(quiz.questions.prefetch_related('choices').order_by('order', 'id'))
        if quiz.random_question_count and quiz.random_question_count < len(questions):
            questions = random.sample(questions, quiz.random_question_count)
        if quiz.shuffle_questions:
            random.shuffle(questions)
        return questions

    def _assert_quiz_access(self, quiz, user):
        """Require an active enrollment for quizzes attached to a course."""
        if not quiz.course_id or user.is_staff or quiz.course.teacher_id == user.id:
            return
        if not Enrollment.objects.filter(
            course=quiz.course, student=user, status='active'
        ).exists():
            raise PermissionDenied('Inscrivez-vous à ce cours pour accéder à ce quiz.')

    def _serialize_learner_questions(self, quiz, questions):
        """Sérialise les questions sans jamais exposer le corrigé (spec §33 règle 3)."""
        payload = []
        for question in questions:
            data = QuizQuestionLearnerSerializer(question).data
            if quiz.shuffle_choices and data.get('choices'):
                data['choices'] = random.sample(list(data['choices']), len(data['choices']))
            payload.append(data)
        return payload

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Ouvre une tentative et renvoie les questions sans le corrigé.

        Le chronomètre est autoritaire côté serveur : ``started_at`` est
        enregistré et ``expires_at`` déduit de la durée du quiz (spec §19).
        """
        quiz = self.get_object()
        self._assert_quiz_access(quiz, request.user)
        existing_attempt = QuizAttempt.objects.filter(
            quiz=quiz, student=request.user, status='IN_PROGRESS'
        ).order_by('-started_at').first()
        if existing_attempt and existing_attempt.selected_question_ids:
            selected_ids = existing_attempt.selected_question_ids
            questions_by_id = {
                question.id: question
                for question in quiz.questions.prefetch_related('choices').filter(id__in=selected_ids)
            }
            questions = [questions_by_id[question_id] for question_id in selected_ids if question_id in questions_by_id]
        else:
            questions = self._learner_questions(quiz)
        if not questions:
            return Response(
                {'detail': 'Ce quiz ne contient aucune question pour le moment.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        blocked, message = self._attempt_limit_reached(quiz, request.user)
        if blocked:
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

        attempt = existing_attempt
        created = False
        if attempt is None:
            attempt = QuizAttempt.objects.create(
                student=request.user,
                quiz=quiz,
                score=0,
                raw_score=0,
                max_score=sum(question.points for question in questions),
                selected_question_ids=[question.id for question in questions],
                status='IN_PROGRESS',
            )
            created = True

        return Response(
            {
                'attempt_id': attempt.id,
                'quiz_id': quiz.id,
                'title': quiz.title,
                'started_at': attempt.started_at,
                'duration': quiz.duration,
                'expires_at': attempt.started_at + timedelta(seconds=quiz.duration) if quiz.duration else None,
                'attempts_allowed': quiz.max_attempts or None,
                'allow_multiple_attempts': quiz.allow_multiple_attempts,
                'passing_score': quiz.passing_score,
                'shuffle_questions': quiz.shuffle_questions,
                'shuffle_choices': quiz.shuffle_choices,
                'questions': self._serialize_learner_questions(quiz, questions),
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'], serializer_class=QuizSubmitSerializer)
    def submit(self, request, pk=None):
        """Corrige la tentative et calcule le score côté serveur (spec §17 et §33)."""
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_answers = serializer.validated_data['answers']

        attempt_id = serializer.validated_data.get('attempt_id') or request.data.get('attempt_id')
        attempt = None
        if attempt_id:
            self._assert_quiz_access(quiz, request.user)
            attempt = get_object_or_404(QuizAttempt, id=attempt_id, quiz=quiz, student=request.user)
            if attempt.status != 'IN_PROGRESS':
                return Response({'detail': 'Cette tentative est déjà terminée.'}, status=status.HTTP_400_BAD_REQUEST)
            if quiz.duration and (timezone.now() - attempt.started_at).total_seconds() > quiz.duration:
                attempt.status = 'EXPIRED'
                attempt.submitted_at = timezone.now()
                attempt.duration_seconds = attempt_duration(attempt)
                attempt.save(update_fields=['status', 'submitted_at', 'duration_seconds'])
                return Response(
                    {'detail': 'Le temps du quiz est dépassé.', 'attempt_id': attempt.id},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            legacy_submit = any(
                route in request.path
                for route in ('/quizzes/submit/', '/quiz-attempts/submit/')
            )
            if quiz.duration and not legacy_submit:
                self._assert_quiz_access(quiz, request.user)
                return Response(
                    {'detail': 'Commencez une tentative avant de soumettre ce quiz.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            blocked, message = self._attempt_limit_reached(quiz, request.user)
            if blocked:
                return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

        if attempt and attempt.selected_question_ids:
            selected_ids = attempt.selected_question_ids
            questions_by_id = {
                question.id: question
                for question in quiz.questions.prefetch_related('choices').filter(id__in=selected_ids)
            }
            questions = [questions_by_id[question_id] for question_id in selected_ids if question_id in questions_by_id]
        else:
            questions = list(quiz.questions.prefetch_related('choices').order_by('order', 'id'))
        if not questions:
            return Response({'detail': 'Ce quiz ne contient aucune question.'}, status=status.HTTP_400_BAD_REQUEST)

        graded = grade_attempt(questions, user_answers)

        with transaction.atomic():
            if attempt is None:
                attempt = QuizAttempt.objects.create(
                    student=request.user,
                    quiz=quiz,
                    score=0,
                    max_score=sum(question.points for question in questions),
                    selected_question_ids=[question.id for question in questions],
                    status='IN_PROGRESS',
                )
            attempt.score = graded.percentage
            attempt.raw_score = graded.raw_score
            attempt.max_score = graded.max_score
            attempt.correct_answers = graded.correct_answers
            attempt.wrong_answers = graded.wrong_answers
            attempt.status = 'SUBMITTED'
            attempt.submitted_at = timezone.now()
            attempt.duration_seconds = attempt_duration(attempt)
            attempt.save(update_fields=[
                'score', 'raw_score', 'max_score', 'correct_answers', 'wrong_answers',
                'status', 'submitted_at', 'duration_seconds',
            ])
            AttemptAnswer.objects.filter(attempt=attempt).delete()
            AttemptAnswer.objects.bulk_create(build_attempt_answers(attempt, graded))

<<<<<<< Updated upstream:backend/courses/views/course.py
        notify_quiz_result(request.user, quiz, score_percentage)
        certificate = issue_certificate_if_eligible(request.user, quiz.course)
        return Response({
            'attempt_id': attempt.id,
            'score': score_percentage,
            'xp_earned': quiz.xp_reward if score_percentage >= 70.0 else 0,
            'details': details
        }, status=status.HTTP_201_CREATED)
=======
        passed = graded.percentage >= float(quiz.passing_score or 0)
        return Response(
            {
                'attempt_id': attempt.id,
                'score': graded.percentage,
                'raw_score': float(graded.raw_score),
                'max_score': float(graded.max_score),
                'correct_answers': graded.correct_answers,
                'wrong_answers': graded.wrong_answers,
                'passed': passed,
                'xp_earned': quiz.xp_reward if passed else 0,
                'details': graded.details,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get', 'post'], url_path='questions', serializer_class=QuizQuestionWriteSerializer)
    def add_question(self, request, pk=None):
        """Liste (GET) ou ajoute (POST) une question dans ce quiz (spec §28)."""
        quiz = self.get_object()

        if request.method == 'GET':
            can_edit = user_can_edit_quiz(request.user, quiz)
            serializer_class = QuizQuestionStaffSerializer if can_edit else QuizQuestionLearnerSerializer
            return Response(serializer_class(quiz.questions.prefetch_related('choices'), many=True).data)

        if not user_can_edit_quiz(request.user, quiz):
            raise PermissionDenied('Vous ne pouvez pas modifier ce quiz.')
        serializer = QuizQuestionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save(
            quiz=quiz,
            created_by=request.user,
            order=serializer.validated_data.get('order') or quiz.questions.count() + 1,
        )
        return Response(QuizQuestionStaffSerializer(question).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def publish(self, request, pk=None):
        """Publication d'un quiz par l'administration (spec §26 et §27)."""
        quiz = self.get_object()
        if not quiz.questions.exists():
            return Response(
                {'detail': 'Impossible de publier un quiz sans question.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        quiz.status = 'PUBLISHED'
        quiz.review_note = ''
        quiz.save(update_fields=['status', 'review_note', 'updated_at'])
        return Response(QuizSerializer(quiz, context={'request': request}).data)
>>>>>>> Stashed changes:courses/views/course.py
