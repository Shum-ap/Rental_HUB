import factory
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import UserProfile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword123')  # Установим общий пароль

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    bio = factory.Faker('text', max_nb_chars=200)
    location = factory.Faker('city')
    birth_date = factory.Faker('date_of_birth', minimum_age=18, maximum_age=65)
