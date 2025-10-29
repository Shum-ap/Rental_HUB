import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User, UserProfile, UserType


@pytest.mark.django_db
def test_user_registration_creates_user_and_profile():
    """
    Проверяет, что регистрация создаёт пользователя, профиль и роль tenant.
    """
    client = APIClient()


    url = reverse("register")


    data = {
        "email": "newuser@example.com",
        "first_name": "Alice",
        "last_name": "Müller",
        "password": "TestPass123!",
    }

    response = client.post(url, data, format="json")


    assert response.status_code == 201, response.data
    assert "message" in response.data
    assert response.data["message"] == "User registered successfully"


    user = User.objects.get(email="newuser@example.com")
    assert user.first_name == "Alice"
    assert user.check_password("TestPass123!") is True


    profile = UserProfile.objects.get(user=user)
    assert profile.user_type is not None


    tenant_type = UserType.objects.get(name="tenant")
    assert profile.user_type == tenant_type


    assert "user" in response.data
    user_data = response.data["user"]
    assert user_data["email"] == "newuser@example.com"
    assert user_data["first_name"] == "Alice"
