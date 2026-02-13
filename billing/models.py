# -*- coding: utf-8 -*-
from decimal import Decimal
from django.db import models
from clients.models import Client
from reservations.models import Reservation
from services.models import Service
from restaurant.models import MenuItem

class Invoice(models.Model):
    """Facture avec calculs comptables automatiques"""
    STATUT_CHOICES = [
        ('impaye', 'Impayée'),
        ('partiel', 'Paiement Partiel'),
        ('paye', 'Payée'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Réservation")
    numero_facture = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Numéro")
    date_emission = models.DateField(auto_now_add=True, verbose_name="Date d'émission")
    date_echeance = models.DateField(null=True, blank=True, verbose_name="Date d'échéance")
    
    # Calculs financiers
    sous_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Sous-total")
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'), verbose_name="Taux TVA (%)")
    montant_tva = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant TVA")
    remise = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Remise")
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total TTC")
    
    # Paiement
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='impaye', verbose_name="Statut")
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant payé")
    date_paiement = models.DateField(null=True, blank=True, verbose_name="Date de paiement")
    
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_emission']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
    
    def calculer_totaux(self):
        """Calcule automatiquement les totaux"""
        # Sous-total = somme des lignes
        self.sous_total = sum(line.montant_total for line in self.lines.all())
        
        # TVA sur (sous-total - remise)
        base_taxable = self.sous_total - self.remise
        self.montant_tva = base_taxable * (self.taux_tva / Decimal('100'))
        
        # Total TTC
        self.montant_total = base_taxable + self.montant_tva
        
        # Mise à jour du statut de paiement
        if self.montant_paye >= self.montant_total:
            self.statut = 'paye'
        elif self.montant_paye > 0:
            self.statut = 'partiel'
        else:
            self.statut = 'impaye'
    
    def save(self, *args, **kwargs):
        # Store the old total amount to calculate the difference
        old_montant_total = 0
        old_montant_paye = 0
        if self.pk:
            invoice = Invoice.objects.get(pk=self.pk)
            old_montant_total = invoice.montant_total
            old_montant_paye = invoice.montant_paye

        # Générer numéro de facture automatique
        if not self.numero_facture:
            from django.utils import timezone
            year = timezone.now().year
            count = Invoice.objects.filter(numero_facture__startswith=f'FACT-{year}').count() + 1
            self.numero_facture = f'FACT-{year}-{count:04d}'
        
        super().save(*args, **kwargs)

        # Update client balance
        total_diff = self.montant_total - old_montant_total
        paid_diff = self.montant_paye - old_montant_paye
        self.client.solde += total_diff - paid_diff
        self.client.save(update_fields=['solde'])
    
    def delete(self, *args, **kwargs):
        # Adjust client balance before deleting
        self.client.solde -= self.montant_total
        self.client.save(update_fields=['solde'])
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero_facture} - {self.client} - {self.montant_total} FCFA"
    
    @property
    def reste_a_payer(self):
        """Montant restant à payer"""
        return self.montant_total - self.montant_paye

class InvoiceLine(models.Model):
    """Ligne de facture"""
    facture = models.ForeignKey(Invoice, related_name='lines', on_delete=models.CASCADE, verbose_name="Facture")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Service")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Article de Menu")
    description = models.CharField(max_length=200, verbose_name="Description")
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire", default=0)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Total", default=0)
    
    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
    
    def save(self, *args, **kwargs):
        # Remplir automatiquement depuis le service ou l'article de menu
        if self.service and not self.description:
            self.description = self.service.name
        if self.service and self.prix_unitaire == 0:
            self.prix_unitaire = self.service.price
            
        if self.menu_item and not self.description:
            self.description = self.menu_item.nom
        if self.menu_item and self.prix_unitaire == 0:
            self.prix_unitaire = self.menu_item.prix

        # Calcul automatique du total de la ligne
        self.montant_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
        
        # Recalculer les totaux de la facture
        if self.facture_id:
            self.facture.calculer_totaux()
            self.facture.save(update_fields=['sous_total', 'montant_tva', 'montant_total', 'statut'])
    
    def delete(self, *args, **kwargs):
        facture = self.facture
        super().delete(*args, **kwargs)
        # Recalculer après suppression
        facture.calculer_totaux()
        facture.save(update_fields=['sous_total', 'montant_tva', 'montant_total', 'statut'])
    
    def __str__(self):
        return f"{self.description} - {self.montant_total} FCFA"
