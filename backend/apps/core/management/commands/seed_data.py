import random
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files import File
from faker import Faker
from django.utils import timezone
from django.db import IntegrityError

from apps.listings.models import Property
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.payments.models import Payment

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Полностью очищает и наполняет базу тестовыми данными: пользователи, объекты, бронирования, отзывы, платежи'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Очищаем базу...'))

        # Удаляем все данные в правильном порядке (сначала зависимые модели)
        Payment.objects.all().delete()
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Property.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.SUCCESS(' База очищена'))

        self.stdout.write(self.style.WARNING('Начинаем наполнение базы...'))

        # 0. Суперпользователь
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin1234"
            )
            self.stdout.write(self.style.SUCCESS(" Суперпользователь admin создан (пароль: admin1234)"))
        else:
            self.stdout.write(self.style.NOTICE(" Суперпользователь admin уже существует"))

        # 1. Пользователи
        password = 'test1234'
        users = []
        for i in range(20):
            username = f'user{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': fake.email()}
            )
            if created:
                user.set_password(password)
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(' 20 пользователей созданы (пароль: test1234)'))

        # 2. Объекты недвижимости
        media_path = Path('media/properties')
        images = list(media_path.glob('*.jpg')) + list(media_path.glob('*.png'))

        properties = []
        for i in range(100):
            owner = random.choice(users)
            prop = Property.objects.create(
                owner=owner,
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=200),
                price=random.randint(50, 500),
                rooms=random.randint(1, 5),
                property_type=random.choice(['apartment', 'house', 'studio']),
                location=fake.city(),
                is_active=True,
                is_available=True,
            )
            if images:
                image_file = random.choice(images)
                with open(image_file, 'rb') as f:
                    prop.image.save(image_file.name, File(f), save=True)
            properties.append(prop)
        self.stdout.write(self.style.SUCCESS(' 100 объектов недвижимости созданы'))

        # 3. Бронирования
        bookings = []
        for i in range(50):
            user = random.choice(users)
            prop = random.choice(properties)
            start_date = fake.date_between(start_date='+1d', end_date='+30d')
            end_date = start_date + timezone.timedelta(days=random.randint(2, 14))
            status = random.choice(['pending', 'confirmed', 'cancelled', 'completed'])
            booking = Booking.objects.create(
                user=user,
                rental_property=prop,
                start_date=start_date,
                end_date=end_date,
                status=status,
                is_confirmed=status in ['confirmed', 'completed'],
                is_cancelled=status == 'cancelled',
                is_active=True,
            )
            bookings.append(booking)
        self.stdout.write(self.style.SUCCESS(' 50 бронирований созданы'))

        # 4. Отзывы
        created_reviews = 0
        target_reviews = 150
        while created_reviews < target_reviews:
            user = random.choice(users)
            prop = random.choice(properties)
            try:
                Review.objects.create(
                    user=user,
                    property=prop,
                    rating=random.randint(1, 5),
                    comment=fake.sentence(nb_words=12),
                )
                created_reviews += 1
            except IntegrityError:
                continue
        self.stdout.write(self.style.SUCCESS(f' {created_reviews} отзывов созданы'))

        # Пересчёт рейтингов у объектов
        for prop in properties:
            reviews = prop.reviews.all()
            if reviews.exists():
                avg = sum(r.rating for r in reviews) / reviews.count()
                prop.average_rating = round(avg, 1)
                prop.save(update_fields=["average_rating"])
        self.stdout.write(self.style.SUCCESS(" Рейтинги объектов пересчитаны"))

        # 5. Платежи
        for i in range(50):
            booking = random.choice(bookings)
            days = (booking.end_date - booking.start_date).days
            amount = booking.rental_property.price * days
            Payment.objects.create(
                user=booking.user,
                booking=booking,
                amount=amount,
                status=random.choices(
                    ['pending', 'completed', 'failed'],
                    weights=[1, 5, 1]  # completed чаще
                )[0],
            )
        self.stdout.write(self.style.SUCCESS(' 50 платежей созданы'))

        # Итоговая статистика
        self.stdout.write(self.style.SUCCESS(f"Итого в базе: {User.objects.count()} пользователей"))
        self.stdout.write(self.style.SUCCESS(f"Итого в базе: {Property.objects.count()} объектов"))
        self.stdout.write(self.style.SUCCESS(f"Итого в базе: {Booking.objects.count()} бронирований"))
        self.stdout.write(self.style.SUCCESS(f"Итого в базе: {Review.objects.count()} отзывов"))
        self.stdout.write(self.style.SUCCESS(f"Итого в базе: {Payment.objects.count()} платежей"))

        self.stdout.write(self.style.SUCCESS(' Наполнение базы завершено'))