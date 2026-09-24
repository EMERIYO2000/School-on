from django.urls import path

from .views import (
    BookingConfirmationView,
    RefundView,
    SimulatePaymentView,
    TransactionDetailView,
    TransactionListCreateView,
    WebhookView,
)

urlpatterns = [
    path('', TransactionListCreateView.as_view(), name='payment-list-create'),
    path('<str:transaction_id>/', TransactionDetailView.as_view(), name='payment-detail'),
    path('<str:transaction_id>/refund/', RefundView.as_view(), name='payment-refund'),
    path('webhooks/<str:provider>/', WebhookView.as_view(), name='payment-webhook'),
    path('bookings/<int:booking_id>/<str:role>-confirm/', BookingConfirmationView.as_view(), name='booking-confirm'),
    path('test/<str:transaction_id>/simulate/', SimulatePaymentView.as_view(), name='payment-simulate'),
]