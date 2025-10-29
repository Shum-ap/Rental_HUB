from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, user_profile, UserRegisterView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("profile/", user_profile, name="user-profile"),
    path("register/", UserRegisterView.as_view(), name="register"),
]

urlpatterns += router.urls
