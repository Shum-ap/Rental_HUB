from django.contrib import admin
from .models import SearchHistory

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'search_query', 'location', 'created_at')
    list_filter = ('created_at', 'location')
    search_fields = ('search_query', 'location', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
