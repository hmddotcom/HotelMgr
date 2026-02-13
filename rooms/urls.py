from django.urls import path
from .views import (
    RoomListView, RoomCreateView, RoomUpdateView,
    RoomCategoryListView, RoomCategoryCreateView, RoomCategoryUpdateView, RoomCategoryDeleteView
)

urlpatterns = [
    path('', RoomListView.as_view(), name='room_list'),
    path('add/', RoomCreateView.as_view(), name='room_add'),
    path('<int:pk>/edit/', RoomUpdateView.as_view(), name='room_edit'),

    path('categories/', RoomCategoryListView.as_view(), name='room_category_list'),
    path('categories/add/', RoomCategoryCreateView.as_view(), name='room_category_add'),
    path('categories/<int:pk>/edit/', RoomCategoryUpdateView.as_view(), name='room_category_edit'),
    path('categories/<int:pk>/delete/', RoomCategoryDeleteView.as_view(), name='room_category_delete'),
]
