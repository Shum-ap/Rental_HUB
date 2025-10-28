from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Admin configuration for Listing model.
    Displays listing metadata and supports filtering by status and type.
    """
    list_display = (
        "title",
        "owner",
        "location",
        "price_eur",
        "rooms",
        "listing_type",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("status", "is_active", "listing_type", "created_at")
    search_fields = ("title", "location", "description")
    readonly_fields = ("created_at", "updated_at", "view_count", "average_rating")
    ordering = ("-created_at",)
    filter_horizontal = ()  # For possible ManyToMany fields
