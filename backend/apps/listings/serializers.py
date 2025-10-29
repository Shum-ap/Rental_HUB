from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    popularity_score = serializers.FloatField(source="popularity_score_calc", read_only=True)

    class Meta:
        model = Listing
        fields = "__all__"
        read_only_fields = ("owner", "created_at", "updated_at")
