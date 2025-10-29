from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from myproject.routers import router
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from myproject import views
from apps.users.views import UserRegisterView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("/en/")),

    path("i18n/", include("django.conf.urls.i18n")),

    path("api/v1/", include(router.urls)),

    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/listings/", include("apps.listings.urls")),
    path("api/v1/reservations/", include("apps.reservations.urls")),
    path("api/v1/feedbacks/", include("apps.feedbacks.urls")),
    path("api/v1/log/", include("apps.log.urls")),
    path("api/v1/transactions/", include("apps.transactions.urls")),

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]



urlpatterns += i18n_patterns(
    path("", views.home, name="home"),
    path("", include("apps.listings.urls_html")),

)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
