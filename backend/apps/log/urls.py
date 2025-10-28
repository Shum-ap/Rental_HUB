from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SearchHistoryViewSet, ViewLogViewSet

router = DefaultRouter()
router.register(r"search-history", SearchHistoryViewSet, basename="search-history")
router.register(r"views", ViewLogViewSet, basename="view-log")

urlpatterns = [
    path("", include(router.urls)),
]
