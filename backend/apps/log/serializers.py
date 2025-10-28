from rest_framework import serializers
from apps.log.models import SearchHistory, ViewLog


class SearchHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for user's search history.

    Includes validation of price range and read-only username field.
    """

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = SearchHistory
        fields = [
            "id",
            "username",
            "user",
            "search_query",
            "location",
            "min_price_eur",
            "max_price_eur",
            "rooms",
            "listing_type",
            "created_at",
        ]
        read_only_fields = ["user", "created_at", "username"]

    def validate(self, data):
        """
        Ensure min_price_eur is not greater than max_price_eur.
        """
        min_price_eur = data.get("min_price_eur")
        max_price_eur = data.get("max_price_eur")

        if min_price_eur and max_price_eur and min_price_eur > max_price_eur:
            raise serializers.ValidationError(
                {"price_eur": "Minimum price cannot exceed maximum price."}
            )

        return data


class ViewLogSerializer(serializers.ModelSerializer):
    """
    Serializer for listing view logs.
    """

    class Meta:
        model = ViewLog
        fields = [
            "id",
            "user",
            "listing",
            "viewed_at",
            "ip_address",
            "user_agent",
        ]
        read_only_fields = ["id", "user", "viewed_at"]
