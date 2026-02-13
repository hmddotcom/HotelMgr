from django.apps import AppConfig

class LogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'
    verbose_name = "Logs d'Activité"
    
    def ready(self):
        """Import signals when app is ready"""
        import logs.signals
