# production/middleware.py - Nouveau fichier

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ShiftAccessMiddleware:
    """
    Middleware qui bloque l'accès selon l'horaire d'équipe
    À 15h, seule l'équipe 14h-22h peut accéder, les autres sont bloquées
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs qui ne nécessitent pas de contrôle d'horaire
        exempt_urls = [
            reverse('login'),
            reverse('logout'),
            '/admin/',
            reverse('shift_blocked'),  # Page d'information de blocage
        ]
        
        # Vérifier si l'URL actuelle est exemptée
        current_path = request.path
        if any(current_path.startswith(url) for url in exempt_urls):
            return self.get_response(request)
        
        # Vérifier si l'utilisateur est connecté
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # Les admins passent toujours
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)
            
        # Vérifier le profil utilisateur
        if not hasattr(request.user, 'userprofile'):
            messages.error(request, "Profil utilisateur manquant. Contactez l'administrateur.")
            return redirect('login')
            
        profile = request.user.userprofile
        
        # Vérifier l'accès selon l'heure
        if not profile.can_access_now():
            current_hour = datetime.now().hour
            
            # Détermine quelle équipe devrait être en service
            if 6 <= current_hour < 14:
                current_shift_name = "Équipe du Matin (6h-14h)"
            elif 14 <= current_hour < 22:
                current_shift_name = "Équipe de l'Après-midi (14h-22h)"
            else:
                current_shift_name = "Équipe de Nuit (22h-6h)"
            
            user_shift_name = profile.get_horaire_equipe_display()
            
            # Log du blocage
            logger.warning(f"Access BLOCKED for {request.user.username} "
                         f"(équipe {profile.horaire_equipe}) at {current_hour}h. "
                         f"Current shift should be: {current_shift_name}")
            
            # Message d'information
            messages.warning(request, 
                f"Accès bloqué. Il est {current_hour}h, l'équipe en service est : {current_shift_name}. "
                f"Vous êtes de l'{user_shift_name}."
            )
            
            return redirect('shift_blocked')
        
        return self.get_response(request)


