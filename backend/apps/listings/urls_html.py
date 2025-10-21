from django.urls import path
from myproject import views
from .views_html import (
    property_list_html,
    property_detail_html,
    booking_success,
    booking_confirmation,
    booking_cancelled,
    payment_form,
    payment_success,
    property_add,
)

urlpatterns = [
    # Главная страница
    path("", views.home, name="home"),

    # Список и детали объектов
    path("properties/", property_list_html, name="property-list-html"),
    path("properties/<int:pk>/", property_detail_html, name="property-detail-html"),
    path("properties/add/", property_add, name="property-add"),

    # Страницы бронирования
    path("booking/<int:pk>/success/", booking_success, name="booking-success"),
    path("booking/<int:pk>/confirmation/", booking_confirmation, name="booking-confirmation"),
    path("booking/<int:pk>/cancelled/", booking_cancelled, name="booking-cancelled"),
    path("booking/<int:pk>/pay/", payment_form, name="booking-payment"),
    path("booking/<int:pk>/paid/", payment_success, name="payment-success"),

    # Личный кабинет
    path("profile/", views.user_profile, name="user-profile"),

    # Оплата
    path("payment/", views.payment_form, name="payment-form"),
]
