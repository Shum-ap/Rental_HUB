from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Booking
from .serializers import BookingSerializer
from apps.users.permissions import IsLandlord, IsTenant, IsOwnerOrReadOnly


class BookingViewSet(viewsets.ModelViewSet):
    """
    CRUD для бронирований.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsTenant | permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "start_date": ["gte", "lte"],
        "end_date": ["gte", "lte"],
        "status": ["exact"],
    }
    search_fields = ["status"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted") == "true"
        base_qs = Booking.objects.with_deleted() if include_deleted else Booking.objects.all()

        if not user.is_authenticated:
            return Booking.objects.none()

        # Хост видит брони на свои объекты, арендатор — только свои
        if user.groups.filter(name="Host").exists():
            return base_qs.filter(rental_property__owner=user)
        return base_qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # --- Подтверждение (Host) ---
    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsLandlord])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.rental_property.owner == request.user:
            booking.confirm()
            return Response({"detail": "Booking confirmed."}, status=status.HTTP_200_OK)
        return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

    # --- Отмена (Tenant / владелец брони) ---
    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.cancel()
        return Response({"detail": "Booking cancelled."}, status=status.HTTP_200_OK)

    # --- Soft delete ---
    @action(detail=True, methods=["delete"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def soft_delete(self, request, pk=None):
        booking = self.get_object()
        booking.soft_delete()
        return Response({"detail": "Booking soft-deleted."}, status=status.HTTP_204_NO_CONTENT)

    # --- Restore ---
    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def restore(self, request, pk=None):
        booking = get_object_or_404(Booking.objects.with_deleted(), pk=pk)
        booking.restore()
        return Response({"detail": "Booking restored."}, status=status.HTTP_200_OK)

    # --- Hard delete ---
    @action(detail=True, methods=["delete"], url_path="hard-delete", permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def hard_delete(self, request, pk=None):
        booking = get_object_or_404(Booking.objects.with_deleted(), pk=pk)
        booking.hard_delete()
        return Response({"detail": "Booking permanently deleted."}, status=status.HTTP_204_NO_CONTENT)
