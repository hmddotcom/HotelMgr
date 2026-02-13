from django.db import models

class RoomCategory(models.Model):
    nom = models.CharField(max_length=50)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    # image = models.ImageField(...) # Keeping it simple for now without media config

    def __str__(self):
        return f"{self.nom} ({self.prix}€)"

class Room(models.Model):
    STATUS_CHOICES = [
        ('disponible', 'Disponible'),
        ('occupee', 'Occupée'),
        ('maintenance', 'Maintenance'),
    ]
    
    CLEANING_STATUS_CHOICES = [
        ('sale', 'Sale'),
        ('propre', 'Propre'),
        ('inspectee', 'Inspectée'),
    ]

    numero = models.CharField(max_length=10, unique=True)
    categorie = models.ForeignKey(RoomCategory, on_delete=models.SET_NULL, null=True, related_name='rooms', verbose_name="Catégorie")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponible')
    cleaning_status = models.CharField(max_length=20, choices=CLEANING_STATUS_CHOICES, default='propre')

    def __str__(self):
        return f"Chambre {self.numero}"
