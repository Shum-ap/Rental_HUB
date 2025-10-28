from django.db import models
from django.conf import settings
from .listing import Listing

class Rental(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="rentals")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rentals")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rental {self.id} for {self.listing}"