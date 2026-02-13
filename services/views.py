from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import ServiceCategory, Service, RoomCleaning

class ServiceCategoryListView(ListView):
    model = ServiceCategory
    template_name = 'services/category_list.html'
    context_object_name = 'categories'

class ServiceCategoryCreateView(CreateView):
    model = ServiceCategory
    fields = ['name', 'description']
    template_name = 'services/category_form.html'
    success_url = reverse_lazy('service_category_list')

class ServiceCategoryUpdateView(UpdateView):
    model = ServiceCategory
    fields = ['name', 'description']
    template_name = 'services/category_form.html'
    success_url = reverse_lazy('service_category_list')

class ServiceCategoryDeleteView(DeleteView):
    model = ServiceCategory
    template_name = 'services/category_confirm_delete.html'
    success_url = reverse_lazy('service_category_list')

class ServiceListView(ListView):
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'

class ServiceCreateView(CreateView):
    model = Service
    fields = ['category', 'name', 'price', 'description']
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('service_list')

class ServiceUpdateView(UpdateView):
    model = Service
    fields = ['category', 'name', 'price', 'description']
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('service_list')

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'services/service_confirm_delete.html'
    success_url = reverse_lazy('service_list')

# Views pour le nettoyage des chambres
class RoomCleaningListView(ListView):
    model = RoomCleaning
    template_name = 'services/room_cleaning_list.html'
    context_object_name = 'cleanings'

class RoomCleaningCreateView(CreateView):
    model = RoomCleaning
    fields = ['chambre', 'priorite', 'notes']
    template_name = 'services/room_cleaning_form.html'
    success_url = reverse_lazy('room_cleaning_list')
    
    def form_valid(self, form):
        form.instance.agent = self.request.user
        messages.success(self.request, "Demande de nettoyage créée avec succès.")
        return super().form_valid(form)

class RoomCleaningUpdateView(UpdateView):
    model = RoomCleaning
    fields = ['chambre', 'agent', 'priorite', 'notes', 'statut']
    template_name = 'services/room_cleaning_form.html'
    success_url = reverse_lazy('room_cleaning_list')

class RoomCleaningDeleteView(DeleteView):
    model = RoomCleaning
    template_name = 'services/room_cleaning_confirm_delete.html'
    success_url = reverse_lazy('room_cleaning_list')

def start_cleaning(request, pk):
    cleaning = get_object_or_404(RoomCleaning, pk=pk)
    if cleaning.statut == 'a_faire':
        cleaning.statut = 'en_cours'
        cleaning.date_debut = timezone.now()
        cleaning.agent = request.user
        cleaning.save()
        messages.success(request, f"Nettoyage de la chambre {cleaning.chambre.numero} démarré.")
    return redirect('room_cleaning_list')

def complete_cleaning(request, pk):
    cleaning = get_object_or_404(RoomCleaning, pk=pk)
    if cleaning.statut == 'en_cours':
        cleaning.statut = 'termine'
        cleaning.date_fin = timezone.now()
        cleaning.save()
        messages.success(request, f"Nettoyage de la chambre {cleaning.chambre.numero} terminé.")
    return redirect('room_cleaning_list')

def validate_cleaning(request, pk):
    cleaning = get_object_or_404(RoomCleaning, pk=pk)
    if cleaning.statut == 'termine':
        cleaning.statut = 'valide'
        cleaning.valide_par = request.user
        cleaning.date_validation = timezone.now()
        cleaning.save()
        # Mettre à jour le statut de la chambre
        cleaning.chambre.cleaning_status = 'clean'
        cleaning.chambre.save()
        messages.success(request, f"Nettoyage de la chambre {cleaning.chambre.numero} validé.")
    return redirect('room_cleaning_list')