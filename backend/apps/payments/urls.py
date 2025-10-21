from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
]
