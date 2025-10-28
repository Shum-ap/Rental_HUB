import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.listings.models.listing import Listing
from apps.listings.utils import send_new_property_notification

logger = logging.getLogger("log_views")

@receiver(post_save, sender=Listing)
def notify_new_property(sender, instance, created, **kwargs):
    """Triggered when a new listing is created."""
    if created:
        try:
            send_new_property_notification(instance)
            logger.info(f"New listing created: {instance.title} by {instance.owner.email}")
        except Exception as e:
            logger.error(f"Failed to send listing notification for {instance.id}: {e}", exc_info=True)
