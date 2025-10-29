from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.users.models import UserProfile, UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for viewing/updating user data."""
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]
        read_only_fields = ["id", "email"]


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration, automatically creating a UserProfile."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        tenant_type, _ = UserType.objects.get_or_create(
            name="tenant",
            defaults={"description": "Default tenant role"},
        )

        UserProfile.objects.create(user=user, user_type=tenant_type)

        return user
