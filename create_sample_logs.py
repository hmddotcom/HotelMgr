# -*- coding: utf-8 -*-
"""
Script to create sample activity logs for testing
Run with: python manage.py shell < create_sample_logs.py
"""
from logs.models import ActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()

# Get or create a test user
user, _ = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@hotel.com', 'is_staff': True, 'is_superuser': True}
)

# Create sample logs
ActivityLog.log_event(
    user=user,
    event_type='login',
    module='auth',
    action="Connexion reussie",
    details="Connexion depuis l'interface web",
    severity='info',
    ip_address='127.0.0.1'
)

ActivityLog.log_event(
    user=user,
    event_type='create',
    module='clients',
    action="Creation d'un nouveau client",
    details='Client: Jean Dupont',
    object_type='Client',
    object_id='1',
    object_repr='Jean Dupont',
    severity='info'
)

ActivityLog.log_event(
    user=user,
    event_type='update',
    module='reservations',
    action='Modification de reservation',
    details='Changement de dates',
    object_type='Reservation',
    object_id='1',
    old_values={'check_in': '2026-02-10', 'check_out': '2026-02-15'},
    new_values={'check_in': '2026-02-12', 'check_out': '2026-02-17'},
    severity='info'
)

ActivityLog.log_event(
    user=user,
    event_type='delete',
    module='complaints',
    action="Suppression d'une plainte",
    details='Plainte resolue et archivee',
    object_type='Complaint',
    object_id='5',
    severity='warning'
)

ActivityLog.log_event(
    user=None,
    event_type='system',
    module='settings',
    action='Sauvegarde automatique des parametres',
    details='Backup quotidien effectue',
    severity='info'
)

ActivityLog.log_event(
    user=user,
    event_type='error',
    module='billing',
    action='Erreur lors de la generation de facture',
    details='Erreur: Division par zero dans le calcul de la TVA',
    severity='error'
)

print("6 logs d'exemple crees avec succes!")
print(f"Total logs: {ActivityLog.objects.count()}")
