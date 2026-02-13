from django.db import models
from reservations.models import Reservation
from django.conf import settings

class Affiliation(models.Model):
    VALIDATION_STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    nom_entreprise = models.CharField(max_length=100, verbose_name="Nom de l'entreprise")
    contact_entreprise = models.CharField(max_length=100, verbose_name="Contact de l'entreprise")
    statut_validation = models.CharField(max_length=20, choices=VALIDATION_STATUS_CHOICES, default='en_attente', verbose_name="Statut de validation")
    valide_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='validations_affiliation')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Affiliation pour la réservation {self.reservation.id} ({self.nom_entreprise})"
