from django.contrib import admin
from .models import Transaction
# Register your models here.

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'payer', 'course', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'payer__username', 'course__title')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)