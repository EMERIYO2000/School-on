import hashlib
import json
from unittest.mock import patch
from decimal import Decimal

from django.conf import settings
from django.test import RequestFactory, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from bookings.models import Booking
from utilisateurs.models import CustomUser, TutorProfile

from .models import Transaction
from .providers import get_payment_provider


@override_settings(PAYMENT_FAKE_ENABLED=True, PAYMENT_WEBHOOK_SECRET='test-secret')
class PaymentFlowTests(APITestCase):
	def setUp(self):
		self.student = CustomUser.objects.create_user(
			username='student@example.com', email='student@example.com', password='Password123!',
		)
		self.mentor = CustomUser.objects.create_user(
			username='mentor@example.com', email='mentor@example.com', password='Password123!',
		)
		self.tutor_profile = TutorProfile.objects.create(user=self.mentor, hourly_rate=20000)
		self.booking = Booking.objects.create(
			student=self.student,
			tutor=self.tutor_profile,
			date_requested='2026-10-01',
			time_requested='10:00',
			adress='Bujumbura',
		)
		self.client.force_authenticate(self.student)

	def test_payment_uses_server_amount_and_webhook_confirms_booking(self):
		response = self.client.post('/api/payments/', {
			'booking_id': self.booking.id,
			'payment_method': 'TEST',
			'idempotency_key': 'booking-payment-1',
			'amount': '1',
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		payment = Transaction.objects.get()
		self.assertEqual(payment.amount, Decimal('20000.00'))
		self.assertEqual(payment.platform_fee, Decimal('1000.00'))
		self.assertEqual(payment.status, 'PENDING')
		self.assertEqual(response.data['payment_reason'], "Réservation d'un enseignant")

		webhook = self.client.post('/api/payments/webhooks/fake/', {
			'provider_transaction_id': payment.provider_transaction_id,
			'provider_event_id': 'fake-event-1',
			'event': 'PAYMENT_COMPLETED',
			'amount': '20000.00',
			'currency': 'BIF',
		}, format='json', HTTP_X_FAKE_WEBHOOK_SECRET='test-secret')

		self.assertEqual(webhook.status_code, status.HTTP_200_OK)
		payment.refresh_from_db()
		self.booking.refresh_from_db()
		self.assertEqual(payment.status, 'PAID')
		self.assertEqual(self.booking.status, 'confirmed')

		duplicate = self.client.post('/api/payments/webhooks/fake/', {
			'provider_transaction_id': payment.provider_transaction_id,
			'provider_event_id': 'fake-event-1',
			'event': 'PAYMENT_COMPLETED',
		}, format='json', HTTP_X_FAKE_WEBHOOK_SECRET='test-secret')
		self.assertEqual(duplicate.status_code, status.HTTP_200_OK)
		self.assertEqual(payment.events.count(), 3)

	def test_idempotency_returns_one_transaction(self):
		payload = {
			'booking_id': self.booking.id,
			'payment_method': 'TEST',
			'idempotency_key': 'same-payment',
		}
		first = self.client.post('/api/payments/', payload, format='json')
		second = self.client.post('/api/payments/', payload, format='json')

		self.assertEqual(first.status_code, status.HTTP_201_CREATED)
		self.assertEqual(second.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Transaction.objects.count(), 1)

	def test_lumicash_provider_is_available_and_validates_webhook(self):
		provider = get_payment_provider('lumicash')
		self.assertEqual(provider.name, 'lumicash')

		payload = {
			'provider_transaction_id': 'LUMI-TEST-101',
			'event': 'PAYMENT_COMPLETED',
			'amount': '20000.00',
			'currency': 'BIF',
		}
		raw_body = json.dumps(payload, separators=(',', ':')).encode('utf-8')
		signature = __import__('hmac').new(
			settings.PAYMENT_WEBHOOK_SECRET.encode('utf-8'),
			raw_body,
			hashlib.sha256,
		).hexdigest()
		request = RequestFactory().post(
			'/api/payments/webhooks/lumicash/',
			data=raw_body,
			content_type='application/json',
			HTTP_X_LUMICASH_SIGNATURE=signature,
		)
		self.assertTrue(provider.verify_webhook(request))

	@override_settings(
		PAYMENT_BITLIBERA_ENABLED=True,
		PAYMENT_BITLIBERA_API_URL='https://bitlibera.test',
		PAYMENT_BITLIBERA_API_KEY='test-key',
	)
	@patch('payments.providers.execute_onramp')
	def test_bitlibera_provider_executes_server_amount(self, execute_onramp):
		execute_onramp.return_value = {'ok': True, 'data': {'order_id': 'BL-123'}}
		from .services import create_payment

		payment = create_payment(
			payer=self.student,
			booking_id=self.booking.id,
			payment_method='bitlibera',
			idempotency_key='bitlibera-payment-1',
			bitlibera_phone='+25770000000',
			bitlibera_otp='123456',
		)

		execute_onramp.assert_called_once_with(
			'+25770000000', 20000, '123456', payment.transaction_id,
		)
		self.assertEqual(payment.provider, 'bitlibera')
		self.assertEqual(payment.provider_transaction_id, 'BL-123')
