from django.db import models
from django.utils import timezone
from django.conf import settings
from rooms.models import Room

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie de service"
        verbose_name_plural = "Catégories de service"

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name="Catégorie")
    name = models.CharField(max_length=100, verbose_name="Nom du service")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

class RoomCleaning(models.Model):
    STATUS_CHOICES = [
        ('a_faire', 'À faire'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('valide', 'Validé'),
    ]
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('tres_urgent', 'Très urgent'),
    ]
    
    chambre = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Chambre")
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Agent de nettoyage")
    date_demande = models.DateTimeField(default=timezone.now, verbose_name="Date de demande")
    date_debut = models.DateTimeField(null=True, blank=True, verbose_name="Date de début")
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='a_faire', verbose_name="Statut")
    priorite = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name="Priorité")
    notes = models.TextField(blank=True, verbose_name="Notes")
    valide_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='validations_nettoyage', verbose_name="Validé par")
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")

    def __str__(self):
        return f"Nettoyage {self.chambre.numero} - {self.get_statut_display()}"

    class Meta:
        verbose_name = "Nettoyage de chambre"
        verbose_name_plural = "Nettoyages de chambres"
        ordering = ['-date_demande', 'priorite']