import hashlib
import hmac
import uuid

from django.conf import settings


class PaymentProvider:
    name = 'base'

    def create_payment(self, transaction):
        raise NotImplementedError

    def refund(self, transaction):
        raise NotImplementedError

    def release_or_payout(self, transaction):
        raise NotImplementedError

    def verify_webhook(self, request):
        raise NotImplementedError

    def _read_payload(self, request):
        body = request.body
        if isinstance(body, bytes):
            return body
        if isinstance(body, str):
            return body.encode('utf-8')
        return b''

    def _verify_hmac(self, request, header_name, secret_name='PAYMENT_WEBHOOK_SECRET'):
        expected_secret = getattr(settings, secret_name, '')
        if not expected_secret:
            return False
        signature = request.headers.get(header_name)
        if not signature:
            return False
        payload = self._read_payload(request)
        digest = hmac.new(expected_secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature)


class FakePaymentProvider(PaymentProvider):
    name = 'fake'

    def __init__(self):
        if not getattr(settings, 'PAYMENT_FAKE_ENABLED', settings.DEBUG):
            raise RuntimeError('Le FakePaymentProvider est désactivé hors développement et test.')

    def create_payment(self, transaction):
        return {'provider_transaction_id': f'FAKE-{uuid.uuid4().hex.upper()}', 'status': 'PENDING'}

    def refund(self, transaction):
        return {'event': 'REFUND_COMPLETED', 'provider_event_id': f'FAKE-REFUND-{uuid.uuid4().hex}'}

    def release_or_payout(self, transaction):
        return {'event': 'PAYOUT_COMPLETED', 'provider_event_id': f'FAKE-PAYOUT-{uuid.uuid4().hex}'}

    def verify_webhook(self, request):
        expected = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', '')
        return bool(expected) and request.headers.get('X-Fake-Webhook-Secret') == expected


class LumicashPaymentProvider(PaymentProvider):
    name = 'lumicash'

    def __init__(self):
        enabled = getattr(settings, 'PAYMENT_LUMICASH_ENABLED', True)
        if not enabled:
            raise RuntimeError('Le provider Lumicash est désactivé dans la configuration.')

    def create_payment(self, transaction):
        transaction_ref = f'LUMI-{uuid.uuid4().hex[:18].upper()}'
        return {
            'provider_transaction_id': transaction_ref,
            'status': 'PENDING',
            'provider_reference': transaction_ref,
            'currency': getattr(transaction, 'currency', 'BIF'),
        }

    def refund(self, transaction):
        return {'event': 'REFUND_COMPLETED', 'provider_event_id': f'LUMI-REFUND-{uuid.uuid4().hex}'}

    def release_or_payout(self, transaction):
        return {'event': 'PAYOUT_COMPLETED', 'provider_event_id': f'LUMI-PAYOUT-{uuid.uuid4().hex}'}

    def verify_webhook(self, request):
        header_name = 'X-LUMICASH-SIGNATURE'
        if request.headers.get(header_name):
            return self._verify_hmac(request, header_name)
        fallback = request.headers.get('X-Lumicash-Signature')
        if fallback:
            return self._verify_hmac(request, 'X-Lumicash-Signature')
        return False


def get_payment_provider(name='fake'):
    providers = {
        'fake': FakePaymentProvider,
        'lumicash': LumicashPaymentProvider,
    }
    try:
        return providers[name.lower()]()
    except KeyError as exc:
        raise ValueError(f'Provider inconnu: {name}') from exc
