import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from apps.users.models import User
from apps.listings.models import Listing
from apps.reservations.models import Reservation
from apps.feedbacks.models import Feedback

@pytest.mark.django_db
class TestFeedbackAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.listing = Listing.objects.create(
            title="Test Listing",
            description="Nice place",
            location="Berlin",
            price_eur=100,
            rooms=2,
            listing_type="apartment",
            owner=self.user,
        )
        self.past_reservation = Reservation.objects.create(
            user=self.user,
            rental_property=self.listing,
            start_date=timezone.now().date().replace(day=1),
            end_date=timezone.now().date().replace(day=5),
            status="confirmed",
            is_confirmed=True,
        )

    def test_create_feedback(self):
        payload = {
            "rental_property": self.listing.id,
            "rating": 4,
            "comment": "Great stay!"
        }
        response = self.client.post("/api/v1/feedbacks/", payload)
        assert response.status_code == 201
        assert Feedback.objects.count() == 1
