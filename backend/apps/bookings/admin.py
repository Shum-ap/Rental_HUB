from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('rental_property', 'user', 'start_date', 'end_date', 'is_confirmed', 'is_cancelled', 'is_active', 'created_at')
    list_filter = ('is_confirmed', 'is_cancelled', 'is_active', 'created_at')
    search_fields = ('rental_property__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
