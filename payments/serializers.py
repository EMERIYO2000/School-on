from decimal import Decimal

from rest_framework import serializers

from .models import Deposit, Transaction, Withdrawal


class TransactionSerializer(serializers.ModelSerializer):
    payment_reason = serializers.CharField(read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'transaction_id', 'payer', 'payee', 'course', 'booking', 'provider',
            'payment_method', 'payment_reason', 'amount', 'currency', 'platform_fee', 'provider_fee', 'provider_payment_request',
            'mentor_amount', 'status', 'provider_transaction_id', 'idempotency_key',
            'created_at', 'updated_at', 'completed_at',
        )
        read_only_fields = fields


class CreateTransactionSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField(required=False)
    course_id = serializers.IntegerField(required=False)
    payment_method = serializers.ChoiceField(choices=Transaction.PAYMENT_METHODS, default='TEST')
    idempotency_key = serializers.CharField(max_length=100)
    bitlibera_phone = serializers.CharField(required=False, write_only=True, max_length=30)
    bitlibera_otp = serializers.CharField(required=False, write_only=True, max_length=20)

    def validate(self, attrs):
        if bool(attrs.get('booking_id')) == bool(attrs.get('course_id')):
            raise serializers.ValidationError('Sélectionnez exactement un objet à payer : un cours ou une réservation.')
        return attrs


class BitliberaOtpSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=30)
    amount = serializers.IntegerField(min_value=1)


class SimulationSerializer(serializers.Serializer):
    result = serializers.ChoiceField(choices=('success', 'failure'))


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ('id', 'amount', 'currency', 'method', 'destination', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'status', 'created_at', 'updated_at')


class CreateWithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    currency = serializers.CharField(max_length=3, default='BIF')
    method = serializers.ChoiceField(choices=Withdrawal.METHOD_CHOICES)
    destination = serializers.CharField(max_length=255)


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ('reference', 'method', 'amount', 'currency', 'status', 'provider_reference', 'payment_request', 'instructions', 'created_at', 'updated_at', 'completed_at')
        read_only_fields = ('reference', 'status', 'provider_reference', 'payment_request', 'instructions', 'created_at', 'updated_at', 'completed_at')


class CreateDepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    currency = serializers.CharField(max_length=3, default='BIF')
    method = serializers.ChoiceField(choices=Deposit.METHOD_CHOICES)
    bitlibera_phone = serializers.CharField(required=False, write_only=True, max_length=30)
    bitlibera_otp = serializers.CharField(required=False, write_only=True, max_length=20)
