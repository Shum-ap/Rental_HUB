from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import SoftDeleteModel

User = get_user_model()


class UserType(SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserProfile(SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type.name if self.user_type else 'No Type'})"