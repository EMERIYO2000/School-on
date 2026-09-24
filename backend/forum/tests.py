from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from courses.models import Category

from .models import ForumPost, ForumThread


class ForumApiTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(
			email='forum@example.com', username='forum-user', password='Password123!',
		)
		Category.objects.create(name='Etudes')
		self.client = APIClient()
		self.client.force_authenticate(self.user)

	def test_create_thread_and_reply(self):
		response = self.client.post('/api/community/threads/', {
			'title': 'Question de test', 'content': 'Contenu de test', 'category': 'etudes',
		}, format='json')
		self.assertEqual(response.status_code, 201)
		thread = ForumThread.objects.get()
		reply = self.client.post(f'/api/community/threads/{thread.id}/replies/', {'content': 'Réponse utile'}, format='json')
		self.assertEqual(reply.status_code, 201)
		self.assertEqual(ForumPost.objects.count(), 1)

	def test_closed_thread_rejects_reply(self):
		thread = ForumThread.objects.create(author=self.user, title='Fermé', content='Contenu')
		thread.is_closed = True
		thread.save(update_fields=['is_closed'])
		response = self.client.post(f'/api/community/threads/{thread.id}/replies/', {'content': 'Réponse'}, format='json')
		self.assertEqual(response.status_code, 400)
from django.test import TestCase

# Create your tests here.
