from django.core.management.base import BaseCommand
from apps.listings.factories import PropertyFactory
from apps.users.factories import UserFactory, UserProfileFactory
from apps.listings.models import Property
from apps.users.models import UserProfile

class Command(BaseCommand):
    help = 'Заполняет базу данных фейковыми данными'

    def add_arguments(self, parser):
        parser.add_argument('--properties', type=int, default=10, help='Количество объявлений')
        parser.add_argument('--users', type=int, default=5, help='Количество пользователей')

    def handle(self, *args, **options):
        num_properties = options['properties']
        num_users = options['users']

        self.stdout.write(f'Создаём {num_users} пользователей...')
        users = UserFactory.create_batch(num_users)

        for user in users:
            UserProfileFactory(user=user)

        self.stdout.write(f'Создаём {num_properties} объявлений...')
        PropertyFactory.create_batch(num_properties)

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано: {num_properties} объявлений и {num_users} пользователей с профилями.'
            )
        )
