from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.transactions.models import Transaction
from apps.reservations.models import Reservation


@receiver(post_save, sender=Transaction)
def update_reservation_status_on_payment(sender, instance, created, **kwargs):
    """
    Когда платёж успешно завершён — обновляем статус бронирования.
    """
    if created and instance.status == "completed":
        reservation = instance.reservation  # новое имя вместо booking
        reservation.status = "confirmed"
        reservation.is_confirmed = True
        reservation.save(update_fields=["status", "is_confirmed"])
