from django.db.models import Q
from rest_framework import generics, permissions

from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
	"""List and create mentor session requests for the current user."""
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = BookingSerializer

	def get_queryset(self):
		return Booking.objects.select_related('student', 'tutor__user').filter(
			Q(student=self.request.user) | Q(tutor__user=self.request.user)
		).order_by('-created_at')

	def perform_create(self, serializer):
		serializer.save(student=self.request.user)
