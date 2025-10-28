from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

router = DefaultRouter()
router.register(r"", TransactionViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
]
