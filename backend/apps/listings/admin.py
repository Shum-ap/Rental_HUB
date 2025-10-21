from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'location', 'price', 'rooms', 'property_type', 'is_active', 'is_available', 'created_at')
    list_filter = ('is_active', 'is_available', 'property_type', 'created_at')
    search_fields = ('title', 'location', 'description')
    readonly_fields = ('created_at', 'updated_at', 'view_count', 'average_rating')
    ordering = ('-created_at',)
    filter_horizontal = ()  # Если есть ManyToMany поля
