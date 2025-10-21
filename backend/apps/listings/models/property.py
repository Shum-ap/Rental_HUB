from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from apps.core.models import SoftDeleteModel
from apps.core.querysets import SoftDeleteManager


class Property(SoftDeleteModel):
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveIntegerField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="properties/", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    objects = SoftDeleteManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.title

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")
        if self.rooms < 1:
            raise ValidationError("Property must have at least one room.")

    @property
    def popularity_score(self):
        return (float(self.average_rating) * 10) + (self.view_count / 10)

    def pause_availability(self):
        self.is_available = False
        self.save()

    def resume_availability(self):
        self.is_available = True
        self.save()


# Сигналы
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.listings.utils import send_new_property_notification


@receiver(post_save, sender=Property)
def notify_new_property(sender, instance, created, **kwargs):
    if created:
        send_new_property_notification(instance)