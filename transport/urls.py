from django.urls import path
from .views import TransportListView, TransportCreateView

urlpatterns = [
    path('', TransportListView.as_view(), name='transport_list'),
    path('add/', TransportCreateView.as_view(), name='transport_add'),
]
