from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import CommunityCategory, CommunityReport, ForumPost, ForumThread


class CommunityApiTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.author = user_model.objects.create_user(email='forum-author@example.com', username='forum-author', password='Password123!')
		self.helper = user_model.objects.create_user(email='forum-helper@example.com', username='forum-helper', password='Password123!')
		self.category = CommunityCategory.objects.create(name='Maths test', slug='maths-test')

	def test_authenticated_user_can_create_reply_and_accept_solution(self):
		self.client.force_authenticate(user=self.author)
		created = self.client.post('/api/community/threads/', {
			'title': 'Comprendre le discriminant',
			'content': 'Je cherche une explication éducative du discriminant.',
			'category': self.category.slug,
			'content_type': 'QUESTION',
		}, format='json')
		self.assertEqual(created.status_code, 201, created.data)
		thread_id = created.data['id']

		self.client.force_authenticate(user=self.helper)
		reply = self.client.post(f'/api/community/threads/{thread_id}/replies/', {'content': 'Commence par calculer b² - 4ac.'}, format='json')
		self.assertEqual(reply.status_code, 201, reply.data)
		post_id = reply.data['id']

		self.client.force_authenticate(user=self.author)
		accepted = self.client.post(f'/api/community/posts/{post_id}/accept/')
		self.assertEqual(accepted.status_code, 200, accepted.data)
		self.assertTrue(ForumThread.objects.get(id=thread_id).accepted_post_id == post_id)

	def test_anonymous_cannot_publish_and_locked_thread_rejects_reply(self):
		anonymous = self.client.post('/api/community/threads/', {
			'title': 'Question anonyme', 'content': 'Contenu suffisamment long pour un test.', 'category': self.category.slug,
		}, format='json')
		self.assertEqual(anonymous.status_code, 401)
		thread = ForumThread.objects.create(author=self.author, category=self.category, title='Thread verrouillé', content='Une question éducative assez longue.', status='LOCKED', is_closed=True)
		self.client.force_authenticate(user=self.helper)
		response = self.client.post(f'/api/community/threads/{thread.id}/replies/', {'content': 'Réponse impossible sur un thread verrouillé.'}, format='json')
		self.assertEqual(response.status_code, 400)

# Create your tests here.
