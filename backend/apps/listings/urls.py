from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
urlpatterns = [ path('', include(router.urls)) ]