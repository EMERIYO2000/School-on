from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommunityCategoryViewSet, CommunityReportViewSet, ForumPostViewSet, ForumThreadViewSet

router = DefaultRouter()
router.register(r'categories', CommunityCategoryViewSet, basename='community-category')
router.register(r'threads', ForumThreadViewSet, basename='community-thread')
router.register(r'posts', ForumPostViewSet, basename='community-post')
router.register(r'reports', CommunityReportViewSet, basename='community-report')

urlpatterns = [path('', include(router.urls))]