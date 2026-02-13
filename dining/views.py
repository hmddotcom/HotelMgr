# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, ListView
from dining.models import Table, MenuItem
from billing.models import Invoice

class POSView(TemplateView):
    template_name = "pos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = Table.objects.all().order_by('numero')
        return context

class OrderListView(ListView):
    model = Invoice
    template_name = 'dining/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # On filtre pour n'afficher que les factures qui ne sont pas liées à un client 
        # (donc les commandes du restaurant)
        return Invoice.objects.filter(client__isnull=True).order_by('-date_creation')

class MenuItemListView(ListView):
    model = MenuItem
    template_name = 'dining/menu_item_list.html'
    context_object_name = 'menu_items'
    ordering = ['category', 'name']
