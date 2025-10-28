import pytest
from rest_framework.test import APIClient
from apps.users.models import User

@pytest.mark.django_db
class TestSearchHistory:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="searcher", password="pass")
        self.client.force_authenticate(user=self.user)

    def test_search_history_recorded(self):
        response = self.client.get("/api/v1/listings/", {
            "location": "Berlin",
            "price_eur__gte": 500,
            "search": "Nice"
        })
        assert response.status_code == 200

        from apps.log.models import SearchHistory
        assert SearchHistory.objects.count() == 1
        history = SearchHistory.objects.first()
        assert history.user == self.user
        assert history.location == "Berlin"
