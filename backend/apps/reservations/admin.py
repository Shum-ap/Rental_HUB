from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Reservation model.
    Displays key booking details and allows filtering by status and date.
    """

    list_display = (
        "rental_property",
        "user",
        "start_date",
        "end_date",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "start_date",
        "end_date",
        "created_at",
    )

    search_fields = (
        "rental_property__title",
        "user__email",
    )

    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
