from settings.models import AppSettings

def app_settings(request):
    """Provides global settings like hotel name to all templates"""
    settings = AppSettings.load()
    return {
        'app_settings': settings,
    }
