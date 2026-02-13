from django.db import models
from clients.models import Client

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    sujet = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nouveau')
