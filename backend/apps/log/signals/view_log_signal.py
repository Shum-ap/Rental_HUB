import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.listings.models import Listing
from apps.log.models import ViewLog

logger = logging.getLogger("log_views")
User = get_user_model()


@receiver(post_save, sender=Listing)
def create_view_log_on_property_view(sender, instance, created, **kwargs):
    """
    Automatically creates a ViewLog entry when a Listing object is viewed.
    Only triggers if the 'viewed_by' attribute is temporarily set.
    """
    user = getattr(instance, "viewed_by", None)
    request = getattr(instance, "request", None)

    if user and user.is_authenticated:
        try:
            ip_address = getattr(request, "META", {}).get("REMOTE_ADDR") if request else None
            user_agent = getattr(request, "META", {}).get("HTTP_USER_AGENT", "")[:300]

            ViewLog.objects.create(
                user=user,
                listing=instance,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            logger.info(f"ViewLog created automatically for Listing {instance.id} by {user.email}")

        except Exception as e:
            logger.error(f"Failed to create ViewLog for Listing {instance.id}: {e}", exc_info=True)
