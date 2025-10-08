# production/middleware.py

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ShiftAccessMiddleware:
    """
    Middleware qui bloque l'accès selon l'horaire d'équipe
    Seule l'équipe en service peut accéder
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs exemptées du contrôle d'horaire
        exempt_urls = [
            reverse('login'),
            reverse('logout'),
            '/admin/',
            reverse('shift_blocked'),
        ]

        current_path = request.path
        if any(current_path.startswith(url) for url in exempt_urls):
            return self.get_response(request)

        # Vérifier si l'utilisateur est connecté
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Admins et staff passent toujours
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

            # Détermine l'équipe actuellement en service
            if 6 <= current_hour < 14:
                current_shift_name = "Matin"
            elif 14 <= current_hour < 22:
                current_shift_name = "Après-midi"
            else:
                current_shift_name = "Nuit"

            # Récupérer l'équipe de l'utilisateur
            user_shift_name = profile.horaire_equipe  # Assure-toi que le champ a exactement "Matin", "Après-midi", ou "Nuit"

            # Log du blocage
            logger.warning(
                f"Access BLOCKED for {request.user.username} "
                f"(équipe {user_shift_name}) at {current_hour}h. "
                f"Current shift should be: {current_shift_name}"
            )

            # Message d'information
            messages.warning(
                request,
                f"Accès bloqué. Il est {current_hour}h, l'équipe en service est : {current_shift_name}. "
                f"Vous êtes de l'équipe : {user_shift_name}."
            )

            return redirect('shift_blocked')

        return self.get_response(request)
