from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import TransportRequest
from django import forms

class TransportForm(forms.ModelForm):
    class Meta:
        model = TransportRequest
        fields = ['client', 'vehicule', 'destination', 'date_depart', 'prix', 'statut']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'date_depart': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class TransportListView(ListView):
    model = TransportRequest
    template_name = 'transport/transport_list.html'
    context_object_name = 'requests'

class TransportCreateView(CreateView):
    model = TransportRequest
    form_class = TransportForm
    template_name = 'transport/transport_form.html'
    success_url = reverse_lazy('transport_list')
