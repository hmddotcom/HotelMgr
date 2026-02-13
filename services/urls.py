from django.urls import path
from .views import (
    ServiceCategoryListView, ServiceCategoryCreateView, ServiceCategoryUpdateView, ServiceCategoryDeleteView,
    ServiceListView, ServiceCreateView, ServiceUpdateView, ServiceDeleteView,
    RoomCleaningListView, RoomCleaningCreateView, RoomCleaningUpdateView, RoomCleaningDeleteView,
    start_cleaning, complete_cleaning, validate_cleaning
)

urlpatterns = [
    # URLs for Service Categories
    path('categories/', ServiceCategoryListView.as_view(), name='service_category_list'),
    path('categories/add/', ServiceCategoryCreateView.as_view(), name='service_category_add'),
    path('categories/<int:pk>/edit/', ServiceCategoryUpdateView.as_view(), name='service_category_edit'),
    path('categories/<int:pk>/delete/', ServiceCategoryDeleteView.as_view(), name='service_category_delete'),

    # URLs for Services
    path('', ServiceListView.as_view(), name='service_list'),
    path('add/', ServiceCreateView.as_view(), name='service_add'),
    path('<int:pk>/edit/', ServiceUpdateView.as_view(), name='service_edit'),
    path('<int:pk>/delete/', ServiceDeleteView.as_view(), name='service_delete'),

    # URLs for Room Cleaning
    path('nettoyage-chambres/', RoomCleaningListView.as_view(), name='room_cleaning_list'),
    path('nettoyage-chambres/add/', RoomCleaningCreateView.as_view(), name='room_cleaning_add'),
    path('nettoyage-chambres/<int:pk>/edit/', RoomCleaningUpdateView.as_view(), name='room_cleaning_edit'),
    path('nettoyage-chambres/<int:pk>/delete/', RoomCleaningDeleteView.as_view(), name='room_cleaning_delete'),
    path('nettoyage-chambres/<int:pk>/start/', start_cleaning, name='start_cleaning'),
    path('nettoyage-chambres/<int:pk>/complete/', complete_cleaning, name='complete_cleaning'),
    path('nettoyage-chambres/<int:pk>/validate/', validate_cleaning, name='validate_cleaning'),
]
