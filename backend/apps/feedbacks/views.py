import logging
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.feedbacks.models import Feedback
from apps.feedbacks.serializers import FeedbackSerializer
from apps.users.permissions import IsTenant, IsOwnerOrReadOnly
from apps.reservations.models import Reservation

logger = logging.getLogger("log_views")


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for user feedbacks.
    Supports CRUD, soft-delete, restore, and hard-delete actions.
    Users can only leave feedback for properties they have stayed at.
    """
    queryset = Feedback.objects.all().order_by("-created_at")
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        """
        Return permissions based on action type.
        - Only tenants can create feedback.
        - Only the feedback owner can update/delete/restore.
        """
        try:
            if self.action == "create":
                permission_classes = [permissions.IsAuthenticated, IsTenant]
            elif self.action in ["update", "partial_update", "destroy", "soft_delete", "restore", "hard_delete"]:
                permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
            else:
                permission_classes = [permissions.AllowAny]
            return [permission() for permission in permission_classes]
        except Exception as e:
            logger.error("Error determining permissions in FeedbackViewSet: %s", e, exc_info=True)
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """
        Validate that the user has stayed at the property before allowing feedback.
        """
        user = self.request.user
        property_id = self.request.data.get("rental_property")

        if not property_id:
            raise PermissionDenied("The 'rental_property' field is required.")

        has_stayed = Reservation.objects.filter(
            user=user,
            rental_property_id=property_id,
            end_date__lt=timezone.now().date(),
            is_deleted=False,
            status__in=["confirmed", "completed"]
        ).exists()

        if not has_stayed:
            raise PermissionDenied("You can only leave feedback for properties you have stayed at.")

        serializer.save(user=user)
        logger.info("Feedback created by user %s for property_id=%s", user, property_id)

    def create(self, request, *args, **kwargs):
        """
        Handles feedback creation with error logging.
        """
        try:
            response = super().create(request, *args, **kwargs)
            logger.info("Feedback created via API by user %s", request.user)
            return response
        except Exception as e:
            logger.error("Error during feedback creation: %s", e, exc_info=True)
            return Response({"detail": "Error creating feedback."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["delete"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        """Soft delete a feedback (marks as deleted without removing it from DB)."""
        try:
            review = self.get_object()
            review.soft_delete()
            logger.warning("Feedback ID %s soft-deleted by user %s", review.id, request.user)
            return Response({"detail": "Feedback soft-deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Error soft-deleting feedback ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error deleting feedback."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["patch"], url_path="restore")
    def restore(self, request, pk=None):
        """Restore a previously soft-deleted feedback."""
        try:
            review = get_object_or_404(Feedback.objects.with_deleted(), pk=pk)
            self.check_object_permissions(request, review)
            review.restore()
            logger.info("Feedback ID %s restored by user %s", pk, request.user)
            return Response({"detail": "Feedback restored."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error restoring feedback ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error restoring feedback."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["delete"], url_path="hard-delete")
    def hard_delete(self, request, pk=None):
        """Permanently delete a feedback from the database."""
        try:
            review = get_object_or_404(Feedback.objects.with_deleted(), pk=pk)
            self.check_object_permissions(request, review)
            review.hard_delete()
            logger.warning("Feedback ID %s permanently deleted by user %s", pk, request.user)
            return Response({"detail": "Feedback permanently deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Error hard-deleting feedback ID %s: %s", pk, e, exc_info=True)
            return Response({"detail": "Error deleting feedback."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
