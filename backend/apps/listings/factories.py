import factory
from django.contrib.auth.models import User
from .models import Property

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword123')

class PropertyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Property

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    location = factory.Faker('address')
    price = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    rooms = factory.Faker('random_int', min=1, max=5)
    property_type = factory.Faker('random_element', elements=[choice[0] for choice in Property.PROPERTY_TYPES])
    owner = factory.SubFactory('apps.users.factories.UserFactory')  # Правильный путь
    is_active = factory.Faker('boolean')
    is_available = factory.Faker('boolean', chance_of_getting_true=80)

    @factory.lazy_attribute
    def image(self):
        import os
        import random
        from django.conf import settings

        # Путь к папке с изображениями
        media_path = os.path.join(settings.BASE_DIR, 'media', 'properties')
        if os.path.exists(media_path):
            images = [f for f in os.listdir(media_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                return f"properties/{random.choice(images)}"
        return None
