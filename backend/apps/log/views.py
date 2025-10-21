from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import SearchHistory
from .serializers import SearchHistorySerializer


class SearchHistoryViewSet(viewsets.ModelViewSet):
    """
    CRUD для истории поиска.
    - Пользователь видит только свои записи
    - При создании user проставляется автоматически
    """
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Search history saved", "data": response.data},
            status=status.HTTP_201_CREATED,
        )