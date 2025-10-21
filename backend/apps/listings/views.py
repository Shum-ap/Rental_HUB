from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import Property
from .serializers import PropertySerializer
from apps.users.permissions import IsLandlord, IsOwnerOrReadOnly
from apps.bookings.models import Booking


class PropertyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PropertyViewSet(viewsets.ModelViewSet):
    """
    CRUD для объектов недвижимости с поддержкой soft-delete и кэширования списка.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    pagination_class = PropertyPagination
    permission_classes = [IsLandlord | permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "price": ["gte", "lte"],
        "rooms": ["gte", "lte"],
        "property_type": ["exact"],
        "location": ["icontains"],
    }
    search_fields = ["title", "description", "location"]
    ordering_fields = ["price", "created_at", "average_rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        include_deleted = self.request.query_params.get("include_deleted") == "true"
        qs = Property.objects.with_deleted() if include_deleted else Property.objects.all()
        return qs.filter(is_active=True, is_available=True)

    def list(self, request, *args, **kwargs):
        cache_key = f"property_list_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=300)
            return response
        return Response(cached_data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # --- Soft delete ---
    @action(detail=True, methods=["delete"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def soft_delete(self, request, pk=None):
        property_obj = self.get_object()
        property_obj.soft_delete()
        return Response({"detail": "Property soft-deleted."}, status=status.HTTP_204_NO_CONTENT)

    # --- Restore ---
    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def restore(self, request, pk=None):
        property_obj = get_object_or_404(Property.objects.with_deleted(), pk=pk)
        self.check_object_permissions(request, property_obj)
        property_obj.restore()
        return Response({"detail": "Property restored."}, status=status.HTTP_200_OK)

    # --- Hard delete ---
    @action(detail=True, methods=["delete"], url_path="hard-delete", permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def hard_delete(self, request, pk=None):
        property_obj = get_object_or_404(Property.objects.with_deleted(), pk=pk)
        self.check_object_permissions(request, property_obj)
        property_obj.hard_delete()
        return Response({"detail": "Property permanently deleted."}, status=status.HTTP_204_NO_CONTENT)
