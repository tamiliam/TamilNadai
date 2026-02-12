"""Context processors to inject role variables into all templates."""


def user_role(request):
    """Inject user_role, is_admin, is_reviewer_or_above into template context."""
    if not request.user.is_authenticated:
        return {"user_role": None, "is_admin": False, "is_reviewer_or_above": False}

    profile = getattr(request.user, "profile", None)
    role = profile.role if profile else "member"

    return {
        "user_role": role,
        "is_admin": role == "admin",
        "is_reviewer_or_above": role in ("admin", "reviewer"),
        "user_avatar": profile.avatar if profile and profile.avatar else "",
    }
