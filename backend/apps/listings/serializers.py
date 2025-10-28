from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    popularity_score = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = "__all__"
        read_only_fields = ("owner", "created_at", "updated_at")

    def get_popularity_score(self, obj):
        return obj.popularity_score
