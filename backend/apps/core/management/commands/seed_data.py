import random
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from faker import Faker
from django.core.files import File
from apps.users.models import UserProfile, UserType
from apps.listings.models import Listing
from apps.reservations.models import Reservation
from apps.feedbacks.models import Feedback
from apps.log.models import SearchHistory, ViewLog


fake = Faker(["en_GB", "en_US"])
User = get_user_model()


class Command(BaseCommand):
    """
    Django management command to seed the database with test data.

    Creates:
    - User roles and profiles (admin, moderator, landlord, tenant)
    - Random listings with optional images
    - Reservations, feedbacks, search histories, and view logs
    """

    help = "Populate the database with test data (users, listings, reservations, feedbacks, history)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            type=str,
            default="test12345",
            help="Password for all generated users."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password = options["password"]
        self.stdout.write(self.style.MIGRATE_HEADING("=== STARTING FULL DATABASE SEED ==="))

        # === USER TYPES ===
        try:
            landlord_type, _ = UserType.objects.get_or_create(
                name="landlord", defaults={"description": "Landlord"}
            )
            tenant_type, _ = UserType.objects.get_or_create(
                name="tenant", defaults={"description": "Tenant"}
            )
            moderator_type, _ = UserType.objects.get_or_create(
                name="moderator", defaults={"description": "Moderator"}
            )
            admin_type, _ = UserType.objects.get_or_create(
                name="admin", defaults={"description": "Administrator"}
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating user roles/types: {e}"))

        # === ADMIN & MODERATOR ===
        try:
            admin, _ = User.objects.get_or_create(
                email="admin@rentalhub.com",
                defaults={"first_name": "Admin", "is_staff": True, "is_superuser": True}
            )
            admin.set_password(password)
            admin.save()
            UserProfile.objects.get_or_create(
                user=admin, defaults={"role": "admin", "user_type": admin_type}
            )

            moderator, _ = User.objects.get_or_create(
                email="moderator@rentalhub.com",
                defaults={"first_name": "Moderator", "is_staff": True}
            )
            moderator.set_password(password)
            moderator.save()
            UserProfile.objects.get_or_create(
                user=moderator, defaults={"role": "moderator", "user_type": moderator_type}
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating admin/moderator: {e}"))

        # === USERS (LANDLORDS & TENANTS) ===
        landlords, tenants = [], []
        try:
            for i in range(5):
                user = User.objects.create(
                    email=f"landlord{i + 1}@rentalhub.com",
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                user.set_password(password)
                user.save()
                landlords.append(user)
                UserProfile.objects.get_or_create(
                    user=user, defaults={"role": "landlord", "user_type": landlord_type}
                )

            for i in range(10):
                user = User.objects.create(
                    email=f"tenant{i + 1}@rentalhub.com",
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                user.set_password(password)
                user.save()
                tenants.append(user)
                UserProfile.objects.get_or_create(
                    user=user, defaults={"role": "tenant", "user_type": tenant_type}
                )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating users: {e}"))

        # === LISTINGS ===
        cities = ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Dresden"]
        listing_types = [choice[0] for choice in Listing.ListingType.choices]

        media_path = os.path.join(settings.MEDIA_ROOT, "properties")  # <== исправлено
        available_images = []
        try:
            if os.path.exists(media_path):
                available_images = [
                    os.path.join("properties", f)
                    for f in os.listdir(media_path)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ]
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error loading media images: {e}"))

        listings = []
        try:
            for _ in range(30):
                owner = random.choice(landlords)
                listing_type = random.choice(listing_types)
                image_path = random.choice(available_images) if available_images else None

                title = f"{dict(Listing.ListingType.choices)[listing_type]} in {random.choice(cities)}"
                description = fake.paragraph(nb_sentences=3)
                location = f"{random.choice(cities)}, {fake.street_address()}"

                prop = Listing.objects.create(
                    owner=owner,
                    title=title,
                    description=description,
                    location=location,
                    price_eur=random.randint(50, 500),
                    rooms=random.randint(1, 5),
                    listing_type=listing_type,
                    is_active=True,
                    status=Listing.AvailabilityStatus.AVAILABLE,
                )

                if image_path:
                    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'rb') as img_file:
                            prop.image.save(os.path.basename(full_path), File(img_file))

                listings.append(prop)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating listings: {e}"))

        # === RESERVATIONS ===
        try:
            if listings:
                for tenant in tenants:
                    for _ in range(random.randint(1, 3)):
                        prop = random.choice(listings)
                        start_date = timezone.now().date() + timezone.timedelta(days=random.randint(1, 15))
                        end_date = start_date + timezone.timedelta(days=random.randint(2, 7))
                        Reservation.objects.create(
                            user=tenant,
                            rental_property=prop,
                            start_date=start_date,
                            end_date=end_date,
                            status=random.choice(["pending", "confirmed", "completed"]),
                            is_confirmed=True,
                        )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating reservations: {e}"))

        # === FEEDBACKS ===
        try:
            if listings:
                for tenant in tenants:
                    for prop in random.sample(listings, k=min(5, len(listings))):
                        Feedback.objects.create(
                            user=tenant,
                            listing=prop,
                            rating=random.randint(3, 5),
                            comment=fake.sentence(nb_words=10),
                        )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating feedbacks: {e}"))

        # === SEARCH HISTORY ===
        try:
            search_terms = [
                "cheap apartment", "sea view", "city center", "house with garden",
                "2 bedrooms", "pet friendly", "villa", "student flat"
            ]
            for tenant in tenants:
                for term in random.sample(search_terms, k=3):
                    SearchHistory.objects.create(
                        user=tenant,
                        search_query=term,
                        location=random.choice(cities),
                        min_price_eur=random.choice([None, 200, 400]),
                        max_price_eur=random.choice([600, 1000, 2000]),
                        rooms=random.randint(1, 4),
                        listing_type=random.choice(listing_types),
                    )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating search history: {e}"))

        # === VIEW LOGS ===
        try:
            if listings:
                for tenant in tenants:
                    for prop in random.sample(listings, k=min(5, len(listings))):
                        ViewLog.objects.create(
                            user=tenant,
                            listing=prop,
                            viewed_at=timezone.now() - timezone.timedelta(days=random.randint(0, 30)),
                        )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error creating view logs: {e}"))

        self.stdout.write(self.style.SUCCESS(f" Database seeded successfully. Password for all users: {password}"))
