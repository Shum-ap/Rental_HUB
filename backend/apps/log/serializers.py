from rest_framework import serializers
from .models import SearchHistory


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = [
            "id",
            "user",
            "search_query",
            "location",
            "min_price",
            "max_price",
            "rooms",
            "property_type",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]