from django.contrib import admin
from django.urls import path, include
from hotel_project.views import DashboardView, POSView

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

if django_settings.DEBUG:
    urlpatterns += static(django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT)

