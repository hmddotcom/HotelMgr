from django.urls import path
from .views import ComplaintListView, ComplaintCreateView

urlpatterns = [
    path('', ComplaintListView.as_view(), name='complaint_list'),
    path('add/', ComplaintCreateView.as_view(), name='complaint_add'),
]
