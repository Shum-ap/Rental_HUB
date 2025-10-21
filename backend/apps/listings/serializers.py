from rest_framework import serializers
from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Property
        fields = "__all__"
        read_only_fields = ("owner", "created_at", "updated_at")