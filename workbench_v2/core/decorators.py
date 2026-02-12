"""Permission decorators for role-based access control."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def require_role(min_role):
    """Decorator that requires at least `min_role` (admin > reviewer > member).

    Usage:
        @require_role("reviewer")   # reviewer or admin
        @require_role("admin")      # admin only
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, "profile", None)
            if profile and profile.has_role(min_role):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission for this action.")
            return redirect("dashboard")
        return wrapper
    return decorator
