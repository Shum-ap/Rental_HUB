from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import UserProfile, UserType

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Автоматически создаёт профиль при создании пользователя
    и добавляет его в соответствующую группу.
    """
    if created:
        tenant_type, _ = UserType.objects.get_or_create(
            name="tenant", defaults={"description": "Арендатор"}
        )
        profile = UserProfile.objects.create(user=instance, user_type=tenant_type)

        tenant_group, _ = Group.objects.get_or_create(name="Tenant")
        instance.groups.add(tenant_group)
        print(f"[SIGNAL] Новый пользователь {instance.username} добавлен в группу Tenant.")
    else:
        # При обновлении пользователя — обновляем профиль
        if hasattr(instance, "profile"):
            instance.profile.save()


@receiver(post_save, sender=UserProfile)
def sync_user_group_with_usertype(sender, instance, **kwargs):
    """
    При изменении типа пользователя (user_type)
    обновляет его принадлежность к Django-группам.
    """
    user = instance.user
    if not user:
        return

    # Удаляем из всех ролей-групп, чтобы не было дубликатов
    role_groups = ["Tenant", "Host", "Admin", "Moderator"]
    user.groups.remove(*Group.objects.filter(name__in=role_groups))

    user_type_name = instance.user_type.name.capitalize() if instance.user_type else None
    if user_type_name in role_groups:
        group, _ = Group.objects.get_or_create(name=user_type_name)
        user.groups.add(group)
        print(f"[SIGNAL] Пользователь {user.username} перемещён в группу {user_type_name}.")
