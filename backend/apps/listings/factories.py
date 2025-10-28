import factory
import os
import random
from decimal import Decimal
from django.conf import settings
from apps.listings.models import Listing
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name", locale="en_GB")
    email = factory.Faker("email", locale="en_GB")
    first_name = factory.Faker("first_name", locale="en_GB")
    last_name = factory.Faker("last_name", locale="en_GB")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword123")


class ListingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Listing

    title = factory.Faker("sentence", nb_words=4, locale="en_GB")
    description = factory.Faker("paragraph", nb_sentences=3, locale="en_GB")
    location = factory.Faker(
        "city", locale=random.choice(["en_GB", "de_DE", "fr_FR", "es_ES", "it_IT"])
    )
    price_eur = factory.LazyFunction(lambda: Decimal(random.randint(50, 500)))
    rooms = factory.Faker("random_int", min=1, max=5)
    listing_type = factory.Faker(
        "random_element", elements=[choice[0] for choice in Listing.PROPERTY_TYPES]
    )
    owner = factory.SubFactory("apps.users.factories.UserFactory")
    is_active = True
    is_available = True

    @factory.lazy_attribute
    def image(self):
        """
        Выбирает случайное изображение из media/listings/
        Если файлов нет — возвращает default.jpg
        """
        media_path = os.path.join(settings.MEDIA_ROOT, "listings")
        if os.path.exists(media_path):
            images = [f for f in os.listdir(media_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            if images:
                return f"listings/{random.choice(images)}"

        # Файл-заглушка
        default_path = os.path.join(settings.MEDIA_ROOT, "listings", "default.jpg")
        if not os.path.exists(default_path):
            # если default.jpg нет — создаём пустой
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
            with open(default_path, "wb") as f:
                f.write(b"")
        return "listings/default.jpg"
