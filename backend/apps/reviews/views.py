from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Review
from .serializers import ReviewSerializer
from apps.users.permissions import IsTenant, IsOwnerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD для отзывов с поддержкой soft-delete.
    """
    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [permissions.IsAuthenticated, IsTenant]
        elif self.action in ["update", "partial_update", "destroy", "soft_delete", "restore", "hard_delete"]:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["delete"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        review = self.get_object()
        review.soft_delete()
        return Response({"detail": "Review soft-deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="restore")
    def restore(self, request, pk=None):
        review = get_object_or_404(Review.objects.with_deleted(), pk=pk)
        self.check_object_permissions(request, review)
        review.restore()
        return Response({"detail": "Review restored."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="hard-delete")
    def hard_delete(self, request, pk=None):
        review = get_object_or_404(Review.objects.with_deleted(), pk=pk)
        self.check_object_permissions(request, review)
        review.hard_delete()
        return Response({"detail": "Review permanently deleted."}, status=status.HTTP_204_NO_CONTENT)
