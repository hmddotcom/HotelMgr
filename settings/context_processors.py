# -*- coding: utf-8 -*-
import time
from settings.models import AppSettings, Permission

def app_settings_processor(request):
    """
    Injecte les paramètres de l'application (singleton AppSettings) dans le contexte de tous les templates.
    """
    try:
        # Utilise la méthode 'load' du modèle pour récupérer l'instance unique
        settings = AppSettings.load()
    except AppSettings.DoesNotExist:
        settings = None
    
    allowed_modules = []
    allowed_actions = {}
    if getattr(request, 'user', None) and request.user.is_authenticated:
        if request.user.is_superuser:
            allowed_modules = [key for key, _label in Permission.MODULE_CHOICES]
            allowed_actions = {module: ['view', 'add', 'edit', 'delete'] for module in allowed_modules}
        else:
            role = getattr(request.user, 'role', None)
            if role:
                allowed_modules = list(
                    Permission.objects.filter(role=role).values_list('module', flat=True).distinct()
                )
                for module, action in Permission.objects.filter(role=role).values_list('module', 'action'):
                    allowed_actions.setdefault(module, set()).add(action)
                allowed_actions = {module: sorted(actions) for module, actions in allowed_actions.items()}

    return {
        'app_settings': settings,
        'cache_version': int(time.time()),
        'allowed_modules': allowed_modules,
        'allowed_actions': allowed_actions,
    }
