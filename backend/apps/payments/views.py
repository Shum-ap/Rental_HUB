from rest_framework import viewsets, permissions
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Полноценный CRUD для платежей.
    - Админ видит все платежи
    - Обычный пользователь видит только свои
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        # автоматически проставляем пользователя при создании
        serializer.save(user=self.request.user)