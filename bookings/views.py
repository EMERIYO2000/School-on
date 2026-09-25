from django.db import models
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    """List the current user's mentoring sessions and create learner requests."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.select_related('student', 'tutor__user').order_by('-date_requested', '-time_requested')
        return Booking.objects.filter(
            models.Q(student=user) | models.Q(tutor__user=user)
        ).select_related('student', 'tutor__user').prefetch_related('payment_transactions').order_by('-date_requested', '-time_requested')

    def perform_create(self, serializer):
        if self.request.user.is_teacher:
            raise ValidationError({'detail': 'Un mentor ne peut pas réserver une session en tant qu’apprenant.'})
        tutor = serializer.validated_data['tutor']
        if tutor.user_id == self.request.user.id:
            raise ValidationError({'mentor': 'Tu ne peux pas réserver une session avec toi-même.'})
        serializer.save(student=self.request.user)
