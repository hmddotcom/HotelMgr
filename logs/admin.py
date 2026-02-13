from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'event_type', 'module', 'action', 'severity']
    list_filter = ['event_type', 'module', 'severity', 'timestamp']
    search_fields = ['action', 'details', 'user__username']
    readonly_fields = ['timestamp', 'user', 'event_type', 'module', 'action', 
                       'details', 'object_type', 'object_id', 'object_repr',
                       'old_values', 'new_values', 'ip_address', 'user_agent', 'severity']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        # Logs are created automatically, not manually
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete logs
        return request.user.is_superuser
