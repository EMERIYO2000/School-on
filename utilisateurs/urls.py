from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .viewset import AuthViewSet, ProfileViewSet, UserFeaturesViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'users', UserFeaturesViewSet, basename='user-features')

urlpatterns = [
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Compatibility aliases for API clients that omit the trailing slash.
    path('auth/register', AuthViewSet.as_view({'post': 'register'}), name='auth-register-no-slash'),
    path('auth/login', AuthViewSet.as_view({'post': 'login'}), name='auth-login-no-slash'),
    path('', include(router.urls)),
]
