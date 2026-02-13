# -*- coding: utf-8 -*-
import json
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from .models import Order, OrderItem, MenuItem
from reservations.models import Reservation
from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def place_order_api(request):
    """API endpoint to process orders from the POS interface"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"DEBUG: place_order_api received: {data}")
            type_commande = data.get('type_commande')
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'success': False, 'error': 'Panier vide'})

            order = Order(
                agent=request.user,
                type_commande=type_commande,
                numero_table=data.get('table'),
                mode_paiement=data.get('payment_method'),
                statut='en_prepa'
            )

            if type_commande == 'resident':
                res_id = data.get('reservation_id')
                if not res_id:
                    return JsonResponse({'success': False, 'error': 'ID Réservation manquant'})
                reservation = get_object_or_404(Reservation, pk=res_id)
                order.client = reservation.client
                order.chambre = reservation.chambre
            else:
                order.nom_client_passage = data.get('customer_name') or "Client de passage"
                if order.mode_paiement != 'chambre':
                    order.paiement_effectue = True
            
            order.save()

            for item in items:
                plat = MenuItem.objects.get(pk=item['id'])
                OrderItem.objects.create(
                    commande=order,
                    plat=plat,
                    quantite=item['qty'],
                    prix_unitaire=plat.prix
                )
            
            print(f"DEBUG: Order {order.id} saved successfully")
            return JsonResponse({'success': True, 'order_id': order.id})
        except Exception as e:
            print(f"DEBUG error in place_order_api: {str(e)}")
            return JsonResponse({'success': False, 'error': f"Erreur serveur: {str(e)}"}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)


@login_required
def get_pending_orders_api(request):
    try:
        pending_orders = Order.objects.filter(statut__in=['en_prepa', 'livre']).order_by('-date')[:10]
        data = []
        for order in pending_orders:
            data.append({
                'id': order.id,
                'total': float(order.total),
                'date': order.date.strftime('%H:%M'),
                'client': order.get_client_name(),
                'agent': order.agent.username if order.agent else 'Système'
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

class OrderListView(ListView):
    model = Order
    template_name = 'restaurant/order_list.html'
    context_object_name = 'orders'
    ordering = ['-date']

class OrderCreateView(CreateView):
    model = Order
    fields = ['type_commande', 'client', 'chambre', 'nom_client_passage', 'numero_table', 'statut', 'mode_paiement']
    template_name = 'restaurant/order_form.html'
    success_url = reverse_lazy('order_list')

# MenuItem CRUD
class MenuItemListView(ListView):
    model = MenuItem
    template_name = 'restaurant/menu_item_list.html'
    context_object_name = 'items'
    ordering = ['categorie', 'nom']

class MenuItemCreateView(CreateView):
    model = MenuItem
    fields = ['nom', 'prix', 'categorie', 'image', 'description', 'temps_cuisson']
    template_name = 'restaurant/menu_item_form.html'
    success_url = reverse_lazy('menu_item_list')

class MenuItemUpdateView(UpdateView):
    model = MenuItem
    fields = ['nom', 'prix', 'categorie', 'image', 'description', 'temps_cuisson']
    template_name = 'restaurant/menu_item_form.html'
    success_url = reverse_lazy('menu_item_list')

class MenuItemDeleteView(DeleteView):
    model = MenuItem
    template_name = 'restaurant/menu_item_confirm_delete.html'
    success_url = reverse_lazy('menu_item_list')

def order_details_api(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id)
        items_list = []
        for item in order.items.all():
            items_list.append({
                'name': item.plat.nom,
                'quantity': item.quantite,
                'price': float(item.prix_unitaire),
                'total': float(item.total)
            })

        data = {
            'success': True,
            'id': order.id,
            'date': order.date.isoformat(),
            'type_commande': order.type_commande,
            'client_name': order.get_client_name(),
            'agent_name': order.agent.username if order.agent else 'N/A',
            'numero_table': order.numero_table or '-',
            'total': float(order.total),
            'items': items_list
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
