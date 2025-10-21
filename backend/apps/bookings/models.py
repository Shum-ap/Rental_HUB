from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.listings.models import Property
from apps.core.models import SoftDeleteModel

User = get_user_model()


class Booking(SoftDeleteModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="bookings")

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    is_confirmed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="booking_valid_dates",
            )
        ]

    def __str__(self):
        return f"{self.user.username} booking for {self.rental_property.title} ({self.start_date} → {self.end_date})"

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError("Дата выезда должна быть позже даты заезда.")
        if self.start_date < timezone.now().date():
            raise ValidationError("Нельзя бронировать на прошедшие даты.")

    @property
    def nights(self):
        """Количество ночей проживания"""
        return max(0, (self.end_date - self.start_date).days)

    @property
    def computed_total(self):
        """Вычислить сумму без сохранения"""
        return self.nights * self.rental_property.price if self.nights > 0 else 0

    def calculate_total_price(self):
        """Вычислить и обновить сумму"""
        self.total_price = self.computed_total
        return self.total_price

    def save(self, *args, **kwargs):
        self.total_price = self.computed_total
        super().save(*args, **kwargs)

    def confirm(self):
        self.status = "confirmed"
        self.is_confirmed = True
        self.is_cancelled = False
        self.is_active = True
        self.save(update_fields=["status", "is_confirmed", "is_cancelled", "is_active", "updated_at", "total_price"])

    def cancel(self):
        self.status = "cancelled"
        self.is_confirmed = False
        self.is_cancelled = True
        self.is_active = False
        self.save(update_fields=["status", "is_confirmed", "is_cancelled", "is_active", "updated_at"])

    def complete(self):
        self.status = "completed"
        self.is_active = False
        self.save(update_fields=["status", "is_active", "updated_at"])

    @property
    def formatted_dates(self):
        """Возвращает удобный формат"""
        return f"{self.start_date.strftime('%d.%m.%Y')} — {self.end_date.strftime('%d.%m.%Y')}"

    @property
    def status_display(self):
        """Возвращает статус"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
