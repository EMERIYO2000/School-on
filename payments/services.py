from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import transaction as db_transaction
from django.utils import timezone

from bookings.models import Booking
from courses.models import Course, Enrollment

from .models import Transaction, TransactionEvent
from .providers import get_payment_provider


ALLOWED_TRANSITIONS = {
    'CREATED': {'PENDING', 'FAILED'},
    'PENDING': {'PROCESSING', 'PAID', 'FAILED'},
    'PROCESSING': {'PAID', 'FAILED'},
    'PAID': {'HELD', 'REFUND_PENDING', 'DISPUTED'},
    'HELD': {'READY_TO_RELEASE', 'REFUND_PENDING', 'DISPUTED'},
    'READY_TO_RELEASE': {'RELEASED', 'PAYOUT_FAILED'},
    'RELEASED': {'COMPLETED', 'PAYOUT_FAILED'},
    'REFUND_PENDING': {'REFUNDED', 'FAILED'},
}


def _money(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _record_event(payment, event_type, old_status='', new_status='', provider_event_id=None, payload=None):
    return TransactionEvent.objects.create(
        transaction=payment,
        event_type=event_type,
        old_status=old_status,
        new_status=new_status,
        provider_event_id=provider_event_id,
        payload_json=payload or {},
    )


def transition(payment, new_status, event_type, payload=None, provider_event_id=None):
    if new_status != payment.status and new_status not in ALLOWED_TRANSITIONS.get(payment.status, set()):
        raise ValueError(f'Transition interdite: {payment.status} -> {new_status}')
    old_status = payment.status
    payment.status = new_status
    if new_status == 'COMPLETED':
        payment.completed_at = timezone.now()
    payment.save(update_fields=['status', 'completed_at', 'updated_at'])
    _record_event(payment, event_type, old_status, new_status, provider_event_id, payload)
    return payment


@db_transaction.atomic
def create_payment(*, payer, booking_id=None, course_id=None, payment_method='TEST', idempotency_key=None):
    if not idempotency_key:
        raise ValueError('idempotency_key est obligatoire.')
    existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        if existing.payer_id != payer.id:
            raise ValueError('Cette idempotency_key appartient à un autre utilisateur.')
        return existing
    if booking_id and course_id:
        raise ValueError('Choisissez une réservation ou un cours, pas les deux.')
    if not booking_id and not course_id:
        raise ValueError('booking_id ou course_id est obligatoire.')

    booking = Booking.objects.select_related('tutor__user').filter(id=booking_id, student=payer).first() if booking_id else None
    course = Course.objects.select_related('teacher').filter(id=course_id).first() if course_id else None
    if booking_id and not booking:
        raise ValueError('Réservation introuvable ou non accessible.')
    if course_id and not course:
        raise ValueError('Cours introuvable.')

    if booking:
        amount = _money(booking.tutor.hourly_rate)
        payee = booking.tutor.user
        if amount <= 0:
            raise ValueError('Le tarif horaire du mentor doit être supérieur à zéro.')
        booking.status = 'pending_payment'
        booking.save(update_fields=['status', 'updated_at'])
    else:
        amount = _money(course.price)
        payee = course.teacher
        if amount <= 0:
            raise ValueError('Le prix du cours doit être supérieur à zéro.')

    normalized_method = (payment_method or 'TEST').lower()
    provider_name = 'lumicash' if normalized_method == 'lumicash' else 'fake'

    fee_rate = Decimal(str(getattr(settings, 'PAYMENT_PLATFORM_FEE_RATE', '0.10')))
    platform_fee = _money(amount * fee_rate)
    payment = Transaction.objects.create(
        payer=payer,
        payee=payee,
        course=course,
        booking=booking,
        amount=amount,
        platform_fee=platform_fee,
        mentor_amount=amount - platform_fee,
        payment_method=normalized_method,
        provider=provider_name,
        idempotency_key=idempotency_key,
    )
    _record_event(payment, 'TRANSACTION_CREATED', '', 'CREATED', payload={'amount': str(amount), 'currency': payment.currency})
    provider = get_payment_provider(payment.provider)
    response = provider.create_payment(payment)
    payment.provider_transaction_id = response['provider_transaction_id']
    payment.save(update_fields=['provider_transaction_id', 'updated_at'])
    transition(payment, 'PENDING', 'PAYMENT_CREATED', response)
    return payment


@db_transaction.atomic
def process_provider_event(payment, event, provider_event_id=None, payload=None):
    if provider_event_id and TransactionEvent.objects.filter(provider_event_id=provider_event_id).exists():
        return payment
    status_by_event = {
        'PAYMENT_COMPLETED': 'PAID',
        'PAYMENT_FAILED': 'FAILED',
        'REFUND_COMPLETED': 'REFUNDED',
        'PAYOUT_COMPLETED': 'COMPLETED',
    }
    new_status = status_by_event.get(event)
    if not new_status:
        raise ValueError(f'Evénement provider inconnu: {event}')
    if event == 'REFUND_COMPLETED' and payment.status != 'REFUND_PENDING':
        raise ValueError('Un remboursement doit être demandé avant sa confirmation.')
    if event == 'PAYOUT_COMPLETED' and payment.status not in {'RELEASED', 'READY_TO_RELEASE'}:
        raise ValueError('Le payout est impossible dans cet état.')
    transition(payment, new_status, event, payload, provider_event_id)
    if payment.booking and new_status == 'PAID':
        payment.booking.status = 'confirmed'
        payment.booking.save(update_fields=['status', 'updated_at'])
    if payment.course and new_status == 'PAID':
        Enrollment.objects.update_or_create(
            student=payment.payer,
            course=payment.course,
            defaults={'status': 'active'},
        )
    return payment


@db_transaction.atomic
def request_refund(payment):
    if payment.status not in {'PAID', 'HELD'}:
        raise ValueError('Cette transaction ne peut pas être remboursée dans son état actuel.')
    transition(payment, 'REFUND_PENDING', 'REFUND_REQUESTED')
    return payment