import logging
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
from django.http import HttpRequest
from apps.listings.models import Listing
from apps.feedbacks.models import Feedback
from apps.log.models import SearchHistory, ViewLog

logger = logging.getLogger("log_views")


def home(request: HttpRequest):
    """
    Home page: shows top 6 active and available listings
    ordered by number of feedbacks and average rating.
    """
    listings = (
        Listing.objects.filter(
            is_active=True,
            status=Listing.AvailabilityStatus.AVAILABLE
        )
        .annotate(
            review_count=Count("feedbacks"),
            avg_rating=Avg("feedbacks__rating"),
        )
        .order_by("-review_count", "-avg_rating")[:6]
    )
    return render(request, "home.html", {"listings": listings})


def property_list(request: HttpRequest):
    """
    Listing list with filters and search.
    Saves search history for authenticated users.
    """
    listings = Listing.objects.filter(
        is_active=True,
        status=Listing.AvailabilityStatus.AVAILABLE
    )

    search_query = request.GET.get("search")
    min_price_eur = request.GET.get("min_price_eur")
    max_price_eur = request.GET.get("max_price_eur")
    rooms = request.GET.get("rooms")
    listing_type = request.GET.get("listing_type")
    sort_by = request.GET.get("sort")

    if search_query:
        listings = listings.filter(
            title__icontains=search_query
        ) | listings.filter(description__icontains=search_query)

    if min_price_eur:
        listings = listings.filter(price_eur__gte=min_price_eur)
    if max_price_eur:
        listings = listings.filter(price_eur__lte=max_price_eur)
    if rooms:
        listings = listings.filter(rooms__gte=rooms)
    if listing_type:
        listings = listings.filter(listing_type__icontains=listing_type)

    if sort_by == "price_eur_asc":
        listings = listings.order_by("price_eur")
    elif sort_by == "price_eur_desc":
        listings = listings.order_by("-price_eur")
    elif sort_by == "newest":
        listings = listings.order_by("-created_at")
    elif sort_by == "oldest":
        listings = listings.order_by("created_at")

    listings = listings.annotate(
        review_count=Count("feedbacks"),
        avg_rating=Avg("feedbacks__rating"),
    )

    # Log search usage
    try:
        any_filter = any([search_query, min_price_eur, max_price_eur, rooms, listing_type])
        if request.user.is_authenticated and any_filter:
            SearchHistory.objects.create(
                user=request.user,
                search_query=search_query or "",
                location="",
                min_price_eur=min_price_eur or None,
                max_price_eur=max_price_eur or None,
                rooms=int(rooms) if (rooms and rooms.isdigit()) else None,
                listing_type=listing_type or None,
            )
            logger.info(
                "SearchHistory saved for user=%s query=%s",
                request.user.email,
                (search_query or "").strip()
            )
    except Exception as exc:
        logger.error("Failed to save SearchHistory: %s", exc)

    return render(request, "listings/property_list.html", {"listings": listings})


def property_detail(request: HttpRequest, pk: int):
    """
    Listing detail page with review display and view logging.
    """
    property_obj = get_object_or_404(Listing, pk=pk, is_active=True)

    try:
        if request.user.is_authenticated:
            ViewLog.objects.create(
                user=request.user,
                property=property_obj,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:300],
            )
            logger.info(
                "ViewLog created user=%s property_id=%s",
                request.user.email,
                property_obj.id,
            )
    except Exception as exc:
        logger.error(
            "Failed to create ViewLog for property_id=%s: %s",
            property_obj.id,
            exc,
        )

    feedbacks = Feedback.objects.filter(property=property_obj).select_related("user")
    property_obj.review_count = feedbacks.count()
    property_obj.avg_rating = feedbacks.aggregate(avg=Avg("rating"))["avg"] or 0

    return render(
        request,
        "listings/property_detail.html",
        {"property": property_obj, "feedbacks": feedbacks},
    )


def user_profile(request: HttpRequest):
    """User profile page placeholder."""
    return render(request, "listings/user_profile.html")


def payment_form(request: HttpRequest):
    """Transaction form placeholder."""
    return render(request, "listings/payment_form.html")
