import logging
from decimal import Decimal
from django.db import models
from django.db.models import F
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import SoftDeleteModel
from apps.core.querysets import SoftDeleteManager

logger = logging.getLogger("log_views")


class Listing(SoftDeleteModel):
    class ListingType(models.TextChoices):
        APARTMENT = "apartment", _("Apartment")
        HOUSE = "house", _("House")
        STUDIO = "studio", _("Studio")
        VILLA = "villa", _("Villa")
        LOFT = "loft", _("Loft")

    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = "available", _("Available")
        RESERVED = "reserved", _("Reserved")
        UNAVAILABLE = "unavailable", _("Unavailable")
        PAUSED = "paused", _("Paused")

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price_eur = models.DecimalField(
        _("PriceEUR (€)"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Rental price in euros (€) per night."),
    )
    rooms = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text=_("Number of rooms (1–50)."),
    )
    listing_type = models.CharField(
        max_length=20,
        choices=ListingType.choices,
        default=ListingType.APARTMENT,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings"
    )
    image = models.ImageField(upload_to="properties/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
    )
    view_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("5.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()

    class Meta:
        db_table = "listings_listing"
        ordering = ["-created_at"]
        verbose_name = _("Listing")
        verbose_name_plural = _("Listings")
        indexes = [
            models.Index(fields=["location"]),
            models.Index(fields=["price_eur"]),
            models.Index(fields=["listing_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.location}"

    @property
    def popularity_score(self):
        return (float(self.average_rating) * 10) + (self.view_count / 10)

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            logger.info(
                "Listing saved | id=%s title='%s' owner=%s status=%s price_eur=%.2f€",
                self.id, self.title, self.owner.email, self.status, self.price_eur,
            )
        except Exception as exc:
            logger.error("Error saving listing '%s' (owner=%s): %s", self.title, self.owner.email, exc)
            raise

    def pause_availability(self):
        self.status = self.AvailabilityStatus.PAUSED
        self.save(update_fields=["status"])
        logger.info("Listing paused | %s", self)

    def resume_availability(self):
        self.status = self.AvailabilityStatus.AVAILABLE
        self.save(update_fields=["status"])
        logger.info("Listing resumed | %s", self)

    def mark_reserved(self):
        self.status = self.AvailabilityStatus.RESERVED
        self.save(update_fields=["status"])
        logger.info("Listing reserved | %s", self)

    def mark_unavailable(self):
        self.status = self.AvailabilityStatus.UNAVAILABLE
        self.save(update_fields=["status"])
        logger.warning("Listing marked unavailable | %s", self)

    def increment_view_count(self):
        Listing.objects.filter(pk=self.pk).update(view_count=F("view_count") + 1)
        logger.info("Listing viewed | id=%s title='%s'", self.id, self.title)
