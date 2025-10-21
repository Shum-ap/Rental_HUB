from django.core.management.base import BaseCommand
from apps.users.models import UserType

class Command(BaseCommand):
    help = "Создание базовых ролей пользователей"

    def handle(self, *args, **options):
        roles = [
            ("tenant", "Арендатор"),
            ("landlord", "Арендодатель"),
            ("moderator", "Модератор"),
            ("admin", "Администратор"),
        ]
        for name, desc in roles:
            obj, created = UserType.objects.get_or_create(name=name, defaults={"description": desc})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создана роль: {name}"))
            else:
                self.stdout.write(f"Роль {name} уже существует")
