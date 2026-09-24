from notifications.models import DeviceToken, Notification
from utilisateurs.utils.fcm_utils import send_fcm_notification


def get_user_device_token(user):
    if not user or not getattr(user, 'is_authenticated', False):
        return None

    device = DeviceToken.objects.filter(user=user).first()
    if device and device.token:
        return device.token
    if getattr(user, 'fcm', None):
        return user.fcm
    return None


def create_notification(user, title, message, *, notification_type='SYSTEM', sender=None,
                       related_object_type=None, related_object_id=None):
    if not user:
        return None

    return Notification.objects.create(
        recipient=user,
        sender=sender,
        title=title,
        message=message,
        notification_type=notification_type,
        related_object_type=related_object_type or '',
        related_object_id=related_object_id,
    )


def notify_user(user, title, message, *, notification_type='SYSTEM', sender=None,
                related_object_type=None, related_object_id=None, push_data=None, send_push=True):
    notification = create_notification(
        user,
        title,
        message,
        notification_type=notification_type,
        sender=sender,
        related_object_type=related_object_type,
        related_object_id=related_object_id,
    )

    if send_push:
        token = get_user_device_token(user)
        if token:
            payload = push_data or {
                'type': notification_type.lower(),
                'notification_id': str(notification.id),
            }
            send_fcm_notification(
                fcm_token=token,
                title=title,
                body=message,
                data=payload,
            )

    return notification


def notify_course_published(course, user):
    return notify_user(
        user,
        'Cours publié',
        f'Votre cours « {course.title} » a été publié et est maintenant visible pour les apprenants.',
        notification_type='COURSE',
        related_object_type='course',
        related_object_id=course.id,
        push_data={'type': 'COURSE_PUBLISHED', 'course_id': str(course.id)},
    )


def notify_course_rejected(course, user, reason):
    return notify_user(
        user,
        'Publication de cours refusée',
        f'Votre cours « {course.title} » a été rejeté. Motif : {reason}',
        notification_type='COURSE',
        related_object_type='course',
        related_object_id=course.id,
        push_data={'type': 'COURSE_REJECTED', 'course_id': str(course.id)},
    )


def notify_quiz_result(user, quiz, score):
    return notify_user(
        user,
        'Résultat du quiz',
        f'Votre quiz « {quiz.title} » est terminé. Score : {score}%.',
        notification_type='QUIZ',
        related_object_type='quiz',
        related_object_id=quiz.id,
        push_data={'type': 'QUIZ_RESULT', 'quiz_id': str(quiz.id), 'score': str(score)},
    )


def notify_payment_status(user, payment, title, message):
    return notify_user(
        user,
        title,
        message,
        notification_type='PAYMENT',
        related_object_type='payment',
        related_object_id=payment.id,
        push_data={'type': 'PAYMENT_STATUS', 'payment_id': str(payment.id), 'status': payment.status},
    )
