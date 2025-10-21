from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg
from apps.reviews.models import Review


@receiver(post_save, sender=Review)
def update_property_average_rating(sender, instance, **kwargs):
    """
    После сохранения отзыва пересчитываем средний рейтинг объекта.
    """
    try:
        prop = instance.property
        avg = Review.objects.filter(property=prop).aggregate(Avg("rating"))["rating__avg"] or 0
        prop.average_rating = avg
        prop.save(update_fields=["average_rating"])
        print(f"[SIGNAL] Средний рейтинг '{prop.title}' обновлён до {avg:.2f}.")
    except Exception as e:
        print(f"[SIGNAL ERROR] Ошибка при пересчёте рейтинга: {e}")
