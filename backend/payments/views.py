import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking

from django.db.models import Sum

from .models import Deposit, Transaction, Withdrawal
from .providers import BlinkDepositProvider, get_payment_provider
from .serializers import CreateDepositSerializer, CreateTransactionSerializer, CreateWithdrawalSerializer, DepositSerializer, SimulationSerializer, TransactionSerializer, WithdrawalSerializer
from .services import create_payment, process_provider_event, request_refund, transition


class TransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(payer=self.request.user).select_related('booking', 'course')

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
        if deposit.method == 'blink' and deposit.status == 'PENDING' and deposit.payment_request:
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
        booking = get_object_or_404(Booking.objects.select_related('tutor__user'), id=booking_id)
        if role == 'student' and booking.student_id != request.user.id:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        if role == 'mentor' and booking.tutor.user_id != request.user.id:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        setattr(booking, f'{role}_confirmed', True)
        if booking.student_confirmed and booking.mentor_confirmed:
            booking.status = 'completed'
        booking.save(update_fields=[f'{role}_confirmed', 'status', 'updated_at'])
        return Response({
            'booking_id': booking.id,
            'status': booking.status,
            'student_confirmed': booking.student_confirmed,
            'mentor_confirmed': booking.mentor_confirmed,
        })
