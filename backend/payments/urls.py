from django.urls import path

from .views import (
    BookingConfirmationView,
    DepositListCreateView,
    DepositStatusView,
    RefundView,
    SimulatePaymentView,
    TransactionDetailView,
    TransactionListCreateView,
    WalletEarningsView,
    WalletSummaryView,
    WalletTransactionsView,
    WithdrawalListCreateView,
    WebhookView,
)

urlpatterns = [
    path('', TransactionListCreateView.as_view(), name='payment-list-create'),
    path('wallet/summary/', WalletSummaryView.as_view(), name='wallet-summary'),
    path('wallet/deposits/', DepositListCreateView.as_view(), name='wallet-deposits'),
    path('wallet/deposits/<str:reference>/status/', DepositStatusView.as_view(), name='wallet-deposit-status'),
    path('wallet/transactions/', WalletTransactionsView.as_view(), name='wallet-transactions'),
    path('wallet/earnings/', WalletEarningsView.as_view(), name='wallet-earnings'),
    path('wallet/withdrawals/', WithdrawalListCreateView.as_view(), name='wallet-withdrawals'),
    path('<str:transaction_id>/', TransactionDetailView.as_view(), name='payment-detail'),
    path('<str:transaction_id>/refund/', RefundView.as_view(), name='payment-refund'),
    path('webhooks/<str:provider>/', WebhookView.as_view(), name='payment-webhook'),
    path('bookings/<int:booking_id>/<str:role>-confirm/', BookingConfirmationView.as_view(), name='booking-confirm'),
    path('test/<str:transaction_id>/simulate/', SimulatePaymentView.as_view(), name='payment-simulate'),
]