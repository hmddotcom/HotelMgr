from django.urls import path
from .views import ReservationListView, ReservationCreateView, ReservationUpdateView, ReservationDeleteView, check_in_reservation, check_out_reservation, chambres_disponibles_api

urlpatterns = [
    path('', ReservationListView.as_view(), name='reservation_list'),
    path('add/', ReservationCreateView.as_view(), name='reservation_add'),
    path('<int:pk>/edit/', ReservationUpdateView.as_view(), name='reservation_edit'),
    path('<int:pk>/delete/', ReservationDeleteView.as_view(), name='reservation_delete'),
    path('<int:pk>/check-in/', check_in_reservation, name='reservation_check_in'),
    path('<int:pk>/check-out/', check_out_reservation, name='reservation_check_out'),
    path('chambres-disponibles/', chambres_disponibles_api, name='chambres_disponibles_api'),
]
