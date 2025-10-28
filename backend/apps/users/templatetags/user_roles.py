from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def user_role(context):
    """
    Returns user's role (tenant, landlord, admin, moderator).
    Example: {% user_role as role %} → {{ role }}
    """
    request = context.get("request")
    user = getattr(request, "user", None)

    if not user or not user.is_authenticated:
        return "anonymous"

    try:
        return getattr(user.profile.user_type, "name", "").lower()
    except AttributeError:
        return "unknown"


@register.filter
def has_role(user, role_name):
    """
    Template filter to check role:
    {% if user|has_role:"landlord" %}
        ...
    {% endif %}
    """
    if not user.is_authenticated:
        return False

    try:
        user_role = getattr(user.profile.user_type, "name", "").lower()
        return user_role == role_name.lower() or user_role == "admin"
    except AttributeError:
        return False
