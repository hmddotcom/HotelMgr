from django.urls import path
from .views import LogListView, LogDetailView, export_logs_csv

urlpatterns = [
    path('', LogListView.as_view(), name='log_list'),
    path('<int:pk>/', LogDetailView.as_view(), name='log_detail'),
    path('export/', export_logs_csv, name='log_export'),
]
