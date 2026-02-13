from django.db import models
from clients.models import Client
from rooms.models import Room
from django.conf import settings

class DishCategory(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Catégorie de plat"
        verbose_name_plural = "Catégories de plats"

class MenuItem(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du plat")
    prix = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Prix")
    categorie = models.ForeignKey(DishCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Catégorie")
    image = models.ImageField(upload_to='menu/', blank=True, null=True, verbose_name="Photo du plat")
    description = models.TextField(blank=True, null=True, verbose_name="Détails / Ingrédients")
    temps_cuisson = models.PositiveIntegerField(default=15, help_text="En minutes", verbose_name="Temps de cuisson")

    def __str__(self):
        return self.nom

class Order(models.Model):
    STATUS_CHOICES = [
        ('en_prepa', 'En préparation'),
        ('livre', 'Livré/Servi'),
        ('paye', 'Payé'),
    ]

    ORDER_TYPE_CHOICES = [
        ('resident', 'Résident (Chambre)'),
        ('passage', 'Client de Passage'),
    ]

    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Agent")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Client")
    chambre = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Chambre")
    
    type_commande = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='passage', verbose_name="Type de client")
    nom_client_passage = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom (Client passage)")
    numero_table = models.CharField(max_length=10, blank=True, null=True, verbose_name="Table")
    
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_prepa', verbose_name="Statut")
    
    paiement_effectue = models.BooleanField(default=False, verbose_name="Payé")
    mode_paiement = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'),
        ('carte', 'Carte'),
        ('mobile', 'Mobile Money'),
        ('chambre', 'Sur la chambre'),
        ('abonnee', 'Abonné'),
    ], default='cash', verbose_name="Mode de paiement")
    
    @property
    def total(self):
        return sum(item.total for item in self.items.all())

    def save(self, *args, **kwargs):
        # Automatically trigger billing for residents when status is 'livre'
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            if old_order.statut != 'livre' and self.statut == 'livre':
                if self.type_commande == 'resident' and self.chambre:
                    # Logic to integrate into existing invoice for active reservation
                    from billing.models import Invoice, InvoiceLine
                    if self.chambre.reservation_set.filter(statut='active').exists():
                        reservation = self.chambre.reservation_set.filter(statut='active').first()
                        client = reservation.client
                        
                        invoice, created = Invoice.objects.get_or_create(
                            client=client,
                            statut='impaye',
                            defaults={'reservation': reservation}
                        )
                        
                        for item in self.items.all():
                            InvoiceLine.objects.create(
                                facture=invoice,
                                description=f"Restaurant: {item.plat.nom}",
                                quantite=item.quantite,
                                prix_unitaire=item.plat.prix
                            )
                        
                        invoice.calculer_totaux()
                        invoice.save()

        super().save(*args, **kwargs)

    def get_client_name(self):
        if self.type_commande == 'resident':
            if self.chambre and self.chambre.reservation_set.filter(statut='active').exists():
                return self.chambre.reservation_set.filter(statut='active').first().client.get_full_name()
            elif self.client:
                return self.client.get_full_name()
            return "Résident Inconnu"
        else: # 'passage'
            return self.nom_client_passage or "Client de Passage"

    def __str__(self):
        ident = self.get_client_name()
        return f"Commande {self.id} - {ident} ({self.total} FCFA)"

class OrderItem(models.Model):
    commande = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    plat = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Prix Unitaire")

    @property
    def total(self):
        return self.prix_unitaire * self.quantite

    def __str__(self):
        return f"{self.quantite}x {self.plat.nom}"
