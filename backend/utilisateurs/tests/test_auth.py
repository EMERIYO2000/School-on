from django.core.files.uploadedfile import SimpleUploadedFile
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
    def test_admin_can_approve_mentor_verification(self):
        applicant = CustomUser.objects.create_user(
            username='applicant@example.com',
            email='applicant@example.com',
            password='Password123!'
        )
        admin = CustomUser.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='Password123!',
            is_staff=True,
            is_superuser=True,
        )
        application = applicant.teacher_applications.create(
            bio='Professeur de mathématiques',
            skills='Algèbre',
            status='pending',
        )
        self.client.force_authenticate(user=admin)

        response = self.client.post(
            f'/api/auth/mentor-applications/{application.id}/review/',
            {'action': 'approve', 'review_note': 'Candidature validée'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        applicant.refresh_from_db()
        self.assertEqual(application.status, 'approved')
        self.assertTrue(applicant.is_teacher)
        self.assertEqual(applicant.user_type, 'TEACHER')
        self.assertTrue(applicant.tutor_profile.is_verified)

    def test_admin_cannot_review_already_processed_mentor_application(self):
        applicant = CustomUser.objects.create_user(
            username='processed@example.com',
            email='processed@example.com',
            password='Password123!'
        )
        admin = CustomUser.objects.create_user(
            username='admin2@example.com',
            email='admin2@example.com',
            password='Password123!',
            is_staff=True,
            is_superuser=True,
        )
        application = applicant.teacher_applications.create(
            bio='Professeur de mathématiques',
            skills='Algèbre',
            status='approved',
            review_note='Déjà validée',
        )
        self.client.force_authenticate(user=admin)

        response = self.client.post(
            f'/api/auth/mentor-applications/{application.id}/review/',
            {'action': 'reject', 'review_note': 'Nouveau refus'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(application.status, 'approved')

    def test_mentor_application_supports_identity_and_diploma_documents(self):
        user = CustomUser.objects.create_user(
            username='documentedmentor@example.com',
            email='documentedmentor@example.com',
            password='Password123!'
        )
        self.client.force_authenticate(user=user)

        identity = SimpleUploadedFile('identity.jpg', b'identity-content', content_type='image/jpeg')
        diploma = SimpleUploadedFile('diploma.pdf', b'diploma-content', content_type='application/pdf')

        response = self.client.post(
            '/api/auth/become-mentor/',
            {
                'bio': 'Professeur de mathématiques',
                'skills': 'Algèbre et géométrie',
                'identity_card': identity,
                'diploma': diploma,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        app = user.teacher_applications.get()
        self.assertTrue(app.identity_card.name.endswith('identity.jpg'))
        self.assertTrue(app.diploma.name.endswith('diploma.pdf'))