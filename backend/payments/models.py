import uuid

from django.conf import settings
from django.db import models


def generate_transaction_id():
    return f'TX-{uuid.uuid4().hex[:20].upper()}'


def generate_deposit_reference():
    return f'DEP-{uuid.uuid4().hex[:20].upper()}'


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('CREATED', 'Créée'),
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En traitement'),
        ('FAILED', 'Échec'),
        ('PAID', 'Payée'),
        ('HELD', 'Bloquée jusqu’à libération'),
        ('READY_TO_RELEASE', 'Prête à être libérée'),
        ('RELEASED', 'Libérée'),
        ('COMPLETED', 'Terminée'),
        ('REFUND_PENDING', 'Remboursement en attente'),
        ('REFUNDED', 'Remboursée'),
        ('DISPUTED', 'Contestée'),
        ('PAYOUT_FAILED', 'Échec du versement'),
    ]
    PAYMENT_METHODS = [
        ('TEST', 'Faux provider'),
        ('lumicash', 'Lumicash'),
        ('eco_cash', 'EcoCash'),
        ('bank_transfer', 'Virement bancaire'),
        ('bitcoin', 'Bitcoin (Lightning Network)'),
    ]

    transaction_id = models.CharField(max_length=100, unique=True, default=generate_transaction_id)
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_transactions')
    payee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transactions')
    course = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')
    provider = models.CharField(max_length=50, default='fake')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='TEST')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BIF')
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provider_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mentor_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED')
    provider_transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    idempotency_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_id} - {self.amount} {self.currency} ({self.status})'


class Deposit(models.Model):
    METHOD_CHOICES = [
        ('lumicash', 'Lumicash'),
        ('bitlibera', 'Bitlibera'),
        ('blink', 'Blink'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En traitement'),
        ('COMPLETED', 'Confirmé'),
        ('FAILED', 'Échoué'),
        ('EXPIRED', 'Expiré'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deposits')
    reference = models.CharField(max_length=100, unique=True, default=generate_deposit_reference)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BIF')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    provider_reference = models.CharField(max_length=255, blank=True)
    payment_request = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} - {self.amount} {self.currency} ({self.status})'


class TransactionEvent(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=80)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    provider_event_id = models.CharField(max_length=120, unique=True, null=True, blank=True)
    payload_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En traitement'),
        ('COMPLETED', 'Terminée'),
        ('FAILED', 'Échouée'),
        ('CANCELLED', 'Annulée'),
    ]
    METHOD_CHOICES = [
        ('lumicash', 'Lumicash'),
        ('eco_cash', 'EcoCash'),
        ('bank_transfer', 'Virement bancaire'),
        ('bitcoin', 'Bitcoin'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BIF')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    destination = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.amount} {self.currency} ({self.status})'


class BlockchainData(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='blockchain_data')
    network = models.CharField(max_length=50)
    chain_id = models.CharField(max_length=50, blank=True)
    tx_hash = models.CharField(max_length=255, unique=True)
    sender_address = models.CharField(max_length=255, blank=True)
    receiver_address = models.CharField(max_length=255, blank=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    confirmations = models.PositiveIntegerField(default=0)


# Backwards-compatible import for code using the original model name.
Payments = Transaction
    