from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg
from apps.feedbacks.models import Feedback


@receiver(post_save, sender=Feedback)
def update_property_average_rating(sender, instance, **kwargs):
    """
    После сохранения отзыва пересчитываем средний рейтинг объекта.
    """
    try:
        prop = instance.listing
        avg = Feedback.objects.filter(listing=prop).aggregate(Avg("rating"))["rating__avg"] or 0
        prop.average_rating = avg
        prop.save(update_fields=["average_rating"])
        print(f"[SIGNAL] Средний рейтинг '{prop.title}' обновлён до {avg:.2f}.")
    except Exception as e:
        print(f"[SIGNAL ERROR] Ошибка при пересчёте рейтинга: {e}")
