# -*- coding: utf-8 -*-
from django.urls import path
from .views import POSView, OrderListView, MenuItemListView

app_name = 'dining'

urlpatterns = [
    path('pos/', POSView.as_view(), name='pos'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('menu/', MenuItemListView.as_view(), name='menu_item_list'),
]
