# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import ActivityLog
import json

# Track models to log
LOGGED_MODELS = [
    'clients.Client',
    'rooms.Room',
    'reservations.Reservation',
    'restaurant.Order',
    'transport.TransportRequest',
    'complaints.Complaint',
    'billing.Invoice',
    'settings.CustomUser',
    'settings.Role',
    'settings.AppSettings',
]

# Store old values before update
_pre_save_instances = {}

def should_log_model(instance):
    """Check if this model should be logged"""
    model_name = f"{instance._meta.app_label}.{instance._meta.model_name}"
    return any(model_name.lower() == logged.lower() for logged in LOGGED_MODELS)

def get_model_fields(instance):
    """Get serializable fields from model instance"""
    fields = {}
    for field in instance._meta.fields:
        try:
            value = getattr(instance, field.name)
            # Convert to string for JSON serialization
            if hasattr(value, 'pk'):
                fields[field.name] = str(value)
            elif isinstance(value, (str, int, float, bool, type(None))):
                fields[field.name] = value
            else:
                fields[field.name] = str(value)
        except:
            pass
    return fields

@receiver(pre_save)
def store_pre_save_instance(sender, instance, **kwargs):
    """Store instance state before save for comparison"""
    if should_log_model(instance) and instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _pre_save_instances[instance.pk] = get_model_fields(old_instance)
        except sender.DoesNotExist:
            pass

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Log creation and updates"""
    if not should_log_model(instance):
        return
    
    # Get current user from thread local (set by middleware)
    user = getattr(instance, '_current_user', None)
    
    model_name = instance._meta.model_name.title()
    app_label = instance._meta.app_label
    
    if created:
        # Log creation
        ActivityLog.log_event(
            user=user,
            event_type='create',
            module=app_label,
            action=f"Création de {model_name}: {str(instance)}",
            details=f"Nouvel enregistrement créé dans {model_name}",
            object_type=model_name,
            object_id=str(instance.pk),
            object_repr=str(instance),
            new_values=get_model_fields(instance),
            severity='info'
        )
    else:
        # Log update
        old_values = _pre_save_instances.pop(instance.pk, None)
        new_values = get_model_fields(instance)
        
        # Only log if there are actual changes
        if old_values and old_values != new_values:
            ActivityLog.log_event(
                user=user,
                event_type='update',
                module=app_label,
                action=f"Modification de {model_name}: {str(instance)}",
                details=f"Enregistrement modifié dans {model_name}",
                object_type=model_name,
                object_id=str(instance.pk),
                object_repr=str(instance),
                old_values=old_values,
                new_values=new_values,
                severity='info'
            )

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Log deletions"""
    if not should_log_model(instance):
        return
    
    user = getattr(instance, '_current_user', None)
    model_name = instance._meta.model_name.title()
    app_label = instance._meta.app_label
    
    ActivityLog.log_event(
        user=user,
        event_type='delete',
        module=app_label,
        action=f"Suppression de {model_name}: {str(instance)}",
        details=f"Enregistrement supprimé de {model_name}",
        object_type=model_name,
        object_id=str(instance.pk),
        object_repr=str(instance),
        old_values=get_model_fields(instance),
        severity='warning'
    )

# Authentication signals
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful login"""
    ActivityLog.log_event(
        user=user,
        event_type='login',
        module='auth',
        action=f"Connexion réussie: {user.username}",
        details=f"L'utilisateur {user.get_full_name() or user.username} s'est connecté",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        severity='info'
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log logout"""
    if user:
        ActivityLog.log_event(
            user=user,
            event_type='logout',
            module='auth',
            action=f"Déconnexion: {user.username}",
            details=f"L'utilisateur {user.get_full_name() or user.username} s'est déconnecté",
            ip_address=get_client_ip(request),
            severity='info'
        )

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts"""
    username = credentials.get('username', 'Unknown')
    ActivityLog.log_event(
        user=None,
        event_type='error',
        module='auth',
        action=f"Tentative de connexion échouée: {username}",
        details=f"Échec d'authentification pour l'utilisateur {username}",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        severity='warning'
    )

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
