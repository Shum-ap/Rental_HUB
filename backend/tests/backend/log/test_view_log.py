import pytest
from rest_framework.test import APIClient
from apps.users.models import User
from apps.listings.models import Property
from apps.log.models import ViewLog

@pytest.mark.django_db
class TestViewLogAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='alex', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.property = Property.objects.create(
            title='Test Apartment',
            description='Nice place',
            location='Berlin',
            price=1000,
            rooms=2,
            property_type='apartment',
            owner=self.user,
            is_active=True,
            is_available=True,
        )

    def test_create_view_log(self):
        response = self.client.post('/api/v1/log/views/', {'property': self.property.id})
        assert response.status_code == 201
        assert ViewLog.objects.count() == 1
        log = ViewLog.objects.first()
        assert log.user == self.user
        assert log.property == self.property

    def test_list_view_logs(self):
        ViewLog.objects.create(user=self.user, property=self.property)
        response = self.client.get('/api/v1/log/views/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['property'] == self.property.id

    def test_user_cannot_see_others_logs(self):
        other_user = User.objects.create_user(username='other', password='pass')
        ViewLog.objects.create(user=other_user, property=self.property)
        response = self.client.get('/api/v1/log/views/')
        assert response.status_code == 200
        assert len(response.data) == 0