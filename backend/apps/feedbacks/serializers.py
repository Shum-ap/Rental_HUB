from rest_framework import serializers
from apps.feedbacks.models import Feedback
from apps.listings.models import Listing


class FeedbackSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    rental_property = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        required=True,
        help_text="ID of the listing being reviewed."
    )

    class Meta:
        model = Feedback
        fields = [
            'id',
            'rental_property',
            'user',
            'rating',
            'comment',
            'created_at',
            'updated_at',
            'is_deleted',
            'deleted_at',
        ]
        read_only_fields = [
            'user',
            'created_at',
            'updated_at',
            'is_deleted',
            'deleted_at',
        ]

    def validate_rating(self, value):
        """Ensure rating is within 1 to 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
