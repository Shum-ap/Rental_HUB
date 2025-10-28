from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.reservations.models import Reservation
from apps.transactions.models import Transaction
from apps.users.serializers import UserSerializer, UserRegisterSerializer

User = get_user_model()


# ------------------------
# HTML VIEWS
# ------------------------

@login_required
def user_profile(request):
    """
    Render the user's profile page (HTML) showing their reservations and transactions.
    """
    try:
        reservations = Reservation.objects.filter(user=request.user).order_by("-start_date")
        transactions = Transaction.objects.filter(booking__user=request.user).order_by("-created_at")

        return render(request, "user_profile.html", {
            "reservations": reservations,
            "transactions": transactions,
        })
    except Exception as e:
        print(f"[user_profile] Error rendering profile: {e}")
        return render(request, "user_profile.html", {
            "reservations": [],
            "transactions": [],
            "error": str(e),
        })


# ------------------------
# API VIEWS
# ------------------------

@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for full CRUD operations on users.

    - Admin users can view all users.
    - Regular users can view and update only their own profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return a queryset limited to the current user unless the requester is staff."""
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_object(self):
        """Allow staff to access any user; restrict regular users to their own."""
        user = self.request.user
        if user.is_staff:
            return super().get_object()
        return user


@extend_schema(tags=["Users"])
class UserRegisterView(viewsets.GenericViewSet):
    """
    API endpoint for user registration.
    Only POST requests are allowed.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account with email, password, and default tenant profile.",
        responses={
            201: OpenApiResponse(response=UserSerializer, description="User successfully registered"),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        output = UserSerializer(user)

        response_data = {
            "message": "User registered successfully",
            "user": output.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
