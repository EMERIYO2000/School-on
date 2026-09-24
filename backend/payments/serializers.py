from decimal import Decimal

from rest_framework import serializers

from .models import Deposit, Transaction, Withdrawal


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'transaction_id', 'payer', 'payee', 'course', 'booking', 'provider',
            'payment_method', 'amount', 'currency', 'platform_fee', 'provider_fee',
            'mentor_amount', 'status', 'provider_transaction_id', 'idempotency_key',
            'created_at', 'updated_at', 'completed_at',
        )
        read_only_fields = fields


class CreateTransactionSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField(required=False)
    course_id = serializers.IntegerField(required=False)
    payment_method = serializers.ChoiceField(choices=Transaction.PAYMENT_METHODS, default='TEST')
    idempotency_key = serializers.CharField(max_length=100)


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