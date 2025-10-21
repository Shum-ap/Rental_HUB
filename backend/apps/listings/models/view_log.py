from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import SoftDeleteModel
from apps.listings.models.property import Property

class ViewLog(SoftDeleteModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='view_logs')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} viewed {self.property.title} at {self.viewed_at}"