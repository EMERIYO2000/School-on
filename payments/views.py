from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking

from .models import Transaction
from .providers import get_payment_provider
from .serializers import CreateTransactionSerializer, SimulationSerializer, TransactionSerializer
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
