import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking

from django.db import transaction as db_transaction
from django.db.models import Sum

from .models import Deposit, Transaction, Withdrawal
from .bitlibera import execute_onramp, request_otp
from .providers import BitliberaPaymentProvider, BlinkDepositProvider, get_payment_provider
from .serializers import BitliberaOtpSerializer, CreateDepositSerializer, CreateTransactionSerializer, CreateWithdrawalSerializer, DepositSerializer, SimulationSerializer, TransactionSerializer, WithdrawalSerializer
from .services import create_payment, process_provider_event, request_refund, transition


class TransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.select_related('booking', 'course', 'payer', 'payee')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(payer=self.request.user)

    def create(self, request, *args, **kwargs):
        input_serializer = CreateTransactionSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            payment = create_payment(payer=request.user, **input_serializer.validated_data)
        except (ValueError, RuntimeError) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TransactionSerializer(payment).data, status=status.HTTP_201_CREATED)


class TransactionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    lookup_field = 'transaction_id'

    def get_queryset(self):
        return Transaction.objects.filter(payer=self.request.user).select_related('booking', 'course')

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.provider == 'blink' and payment.status == 'PENDING' and payment.provider_payment_request:
            try:
                provider_status = BlinkDepositProvider().get_invoice_status(payment.provider_payment_request)
            except RuntimeError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            if provider_status == 'PAID':
                process_provider_event(payment, 'PAYMENT_COMPLETED', f'BLINK-{payment.transaction_id}-PAID', {'status': provider_status})
            elif provider_status in {'EXPIRED', 'CANCELLED'}:
                process_provider_event(payment, 'PAYMENT_FAILED', f'BLINK-{payment.transaction_id}-{provider_status}', {'status': provider_status})
        elif payment.provider == 'bitlibera' and payment.status == 'PENDING' and payment.provider_transaction_id:
            try:
                provider_status = BitliberaPaymentProvider().get_order_status(payment.provider_transaction_id)
            except RuntimeError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            normalized_status = str(provider_status.get('status', '')).upper()
            if normalized_status in {'PAID', 'COMPLETED', 'SUCCESS', 'SUCCEEDED'}:
                process_provider_event(payment, 'PAYMENT_COMPLETED', f'BITLIBERA-{payment.transaction_id}-PAID', provider_status)
            elif normalized_status in {'FAILED', 'CANCELLED', 'EXPIRED'}:
                process_provider_event(payment, 'PAYMENT_FAILED', f'BITLIBERA-{payment.transaction_id}-{normalized_status}', provider_status)
        return Response(self.get_serializer(payment).data)


class BitliberaOtpView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BitliberaOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            provider = get_payment_provider('bitlibera')
            response = request_otp(**serializer.validated_data)
        except (RuntimeError, ValueError) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if not response['ok']:
            return Response({'detail': response['error']}, status=response.get('status', 502))
        return Response(response['data'], status=status.HTTP_200_OK)


class WalletSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        paid = Transaction.objects.filter(payer=request.user, status__in={'PAID', 'COMPLETED', 'RELEASED'})
        pending = Transaction.objects.filter(payer=request.user, status__in={'CREATED', 'PENDING', 'PROCESSING'})
        refunds = Transaction.objects.filter(payer=request.user, status='REFUNDED')
        earnings = Transaction.objects.filter(payee=request.user, status__in={'RELEASED', 'COMPLETED'})
        held = Transaction.objects.filter(payee=request.user, status__in={'PAID', 'HELD', 'READY_TO_RELEASE'})
        withdrawals = Withdrawal.objects.filter(user=request.user, status__in={'PENDING', 'PROCESSING'})
        deposits = Deposit.objects.filter(user=request.user)
        completed_deposits = deposits.filter(status='COMPLETED')
        pending_deposits = deposits.filter(status__in={'PENDING', 'PROCESSING'})

        def total(queryset, field='amount'):
            return queryset.aggregate(value=Sum(field))['value'] or 0

        available = total(earnings, 'mentor_amount') - total(withdrawals)
        return Response({
            'currency': 'BIF',
            'balance': total(completed_deposits) - total(paid),
            'deposited': total(completed_deposits),
            'deposits_pending': total(pending_deposits),
            'spent': total(paid),
            'pending_spent': total(pending),
            'refunded': total(refunds),
            'earnings_available': max(available, 0),
            'earnings_held': total(held, 'mentor_amount'),
            'withdrawals_pending': total(withdrawals),
        })


class WalletProviderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        blink_enabled = bool(getattr(settings, 'PAYMENT_BLINK_ENABLED', False))
        api_configured = bool(getattr(settings, 'PAYMENT_BLINK_API_KEY', ''))
        wallet_configured = bool(getattr(settings, 'PAYMENT_BLINK_WALLET_ID', ''))
        return Response({
            'provider': 'blink',
            'connected': blink_enabled and api_configured and wallet_configured,
            'currency': 'SAT',
            'deposit_currency': 'BIF',
            'wallet_type': 'platform',
        })


class WalletTransactionsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(payer=self.request.user).select_related('booking', 'course')


class DepositListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepositSerializer

    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        input_serializer = CreateDepositSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        method = data['method']
        bitlibera_phone = data.pop('bitlibera_phone', None)
        bitlibera_otp = data.pop('bitlibera_otp', None)
        if method not in {'blink', 'bitlibera'}:
            return Response(
                {'detail': f'Le dépôt {method} n’est pas encore connecté à un fournisseur de paiement.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reference = f'DEP-{uuid.uuid4().hex[:18].upper()}'
        instructions = {
            'lumicash': 'Effectuez le dépôt Lumicash avec cette référence, puis attendez sa confirmation.',
            'bitlibera': 'Effectuez le dépôt Bitlibera avec cette référence, puis attendez sa confirmation.',
            'blink': 'Un invoice Blink sera généré lorsque les identifiants Blink seront configurés.',
        }[method]
        deposit = Deposit.objects.create(
            user=request.user,
            reference=reference,
            instructions=instructions,
            **data,
        )
        if method == 'bitlibera':
            if not bitlibera_phone or not bitlibera_otp:
                deposit.delete()
                return Response({'detail': 'Le téléphone et le code OTP Bitlibera sont requis.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                response = execute_onramp(bitlibera_phone, int(deposit.amount), bitlibera_otp, deposit.reference)
            except RuntimeError as exc:
                deposit.delete()
                return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            if not response['ok']:
                deposit.delete()
                return Response({'detail': response['error']}, status=response.get('status', 502))
            provider_data = response.get('data') or {}
            if not isinstance(provider_data, dict):
                provider_data = {'response': provider_data}
            deposit.provider_reference = str(provider_data.get('order_id') or provider_data.get('id') or deposit.reference)
            deposit.instructions = 'Dépôt Bitlibera en attente de confirmation.'
            deposit.save(update_fields=['provider_reference', 'instructions', 'updated_at'])
        if method == 'blink':
            try:
                invoice = BlinkDepositProvider().create_invoice(
                    deposit.amount,
                    deposit.currency,
                    f'SCHOOL ON dépôt {deposit.reference}',
                )
            except RuntimeError as exc:
                deposit.delete()
                return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            deposit.payment_request = invoice['payment_request']
            deposit.provider_reference = invoice['provider_reference']
            deposit.instructions = 'Paie cet invoice Blink avant son expiration.'
            deposit.save(update_fields=['payment_request', 'provider_reference', 'instructions', 'updated_at'])
        return Response(DepositSerializer(deposit).data, status=status.HTTP_201_CREATED)


class DepositStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference):
        deposit = get_object_or_404(Deposit, reference=reference, user=request.user)
        if deposit.method == 'bitlibera' and deposit.status == 'PENDING' and deposit.provider_reference:
            try:
                provider_status = BitliberaPaymentProvider().get_order_status(deposit.provider_reference)
            except RuntimeError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            normalized_status = str(provider_status.get('status', '')).upper()
            if normalized_status in {'PAID', 'COMPLETED', 'SUCCESS', 'SUCCEEDED'}:
                deposit.status = 'COMPLETED'
                deposit.completed_at = timezone.now()
                deposit.save(update_fields=['status', 'completed_at', 'updated_at'])
            elif normalized_status in {'FAILED', 'CANCELLED', 'EXPIRED'}:
                deposit.status = 'FAILED' if normalized_status == 'FAILED' else 'EXPIRED'
                deposit.save(update_fields=['status', 'updated_at'])
        elif deposit.method == 'blink' and deposit.status == 'PENDING' and deposit.payment_request:
            try:
                provider_status = BlinkDepositProvider().get_invoice_status(deposit.payment_request)
            except RuntimeError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            if provider_status == 'PAID':
                deposit.status = 'COMPLETED'
                deposit.completed_at = timezone.now()
                deposit.save(update_fields=['status', 'completed_at', 'updated_at'])
            elif provider_status in {'EXPIRED', 'CANCELLED'}:
                deposit.status = 'EXPIRED'
                deposit.save(update_fields=['status', 'updated_at'])
        return Response(DepositSerializer(deposit).data)


class WalletEarningsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(payee=self.request.user).select_related('booking', 'course')


class WithdrawalListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WithdrawalSerializer

    def get_queryset(self):
        return Withdrawal.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        input_serializer = CreateWithdrawalSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        available = Transaction.objects.filter(
            payee=request.user,
            status__in={'RELEASED', 'COMPLETED'},
        ).aggregate(value=Sum('mentor_amount'))['value'] or 0
        reserved = Withdrawal.objects.filter(
            user=request.user,
            status__in={'PENDING', 'PROCESSING'},
        ).aggregate(value=Sum('amount'))['value'] or 0
        if data['amount'] > available - reserved:
            return Response({'detail': 'Le montant dépasse vos gains disponibles.'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal = Withdrawal.objects.create(user=request.user, **data)
        return Response(WithdrawalSerializer(withdrawal).data, status=status.HTTP_201_CREATED)


class BlinkWithdrawalSendView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        with db_transaction.atomic():
            withdrawal = get_object_or_404(Withdrawal.objects.select_for_update(), pk=pk)
            if withdrawal.method != 'bitcoin' or withdrawal.status != 'PENDING':
                return Response({'detail': 'Le retrait doit être Bitcoin et en attente.'}, status=status.HTTP_409_CONFLICT)
            withdrawal.status = 'PROCESSING'
            withdrawal.save(update_fields=['status', 'updated_at'])
        try:
            provider = BlinkDepositProvider()
            amount_sats = provider._amount_sats(withdrawal.amount, withdrawal.currency)
            result = provider.send_to_lightning_address(withdrawal.destination, amount_sats)
            provider_status = (result.get('status') or '').upper()
            withdrawal.provider_response = result
            withdrawal.status = 'COMPLETED' if provider_status in {'SUCCESS', 'SUCCEEDED', 'COMPLETED'} else 'PROCESSING'
        except (RuntimeError, ValueError) as exc:
            withdrawal.provider_response = {'error': str(exc)}
            withdrawal.status = 'FAILED'
        withdrawal.save(update_fields=['provider_response', 'status', 'updated_at'])
        return Response(WithdrawalSerializer(withdrawal).data)


class RefundView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transaction_id):
        payment = get_object_or_404(Transaction, transaction_id=transaction_id, payer=request.user)
        try:
            request_refund(payment)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TransactionSerializer(payment).data, status=status.HTTP_200_OK)


class WebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, provider):
        if provider.lower() == 'blink':
            return Response(
                {'detail': 'Blink ne prend pas en charge les webhooks ici; consultez le statut de la transaction.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            payment_provider = get_payment_provider(provider)
        except (ValueError, RuntimeError):
            return Response({'detail': 'Provider indisponible.'}, status=status.HTTP_404_NOT_FOUND)
        if not payment_provider.verify_webhook(request):
            return Response({'detail': 'Signature webhook invalide.'}, status=status.HTTP_403_FORBIDDEN)
        provider_transaction_id = request.data.get('provider_transaction_id')
        payment = get_object_or_404(Transaction, provider=provider, provider_transaction_id=provider_transaction_id)
        try:
            process_provider_event(
                payment,
                request.data.get('event'),
                request.data.get('provider_event_id'),
                request.data,
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'accepted'}, status=status.HTTP_200_OK)


class SimulatePaymentView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, transaction_id):
        if not getattr(settings, 'PAYMENT_FAKE_ENABLED', settings.DEBUG):
            return Response({'detail': 'Simulation désactivée.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SimulationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = get_object_or_404(Transaction, transaction_id=transaction_id, provider='fake')
        event = 'PAYMENT_COMPLETED' if serializer.validated_data['result'] == 'success' else 'PAYMENT_FAILED'
        process_provider_event(payment, event, f'FAKE-SIM-{transaction_id}-{event}', serializer.validated_data)
        return Response(TransactionSerializer(payment).data)


class BookingConfirmationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id, role):
        if role not in {'student', 'mentor'}:
            return Response({'detail': 'Rôle de confirmation invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        booking = get_object_or_404(Booking.objects.select_related('tutor__user'), id=booking_id)
        if role == 'student' and booking.student_id != request.user.id:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        if role == 'mentor' and booking.tutor.user_id != request.user.id:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        setattr(booking, f'{role}_confirmed', True)
        if booking.student_confirmed and booking.mentor_confirmed:
            booking.status = 'completed'
        elif role == 'mentor' and booking.status in {'pending', 'pending_payment'}:
            booking.status = 'accepted'
        booking.save(update_fields=[f'{role}_confirmed', 'status', 'updated_at'])
        return Response({
            'booking_id': booking.id,
            'status': booking.status,
            'student_confirmed': booking.student_confirmed,
            'mentor_confirmed': booking.mentor_confirmed,
        })
