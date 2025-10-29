import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.reservations.models import Reservation
from apps.listings.models import Listing
from apps.reservations.tasks import (
    send_booking_confirmation_email,
    send_booking_canceled_email,
    send_booking_completed_email,
    send_payment_success_email,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Reservation)
def update_property_availability_on_booking(sender, instance, created, **kwargs):
    """При создании бронирования делаем объект недоступным."""
    if created:
        property_obj = instance.rental_property
        property_obj.status = Listing.AvailabilityStatus.UNAVAILABLE
        property_obj.save(update_fields=["status"])
        logger.info(f"[SIGNAL] Listing '{property_obj.title}' marked as unavailable (booked).")


@receiver(post_delete, sender=Reservation)
def restore_property_availability_on_booking_delete(sender, instance, **kwargs):
    """При удалении брони делаем объект снова доступным."""
    property_obj = instance.rental_property
    property_obj.status = Listing.AvailabilityStatus.AVAILABLE
    property_obj.save(update_fields=["status"])
    logger.info(f"[SIGNAL] Listing '{property_obj.title}' marked as available again.")


@receiver(post_save, sender=Reservation)
def handle_booking_emails(sender, instance, created, **kwargs):
    """Асинхронная отправка писем при изменении статуса бронирования."""
    try:
        if created:
            send_booking_confirmation_email.delay(instance.id)
            logger.info(f"[SIGNAL] Reservation #{instance.id}: confirmation email queued.")
        elif instance.status == "confirmed":
            send_payment_success_email.delay(instance.id)
            logger.info(f"[SIGNAL] Reservation #{instance.id}: payment success email queued.")
        elif instance.status == "completed":
            send_booking_completed_email.delay(instance.id)
            logger.info(f"[SIGNAL] Reservation #{instance.id}: completion email queued.")
        elif instance.status == "cancelled":
            send_booking_canceled_email.delay(instance.id)
            logger.info(f"[SIGNAL] Reservation #{instance.id}: cancellation email queued.")
    except Exception as e:
        logger.error(f"[SIGNAL ERROR] Failed to send email for booking #{instance.id}: {e}")
