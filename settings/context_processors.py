# -*- coding: utf-8 -*-
import time
from settings.models import AppSettings

def app_settings_processor(request):
    """
    Injecte les paramètres de l'application (singleton AppSettings) dans le contexte de tous les templates.
    """
    try:
        # Utilise la méthode 'load' du modèle pour récupérer l'instance unique
        settings = AppSettings.load()
    except AppSettings.DoesNotExist:
        settings = None
    
    return {
        'app_settings': settings,
        'cache_version': int(time.time())
    }
