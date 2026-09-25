from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from courses.models import Course, Enrollment, Lesson, LessonProgress, Quiz, QuizAttempt

from .models import Certificate
from .services import issue_certificate_if_eligible


class CertificateFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_model = get_user_model()
        self.student = user_model.objects.create_user(
            email='student-certificate@example.com',
            username='student-certificate',
            password='Strong-password-123',
            first_name='Student',
            last_name='Certificate',
        )
        self.teacher = user_model.objects.create_user(
            email='teacher-certificate@example.com',
            username='teacher-certificate',
            password='Strong-password-123',
            is_teacher=True,
            user_type='TEACHER',
        )
        self.course = Course.objects.create(
            title='Course certificate test',
            teacher=self.teacher,
            status='PUBLISHED',
            is_published=True,
            certification_enabled=True,
        )
        self.lesson = Lesson.objects.create(course=self.course, title='Lesson 1')
        self.quiz = Quiz.objects.create(course=self.course, title='Final quiz', status='PUBLISHED')
        Enrollment.objects.create(student=self.student, course=self.course, status='active')

    def test_certificate_is_issued_after_completion_and_passing_quiz(self):
        LessonProgress.objects.create(student=self.student, lesson=self.lesson, is_completed=True)
        QuizAttempt.objects.create(student=self.student, quiz=self.quiz, score=85, status='SUBMITTED')

        certificate = issue_certificate_if_eligible(self.student, self.course)

        self.assertIsNotNone(certificate)
        self.assertTrue(certificate.certificate_id.startswith('SO-CERT-'))
        self.assertIsNotNone(certificate.study_started_at)
        self.assertIsNotNone(certificate.study_completed_at)
        self.assertIsNotNone(Enrollment.objects.get(student=self.student, course=self.course).completed_at)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_certificate_can_be_verified_publicly(self):
        certificate = Certificate.objects.create(student=self.student, course=self.course)
        response = self.client.get(f'/api/certificates/verify/{certificate.certificate_id}/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['certificate_id'], certificate.certificate_id)

    def test_certificate_can_be_downloaded_as_pdf(self):
        certificate = Certificate.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/certificates/{certificate.certificate_id}/download/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'{certificate.certificate_id}.pdf', response['Content-Disposition'])
        pdf_bytes = b''.join(response.streaming_content)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_student_can_set_signature_text(self):
        certificate = Certificate.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/certificates/{certificate.certificate_id}/signature/',
            {'signature_text': 'Signature de Student'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        certificate.refresh_from_db()
        self.assertEqual(certificate.student_signature_text, 'Signature de Student')
