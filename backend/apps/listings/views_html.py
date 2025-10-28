import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.listings.models import Listing
from apps.reservations.models import Reservation
from apps.feedbacks.models import Feedback
from apps.users.decorators import landlord_required
from apps.log.models import ViewLog, SearchHistory

logger = logging.getLogger("log_views")


def property_list_html(request):
    """
    HTML list of active & available listings.
    Supports search filtering and multilingual display.
    If GET params present, optionally store SearchHistory for authenticated users.
    """
    listings = Listing.objects.filter(is_active=True, status=Listing.AvailabilityStatus.AVAILABLE)

    search_query = request.GET.get("search")
    if search_query:
        listings = (
            listings.filter(title__icontains=search_query)
            | listings.filter(description__icontains=search_query)
        )

    try:
        if request.user.is_authenticated and search_query:
            SearchHistory.objects.create(
                user=request.user,
                search_query=search_query,
                location="",
            )
            logger.info("SearchHistory saved (HTML) user=%s query=%s",
                        request.user.email, search_query)
    except Exception as exc:
        logger.error("Failed to save SearchHistory (HTML): %s", exc)

    return render(request, "listings/property_list.html", {"listings": listings})


def property_detail_html(request, pk):
    """
    HTML detail page with booking, feedback display and feedback form.
    Also records a ViewLog for authenticated users.
    """
    property_obj = get_object_or_404(Listing, pk=pk, is_active=True)

    # === Log view ===
    try:
        if request.user.is_authenticated:
            ViewLog.objects.create(
                user=request.user,
                listing=property_obj,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:300],
            )
            logger.info("ViewLog created (HTML) user=%s property_id=%s",
                        request.user.email, property_obj.id)
    except Exception as exc:
        logger.error("Failed to create ViewLog (HTML) for property_id=%s: %s",
                     property_obj.id, exc)

    # === Booking logic ===
    if request.method == "POST" and "book" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, _("Please log in to make a booking."))
            return redirect("/admin/login/")

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not start_date or not end_date:
            messages.error(request, _("Please select check-in and check-out dates."))
            return redirect(request.path)

        try:
            start_date_parsed = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_parsed = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, _("Invalid date format."))
            return redirect(request.path)

        if start_date_parsed < timezone.now().date():
            messages.error(request, _("You cannot book a past date."))
            return redirect(request.path)

        if end_date_parsed <= start_date_parsed:
            messages.error(request, _("Check-out date must be after check-in date."))
            return redirect(request.path)

        booking = Reservation.objects.create(
            user=request.user,
            rental_property=property_obj,
            start_date=start_date_parsed,
            end_date=end_date_parsed,
        )

        messages.success(request, _("Booking created successfully! Total: €%(price)s") % {
            "price": booking.total_price_eur
        })
        return redirect("booking-confirmation", pk=booking.id)

    # === Feedback creation ===
    elif request.method == "POST" and "review" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, _("Please log in to leave a review."))
            return redirect("/admin/login/")

        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        if not rating or not rating.isdigit():
            messages.error(request, _("Invalid rating value."))
            return redirect(request.path)

        rating = int(rating)
        if rating < 1 or rating > 5:
            messages.error(request, _("Rating must be between 1 and 5."))
            return redirect(request.path)

        Feedback.objects.update_or_create(
            user=request.user,
            listing=property_obj,
            defaults={"rating": rating, "comment": comment},
        )
        messages.success(request, _("Review successfully saved."))
        return redirect(request.path)

    # === Retrieve all feedbacks ===
    feedbacks = Feedback.objects.filter(listing=property_obj).select_related("user").order_by("-created_at")

    return render(
        request,
        "listings/property_detail.html",
        {
            "listing": property_obj,
            "feedbacks": feedbacks,
        },
    )


def booking_success(request, pk):
    booking = get_object_or_404(Reservation, pk=pk)
    return render(request, "listings/booking_success.html", {"booking": booking})


def booking_confirmation(request, pk):
    booking = get_object_or_404(Reservation, pk=pk)
    return render(request, "listings/booking_confirmation.html", {"booking": booking})


def booking_cancelled(request, pk):
    booking = get_object_or_404(Reservation, pk=pk)
    return render(request, "listings/booking_cancelled.html", {"booking": booking})


def payment_form(request, pk):
    booking = get_object_or_404(Reservation, pk=pk)
    if request.method == "POST":
        booking.confirm()
        messages.success(request, _("Payment successful!"))
        return redirect("payment-success", pk=booking.id)
    return render(request, "listings/payment_form.html", {"booking": booking})


def payment_success(request, pk):
    booking = get_object_or_404(Reservation, pk=pk)
    return render(request, "listings/payment_success.html", {"booking": booking})


@landlord_required
def property_add(request):
    """
    Landlord-only: creates a new listing.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        price_eur = request.POST.get("price_eur")
        rooms = request.POST.get("rooms")
        listing_type = request.POST.get("listing_type")
        image = request.FILES.get("image")

        if not title or not price_eur or not location:
            messages.error(request, _("Please fill all required fields."))
            return redirect(request.path)

        try:
            price_eur = float(price_eur)
        except ValueError:
            messages.error(request, _("Price must be a number."))
            return redirect(request.path)

        Listing.objects.create(
            title=title,
            description=description,
            location=location,
            price_eur=price_eur,
            rooms=rooms or 1,
            listing_type=listing_type or "apartment",
            owner=request.user,
            image=image if image else None,
            is_active=True,
            status=Listing.AvailabilityStatus.AVAILABLE,
        )

        messages.success(request, _("Listing “%(title)s” added successfully!") % {"title": title})
        return redirect("listing-list-html")

    return render(request, "listings/property_add.html")
