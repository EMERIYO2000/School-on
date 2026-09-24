from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArchiveResourceViewSet,
    CategoryViewSet,
    ChapterViewSet,
    ContentBlockViewSet,
    CourseViewSet,
    LearnerQuestionViewSet,
    LessonViewSet,
    QuestionViewSet,
    QuizAttemptViewSet,
    QuizViewSet,
    StateExamViewSet,
)

router = DefaultRouter()
# Référentiels
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'exams', StateExamViewSet, basename='state-exam')
router.register(r'archive-resources', ArchiveResourceViewSet, basename='archive-resource')

# Learning Engine (spec SCHOOL_ON_Learning_Quiz_Engine)
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'content-blocks', ContentBlockViewSet, basename='content-block')
router.register(r'lessons', LessonViewSet, basename='lesson')

# Quiz / Assessment Engine
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')

# Questions des apprenants
router.register(r'learner-questions', LearnerQuestionViewSet, basename='learner-question')

urlpatterns = [
    # Rétrocompatibilité : l'ancienne route de soumission était
    # POST /api/courses/quizzes/submit/{id}/ et
    # POST /api/courses/quiz-attempts/submit/{id}/.
    # La route canonique est maintenant POST /api/courses/quizzes/{id}/submit/.
    path(
        'quizzes/submit/<int:pk>/',
        QuizViewSet.as_view({'post': 'submit'}),
        name='quiz-submit-legacy',
    ),
    path(
        'quiz-attempts/submit/<int:pk>/',
        QuizViewSet.as_view({'post': 'submit'}),
        name='quiz-submit-legacy-attempt',
    ),
    path('', include(router.urls)),
]