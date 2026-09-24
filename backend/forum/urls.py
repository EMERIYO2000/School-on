from django.urls import path

from .views import ThreadCloseView, ThreadDetailView, ThreadListCreateView, ThreadReplyView

urlpatterns = [
    path('threads/', ThreadListCreateView.as_view(), name='forum-threads'),
    path('threads/<int:pk>/', ThreadDetailView.as_view(), name='forum-thread-detail'),
    path('threads/<int:thread_id>/replies/', ThreadReplyView.as_view(), name='forum-thread-replies'),
    path('threads/<int:thread_id>/close/', ThreadCloseView.as_view(), name='forum-thread-close'),
]