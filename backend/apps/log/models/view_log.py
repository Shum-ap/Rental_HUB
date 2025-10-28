import logging
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.listings.models import Listing
from apps.core.models import SoftDeleteModel
from apps.core.querysets import SoftDeleteManager

logger = logging.getLogger("log_views")


class ViewLog(SoftDeleteModel):
    """
    Tracks listing views by users for analytics and recommendations.
    Prevents repeated logs from the same user within a short timeframe.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="view_logs"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="view_logs"
    )
    viewed_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    objects = SoftDeleteManager()

    class Meta:
        ordering = ["-viewed_at"]
        verbose_name = _("Listing View Log")
        verbose_name_plural = _("Listing View Logs")
        indexes = [
            models.Index(fields=["user", "listing"]),
            models.Index(fields=["listing"]),
        ]
        unique_together = ("user", "listing", "viewed_at")

    def __str__(self):
        return f"{self.user.email} viewed {self.listing.title} at {self.viewed_at:%Y-%m-%d %H:%M}"

    def clean(self):
        """Validate IP and user agent length."""
        if self.user_agent and len(self.user_agent) > 300:
            raise ValueError(_("User-Agent string is too long."))
        if not self.listing.is_active:
            raise ValueError(_("Cannot log views for inactive listing."))

    def save(self, *args, **kwargs):
        """
        Save view entry with validation and duplicate prevention.
        If the same user views the same listing within 10 minutes,
        the view will not be duplicated.
        """
        try:
            self.full_clean()


            recent_view_exists = ViewLog.objects.filter(
                user=self.user,
                listing=self.listing,
                viewed_at__gte=timezone.now() - timezone.timedelta(minutes=10),
                is_deleted=False,
            ).exists()

            if recent_view_exists:
                logger.info(
                    "Skipped duplicate view log: user=%s listing=%s",
                    self.user.email,
                    self.listing.title,
                )
                return

            super().save(*args, **kwargs)
            logger.info(
                "View logged: user=%s listing_id=%s ip=%s",
                self.user.email,
                self.listing_id,
                self.ip_address or "N/A",
            )

        except Exception as exc:
            logger.error(
                "Error saving view log (user=%s, listing=%s): %s",
                getattr(self.user, "email", "Anonymous"),
                getattr(self.listing, "title", "Unknown"),
                exc,
            )
            raise

    def delete(self, *args, **kwargs):
        """Soft delete and log event."""
        try:
            super().delete(*args, **kwargs)
            logger.warning("View log deleted: %s", self)
        except Exception as exc:
            logger.error("Error deleting view log (%s): %s", self, exc)
            raise
