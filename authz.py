"""Shared authorization helpers.

Lives at the project root rather than inside the `2048` package because that
package name starts with a digit: Django can load it by string
("2048.settings"), but `from 2048.authz import ...` is a syntax error. The
root is on sys.path both under manage.py and under gunicorn (WORKDIR /app), so
a top-level module is importable from every app.
"""

from functools import wraps

from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    """Restricts a view to staff users, 403-ing everyone else.

    Deliberately not django.contrib.admin's staff_member_required: that one
    redirects to a login page, which for an already-logged-in non-staff user
    is both wrong (they are logged in; logging in again changes nothing) and
    broken — our LoginView sets redirect_authenticated_user, so it bounces
    them straight back to the view that rejected them, and the two spin
    forever.

    Anonymous users never reach this check: LoginRequiredMiddleware has
    already sent them to the login page.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped
