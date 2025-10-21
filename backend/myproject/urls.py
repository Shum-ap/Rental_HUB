from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from myproject.routers import router
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from myproject import views

urlpatterns = [
    # Главная страница
    path("", views.home, name="home"),

    # HTML-страницы объявлений
    path("", include("apps.listings.urls_html")),

    # Админка
    path("admin/", admin.site.urls),

    # API
    path("api/v1/", include(router.urls)),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/bookings/", include("apps.bookings.urls")),
    path("payments/", include("apps.payments.urls")),

    # JWT токены
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Документация API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
