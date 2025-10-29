from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.reservations.models import Reservation
from apps.transactions.models import Transaction
from apps.users.serializers import UserSerializer, UserRegisterSerializer

User = get_user_model()


@login_required
def user_profile(request):
    """Render the user's profile page with reservations and transactions."""
    try:
        reservations = Reservation.objects.filter(user=request.user).order_by("-start_date")
        transactions = Transaction.objects.filter(booking__user=request.user).order_by("-created_at")
        return render(
            request,
            "user_profile.html",
            {"reservations": reservations, "transactions": transactions},
        )
    except Exception as e:
        print(f"[user_profile] Error rendering profile: {e}")
        return render(
            request,
            "user_profile.html",
            {"reservations": [], "transactions": [], "error": str(e)},
        )


@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    """Authenticated user management endpoint."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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


@extend_schema(tags=["Users"])
class UserRegisterView(APIView):
    """Public endpoint for registration (open access)."""

    permission_classes = [AllowAny]
    authentication_classes = []  # Отключаем авторизацию

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account with email, password, and default tenant profile.",
        responses={
            201: OpenApiResponse(response=UserSerializer, description="User successfully registered"),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User registered successfully",
            "user": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
