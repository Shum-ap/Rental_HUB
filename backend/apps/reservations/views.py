import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer
from apps.users.permissions import IsLandlord, IsTenant, IsOwnerOrReadOnly

logger = logging.getLogger("log_views")


class ReservationViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing reservations (CRUD).
    - Tenants can create and manage their own reservations.
    - Hosts can confirm reservations for their listings.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
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
        """
        Return filtered queryset depending on user type.
        - Hosts see reservations for their listings.
        - Tenants see their own reservations.
        """
        try:
            user = self.request.user
            include_deleted = self.request.query_params.get("include_deleted") == "true"
            base_qs = Reservation.objects.with_deleted() if include_deleted else Reservation.objects.all()

            if not user.is_authenticated:
                logger.warning("Anonymous user attempted to access reservations.")
                return Reservation.objects.none()

            if user.groups.filter(name="Host").exists():
                qs = base_qs.filter(rental_property__owner=user)
                logger.info("Host %s retrieved their listing reservations.", user)
                return qs
            else:
                qs = base_qs.filter(user=user)
                logger.info("Tenant %s retrieved their reservations.", user)
                return qs
        except Exception as e:
            logger.error("Error retrieving reservations queryset: %s", e, exc_info=True)
            return Reservation.objects.none()

    def perform_create(self, serializer):
        """Automatically assign the current user as the booking owner."""
        try:
            serializer.save(user=self.request.user)
            logger.info("Reservation created successfully by user %s", self.request.user)
        except Exception as e:
            logger.error("Error creating booking: %s", e, exc_info=True)
            raise

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsLandlord])
    def confirm(self, request, pk=None):
        """
        PATCH /api/v1/reservations/<id>/confirm/
        Allows the listing owner (Host) to confirm a booking.
        """
        try:
            booking = self.get_object()
            if booking.rental_property.owner == request.user:
                booking.confirm()
                logger.info("Reservation %s confirmed by host %s", booking.id, request.user)
                return Response({"detail": "Reservation confirmed."}, status=status.HTTP_200_OK)
            logger.warning("User %s tried to confirm unauthorized booking %s", request.user, booking.id)
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error("Error confirming booking ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error confirming booking."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def cancel(self, request, pk=None):
        """
        PATCH /api/v1/reservations/<id>/cancel/
        Allows tenant or host to cancel their own booking.
        """
        try:
            booking = self.get_object()
            booking.cancel()
            logger.info("Reservation %s cancelled by user %s", booking.id, request.user)
            return Response({"detail": "Reservation cancelled."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error cancelling booking ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error cancelling booking."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["delete"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def soft_delete(self, request, pk=None):
        """Soft delete a booking (mark as deleted)."""
        try:
            booking = self.get_object()
            booking.soft_delete()
            logger.warning("Reservation %s soft-deleted by user %s", booking.id, request.user)
            return Response({"detail": "Reservation soft-deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Error soft-deleting booking ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error deleting booking."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def restore(self, request, pk=None):
        """Restore a previously soft-deleted booking."""
        try:
            booking = get_object_or_404(Reservation.objects.with_deleted(), pk=pk)
            booking.restore()
            logger.info("Reservation %s restored by user %s", booking.id, request.user)
            return Response({"detail": "Reservation restored."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error restoring booking ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error restoring booking."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["delete"], url_path="hard-delete", permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def hard_delete(self, request, pk=None):
        """Permanently delete a booking."""
        try:
            booking = get_object_or_404(Reservation.objects.with_deleted(), pk=pk)
            booking.hard_delete()
            logger.warning("Reservation %s permanently deleted by user %s", booking.id, request.user)
            return Response({"detail": "Reservation permanently deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Error hard-deleting booking ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error deleting booking."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
