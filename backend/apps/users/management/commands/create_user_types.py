from django.core.management.base import BaseCommand
from apps.users.models import UserType


class Command(BaseCommand):
    """
    Django management command to create base user types.

    Creates:
    - Tenant
    - Landlord
    """

    help = "Creates base user types (tenant and landlord)."

    def handle(self, *args, **options):
        try:
            types = [
                ("tenant", "Tenant — can search and book accommodations."),
                ("landlord", "Landlord — can create and manage listing listings."),
            ]

            for name, desc in types:
                obj, created = UserType.objects.get_or_create(
                    name=name, defaults={"description": desc}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f" Created user type: {name}"))
                else:
                    self.stdout.write(f" User type already exists: {name}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f" Error creating user types: {e}"))
