from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """
    Универсальный декоратор для проверки ролей через user.profile.user_type.name
    Пример: @role_required(["landlord", "admin"])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Сначала войдите в систему.")
                return redirect("/admin/login/")

            try:
                user_type = getattr(request.user.profile.user_type, "name", "").lower()
            except AttributeError:
                messages.error(request, "Не определён тип пользователя.")
                return redirect("/")

            if user_type not in [r.lower() for r in allowed_roles]:
                messages.error(request, "У вас нет прав для доступа к этой странице.")
                return redirect("/")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# --- Удобные сокращения ---

def tenant_required(view_func):
    return role_required(["tenant", "admin", "moderator"])(view_func)


def landlord_required(view_func):
    return role_required(["landlord", "admin", "moderator"])(view_func)


def admin_required(view_func):
    return role_required(["admin"])(view_func)


def moderator_required(view_func):
    return role_required(["moderator", "admin"])(view_func)
