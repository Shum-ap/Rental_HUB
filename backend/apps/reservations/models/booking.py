import logging
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import SoftDeleteModel
from apps.core.querysets import SoftDeleteManager
from apps.listings.models import Listing

logger = logging.getLogger("log_views")


class Reservation(SoftDeleteModel):
    """
    Represents a listing booking made by a tenant.

    Includes:
    - Full date validation
    - Automatic status transitions
    - Total price_eur calculation
    - Lifecycle logging
    """

    class ReservationStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    rental_property = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reservations")

    start_date = models.DateField()
    end_date = models.DateField()
    total_price_eur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
    )
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
    )

    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()

    class Meta:
        ordering = ["-start_date"]
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["rental_property"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Reservation #{self.id} by {self.user.email} — {self.rental_property.title}"

    def calculate_total_price_eur(self):
        """Recalculate total price_eur based on listing price and number of days."""
        days = (self.end_date - self.start_date).days
        self.total_price_eur = Decimal(days) * self.rental_property.price_eur
        return self.total_price_eur

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            self.calculate_total_price_eur()
            super().save(*args, **kwargs)
            logger.info(
                "Reservation saved | id=%s user=%s listing=%s status=%s total=%.2f",
                self.id,
                self.user.email,
                self.rental_property.id,
                self.status,
                self.total_price_eur,
            )
        except Exception as exc:
            logger.error("Error saving booking (user=%s listing=%s): %s", self.user.email, self.rental_property.id, exc)
            raise

    def confirm(self):
        try:
            self.status = self.ReservationStatus.CONFIRMED
            self.is_confirmed = True
            self.rental_property.mark_unavailable()
            self.save(update_fields=["status", "is_confirmed"])
            logger.info("Reservation confirmed | id=%s user=%s", self.id, self.user.email)
        except Exception as exc:
            logger.error("Failed to confirm booking #%s: %s", self.id, exc)
            raise

    def complete(self):
        try:
            self.status = self.ReservationStatus.COMPLETED
            self.rental_property.resume_availability()
            self.save(update_fields=["status"])
            logger.info("Reservation completed | id=%s user=%s", self.id, self.user.email)
        except Exception as exc:
            logger.error("Failed to complete booking #%s: %s", self.id, exc)
            raise

    def cancel(self):
        try:
            self.status = self.ReservationStatus.CANCELLED
            self.is_confirmed = False
            self.rental_property.resume_availability()
            self.save(update_fields=["status", "is_confirmed"])
            logger.warning("Reservation cancelled | id=%s user=%s", self.id, self.user.email)
        except Exception as exc:
            logger.error("Failed to cancel booking #%s: %s", self.id, exc)
            raise
