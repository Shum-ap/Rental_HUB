from django.core.management.base import BaseCommand
from apps.users.models import UserType


class Command(BaseCommand):
    """
    Django management command to create base user roles.

    Creates:
    - Tenant
    - Landlord
    - Moderator
    - Admin
    """

    help = "Creates default user roles."

    def handle(self, *args, **options):
        try:
            roles = [
                ("tenant", "Tenant — can rent and book listings."),
                ("landlord", "Landlord — can post and manage listings."),
                ("moderator", "Moderator — can review and approve listings."),
                ("admin", "Admin — full system access."),
            ]

            for name, desc in roles:
                obj, created = UserType.objects.get_or_create(
                    name=name, defaults={"description": desc}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f" Role created: {name}"))
                else:
                    self.stdout.write(f" Role already exists: {name}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f" Error creating roles: {e}"))
