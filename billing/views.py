from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceLine

def add_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            invoice.montant_paye += float(amount)
            invoice.date_paiement = timezone.now().date()
            invoice.calculer_totaux()
            invoice.save()
            messages.success(request, f"Paiement de {amount} ajouté à la facture {invoice.numero_facture}.")
            return redirect('invoice_list')
    return render(request, 'billing/add_payment.html', {'invoice': invoice})


class InvoiceListView(ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'

InvoiceLineFormSet = inlineformset_factory(
    Invoice, InvoiceLine,
    fields=('service', 'description', 'quantite', 'prix_unitaire'),
    extra=1,
    can_delete=True
)

class InvoiceCreateView(CreateView):
    model = Invoice
    fields = ['client', 'reservation']
    template_name = 'billing/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['lines'] = InvoiceLineFormSet(self.request.POST)
        else:
            data['lines'] = InvoiceLineFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lines = context['lines']
        if lines.is_valid():
            self.object = form.save()
            lines.instance = self.object
            lines.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class InvoiceUpdateView(UpdateView):
    model = Invoice
    fields = ['client', 'reservation']
    template_name = 'billing/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['lines'] = InvoiceLineFormSet(self.request.POST, instance=self.object)
        else:
            data['lines'] = InvoiceLineFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        lines = context['lines']
        if lines.is_valid():
            self.object = form.save()
            lines.instance = self.object
            lines.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
