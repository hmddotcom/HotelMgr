from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    """Comprehensive activity logging for audit trail"""
    
    EVENT_TYPES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('view', 'Consultation'),
        ('error', 'Erreur'),
        ('system', 'Système'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('critical', 'Critique'),
    ]
    
    MODULE_CHOICES = [
        ('clients', 'Clients'),
        ('rooms', 'Chambres'),
        ('reservations', 'Réservations'),
        ('restaurant', 'Restauration'),
        ('transport', 'Transport'),
        ('complaints', 'Plaintes'),
        ('billing', 'Facturation'),
        ('settings', 'Système'),
        ('auth', 'Authentification'),
    ]
    
    # Who & When
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activity_logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # What
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    module = models.CharField(max_length=20, choices=MODULE_CHOICES, db_index=True)
    action = models.CharField(max_length=255)  # Description courte
    details = models.TextField(blank=True)  # Détails complets
    
    # Object tracking
    object_type = models.CharField(max_length=50, blank=True)  # Model name
    object_id = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)  # String representation
    
    # Changes tracking (for updates)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info', db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'module']),
            models.Index(fields=['user', '-timestamp']),
        ]
        verbose_name = "Log d'activité"
        verbose_name_plural = "Logs d'activité"
    
    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.user} - {self.action}"
    
    @classmethod
    def log_event(cls, user, event_type, module, action, **kwargs):
        """Helper method to create a log entry"""
        return cls.objects.create(
            user=user,
            event_type=event_type,
            module=module,
            action=action,
            **kwargs
        )
