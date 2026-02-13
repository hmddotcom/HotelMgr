# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        from clients.models import Client
        from reservations.models import Reservation
        from rooms.models import Room
        from restaurant.models import Order
        
        context = super().get_context_data(**kwargs)
        context['client_count'] = Client.objects.count()
        context['active_res_count'] = Reservation.objects.filter(statut='active').count()
        context['available_rooms'] = Room.objects.filter(statut='disponible').count()
        context['today_orders'] = Order.objects.filter(statut='servi').count() # Example stat
        return context

@method_decorator(login_required, name='dispatch')
class POSView(TemplateView):
    template_name = "pos.html"

    def get_context_data(self, **kwargs):
        from restaurant.models import MenuItem
        from reservations.models import Reservation
        from services.models import Service
        
        context = super().get_context_data(**kwargs)
        context['menu_items'] = MenuItem.objects.all().order_by('categorie', 'nom')
        context['categories'] = MenuItem.objects.values_list('categorie', flat=True).distinct()
        context['active_reservations'] = Reservation.objects.filter(statut='active')
        context['services'] = Service.objects.all()
        return context
