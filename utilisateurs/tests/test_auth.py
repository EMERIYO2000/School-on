from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from utilisateurs.models import CustomUser


class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.user_data = {
            "full_name": "Wilson Emeriyo",
            "email": "wilson@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "phone_number": "+25760000000",
            "user_type": "STUDENT"
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, "wilson@example.com")

    def test_registered_user_can_login(self):
        register_response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.login_url, {
            'login_id': self.user_data['email'],
            'password': self.user_data['password'],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_register_password_mismatch(self):
        data = self.user_data.copy()
        data['confirm_password'] = 'WrongPassword!'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username_returns_validation_error(self):
        CustomUser.objects.create_user(
            username='azarie', email='existing@example.com', password='Password123!',
        )
        data = self.user_data.copy()
        data['username'] = 'azarie'
        data['email'] = 'new@example.com'

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_login_success(self):
        CustomUser.objects.create_user(
            username="wilson@example.com",
            email="wilson@example.com",
            password="Password123!"
        )
        login_data = {
            "login_id": "wilson@example.com",
            "password": "Password123!"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_registered_user_can_become_parent(self):
        user = CustomUser.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='Password123!',
        )
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/auth/become-parent/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.user_type, 'PARENT')
        self.assertTrue(user.is_parent)
        self.assertTrue(hasattr(user, 'parent_profile'))

    def test_registered_user_can_apply_to_become_mentor(self):
        user = CustomUser.objects.create_user(
            username='mentor@example.com',
            email='mentor@example.com',
            password='Password123!',
        )
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/auth/become-mentor/', {
            'bio': 'Professeur de mathématiques',
            'skills': 'Algèbre',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.teacher_applications.count(), 1)
        self.assertEqual(user.teacher_applications.get().status, 'pending')