from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from apps.listings.models import Property


def home(request):
    properties = (
        Property.objects.filter(is_active=True, is_available=True)
        .annotate(review_count=Count("reviews"))
        .order_by("-review_count")[:6]
    )
    return render(request, "home.html", {"properties": properties})


def property_list(request):
    properties = Property.objects.filter(is_active=True, is_available=True)
    return render(request, "listings/property_list.html", {"properties": properties})


def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk, is_active=True)
    return render(request, "listings/property_detail.html", {"property": property_obj})


def user_profile(request):
    return render(request, "listings/user_profile.html")


def payment_form(request):
    return render(request, "listings/payment_form.html")
