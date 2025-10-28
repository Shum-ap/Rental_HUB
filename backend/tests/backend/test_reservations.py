import pytest
from rest_framework.test import APIClient
from datetime import timedelta
from django.utils import timezone
from apps.users.models import User
from apps.listings.models import Listing
from apps.reservations.models import Reservation

@pytest.mark.django_db
class TestReservationAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tenant", password="pass")
        self.client.force_authenticate(user=self.user)
        self.listing = Listing.objects.create(
            title="Test Property",
            description="Nice place",
            location="Berlin",
            price_eur=100,
            rooms=2,
            listing_type="apartment",
            owner=self.user,
        )

    def test_create_reservation(self):
        today = timezone.now().date()
        payload = {
            "rental_property": self.listing.id,
            "start_date": today + timedelta(days=1),
            "end_date": today + timedelta(days=3),
        }
        response = self.client.post("/api/v1/reservations/", payload)
        assert response.status_code == 201
        assert Reservation.objects.count() == 1
