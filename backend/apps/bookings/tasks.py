from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template import TemplateDoesNotExist


@shared_task
def send_booking_confirmation_email(booking_id):
    from .models import Booking
    booking = Booking.objects.get(id=booking_id)

    subject = f"Подтверждение бронирования {booking.rental_property.title}"
    try:
        html_message = render_to_string('emails/../../templates/listings/booking_confirmation.html', {'booking': booking})
    except TemplateDoesNotExist:
        html_message = f"<p>Ваше бронирование подтверждено: {booking.rental_property.title}</p>"

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'noreply@rentalhub.com',
        [booking.user.email],
        html_message=html_message
    )


@shared_task
def send_booking_cancelled_email(booking_id):
    from .models import Booking
    booking = Booking.objects.get(id=booking_id)

    subject = f"Бронирование отменено: {booking.rental_property.title}"
    try:
        html_message = render_to_string('emails/../../templates/listings/booking_cancelled.html', {'booking': booking})
    except TemplateDoesNotExist:
        html_message = f"<p>Ваше бронирование отменено: {booking.rental_property.title}</p>"

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'noreply@rentalhub.com',
        [booking.user.email],
        html_message=html_message
    )


@shared_task
def send_payment_success_email(booking_id):
    from .models import Booking
    booking = Booking.objects.get(id=booking_id)

    subject = f"Оплата прошла успешно: {booking.rental_property.title}"
    try:
        html_message = render_to_string('emails/../../templates/listings/payment_success.html', {'booking': booking})
    except TemplateDoesNotExist:
        html_message = f"<p>Оплата прошла успешно: {booking.rental_property.title}</p>"

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'noreply@rentalhub.com',
        [booking.user.email],
        html_message=html_message
    )