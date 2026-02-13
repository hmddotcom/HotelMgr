from django.db import models
from clients.models import Client

class Vehicle(models.Model):
    modele = models.CharField(max_length=100)
    immatriculation = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.modele} ({self.immatriculation})"

class TransportRequest(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('termine', 'Terminé'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vehicule = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    destination = models.CharField(max_length=200)
    date_depart = models.DateTimeField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
