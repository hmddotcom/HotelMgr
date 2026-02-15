from django.contrib import admin
from django.urls import path, include, re_path
from hotel_project.views import DashboardView, POSView
import sys

admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    path('pos/', POSView.as_view(), name='pos'),
    path('clients/', include('clients.urls')),
    path('rooms/', include('rooms.urls')),
    path('reservations/', include('reservations.urls')),
    path('restaurant/', include('restaurant.urls')),
    path('api/', include('restaurant.api_urls')),
    path('transport/', include('transport.urls')),
    path('complaints/', include('complaints.urls')),
    path('billing/', include('billing.urls')),
    path('system/', include('settings.urls')),
    path('logs/', include('logs.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reports/', include('reports.urls')),
    path('services/', include('services.urls')),
]

# Serve media files in development
from django.conf import settings as django_settings
from django.conf.urls.static import static
from django.views.static import serve as media_serve

if django_settings.DEBUG:
    urlpatterns += static(django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT)
elif 'runserver' in sys.argv:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', media_serve, {'document_root': django_settings.MEDIA_ROOT}),
    ]

