from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reservation
from .forms import ReservationForm
from clients.models import Client
from rooms.models import Room
from django import forms
from django.utils import timezone
from datetime import timedelta

class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/reservation_list.html'
    context_object_name = 'reservations'
    ordering = ['-date_debut']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre par statut
        statut_filter = self.request.GET.get('statut')
        if statut_filter:
            queryset = queryset.filter(statut=statut_filter)
        
        # Filtre temporel
        time_filter = self.request.GET.get('time')
        if time_filter == 'active':
            queryset = queryset.filter(statut='active')
        elif time_filter == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(date_debut=today)
        elif time_filter == 'week':
            week_start = timezone.now().date() - timedelta(days=7)
            queryset = queryset.filter(date_debut__gte=week_start)
        elif time_filter == 'month':
            month_start = timezone.now().date() - timedelta(days=30)
            queryset = queryset.filter(date_debut__gte=month_start)
        elif time_filter == 'future':
            queryset = queryset.filter(date_debut__gt=timezone.now().date())
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ReservationForm()
        context['current_statut_filter'] = self.request.GET.get('statut', '')
        context['current_time_filter'] = self.request.GET.get('time', '')
        return context

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    success_url = reverse_lazy('reservation_list')

    def form_valid(self, form):
        # La logique de création du client est dans le form.save()
        self.object = form.save()
        messages.success(self.request, f"La réservation pour le client {self.object.client.nom} a été créée avec succès.")
        return redirect(self.get_success_url())

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required

from affiliations.models import Affiliation
from services.models import RoomCleaning

@login_required
def check_in_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Check if the reservation can be checked in
    if reservation.statut == 'confirmee':
        # Update reservation status
        reservation.statut = 'active'
        reservation.save()
        
        # Update room status
        reservation.chambre.statut = 'occupee'
        reservation.chambre.save()
        
        messages.success(request, f"Le client {reservation.client.nom} a été enregistré (check-in) avec succès.")
    else:
        messages.error(request, "Cette réservation ne peut pas être enregistrée (check-in).")
        
    return redirect('reservation_list')


@login_required
def chambres_disponibles_api(request):
    """API endpoint pour récupérer les chambres disponibles pour des dates données"""
    date_debut_str = request.GET.get('date_debut')
    date_fin_str = request.GET.get('date_fin')
    
    if not date_debut_str or not date_fin_str:
        return JsonResponse({'error': 'Les paramètres date_debut et date_fin sont requis'}, status=400)
    
    try:
        date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        
        # Vérifier que la date de fin est après la date de début
        if date_fin <= date_debut:
            return JsonResponse({'error': 'La date de fin doit être après la date de début'}, status=400)
        
        # Trouver les chambres déjà réservées pour ces dates
        from .models import Reservation
        from rooms.models import Room
        
        chambres_occupees = Reservation.objects.filter(
            date_debut__lt=date_fin,
            date_fin__gt=date_debut,
            statut__in=['en_attente', 'confirmee', 'active']
        ).values_list('chambre_id', flat=True)
        
        # Filtrer les chambres disponibles (non occupées, statut disponible et statut de nettoyage inspectée)
        chambres_disponibles = Room.objects.filter(
            statut='disponible',
            cleaning_status='inspectee'
        ).exclude(
            id__in=chambres_occupees
        ).select_related('categorie')
        
        # Préparer les données de réponse
        chambres_data = []
        for chambre in chambres_disponibles:
            chambres_data.append({
                'id': chambre.id,
                'numero': chambre.numero,
                'categorie_nom': chambre.categorie.nom if chambre.categorie else 'Sans catégorie',
                'categorie_prix': float(chambre.categorie.prix) if chambre.categorie else 0.00
            })
        
        return JsonResponse({'chambres': chambres_data})
        
    except ValueError:
        return JsonResponse({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erreur serveur: {str(e)}'}, status=500)

from affiliations.models import Affiliation

@login_required
def check_out_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Check if the reservation can be checked out
    if reservation.statut == 'active':
        can_check_out = False
        
        # Condition 1: Client's balance is zero
        if reservation.client.solde == 0:
            can_check_out = True
        
        # Condition 2: Affiliation is validated
        try:
            affiliation = Affiliation.objects.get(reservation=reservation)
            if affiliation.statut_validation == 'validee':
                can_check_out = True
        except Affiliation.DoesNotExist:
            pass # No affiliation, so we rely on the balance
            
        if can_check_out:
            # Update reservation status
            reservation.statut = 'terminee'
            reservation.save()
            
            # Update room status
            reservation.chambre.statut = 'disponible'
            reservation.chambre.cleaning_status = 'sale'
            reservation.chambre.save()
            
            # Create automatic cleaning request with medium priority
            RoomCleaning.objects.create(
                chambre=reservation.chambre,
                statut='a_faire',
                priorite='normal',
                notes=f"Nettoyage automatique après checkout de la réservation #{reservation.pk}"
            )
            
            messages.success(request, f"Le client {reservation.client.nom} a été libéré (check-out) avec succès. Une demande de nettoyage a été créée.")
        else:
            messages.error(request, "Le check-out a échoué. Le solde du client n'est pas nul ou l'affiliation n'est pas validée.")
    else:
        messages.error(request, "Cette réservation ne peut pas être libérée (check-out).")
        
    return redirect('reservation_list')

class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    success_url = reverse_lazy('reservation_list')

class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'reservations/reservation_confirm_delete.html'
    success_url = reverse_lazy('reservation_list')
    
    def post(self, request, *args, **kwargs):
        messages.success(self.request, "La réservation a été supprimée avec succès.")
        return super().post(request, *args, **kwargs)
