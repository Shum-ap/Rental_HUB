from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet
from apps.listings.views import ListingViewSet
from apps.reservations.views import ReservationViewSet
from apps.transactions.views import TransactionViewSet
from apps.feedbacks.views import FeedbackViewSet
from apps.log.views import SearchHistoryViewSet, ViewLogViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"listings", ListingViewSet, basename="property")
router.register(r"reservations", ReservationViewSet, basename="booking")
router.register(r"transactions", TransactionViewSet, basename="payment")
router.register(r"feedbacks", FeedbackViewSet, basename="review")
router.register(r"search-history", SearchHistoryViewSet, basename="search-history")
router.register(r"views", ViewLogViewSet, basename="view-log")
