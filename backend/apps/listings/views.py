from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import F, ExpressionWrapper, FloatField
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
import logging

from apps.listings.models import Listing
from .serializers import ListingSerializer
from apps.users.permissions import IsLandlord, IsOwnerOrReadOnly
from apps.reservations.models import Reservation
from apps.log.models import ViewLog, SearchHistory

logger = logging.getLogger("log_views")


class ListingPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ListingViewSet(viewsets.ModelViewSet):
    """
    CRUD for listings with soft-delete and cached list.
    Also writes ViewLog on retrieve and SearchHistory on list when filters are used.
    """
    serializer_class = ListingSerializer
    pagination_class = ListingPagination
    permission_classes = [IsLandlord | permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "price_eur": ["gte", "lte"],
        "rooms": ["gte", "lte"],
        "listing_type": ["exact"],
        "location": ["icontains"],
    }
    search_fields = ["title", "description", "location"]
    ordering_fields = ["price_eur", "created_at", "average_rating", "popularity_score_calc"]
    ordering = ["-created_at"]

    def get_queryset(self):
        include_deleted = self.request.query_params.get("include_deleted") == "true"
        qs = Listing.objects.with_deleted() if include_deleted else Listing.objects.all()

        qs = qs.filter(is_active=True, is_available=True)

        # 🔧 Переименовано, чтобы не конфликтовало с @property
        popularity_expr = ExpressionWrapper(
            F("average_rating") * 10 + F("view_count") / 10.0,
            output_field=FloatField()
        )
        qs = qs.annotate(popularity_score_calc=popularity_expr)

        return qs

    def list(self, request, *args, **kwargs):
        cache_key = f"property_list_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=300)
        else:
            response = Response(cached_data)

        try:
            if request.user.is_authenticated:
                q = request.query_params.get("search") or ""
                any_filter = bool(q or request.query_params.get("price_eur__gte") or
                                  request.query_params.get("price_eur__lte") or
                                  request.query_params.get("rooms__gte") or
                                  request.query_params.get("rooms__lte") or
                                  request.query_params.get("listing_type") or
                                  request.query_params.get("location"))
                if any_filter:
                    SearchHistory.objects.create(
                        user=request.user,
                        search_query=q,
                        location=request.query_params.get("location") or "",
                        min_price_eur=request.query_params.get("price_eur__gte") or None,
                        max_price_eur=request.query_params.get("price_eur__lte") or None,
                        rooms=(request.query_params.get("rooms__gte")
                               or request.query_params.get("rooms__lte") or None),
                        listing_type=request.query_params.get("listing_type") or None,
                    )
                    logger.info("SearchHistory saved (API) user=%s query=%s",
                                request.user.email, q)
        except Exception as exc:
            logger.error("Failed to save SearchHistory (API): %s", exc)

        return response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            if request.user.is_authenticated:
                ViewLog.objects.create(
                    user=request.user,
                    listing=instance,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:300],
                )
                Listing.objects.filter(id=instance.id).update(view_count=F("view_count") + 1)

                logger.info("ViewLog created (API) user=%s property_id=%s",
                            request.user.email, instance.id)
        except Exception as exc:
            logger.error("Failed to create ViewLog (API) for property_id=%s: %s",
                         instance.id, exc)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["delete"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def soft_delete(self, request, pk=None):
        property_obj = self.get_object()
        property_obj.soft_delete()
        return Response({"detail": "Listing soft-deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def restore(self, request, pk=None):
        property_obj = get_object_or_404(Listing.objects.with_deleted(), pk=pk)
        self.check_object_permissions(request, property_obj)
        property_obj.restore()
        return Response({"detail": "Listing restored."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="hard-delete", permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def hard_delete(self, request, pk=None):
        property_obj = get_object_or_404(Listing.objects.with_deleted(), pk=pk)
        self.check_object_permissions(request, property_obj)
        property_obj.hard_delete()
        return Response({"detail": "Listing permanently deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def pause(self, request, pk=None):
        listing = self.get_object()
        listing.pause_availability()
        return Response({"detail": "Listing paused."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly])
    def resume(self, request, pk=None):
        listing = self.get_object()
        listing.resume_availability()
        return Response({"detail": "Listing resumed."}, status=status.HTTP_200_OK)
