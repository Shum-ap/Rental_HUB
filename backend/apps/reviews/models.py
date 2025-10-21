from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.listings.models import Property
from apps.core.models import SoftDeleteModel

User = get_user_model()

class Review(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} → {self.property.title} ({self.rating})"

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")