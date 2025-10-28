from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.template import TemplateDoesNotExist


@shared_task
def send_booking_confirmation_email(booking_id):
    from .models import Reservation
    booking = Reservation.objects.get(id=booking_id)

    subject = f"Reservation Confirmation — {booking.rental_property.title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [booking.user.email]

    nights = (booking.end_date - booking.start_date).days
    context = {
        "booking": booking,
        "nights": nights,
        "site_url": "https://rentalhub.com" if not settings.DEBUG else "http://127.0.0.1:8000",
    }

    try:
        html_content = render_to_string("emails/booking_confirmation_email.html", context)
        text_content = render_to_string("emails/booking_confirmation_email.txt", context)
    except TemplateDoesNotExist:
        html_content = f"<p>Your booking for {booking.rental_property.title} is confirmed.</p>"
        text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_booking_canceled_email(booking_id):
    from .models import Reservation
    booking = Reservation.objects.get(id=booking_id)

    subject = f"Reservation Canceled — {booking.rental_property.title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [booking.user.email]

    context = {
        "booking": booking,
        "site_url": "https://rentalhub.com" if not settings.DEBUG else "http://127.0.0.1:8000",
    }

    try:
        html_content = render_to_string("emails/booking_canceled_email.html", context)
        text_content = render_to_string("emails/booking_canceled_email.txt", context)
    except TemplateDoesNotExist:
        html_content = f"<p>Your booking for {booking.rental_property.title} was canceled.</p>"
        text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_booking_completed_email(booking_id):
    from .models import Reservation
    booking = Reservation.objects.get(id=booking_id)

    subject = f"Reservation Completed — {booking.rental_property.title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [booking.user.email]

    context = {
        "booking": booking,
        "site_url": "https://rentalhub.com" if not settings.DEBUG else "http://127.0.0.1:8000",
    }

    try:
        html_content = render_to_string("emails/booking_completed_email.html", context)
        text_content = render_to_string("emails/booking_completed_email.txt", context)
    except TemplateDoesNotExist:
        html_content = f"<p>Your stay at {booking.rental_property.title} has been successfully completed.</p>"
        text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_payment_success_email(booking_id):
    from .models import Reservation
    booking = Reservation.objects.get(id=booking_id)

    subject = f"Transaction Successful — {booking.rental_property.title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [booking.user.email]

    context = {
        "booking": booking,
        "site_url": "https://rentalhub.com" if not settings.DEBUG else "http://127.0.0.1:8000",
    }

    try:
        html_content = render_to_string("emails/payment_success_email.html", context)
        text_content = render_to_string("emails/payment_success_email.txt", context)
    except TemplateDoesNotExist:
        html_content = f"<p>Your payment for {booking.rental_property.title} was successful.</p>"
        text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
