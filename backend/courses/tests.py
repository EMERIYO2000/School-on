from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from .models import ArchiveResource, AttemptAnswer, Category, Chapter, Choice, Course, CourseReview, Enrollment, ExamQuestion, Lesson, Question, Quiz, StateExam


class CoursesApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.teacher = user_model.objects.create_user(email='teacher@example.com', username='teacher', password='Password123!', is_teacher=True)
        self.student = user_model.objects.create_user(email='student@example.com', username='student', password='Password123!')
        self.course = Course.objects.create(title='Python', slug='python', teacher=self.teacher, price=0)
        self.lesson = Lesson.objects.create(course=self.course, title='Introduction')
        self.quiz = Quiz.objects.create(course=self.course, title='Bases')
        question = Question.objects.create(quiz=self.quiz, text='Deux plus deux ?')
        Choice.objects.create(question=question, text='4', is_correct=True)

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_enrolled_student_can_create_and_update_course_review(self):
        Enrollment.objects.create(student=self.student, course=self.course, status='active')
        self.authenticate(self.student)
        response = self.client.post(f'/api/courses/courses/{self.course.id}/reviews/', {'rating': 5, 'comment': 'Très utile.'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CourseReview.objects.count(), 1)
        self.client.post(f'/api/courses/courses/{self.course.id}/reviews/', {'rating': 4, 'comment': 'Mise à jour.'}, format='json')
        self.assertEqual(CourseReview.objects.count(), 1)

    def test_course_list_does_not_require_authentication(self):
        response = self.client.get('/api/courses/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['title'], 'Python')

    def test_teacher_is_assigned_automatically(self):
        self.authenticate(self.teacher)
        response = self.client.post('/api/courses/courses/', {'title': 'Django', 'slug': 'django', 'teacher': self.student.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Course.objects.get(slug='django').teacher_id, self.teacher.id)

    def test_teacher_is_not_required_from_client(self):
        self.authenticate(self.teacher)
        response = self.client.post('/api/courses/courses/', {
            'title': 'API Django',
            'summary': 'Créer un cours sans envoyer le mentor.',
            'level': 'DEBUTANT',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Course.objects.get(id=response.data['id']).teacher_id, self.teacher.id)

    def test_student_cannot_create_course(self):
        self.authenticate(self.student)
        response = self.client.post('/api/courses/courses/', {'title': 'Cours interdit'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_course_must_pass_review_before_publication(self):
        self.authenticate(self.teacher)
        response = self.client.post('/api/courses/courses/', {
            'title': 'Cours complet de Python',
            'summary': 'Un résumé suffisamment long pour le contrôle.',
            'description': 'Une description détaillée qui présente les objectifs, les compétences visées et le contenu pédagogique du cours de Python.',
            'category': Category.objects.create(name='Programmation').id,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        course = Course.objects.get(id=response.data['id'])
        self.assertEqual(course.status, 'DRAFT')

        rejected_submit = self.client.post(f'/api/courses/courses/{course.id}/submit_review/')
        self.assertEqual(rejected_submit.status_code, 400)
        self.assertIn('chapitre', str(rejected_submit.data['rules']))

        chapter = Chapter.objects.create(course=course, title='Introduction')
        Lesson.objects.create(course=course, chapter=chapter, title='Première leçon', text_content='Contenu')
        submitted = self.client.post(f'/api/courses/courses/{course.id}/submit_review/')
        self.assertEqual(submitted.status_code, 200, submitted.data)
        course.refresh_from_db()
        self.assertEqual(course.status, 'SUBMITTED')

        self.client.force_authenticate(self.student)
        forbidden = self.client.post(f'/api/courses/courses/{course.id}/approve/')
        self.assertEqual(forbidden.status_code, 403)

        staff = self.teacher.__class__.objects.create_superuser(email='admin@example.com', username='admin', password='Password123!')
        self.client.force_authenticate(staff)
        approved = self.client.post(f'/api/courses/courses/{course.id}/approve/')
        self.assertEqual(approved.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(course.status, 'PUBLISHED')

    def test_staff_rejection_requires_reason(self):
        course = Course.objects.create(title='Cours à vérifier', teacher=self.teacher, status='SUBMITTED')
        staff = self.teacher.__class__.objects.create_superuser(email='reviewer@example.com', username='reviewer', password='Password123!')
        self.client.force_authenticate(staff)
        response = self.client.post(f'/api/courses/courses/{course.id}/reject/', {'review_note': 'Court'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_teacher_can_create_and_submit_exam_archive(self):
        self.authenticate(self.teacher)
        response = self.client.post('/api/courses/exams/', {
            'title': "Examen d'Etat 2025",
            'year': 2025,
            'subject': 'Mathématiques',
            'session': 'Ordinaire',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        exam = StateExam.objects.get(id=response.data['id'])
        self.assertEqual(exam.creator_id, self.teacher.id)
        submitted = self.client.post(f'/api/courses/exams/{exam.id}/submit_review/')
        self.assertEqual(submitted.status_code, 200)
        exam.refresh_from_db()
        self.assertEqual(exam.status, 'SUBMITTED')

    def test_teacher_can_upload_archive_resource_and_student_can_download(self):
        exam = StateExam.objects.create(
            title='Archive publiée', year=2024, subject='Sciences', creator=self.teacher, status='PUBLISHED',
        )
        self.authenticate(self.teacher)
        upload = SimpleUploadedFile('sujet.pdf', b'%PDF-test', content_type='application/pdf')
        response = self.client.post('/api/courses/archive-resources/', {
            'exam': exam.id, 'title': 'Sujet PDF 2024', 'resource_type': 'DOCUMENT', 'file': upload,
        }, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ArchiveResource.objects.count(), 1)
        self.assertTrue(response.data['download_url'])

        self.authenticate(self.student)
        listing = self.client.get('/api/courses/exams/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.data[0]['resources']), 1)

    def test_teacher_can_create_quiz_with_questions(self):
        self.authenticate(self.teacher)
        response = self.client.post('/api/courses/quizzes/', {
            'course': self.course.id,
            'title': 'Variables Python',
            'xp_reward': 20,
            'questions': [{
                'text': 'Quel mot-clé définit une fonction ?',
                'explanation': 'Une fonction Python commence avec def.',
                'choices': [
                    {'text': 'def', 'is_correct': True},
                    {'text': 'func', 'is_correct': False},
                ],
            }],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        created_quiz = Quiz.objects.get(id=response.data['id'])
        self.assertEqual(created_quiz.questions.count(), 1)

    def test_student_can_enroll_only_once(self):
        self.authenticate(self.student)
        first = self.client.post(f'/api/courses/courses/{self.course.id}/enroll/')
        second = self.client.post(f'/api/courses/courses/{self.course.id}/enroll/')
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Enrollment.objects.filter(student=self.student, course=self.course).count(), 1)

    def test_paid_course_requires_payment_before_lessons_are_visible(self):
        paid_course = Course.objects.create(title='Cours payant', teacher=self.teacher, price=1000, is_premium=True)
        Lesson.objects.create(course=paid_course, title='Leçon payante')
        self.authenticate(self.student)

        response = self.client.post(
            f'/api/courses/courses/{paid_course.id}/enroll/',
            {'payment_method': 'TEST', 'idempotency_key': 'paid-course-1'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['payment']['status'], 'PENDING')
        self.assertEqual(response.data['enrollment']['status'], 'pending')

    def test_paid_course_is_activated_when_payment_is_confirmed(self):
        from payments.models import Transaction
        from payments.services import process_provider_event

        paid_course = Course.objects.create(title='Cours à débloquer', teacher=self.teacher, price=1000, is_premium=True)
        self.authenticate(self.student)
        response = self.client.post(
            f'/api/courses/courses/{paid_course.id}/enroll/',
            {'payment_method': 'TEST', 'idempotency_key': 'paid-course-2'},
            format='json',
        )
        payment = Transaction.objects.get(transaction_id=response.data['payment']['transaction_id'])

        process_provider_event(payment, 'PAYMENT_COMPLETED', 'test-paid-course-2')

        self.assertEqual(Enrollment.objects.get(student=self.student, course=paid_course).status, 'active')

    def test_correct_answers_are_not_exposed(self):
        response = self.client.get(f'/api/courses/courses/{self.course.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('is_correct', response.data['quizzes'][0]['questions'][0]['choices'][0])

    def test_student_can_submit_quiz_after_enrollment(self):
        self.authenticate(self.student)
        self.client.post(f'/api/courses/courses/{self.course.id}/enroll/')
        choice = self.quiz.questions.first().choices.first()
        response = self.client.post(f'/api/courses/quiz-attempts/submit/{self.quiz.id}/', {'answers': [{'question_id': choice.question_id, 'choice_id': choice.id}]}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 100.0)

    def test_unenrolled_student_cannot_read_lessons(self):
        self.authenticate(self.student)
        response = self.client.get('/api/courses/lessons/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_weighted_multiple_choice_is_corrected_and_saved(self):
        quiz = Quiz.objects.create(course=self.course, title='Types', duration=300)
        question = Question.objects.create(
            quiz=quiz, text='Quels sont des langages ?', question_type='MULTIPLE_CHOICE', points=3,
        )
        python = Choice.objects.create(question=question, text='Python', is_correct=True)
        javascript = Choice.objects.create(question=question, text='JavaScript', is_correct=True)
        Choice.objects.create(question=question, text='HTML', is_correct=False)

        self.authenticate(self.student)
        response = self.client.post(
            f'/api/courses/quiz-attempts/submit/{quiz.id}/',
            {'answers': {str(question.id): [python.id, javascript.id]}},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 100.0)
        attempt = quiz.attempts.get()
        self.assertEqual(attempt.raw_score, 3)
        self.assertEqual(AttemptAnswer.objects.filter(attempt=attempt, is_correct=True).count(), 1)

    def test_numeric_question_is_corrected(self):
        quiz = Quiz.objects.create(course=self.course, title='Calcul', quiz_type='TRAINING')
        question = Question.objects.create(
            quiz=quiz, text='15 x 4 ?', question_type='NUMERIC', correct_numeric=60, points=2,
        )

        self.authenticate(self.student)
        response = self.client.post(
            f'/api/courses/quiz-attempts/submit/{quiz.id}/',
            {'answers': {str(question.id): '60'}},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 100.0)
        self.assertEqual(quiz.attempts.get().raw_score, 2)
