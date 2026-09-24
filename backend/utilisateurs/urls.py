from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .viewset import (
    AuthViewSet,
    MentorAdminViewSet,
    MentorDirectoryViewSet,
    MentorJourneyViewSet,
    MentorReportAdminViewSet,
    ProfileViewSet,
    UserFeaturesViewSet,
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'users', UserFeaturesViewSet, basename='user-features')

# Parcours Utilisateur & Mentor -----------------------------------------------
# Annuaire public des mentors vérifiés + signalement        -> /api/mentors/
router.register(r'mentors', MentorDirectoryViewSet, basename='mentor')
# Parcours « devenir mentor » côté candidat                 -> /api/mentor/
router.register(r'mentor', MentorJourneyViewSet, basename='mentor-journey')
# Review administratif                                      -> /api/admin/mentor-*
router.register(r'admin/mentor-applications', MentorAdminViewSet, basename='mentor-application')
router.register(r'admin/mentor-reports', MentorReportAdminViewSet, basename='mentor-report')

urlpatterns = [
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Compatibility aliases for API clients that omit the trailing slash.
    path('auth/register', AuthViewSet.as_view({'post': 'register'}), name='auth-register-no-slash'),
    path('auth/login', AuthViewSet.as_view({'post': 'login'}), name='auth-login-no-slash'),
    path('', include(router.urls)),
]
