from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    rental_property = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
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
            'rental_property',
            'created_at',
            'updated_at',
            'is_deleted',
            'deleted_at',
        ]