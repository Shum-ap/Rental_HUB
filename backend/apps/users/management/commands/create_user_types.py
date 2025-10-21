from django.core.management.base import BaseCommand
from apps.users.models import UserType

class Command(BaseCommand):
    help = "Создаёт базовые типы пользователей (tenant и landlord)"

    def handle(self, *args, **options):
        types = [
            ("tenant", "Арендатор — может искать и бронировать жильё"),
            ("landlord", "Арендодатель — может публиковать и управлять объявлениями"),
        ]
        for name, desc in types:
            obj, created = UserType.objects.get_or_create(name=name, defaults={"description": desc})
            if created:
                self.stdout.write(self.style.SUCCESS(f" Создан тип пользователя: {name}"))
            else:
                self.stdout.write(f" Тип пользователя {name} уже существует")
