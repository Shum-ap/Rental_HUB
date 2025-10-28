from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_future_date(value):
    """Ensures the given date is not in the past."""
    if value < timezone.now().date():
        raise ValidationError("Date cannot be in the past.")
