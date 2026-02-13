from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Extended User model with role and status"""
    phone = models.CharField(max_length=20, blank=True)
    is_active_custom = models.BooleanField(default=True)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class Role(models.Model):
    """User roles with permissions"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Permission(models.Model):
    """Granular permissions for each module"""
    MODULE_CHOICES = [
        ('clients', 'Clients'),
        ('rooms', 'Chambres'),
        ('reservations', 'Réservations'),
        ('restaurant', 'Restauration'),
        ('transport', 'Transport'),
        ('complaints', 'Plaintes'),
        ('billing', 'Facturation'),
        ('settings', 'Système'),
        ('logs', 'Logs & Historique'),
    ]
    
    ACTION_CHOICES = [
        ('view', 'Voir'),
        ('add', 'Ajouter'),
        ('edit', 'Modifier'),
        ('delete', 'Supprimer'),
    ]
    
    role = models.ForeignKey(Role, related_name='permissions', on_delete=models.CASCADE)
    module = models.CharField(max_length=20, choices=MODULE_CHOICES)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    
    class Meta:
        unique_together = ['role', 'module', 'action']
    
    def __str__(self):
        return f"{self.role.name} - {self.get_module_display()} - {self.get_action_display()}"

class AppSettings(models.Model):
    """Application-wide settings (singleton pattern)"""
    hotel_name = models.CharField(max_length=100, default="Mon Hôtel")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default="EUR")
    timezone = models.CharField(max_length=50, default="UTC")
    
    # Branding
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#3498db")  # Hex color
    sidebar_color = models.CharField(max_length=7, default="#2c3e50")
    
    class Meta:
        verbose_name = "Paramètres Application"
        verbose_name_plural = "Paramètres Application"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
