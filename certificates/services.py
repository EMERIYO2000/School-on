from django.utils import timezone

from courses.models import Course, Enrollment, LessonProgress, QuizAttempt

from .models import Certificate, CertificationProgress, FinalProject


def certification_status(student, course):
    progress, _ = CertificationProgress.objects.get_or_create(student=student, course=course)
    if not course.certification_enabled:
        progress.status = 'NOT_STARTED'
        progress.save(update_fields=['status', 'updated_at'])
        return {'status': progress.status, 'eligible': False, 'progress': 0, 'requirements': {'certification_enabled': False}}

    enrollment = Enrollment.objects.filter(student=student, course=course, status='active').first()
    lessons = course.lessons.count()
    completed = LessonProgress.objects.filter(student=student, lesson__course=course, is_completed=True).count()
    lesson_progress = min(100, round(completed * 100 / lessons)) if lessons else 0
    lesson_ok = lesson_progress >= course.minimum_progress

    quizzes = list(course.quizzes.filter(status='PUBLISHED'))
    attempts = {}
    for attempt in QuizAttempt.objects.filter(student=student, quiz__in=quizzes, status='SUBMITTED').order_by('-submitted_at', '-completed_at'):
        attempts.setdefault(attempt.quiz_id, attempt)
    final_quizzes = [quiz for quiz in quizzes if quiz.is_final_assessment]
    required_quizzes = final_quizzes if course.require_final_assessment else (quizzes if course.all_quizzes_required else quizzes[:1])
    quiz_scores = [attempts.get(quiz.id).score for quiz in required_quizzes if attempts.get(quiz.id)]
    quiz_ok = bool(required_quizzes) and len(quiz_scores) == len(required_quizzes) and all(score >= float(course.minimum_quiz_score) for score in quiz_scores)
    project = FinalProject.objects.filter(student=student, course=course).first()
    project_ok = not course.require_final_project or bool(project and project.status == 'APPROVED' and (project.score is None or project.score >= course.minimum_quiz_score))
    automatic_ok = bool(enrollment and lesson_ok and quiz_ok and project_ok)
    requirements = {
        'course_completion': lesson_ok,
        'quiz': quiz_ok,
        'final_project': project_ok,
        'mentor_approval': not course.require_mentor_approval or progress.mentor_approved,
    }
    eligible = automatic_ok and requirements['mentor_approval']
    if eligible:
        progress.status = 'ELIGIBLE'
    elif automatic_ok and course.require_mentor_approval:
        progress.status = 'PENDING_MENTOR_APPROVAL'
    elif enrollment:
        progress.status = 'IN_PROGRESS'
    else:
        progress.status = 'NOT_STARTED'
    progress.save(update_fields=['status', 'updated_at'])
    return {'status': progress.status, 'eligible': eligible, 'progress': lesson_progress, 'requirements': requirements, 'final_score': max(quiz_scores) if quiz_scores else None}


def issue_certificate_if_eligible(student, course):
    state = certification_status(student, course)
    if not state['eligible']:
        return None
    enrollment = Enrollment.objects.get(student=student, course=course, status='active')
    completion_time = enrollment.completed_at or timezone.now()
    if enrollment.completed_at is None:
        enrollment.completed_at = completion_time
        enrollment.save(update_fields=['completed_at'])
    certificate, created = Certificate.objects.get_or_create(
        student=student,
        course=course,
        defaults={
            'mentor': course.teacher,
            'final_score': state.get('final_score'),
            'study_started_at': enrollment.enrolled_at,
            'study_completed_at': completion_time,
        },
    )
    if created:
        CertificationProgress.objects.filter(student=student, course=course).update(status='CERTIFIED')
    return certificate
