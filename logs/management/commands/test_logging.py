"""
Test auto-logging by creating, updating, and deleting a client
Run with: python manage.py test_logging
"""
from django.core.management.base import BaseCommand
from clients.models import Client
from logs.models import ActivityLog
from logs.middleware import set_current_user
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Test automatic logging functionality'
    
    def handle(self, *args, **options):
        # Get or create test user
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@hotel.com', 'is_staff': True}
        )
        
        # Set current user for logging
        set_current_user(user)
        
        self.stdout.write("🧪 Test de l'enregistrement automatique des logs...")
        
        # Count logs before
        initial_count = ActivityLog.objects.count()
        self.stdout.write(f"Nombre de logs initial: {initial_count}")
        
        # Test 1: Create
        self.stdout.write("\n1️⃣ Test de création...")
        client = Client.objects.create(
            first_name="Test",
            last_name="Logging",
            email="test@example.com",
            phone="1234567890"
        )
        self.stdout.write(self.style.SUCCESS(f"✓ Client créé: {client}"))
        
        # Test 2: Update
        self.stdout.write("\n2️⃣ Test de modification...")
        client.phone = "0987654321"
        client.save()
        self.stdout.write(self.style.SUCCESS(f"✓ Client modifié: {client}"))
        
        # Test 3: Delete
        self.stdout.write("\n3️⃣ Test de suppression...")
        client_str = str(client)
        client.delete()
        self.stdout.write(self.style.SUCCESS(f"✓ Client supprimé: {client_str}"))
        
        # Count logs after
        final_count = ActivityLog.objects.count()
        new_logs = final_count - initial_count
        
        self.stdout.write(f"\n📊 Résultats:")
        self.stdout.write(f"Nombre de logs final: {final_count}")
        self.stdout.write(f"Nouveaux logs créés: {new_logs}")
        
        if new_logs >= 3:
            self.stdout.write(self.style.SUCCESS("\n✅ Test réussi! Les logs sont enregistrés automatiquement."))
            
            # Show recent logs
            self.stdout.write("\n📝 Derniers logs créés:")
            for log in ActivityLog.objects.order_by('-timestamp')[:new_logs]:
                self.stdout.write(f"  - {log.timestamp.strftime('%H:%M:%S')} | {log.event_type} | {log.action}")
        else:
            self.stdout.write(self.style.ERROR("\n❌ Erreur: Les logs n'ont pas été créés automatiquement."))
        
        # Clean up
        set_current_user(None)
