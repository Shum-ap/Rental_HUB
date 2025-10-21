from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.users.serializers import UserSerializer

User = get_user_model()

# HTML Views

@login_required
def user_profile(request):
    """
    HTML-страница профиля пользователя с его бронированиями и платежами
    """
    bookings = Booking.objects.filter(user=request.user).order_by("-start_date")
    payments = Payment.objects.filter(booking__user=request.user).order_by("-created_at")
    return render(request, "user_profile.html", {
        "bookings": bookings,
        "payments": payments,
    })


# API Views

class UserViewSet(viewsets.ModelViewSet):
    """
    Полноценный CRUD для пользователей через DRF ViewSet.
    - Админ видит всех пользователей
    - Обычный пользователь видит только себя
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_object(self):
        user = self.request.user
        if user.is_staff:
            return super().get_object()
        return user


class UserRegisterView(viewsets.ModelViewSet):
    """
    Отдельный ViewSet для регистрации пользователей.
    Разрешён только POST (создание).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post"]