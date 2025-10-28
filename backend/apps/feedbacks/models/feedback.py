import logging
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.listings.models import Listing
from apps.core.models import SoftDeleteModel
from apps.core.querysets import SoftDeleteManager

logger = logging.getLogger("log_views")


class Feedback(SoftDeleteModel):
    """Represents a user's feedback for a listing."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()

    class Meta:
        db_table = "feedbacks_feedback"
        ordering = ["-created_at"]
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")
        unique_together = ("user", "listing")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["listing"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.listing.title} ({self.rating}/5)"
