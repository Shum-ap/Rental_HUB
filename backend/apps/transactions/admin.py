from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'user', 'amount_eur', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reservation__id', 'user__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
