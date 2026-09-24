from rest_framework import serializers

from .models import Transaction


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