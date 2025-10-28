from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.listings.models import Listing
from apps.reservations.models import Reservation


class Command(BaseCommand):
    """
    Django management command to create user groups with proper permissions.

    - Tenant: Can make reservations.
    - Host: Can manage listings.
    - Admin: Has all permissions.
    - Moderator: Has read-only access and moderation permissions.
    """

    help = 'Creates default user groups with associated permissions.'

    def handle(self, *args, **options):
        try:
            self.stdout.write(" Creating user groups...")

            tenant_group, _ = Group.objects.get_or_create(name='Tenant')
            host_group, _ = Group.objects.get_or_create(name='Host')
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            moderator_group, _ = Group.objects.get_or_create(name='Moderator')

            property_content_type = ContentType.objects.get_for_model(Listing)
            property_permissions = Permission.objects.filter(content_type=property_content_type)
            host_group.permissions.set(property_permissions)

            booking_content_type = ContentType.objects.get_for_model(Reservation)
            booking_permissions = Permission.objects.filter(content_type=booking_content_type)
            tenant_group.permissions.set(booking_permissions)

            admin_group.permissions.set(Permission.objects.all())

            moderator_group.permissions.set(
                Permission.objects.filter(codename__in=[
                    'view_property', 'view_booking', 'view_review'
                ])
            )

            self.stdout.write(self.style.SUCCESS(' User groups created successfully.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f" Error creating groups: {e}"))
