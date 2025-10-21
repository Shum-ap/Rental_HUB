from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTenant(BasePermission):
    """Арендатор — может бронировать, оставлять отзывы."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return getattr(getattr(request.user, "profile", None), "user_type", "").name.lower() in [
            "tenant", "admin", "moderator"
        ]


class IsLandlord(BasePermission):
    """Арендодатель — может управлять своими объявлениями."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return getattr(getattr(request.user, "profile", None), "user_type", "").name.lower() in [
            "landlord", "admin", "moderator"
        ]

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "owner", None)
        return owner == request.user


class IsAdmin(BasePermission):
    """Администратор — полный доступ."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return getattr(getattr(request.user, "profile", None), "user_type", "").name.lower() == "admin"


class IsModerator(BasePermission):
    """Модератор — может модерировать контент."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return getattr(getattr(request.user, "profile", None), "user_type", "").name.lower() in [
            "moderator", "admin"
        ]


class IsOwnerOrReadOnly(BasePermission):
    """Редактирование разрешено только владельцу."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "rental_property") and hasattr(obj.rental_property, "owner"):
            return obj.rental_property.owner == request.user
        return False
