from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def role_required(*roles):
    """
    Decorator to restrict view access to specific roles.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this page.")
        return _wrapped_view
    return decorator


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin for Class-Based Views to restrict access to specific roles.
    """
    allowed_roles = []

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        raise PermissionDenied("You do not have permission to access this page.")
