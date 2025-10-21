from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.listings.models import Property
from apps.listings.utils import send_new_property_notification


@receiver(post_save, sender=Property)
def notify_new_property(sender, instance, created, **kwargs):
    """
    При создании нового объекта отправляем уведомление.
    """
    if created:
        try:
            send_new_property_notification(instance)
        except Exception as e:
            print(f"[SIGNAL ERROR] Ошибка при отправке уведомления о новом объекте: {e}")
