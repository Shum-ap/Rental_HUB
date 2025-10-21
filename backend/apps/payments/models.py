from django.db import models
from django.contrib.auth import get_user_model
from apps.bookings.models import Booking
from apps.core.models import SoftDeleteModel

User = get_user_model()


class Payment(SoftDeleteModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # подтягивается из booking.total_price
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.booking.rental_property.title} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = self.booking.total_price
        super().save(*args, **kwargs)