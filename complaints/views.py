from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Complaint
from django import forms

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['client', 'sujet', 'description', 'statut']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

class ComplaintListView(ListView):
    model = Complaint
    template_name = 'complaints/complaint_list.html'
    context_object_name = 'complaints'

class ComplaintCreateView(CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'complaints/complaint_form.html'
    success_url = reverse_lazy('complaint_list')
