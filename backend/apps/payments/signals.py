from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.payments.models import Payment
from apps.bookings.models import Booking

@receiver(post_save, sender=Payment)
def update_booking_status_on_payment(sender, instance, created, **kwargs):
    """
    Если платеж успешный — обновляем статус бронирования.
    """
    if created and instance.status == 'completed':
        booking = instance.booking
        booking.status = 'confirmed'
        booking.is_confirmed = True
        booking.save(update_fields=['status', 'is_confirmed'])