from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet

router = DefaultRouter()
router.register(r'feedbacks', FeedbackViewSet, basename='review')

urlpatterns = router.urls

