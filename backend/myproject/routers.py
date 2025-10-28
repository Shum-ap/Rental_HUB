from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet, UserRegisterView
from apps.listings.views import ListingViewSet
from apps.reservations.views import ReservationViewSet
from apps.transactions.views import TransactionViewSet
from apps.feedbacks.views import FeedbackViewSet
from apps.log.views import SearchHistoryViewSet

router = DefaultRouter()

# Пользователи
router.register(r"users", UserViewSet, basename="user")
router.register(r"register", UserRegisterView, basename="register")

# Основные сущности
router.register(r"listings", ListingViewSet, basename="property")
router.register(r"reservations", ReservationViewSet, basename="booking")
router.register(r"transactions", TransactionViewSet, basename="payment")
router.register(r"feedbacks", FeedbackViewSet, basename="review")

# Логи / история поиска
router.register(r"search-history", SearchHistoryViewSet, basename="search-history")