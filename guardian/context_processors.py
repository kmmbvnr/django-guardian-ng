from django.contrib.auth.context_processors import PermWrapper
from guardian.backends import check_user_support


def auth(request):
    """
    Enhances  django.contrib.auth.context_processor.auth with optimized 'perms'
    template context variable
    """
    if hasattr(request, "user"):
        user = request.user
    else:
        from django.contrib.auth.models import AnonymousUser

        user = AnonymousUser()

    # Pre-fetch the settings.ANONYMOUS_USER_NAME instance to reduce redundant
    # database queries during permission checks. Refer to issue #6 for more
    # details.
    _, guardian_user = check_user_support(user)

    return {
        "user": user,
        "perms": PermWrapper(guardian_user),
    }
