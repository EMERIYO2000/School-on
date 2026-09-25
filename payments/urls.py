from django.urls import path

from .views import (
    BookingConfirmationView,
    BitliberaOtpView,
    BlinkWithdrawalSendView,
    DepositListCreateView,
    DepositStatusView,
    RefundView,
    SimulatePaymentView,
    TransactionDetailView,
    TransactionListCreateView,
    WalletEarningsView,
    WalletProviderStatusView,
    WalletSummaryView,
    WalletTransactionsView,
    WithdrawalListCreateView,
    WebhookView,
)
from bookings.views import BookingListCreateView

urlpatterns = [
    path('', TransactionListCreateView.as_view(), name='payment-list-create'),
    path('bitlibera/request-otp/', BitliberaOtpView.as_view(), name='bitlibera-request-otp'),
    path('wallet/summary/', WalletSummaryView.as_view(), name='wallet-summary'),
    path('wallet/provider-status/', WalletProviderStatusView.as_view(), name='wallet-provider-status'),
    path('wallet/deposits/', DepositListCreateView.as_view(), name='wallet-deposits'),
    path('wallet/deposits/<str:reference>/status/', DepositStatusView.as_view(), name='wallet-deposit-status'),
    path('wallet/transactions/', WalletTransactionsView.as_view(), name='wallet-transactions'),
    path('wallet/earnings/', WalletEarningsView.as_view(), name='wallet-earnings'),
    path('wallet/withdrawals/', WithdrawalListCreateView.as_view(), name='wallet-withdrawals'),
    path('wallet/withdrawals/<int:pk>/blink-send/', BlinkWithdrawalSendView.as_view(), name='wallet-withdrawal-blink-send'),
    path('bookings/', BookingListCreateView.as_view(), name='booking-list-create'),
    path('<str:transaction_id>/', TransactionDetailView.as_view(), name='payment-detail'),
    path('<str:transaction_id>/refund/', RefundView.as_view(), name='payment-refund'),
    path('webhooks/<str:provider>/', WebhookView.as_view(), name='payment-webhook'),
    path('bookings/<int:booking_id>/<str:role>-confirm/', BookingConfirmationView.as_view(), name='booking-confirm'),
    path('test/<str:transaction_id>/simulate/', SimulatePaymentView.as_view(), name='payment-simulate'),
]
