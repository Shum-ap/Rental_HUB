from django.apps import AppConfig
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def send_booking_confirmation_email(booking_id):
    from apps.reservations.models import Reservation
    booking = Reservation.objects.get(id=booking_id)

    subject = f"Подтверждение бронирования {booking.rental_property.title}"
    html_message = render_to_string('emails/../../templates/listings/booking_confirmation.html', {'booking': booking})
    plain_message = strip_tags(html_message)
    from_email = 'noreply@rentalhub.com'
    to = [booking.user.email]

    send_mail(subject, plain_message, from_email, to, html_message=html_message)

@shared_task
def send_booking_cancelled_email(booking_id):
    from apps.reservations.models import Reservation
    booking = Reservation.objects.get(id=booking_id)

    subject = f"Бронирование отменено: {booking.rental_property.title}"
    html_message = render_to_string('emails/../../templates/listings/booking_cancelled.html', {'booking': booking})
    plain_message = strip_tags(html_message)
    from_email = 'noreply@rentalhub.com'
    to = [booking.user.email]

    send_mail(subject, plain_message, from_email, to, html_message=html_message)

@shared_task
def send_payment_success_email(booking_id):
    from apps.reservations.models import Reservation
    booking = Reservation.objects.get(id=booking_id)

    subject = f"Оплата прошла успешно: {booking.rental_property.title}"
    html_message = render_to_string('emails/../../templates/listings/payment_success.html', {'booking': booking})
    plain_message = strip_tags(html_message)
    from_email = 'noreply@rentalhub.com'
    to = [booking.user.email]

    send_mail(subject, plain_message, from_email, to, html_message=html_message)


class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.listings'