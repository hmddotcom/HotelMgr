from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def has_log_permission(user, permission_type='view'):
    """Check if user has permission to access logs"""
    if not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check if user has specific log permission through their role
    if hasattr(user, 'role') and user.role:
        from settings.models import Permission
        return Permission.objects.filter(
            role=user.role,
            module='logs',
            action=permission_type
        ).exists()
    
    return False

def require_log_permission(permission_type='view'):
    """Decorator to require log permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not has_log_permission(request.user, permission_type):
                raise PermissionDenied("Vous n'avez pas la permission d'accéder aux logs.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
