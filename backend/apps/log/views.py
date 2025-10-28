import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _

from apps.log.models import SearchHistory, ViewLog
from apps.log.serializers import SearchHistorySerializer, ViewLogSerializer

logger = logging.getLogger("log_views")


class SearchHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user's search history.

    Endpoints:
    - GET    /api/v1/search-history/          → List all search queries for the current user
    - POST   /api/v1/search-history/          → Add a new search entry
    - DELETE /api/v1/search-history/<id>/     → Delete a specific record
    - DELETE /api/v1/search-history/clear/    → Clear entire user search history
    """

    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns search history entries for the authenticated user.
        """
        return SearchHistory.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        """
        Automatically associates the current user when creating a search entry.
        """
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"Error in perform_create: {e}")
            raise

    def create(self, request, *args, **kwargs):
        """
        Creates a search history record and returns a structured JSON response.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": _("Search query saved successfully."),
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except Exception as e:
            logger.error(f"Error in create: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["delete"], url_path="clear")
    def clear_history(self, request):
        """
        DELETE /api/v1/search-history/clear/
        Clears the entire search history of the authenticated user.
        """
        try:
            queryset = self.get_queryset()
            count = queryset.count()
            queryset.delete()
            return Response(
                {"message": _("Search history cleared."), "deleted": count},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error in clear_history: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ViewLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing listing view logs.

    Endpoints:
    - GET    /api/v1/log/views/        → List all views by the current user
    - POST   /api/v1/log/views/        → Log a new view (auto adds IP/UserAgent)
    - DELETE /api/v1/log/views/<id>/   → Delete a specific view log
    """

    serializer_class = ViewLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns view logs for the authenticated user.
        """
        return ViewLog.objects.filter(user=self.request.user).order_by("-viewed_at")

    def perform_create(self, serializer):
        """
        Automatically sets user, IP, and user-agent on creation.
        Prevents duplicate logs via model logic.
        """
        ip = self.request.META.get("REMOTE_ADDR", "")
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        try:
            serializer.save(
                user=self.request.user,
                ip_address=ip,
                user_agent=user_agent
            )
        except Exception as e:
            logger.error(f"Error in perform_create (ViewLog): {e}")
            raise
