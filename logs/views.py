from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import ActivityLog
from .permissions import has_log_permission, require_log_permission
import csv
from django.http import HttpResponse

class LogListView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'logs/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def dispatch(self, request, *args, **kwargs):
        if not has_log_permission(request.user, 'view'):
            raise PermissionDenied("Vous n'avez pas la permission de consulter les logs.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by event type
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by module
        module = self.request.GET.get('module')
        if module:
            queryset = queryset.filter(module=module)
        
        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by severity
        severity = self.request.GET.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Date range filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(action__icontains=search) |
                Q(details__icontains=search) |
                Q(object_repr__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = ActivityLog.EVENT_TYPES
        context['modules'] = ActivityLog.MODULE_CHOICES
        context['severities'] = ActivityLog.SEVERITY_LEVELS
        
        # Preserve filters in pagination
        context['filters'] = self.request.GET.copy()
        if 'page' in context['filters']:
            del context['filters']['page']
        
        return context

class LogDetailView(LoginRequiredMixin, DetailView):
    model = ActivityLog
    template_name = 'logs/log_detail.html'
    context_object_name = 'log'
    
    def dispatch(self, request, *args, **kwargs):
        if not has_log_permission(request.user, 'view'):
            raise PermissionDenied("Vous n'avez pas la permission de consulter les logs.")
        return super().dispatch(request, *args, **kwargs)

@login_required
@require_log_permission('view')
def export_logs_csv(request):
    """Export filtered logs to CSV"""
    # Get filtered queryset (reuse LogListView logic)
    view = LogListView()
    view.request = request
    logs = view.get_queryset()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logs_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date/Heure', 'Utilisateur', 'Type', 'Module', 'Action', 'Détails', 'Sévérité'])
    
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username if log.user else 'Système',
            log.get_event_type_display(),
            log.get_module_display(),
            log.action,
            log.details[:100],  # Truncate for CSV
            log.get_severity_display(),
        ])
    
    return response
