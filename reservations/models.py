from django.db import models
from clients.models import Client
from rooms.models import Room
from django.core.exceptions import ValidationError
import datetime

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('active', 'Active'),
        ('annulee', 'Annulée'),
        ('terminee', 'Terminée'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('banque', 'Banque'),
        ('post_paye', 'Post-payé'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    chambre = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    # Informations personnelles supplémentaires
    nationalite = models.CharField(max_length=100, blank=True, verbose_name="Nationalité")
    numero_identite = models.CharField(max_length=50, blank=True, verbose_name="Numéro d'identité/Passeport")
    date_expiration_visa = models.DateField(null=True, blank=True, verbose_name="Date d'expiration visa")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='cash')
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Montant Payé (Cash)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.pk:
            return f"Resa {self.pk} - {self.client.nom}"
        else:
            return f"Nouvelle réservation - {self.client.nom if hasattr(self, 'client') and self.client else 'Sans client'}"

    def clean(self):
        """Valider qu'il n'y a pas de chevauchement de réservations pour la même chambre"""
        super().clean()
        
        # Vérifier les chevauchements seulement si la chambre et les dates sont définies
        if self.chambre and self.date_debut and self.date_fin:
            # Vérifier que la date de fin est après la date de début
            if self.date_fin <= self.date_debut:
                raise ValidationError("La date de fin doit être après la date de début")
            
            # Vérifier les chevauchements avec d'autres réservations
            chevauchements = Reservation.objects.filter(
                chambre=self.chambre,
                statut__in=['en_attente', 'confirmee', 'active'],  # Seulement les réservations actives
                date_debut__lt=self.date_fin,
                date_fin__gt=self.date_debut
            )
            
            # Exclure la réservation actuelle si elle existe déjà
            if self.pk:
                chevauchements = chevauchements.exclude(pk=self.pk)
            
            if chevauchements.exists():
                raise ValidationError(
                    f"Cette chambre est déjà réservée du {chevauchements.first().date_debut} "
                    f"au {chevauchements.first().date_fin}"
                )

    def save(self, *args, **kwargs):
        # Valider avant de sauvegarder
        self.full_clean()
        # Vérifier si c'est une nouvelle réservation ou une mise à jour
        is_new = self._state.adding
        if not is_new:
            old_instance = Reservation.objects.get(pk=self.pk)
            old_status = old_instance.statut
        else:
            old_status = None

        super().save(*args, **kwargs)  # Sauvegarder d'abord

        # Si le statut vient de passer à 'active'
        if self.statut == 'active' and old_status != 'active':
            from billing.models import Invoice, InvoiceLine

            # Créer la facture principale pour cette réservation
            invoice, created = Invoice.objects.get_or_create(
                client=self.client,
                reservation=self,
                defaults={'statut': 'impaye'}
            )

            # Si la facture vient d'être créée, ajouter la première nuitée
            if created:
                InvoiceLine.objects.create(
                    facture=invoice,
                    description=f"Nuitée du {self.date_debut.strftime('%d/%m/%Y')} - Chambre {self.chambre.numero}",
                    quantite=1,
                    prix_unitaire=self.chambre.categorie.prix
                )
                invoice.calculer_totaux()
                invoice.save()

