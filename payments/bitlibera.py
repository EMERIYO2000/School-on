from __future__ import annotations

import time

import httpx
from django.conf import settings


def _base_url():
    return getattr(settings, 'PAYMENT_BITLIBERA_API_URL', '').rstrip('/')


def _api_key():
    return getattr(settings, 'PAYMENT_BITLIBERA_API_KEY', '') or ''


def call_bitlibera(method, endpoint, data=None):
    url = f'{_base_url()}{endpoint}'
    last_error = {'ok': False, 'status': 502, 'error': 'Bitlibera est injoignable.'}
    for attempt in (1, 2):
        try:
            response = httpx.request(
                method,
                url,
                json=data,
                headers={'Content-Type': 'application/json', 'x-api-key': _api_key()},
                timeout=int(getattr(settings, 'PAYMENT_BITLIBERA_TIMEOUT', 30)),
            )
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            if 200 <= response.status_code < 300:
                return {'ok': True, 'data': payload}
            last_error = {'ok': False, 'status': response.status_code, 'error': payload}
            if response.status_code < 500:
                return last_error
        except httpx.HTTPError as exc:
            last_error = {
                'ok': False,
                'status': 502,
                'error': 'Le serveur Bitlibera est inaccessible pour le moment. Vérifiez son URL ou sa disponibilité.',
            }
        if attempt == 1:
            time.sleep(2)
    return last_error


def request_otp(phone, amount):
    return call_bitlibera('POST', '/api/v1/onramp/request-otp', {'phone': phone, 'amount': amount})


def execute_onramp(phone, amount, otp, order_id):
    return call_bitlibera(
        'POST',
        '/api/v1/onramp/execute',
        {'phone': phone, 'amount': amount, 'otp': otp, 'order_id': order_id},
    )


def create_offramp_invoice(recipient_phone, amount_bif, order_id):
    return call_bitlibera(
        'POST',
        '/api/v1/offramp/create-invoice',
        {'recipient_phone': recipient_phone, 'amount_bif': amount_bif, 'order_id': order_id},
    )


def order_status(order_id):
    return call_bitlibera('GET', f'/api/v1/orders/{order_id}')