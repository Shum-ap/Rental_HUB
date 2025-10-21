from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet, UserRegisterView
from apps.listings.views import PropertyViewSet
from apps.bookings.views import BookingViewSet
from apps.payments.views import PaymentViewSet
from apps.reviews.views import ReviewViewSet
from apps.log.views import SearchHistoryViewSet

router = DefaultRouter()

# Пользователи
router.register(r"users", UserViewSet, basename="user")
router.register(r"register", UserRegisterView, basename="register")

# Основные сущности
router.register(r"properties", PropertyViewSet, basename="property")
router.register(r"bookings", BookingViewSet, basename="booking")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"reviews", ReviewViewSet, basename="review")

# Логи / история поиска
router.register(r"search-history", SearchHistoryViewSet, basename="search-history")