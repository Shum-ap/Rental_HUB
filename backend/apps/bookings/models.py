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

    check_in_time = models.TimeField(default="12:00", verbose_name="Время заезда")
    check_out_time = models.TimeField(default="16:00", verbose_name="Время выезда")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_confirmed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="booking_valid_dates",
            )
        ]

    def __str__(self):
        return f"Бронь {self.user.username} — {self.rental_property.title} ({self.start_date} → {self.end_date})"

    def clean(self):
        """Валидация дат."""
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError("Дата выезда должна быть позже даты заезда.")
        if self.start_date < timezone.now().date():
            raise ValidationError("Нельзя бронировать на прошедшие даты.")

    def confirm(self):
        """Подтверждение бронирования."""
        self.status = "confirmed"
        self.is_confirmed = True
        self.is_cancelled = False
        self.is_active = True
        self.save(update_fields=["status", "is_confirmed", "is_cancelled", "is_active", "updated_at"])

    def cancel(self):
        """Отмена бронирования."""
        self.status = "cancelled"
        self.is_confirmed = False
        self.is_cancelled = True
        self.is_active = False
        self.save(update_fields=["status", "is_confirmed", "is_cancelled", "is_active", "updated_at"])

    def complete(self):
        """Завершение бронирования."""
        self.status = "completed"
        self.is_active = False
        self.save(update_fields=["status", "is_active", "updated_at"])

    @property
    def duration(self):
        """Количество ночей."""
        return max((self.end_date - self.start_date).days, 0)

    @property
    def total_price(self):
        """Общая сумма бронирования."""
        return self.duration * self.rental_property.price if self.duration > 0 else 0
