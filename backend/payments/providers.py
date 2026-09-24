import hashlib
import hmac
import json
import uuid
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone


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


class BlinkDepositProvider:
    api_url = 'https://api.blink.sv/graphql'

    def __init__(self):
        if not getattr(settings, 'PAYMENT_BLINK_ENABLED', False):
            raise RuntimeError(
                'Blink est désactivé. Configurez PAYMENT_BLINK_ENABLED=true dans school_on_backend/.env.'
            )
        self.api_url = getattr(settings, 'PAYMENT_BLINK_API_URL', self.api_url)
        self.wallet_id = getattr(settings, 'PAYMENT_BLINK_WALLET_ID', '')
        if not self.wallet_id:
            raise RuntimeError('PAYMENT_BLINK_WALLET_ID est requis pour créer un invoice Blink.')

    def _graphql(self, query, variables):
        body = json.dumps({'query': query, 'variables': variables}).encode('utf-8')
        request = Request(self.api_url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f'Blink est momentanément indisponible: {exc}') from exc
        if payload.get('errors'):
            raise RuntimeError(payload['errors'][0].get('message', 'Erreur Blink.'))
        return payload.get('data') or {}

    def _amount_sats(self, amount, currency):
        currency = currency.upper()
        if currency in {'SAT', 'SATS'}:
            return int(Decimal(amount))
        query = '''
            query realtimePrice($currency: DisplayCurrency!) {
                realtimePrice(currency: $currency) {
                    btcSatPrice { base offset }
                }
            }
        '''
        data = self._graphql(query, {'currency': currency}).get('realtimePrice') or {}
        price = data.get('btcSatPrice') or {}
        if price.get('base') is None or price.get('offset') is None:
            raise RuntimeError(f'Blink ne fournit pas de conversion vers les satoshis pour {currency}.')
        sats = Decimal(amount) * Decimal(str(price['base'])) * (Decimal(10) ** int(price['offset']))
        return int(sats.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    def create_invoice(self, amount, currency, memo):
        amount_sats = self._amount_sats(amount, currency)
        if amount_sats <= 0:
            raise RuntimeError('Le montant Blink doit être supérieur à zéro.')
        mutation = '''
            mutation CreateInvoice($input: LnInvoiceCreateOnBehalfOfRecipientInput!) {
                lnInvoiceCreateOnBehalfOfRecipient(input: $input) {
                    invoice { paymentRequest satoshis }
                }
            }
        '''
        data = self._graphql(mutation, {'input': {
            'recipientWalletId': self.wallet_id,
            'amount': str(amount_sats),
            'memo': memo,
            'expiresIn': '15',
        }})
        result = data.get('lnInvoiceCreateOnBehalfOfRecipient') or {}
        invoice = result.get('invoice') or {}
        payment_request = invoice.get('paymentRequest')
        if not payment_request:
            raise RuntimeError('Blink n’a pas retourné de payment request.')
        return {
            'payment_request': payment_request,
            'provider_reference': payment_request,
            'amount_sats': invoice.get('satoshis', amount_sats),
            'expires_at': timezone.now() + timedelta(minutes=15),
        }

    def get_invoice_status(self, payment_request):
        query = '''
            query CheckPaymentStatus($input: LnInvoicePaymentStatusInput!) {
                lnInvoicePaymentStatus(input: $input) { status }
            }
        '''
        data = self._graphql(query, {'input': {'paymentRequest': payment_request}})
        status_data = data.get('lnInvoicePaymentStatus') or {}
        return status_data.get('status', 'PENDING').upper()


def get_payment_provider(name='fake'):
    providers = {
        'fake': FakePaymentProvider,
        'lumicash': LumicashPaymentProvider,
    }
    try:
        return providers[name.lower()]()
    except KeyError as exc:
        raise ValueError(f'Provider inconnu: {name}') from exc
