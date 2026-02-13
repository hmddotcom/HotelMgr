from django.urls import path
from . import views

urlpatterns = [
    path('order/<int:order_id>/', views.order_details_api, name='order_details_api'),
    path('pending-orders/', views.get_pending_orders_api, name='get_pending_orders_api'),
    path('place-order/', views.place_order_api, name='place_order_api'),
]
