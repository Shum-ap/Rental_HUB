from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.bookings.models import Booking
from apps.bookings.tasks import (
    send_booking_confirmation_email,
    send_booking_cancelled_email,
    send_payment_success_email,
)


@receiver(post_save, sender=Booking)
def update_property_availability_on_booking(sender, instance, created, **kwargs):
    """
    При создании бронирования делаем объект недоступным.
    """
    if created:
        property_obj = instance.rental_property
        property_obj.is_available = False
        property_obj.save(update_fields=["is_available"])
        print(f"[SIGNAL] Объект '{property_obj.title}' стал недоступным (забронирован).")


@receiver(post_delete, sender=Booking)
def restore_property_availability_on_booking_delete(sender, instance, **kwargs):
    """
    При удалении брони делаем объект снова доступным.
    """
    property_obj = instance.rental_property
    property_obj.is_available = True
    property_obj.save(update_fields=["is_available"])
    print(f"[SIGNAL] Объект '{property_obj.title}' снова доступен.")


@receiver(post_save, sender=Booking)
def send_booking_emails(sender, instance, created, **kwargs):
    """
    Отправка писем при изменениях бронирования.
    """
    try:
        if created:
            send_booking_confirmation_email.delay(instance.id)
        elif instance.status == "confirmed":
            send_payment_success_email.delay(instance.id)
        elif instance.status == "cancelled":
            send_booking_cancelled_email.delay(instance.id)
    except Exception as e:
        print(f"[SIGNAL ERROR] Ошибка при отправке писем для брони {instance.id}: {e}")
