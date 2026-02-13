from django.db import models

class Table(models.Model):
    STATUS_CHOICES = [
        ('libre', 'Libre'),
        ('occupee', 'Occupée'),
        ('reservee', 'Réservée'),
    ]
    numero = models.CharField(max_length=10, unique=True, verbose_name="Numéro de table")
    capacite = models.PositiveIntegerField(default=4, verbose_name="Capacité")
    statut = models.CharField(max_length=10, choices=STATUS_CHOICES, default='libre', verbose_name="Statut")

    def __str__(self):
        return f"Table N° {self.numero}"

class MenuCategory(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")

    class Meta:
        verbose_name = "Catégorie de menu"
        verbose_name_plural = "Catégories de menu"

    def __str__(self):
        return self.nom

class MenuItem(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom de l'article")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    categorie = models.ForeignKey(MenuCategory, related_name='items', on_delete=models.CASCADE, verbose_name="Catégorie")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")

    class Meta:
        verbose_name = "Article de menu"
        verbose_name_plural = "Articles de menu"

    def __str__(self):
        return self.nom
