from django.urls import path
from .views import (
    OrderListView,
    OrderCreateView,
    MenuItemListView,
    MenuItemCreateView,
    MenuItemUpdateView,
    MenuItemDeleteView,
    place_order_api,
    get_pending_orders_api,
    order_details_api,
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('orders/new/', OrderCreateView.as_view(), name='order_add'),
    path('menu/', MenuItemListView.as_view(), name='menu_item_list'),
    path('menu/new/', MenuItemCreateView.as_view(), name='menu_item_add'),
    path('menu/<int:pk>/edit/', MenuItemUpdateView.as_view(), name='menu_item_edit'),
    path('menu/<int:pk>/delete/', MenuItemDeleteView.as_view(), name='menu_item_delete'),
]
