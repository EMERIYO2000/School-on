from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from utilisateurs.models import TutorProfile


class BookingApiTests(APITestCase):
	def test_student_can_create_booking_from_frontend_contract(self):
		user_model = get_user_model()
		student = user_model.objects.create_user(
			email='student-booking@example.com', username='student-booking', password='Password123!'
		)
		mentor = user_model.objects.create_user(
			email='mentor-booking@example.com', username='mentor-booking', password='Password123!', is_teacher=True
		)
		tutor = TutorProfile.objects.create(user=mentor, mentor_status='VERIFIED', is_verified=True)
		self.client.force_authenticate(user=student)

		response = self.client.post('/api/payments/bookings/', {
			'mentor': tutor.id,
			'scheduled_at': '2099-01-01T10:00:00Z',
			'duration': 60,
			'mode': 'online',
		}, format='json')

		self.assertEqual(response.status_code, 201, response.data)
		self.assertEqual(response.data['mentor'], tutor.id)
		self.assertEqual(response.data['status'], 'pending')

# Create your tests here.
