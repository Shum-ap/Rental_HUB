from django.db import models
from apps.core.models import SoftDeleteModel
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchHistory(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    search_query = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    min_price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rooms = models.PositiveIntegerField(null=True, blank=True)
    listing_type = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search by {self.user.username if self.user else 'Anonymous'}: {self.search_query}"

    @classmethod
    def get_popular_queries(cls, limit=10):
        """Возвращает популярные поисковые запросы"""
        return cls.objects.values('search_query').annotate(
            count=models.Count('search_query')
        ).order_by('-count')[:limit]