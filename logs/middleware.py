from django.utils.deprecation import MiddlewareMixin
from django.contrib.messages import get_messages
from django.utils import timezone
from .models import ActivityLog
import threading

# Thread-local storage for current user tracking
_current_user = threading.local()

class CurrentUserMiddleware(MiddlewareMixin):
    """Middleware pour suivre l'utilisateur courant dans les logs"""
    
    def process_request(self, request):
        # Stocker l'utilisateur courant dans le thread local
        _current_user.value = request.user if request.user.is_authenticated else None
        return None
    
    @classmethod
    def get_current_user(cls):
        """Récupérer l'utilisateur courant depuis n'importe où"""
        return getattr(_current_user, 'value', None)

class MessageLoggingMiddleware(MiddlewareMixin):
    """Middleware pour capturer et logger les messages Django"""
    
    def process_response(self, request, response):
        # Ne logger que pour les requêtes réussies
        if response.status_code >= 200 and response.status_code < 300:
            messages = get_messages(request)
            
            for message in messages:
                # Déterminer le module basé sur l'URL
                module = self._get_module_from_request(request)
                
                # Déterminer le type d'événement basé sur le message
                event_type = self._get_event_type_from_message(str(message))
                
                # Créer le log
                ActivityLog.log_event(
                    user=request.user if request.user.is_authenticated else None,
                    event_type=event_type,
                    module=module,
                    action=str(message),
                    severity='info',
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
        
        return response
    
    def _get_module_from_request(self, request):
        """Déterminer le module basé sur l'URL"""
        path = request.path
        
        if '/clients/' in path:
            return 'clients'
        elif '/reservations/' in path:
            return 'reservations'
        elif '/rooms/' in path:
            return 'rooms'
        elif '/services/' in path:
            return 'services'
        elif '/billing/' in path:
            return 'billing'
        elif '/settings/' in path:
            return 'settings'
        elif '/restaurant/' in path:
            return 'restaurant'
        elif '/transport/' in path:
            return 'transport'
        else:
            return 'system'
    
    def _get_event_type_from_message(self, message):
        """Déterminer le type d'événement basé sur le contenu du message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['crée', 'créée', 'ajout']):
            return 'create'
        elif any(word in message_lower for word in ['modifié', 'mis à jour', 'changé']):
            return 'update'
        elif any(word in message_lower for word in ['supprimé', 'effacé', 'retiré']):
            return 'delete'
        elif 'erreur' in message_lower or 'invalid' in message_lower:
            return 'error'
        else:
            return 'system'
    
    def _get_client_ip(self, request):
        """Récupérer l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip