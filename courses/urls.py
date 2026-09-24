from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, StateExamViewSet, ArchiveResourceViewSet, CourseViewSet, LessonViewSet, QuizViewSet, ContentBlockViewSet, LearnerQuestionViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'exams', StateExamViewSet, basename='state-exam')
router.register(r'archive-resources', ArchiveResourceViewSet, basename='archive-resource')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-attempts', QuizViewSet, basename='quiz-attempt')
router.register(r'content-blocks', ContentBlockViewSet, basename='content-block')
router.register(r'learner-questions', LearnerQuestionViewSet, basename='learner-question')

urlpatterns = [
    path('', include(router.urls)),
]