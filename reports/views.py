from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from billing.models import Invoice
from django.db.models import Sum

@login_required
def report_view(request):
    # Get total revenue
    total_revenue = Invoice.objects.filter(statut='paye').aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    # Get total amount due
    total_due = Invoice.objects.filter(statut__in=['impaye', 'partiel']).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    
    context = {
        'total_revenue': total_revenue,
        'total_due': total_due,
    }
    return render(request, 'reports/report.html', context)
