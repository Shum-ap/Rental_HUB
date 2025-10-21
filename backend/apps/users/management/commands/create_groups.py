from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.listings.models import Property
from apps.bookings.models import Booking

class Command(BaseCommand):
    help = 'Создает группы пользователей с правами'

    def handle(self, *args, **options):
        # Создаем группы
        tenant_group, created = Group.objects.get_or_create(name='Tenant')
        host_group, created = Group.objects.get_or_create(name='Host')
        admin_group, created = Group.objects.get_or_create(name='Admin')
        moderator_group, created = Group.objects.get_or_create(name='Moderator')

        # Права для арендодателя (могут создавать/редактировать объекты)
        property_content_type = ContentType.objects.get_for_model(Property)
        property_permissions = Permission.objects.filter(content_type=property_content_type)
        host_group.permissions.set(property_permissions)

        # Права для арендатора (могут бронировать)
        booking_content_type = ContentType.objects.get_for_model(Booking)
        booking_permissions = Permission.objects.filter(content_type=booking_content_type)
        tenant_group.permissions.set(booking_permissions)

        # Админ — все права
        admin_group.permissions.set(Permission.objects.all())

        # Модератор — только чтение + модерация
        moderator_group.permissions.set(Permission.objects.filter(codename__in=[
            'view_property', 'view_booking', 'view_review'
        ]))

        self.stdout.write(self.style.SUCCESS('Группы успешно созданы'))
