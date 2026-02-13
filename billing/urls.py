from django.urls import path
from .views import InvoiceListView, InvoiceCreateView, InvoiceUpdateView, add_payment

urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('add/', InvoiceCreateView.as_view(), name='invoice_add'),
    path('<int:pk>/edit/', InvoiceUpdateView.as_view(), name='invoice_edit'),
    path('<int:invoice_id>/add_payment/', add_payment, name='add_payment'),
]
