from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True, verbose_name="E-mail")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    piece_identite = models.ImageField(upload_to='identites/', blank=True, null=True, verbose_name="Pièce d'identité")
    adresse = models.TextField(blank=True, null=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
