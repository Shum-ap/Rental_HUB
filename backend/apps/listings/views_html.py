from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from apps.listings.models import Property
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.users.decorators import landlord_required


def property_list_html(request):
    """Отображение списка всех активных и доступных объектов."""
    properties = Property.objects.filter(is_active=True, is_available=True)
    return render(request, "listings/property_list.html", {"properties": properties})


def property_detail_html(request, pk):
    """Страница объекта — просмотр, бронирование и добавление отзывов."""
    property_obj = get_object_or_404(Property, pk=pk, is_active=True)


    if request.method == "POST" and "book" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "Сначала войдите в систему.")
            return redirect(reverse("admin:login"))

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        check_in_time = request.POST.get("check_in_time") or "12:00"
        check_out_time = request.POST.get("check_out_time") or "16:00"

        if not start_date or not end_date:
            messages.error(request, "Укажите даты заезда и выезда.")
            return redirect(request.path)

        try:
            start_date_parsed = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_parsed = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Некорректный формат даты.")
            return redirect(request.path)

        if start_date_parsed < timezone.now().date():
            messages.error(request, "Нельзя бронировать на прошедшую дату.")
            return redirect(request.path)

        if end_date_parsed <= start_date_parsed:
            messages.error(request, "Дата выезда должна быть позже даты заезда.")
            return redirect(request.path)


        booking = Booking.objects.create(
            user=request.user,
            rental_property=property_obj,
            start_date=start_date_parsed,
            end_date=end_date_parsed,
        )


        booking.total_price = booking.total_price
        booking.save(update_fields=["updated_at"])

        messages.success(request, f"Бронирование создано! Итоговая сумма: {booking.total_price} руб.")
        return redirect("booking-confirmation", pk=booking.id)


    elif request.method == "POST" and "review" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "Авторизуйтесь, чтобы оставить отзыв.")
            return redirect(reverse("admin:login"))

        try:
            rating = int(request.POST.get("rating"))
        except (TypeError, ValueError):
            messages.error(request, "Некорректная оценка.")
            return redirect(request.path)

        comment = request.POST.get("comment", "").strip()

        if rating < 1 or rating > 5:
            messages.error(request, "Оценка должна быть от 1 до 5.")
            return redirect(request.path)

        Review.objects.update_or_create(
            user=request.user,
            property=property_obj,
            defaults={"rating": rating, "comment": comment},
        )
        messages.success(request, "Отзыв успешно сохранён.")
        return redirect(request.path)


    return render(request, "listings/property_detail.html", {"property": property_obj})


def booking_success(request, pk):
    """Страница успешного бронирования."""
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "listings/booking_success.html", {"booking": booking})


def booking_confirmation(request, pk):
    """Страница подтверждения бронирования."""
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "listings/booking_confirmation.html", {"booking": booking})


def booking_cancelled(request, pk):
    """Страница отменённого бронирования."""
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "listings/booking_cancelled.html", {"booking": booking})


def payment_form(request, pk):
    """Форма оплаты бронирования."""
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == "POST":

        booking.confirm()
        messages.success(request, "Оплата успешно проведена, бронирование подтверждено.")
        return redirect("payment-success", pk=booking.id)

    return render(request, "listings/payment_form.html", {"booking": booking})


def payment_success(request, pk):
    """Страница успешной оплаты."""
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "listings/payment_success.html", {"booking": booking})


@landlord_required
def property_add(request):
    """Добавление нового жилья (только для арендодателей)."""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        price = request.POST.get("price")
        rooms = request.POST.get("rooms")
        property_type = request.POST.get("property_type")
        image = request.FILES.get("image")

        if not title or not price or not location:
            messages.error(request, "Заполните все обязательные поля.")
            return redirect(request.path)

        try:
            price = float(price)
        except ValueError:
            messages.error(request, "Цена должна быть числом.")
            return redirect(request.path)

        property_obj = Property.objects.create(
            title=title,
            description=description,
            location=location,
            price=price,
            rooms=rooms or 1,
            property_type=property_type or "apartment",
            owner=request.user,
            image=image if image else None,
            is_active=True,
            is_available=True,
        )

        messages.success(request, f"Объявление «{property_obj.title}» успешно добавлено!")
        return redirect("property-list-html")

    return render(request, "listings/property_add.html")
