from django.db import models

class ListingStatusChoices(models.TextChoices):
    AVAILABLE = "available", "Available"
    UNAVAILABLE = "unavailable", "Unavailable"
    RENTED = "rented", "Rented"

class ListingTypeChoices(models.TextChoices):
    APARTMENT = "apartment", "Apartment"
    HOUSE = "house", "House"
    STUDIO = "studio", "Studio"
    VILLA = "villa", "Villa"
