from django.urls import path
from .views import (
    UserListView, UserCreateView, UserUpdateView,
    roles_permissions_view, branding_view, general_settings_view
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('roles/', roles_permissions_view, name='roles_permissions'),
    path('branding/', branding_view, name='branding'),
    path('general/', general_settings_view, name='general_settings'),
]
