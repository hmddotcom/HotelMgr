from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .models import Client
from reservations.models import Reservation
from billing.models import Invoice
from .forms import ClientForm

class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Client.objects.filter(
                Q(nom__icontains=query) | Q(email__icontains=query) | Q(telephone__icontains=query)
            )
        return Client.objects.all().order_by('-created_at')

class ClientCreateView(CreateView):
    model = Client
    fields = ['nom', 'email', 'telephone', 'piece_identite', 'adresse', 'solde']
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('client_list')

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Le client '{self.object.nom}' a été mis à jour avec succès.")
        return response

    def form_invalid(self, form):
        print("Form errors:", form.errors.as_json())
        messages.error(self.request, "Le formulaire contient des erreurs. Veuillez corriger les champs indiqués.")
        return super().form_invalid(form)

class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        context['reservations'] = client.reservation_set.all().order_by('-date_debut')
        context['invoices'] = client.invoice_set.all().order_by('-created_at')
        return context

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Le client a été supprimé avec succès.")
        return super().post(request, *args, **kwargs)