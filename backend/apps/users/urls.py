from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserRegisterView, user_profile


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'register', UserRegisterView, basename='register')

urlpatterns = [
    path("profile/", user_profile, name="user-profile"),
]

urlpatterns += router.urls
