from rest_framework.permissions import BasePermission


class HasGroupPermission(BasePermission):
    """
    Базовый класс проверки принадлежности к группе
    """
    group_names = []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name__in=self.group_names).exists()


class IsTenant(HasGroupPermission):
    """Арендатор — может бронировать, оставлять отзывы, просматривать"""
    group_names = ['Tenant', 'Admin', 'Moderator']


class IsHost(HasGroupPermission):
    """Арендодатель — может создавать/редактировать/удалять свои объявления"""
    group_names = ['Host', 'Admin', 'Moderator']


class IsAdmin(HasGroupPermission):
    """Администратор — полный доступ"""
    group_names = ['Admin']


class IsModerator(HasGroupPermission):
    """Модератор — доступ к модерации"""
    group_names = ['Moderator', 'Admin']


class IsOwnerOrReadOnly(BasePermission):
    """Только владелец может редактировать или удалять"""
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'rental_property') and hasattr(obj.rental_property, 'owner'):
            return obj.rental_property.owner == request.user
        return False

