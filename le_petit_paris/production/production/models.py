# production/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Profil utilisateur pour gérer les horaires d'équipe et contrôles d'accès"""
    HORAIRES_CHOICES = [
        ('6-14', '6h - 14h (Équipe du Matin)'),
        ('14-22', '14h - 22h (Équipe de l\'Après-midi)'),
        ('22-6', '22h - 6h (Équipe de Nuit)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    horaire_equipe = models.CharField(
        max_length=10, 
        choices=HORAIRES_CHOICES,
        null=True,
        blank=True,
        verbose_name="Horaire d'équipe",
        help_text="Définit les heures d'accès autorisées pour cet utilisateur"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Profil actif")
    
    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
        ordering = ['user__username']
    
    def __str__(self):
        horaire_display = self.get_horaire_equipe_display() if self.horaire_equipe else 'Admin/Sans équipe'
        return f"{self.user.username} - {horaire_display}"
    
    def can_access_now(self):
        """Vérifie si l'utilisateur peut accéder maintenant selon l'heure"""
        # Les admins et staff ont toujours accès
        if self.user.is_superuser or self.user.is_staff:
            return True
            
        # Si pas d'équipe assignée, pas d'accès
        if not self.horaire_equipe or not self.is_active:
            return False
            
        current_hour = datetime.now().hour
        
        # Logique d'accès selon l'horaire d'équipe
        if self.horaire_equipe == '06-14':
            return 6 <= current_hour < 14
        elif self.horaire_equipe == '14-22':
            return 14 <= current_hour < 22
        elif self.horaire_equipe == '22-6':
            return current_hour >= 22 or current_hour < 6
            
        return False
    
    def get_next_access_time(self):
        """Retourne l'heure de prochain accès autorisé"""
        if not self.horaire_equipe:
            return None
            
        if self.horaire_equipe == '6-14':
            return "06h00"
        elif self.horaire_equipe == '14-22':
            return "14h00"
        elif self.horaire_equipe == '22-6':
            return "22h00"
        
        return None


class Produit(models.Model):
    """Modèle représentant un produit manufacturé"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du produit")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    code_produit = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="Code produit"
    )
    is_active = models.BooleanField(default=True, verbose_name="Produit actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class LigneProduction(models.Model):
    """Modèle représentant une ligne de production"""
    nom = models.CharField(max_length=100, verbose_name="Nom de la ligne")
    numero = models.IntegerField(unique=True, verbose_name="Numéro de ligne")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    capacite_theorique = models.PositiveIntegerField(
        default=0, 
        verbose_name="Capacité théorique (palettes/h)",
        help_text="Capacité de production théorique par heure"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ligne active")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ligne de Production"
        verbose_name_plural = "Lignes de Production"
        ordering = ['numero']
    
    def __str__(self):
        return f"Ligne {self.numero} - {self.nom}"


class Equipe(models.Model):
    """Modèle représentant une équipe de travail"""
    HORAIRES_CHOICES = [
        ('6-14', '6h - 14h (Équipe du Matin)'),
        ('14-22', '14h - 22h (Équipe de l\'Après-midi)'),
        ('22-6', '22h - 6h (Équipe de Nuit)'),
    ]
    
    nom = models.CharField(max_length=100, verbose_name="Nom de l'équipe")
    horaire = models.CharField(
        max_length=10, 
        choices=HORAIRES_CHOICES,
        verbose_name="Horaire de travail"
    )
    operateur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Opérateur responsable"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Équipe active")
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"
        unique_together = ['operateur', 'horaire']
        ordering = ['horaire', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_horaire_display()})"
    
    def is_active_now(self):
        """Vérifie si cette équipe devrait être active maintenant"""
        current_hour = datetime.now().hour
        
        if self.horaire == '6-14':
            return 6 <= current_hour < 14
        elif self.horaire == '14-22':
            return 14 <= current_hour < 22
        elif self.horaire == '22-6':
            return current_hour >= 22 or current_hour < 6
            
        return False


class ProductionRecord(models.Model):
    """Modèle principal pour les enregistrements de production"""
    
    # Statuts pour le traitement des palettes non conformes
    STATUT_PALETTE_NC_CHOICES = [
        ('en_attente', 'En attente de traitement'),
        ('traitee', 'Traitée - Toutes conformes'),
        ('partiel', 'Traitement partiel'),
        ('rejetee', 'Confirmées non conformes'),
        ('conforme', 'Toutes conformes dès le départ'),
    ]
    
    # Informations de base
    date_heure = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date et heure",
        help_text="Date et heure de l'enregistrement"
    )
    ligne_production = models.ForeignKey(
        LigneProduction,
        on_delete=models.CASCADE,
        verbose_name="Ligne de Production"
    )
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE,
        verbose_name="Produit"
    )
    equipe = models.ForeignKey(
        Equipe, 
        on_delete=models.CASCADE,
        verbose_name="Équipe"
    )
    operateur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Opérateur"
    )

    # Données de production principales
    palettes_produites = models.PositiveIntegerField(
        default=0, 
        verbose_name="Palettes Produites",
        help_text="Nombre total de palettes produites"
    )
    palettes_non_conformes = models.PositiveIntegerField(
        default=0, 
        verbose_name="Palettes Non Conformes",
        help_text="Nombre de palettes identifiées comme non conformes"
    )
    boites_produites = models.PositiveIntegerField(
        default=0, 
        verbose_name="Boîtes Produites",
        help_text="Nombre total de boîtes produites"
    )
    dechets_boites = models.PositiveIntegerField(
        default=0, 
        verbose_name="Déchets Boîtes",
        help_text="Nombre de boîtes mises au rebut (incluant traitements NC)"
    )

    # Gestion des non-conformités
    cause_non_conformite = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Cause des Non-Conformités",
        help_text="Détaillez les raisons des palettes non conformes"
    )
    statut_palette_nc = models.CharField(
        max_length=20, 
        choices=STATUT_PALETTE_NC_CHOICES,
        default='en_attente',
        verbose_name="Statut palettes NC",
        help_text="Statut du traitement des palettes non conformes"
    )
    date_controle_nc = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date du contrôle NC",
        help_text="Date à laquelle le contrôle NC a été effectué"
    )
    commentaire_controle_nc = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Commentaire contrôle NC",
        help_text="Détails du traitement des palettes non conformes"
    )
    fardeaux_recuperes = models.PositiveIntegerField(
        default=0,
        verbose_name="Fardeaux récupérés",
        help_text="Nombre de fardeaux récupérés lors du traitement NC"
    )

    # Gestion des arrêts
    duree_arret_minutes = models.PositiveIntegerField(
        default=0, 
        verbose_name="Durée d'Arrêt (minutes)",
        help_text="Durée totale des arrêts en minutes"
    )
    cause_arret = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Cause de l'Arrêt",
        help_text="Description de la cause des arrêts"
    )

    # Métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Enregistrement actif")
    commentaires = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Commentaires généraux"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Enregistrement de Production"
        verbose_name_plural = "Enregistrements de Production"
        ordering = ['-date_heure']
        indexes = [
            models.Index(fields=['-date_heure']),
            models.Index(fields=['ligne_production', '-date_heure']),
            models.Index(fields=['operateur', '-date_heure']),
            models.Index(fields=['statut_palette_nc']),
        ]
    
    def __str__(self):
        return f"{self.ligne_production} - {self.date_heure.strftime('%d/%m/%Y %H:%M')} - {self.operateur.username}"
    
    # Propriétés calculées
    def palettes_conformes(self):
        """Calcule le nombre de palettes conformes"""
        return max(0, self.palettes_produites - self.palettes_non_conformes)
    
    def taux_conformite(self):
        """Calcule le taux de conformité en pourcentage"""
        if self.palettes_produites == 0:
            return 0
        return round((self.palettes_conformes() / self.palettes_produites) * 100, 2)
    
    def has_arret(self):
        """Vérifie s'il y a eu des arrêts"""
        return self.duree_arret_minutes > 0
    
    def has_non_conformes(self):
        """Vérifie s'il y a des palettes non conformes"""
        return self.palettes_non_conformes > 0
    
    @property
    def temps_arret(self):
        """Propriété pour compatibilité avec les templates"""
        return self.duree_arret_minutes

    # Méthodes pour le traitement des palettes NC
    def can_be_treated(self):
        """Vérifie si les palettes NC peuvent être traitées"""
        return (
            self.palettes_non_conformes > 0 and 
            self.statut_palette_nc in ['en_attente', 'partiel']
        )

    def get_remaining_nc_palettes(self):
        """Retourne le nombre de palettes NC restantes à traiter"""
        if self.statut_palette_nc == 'traitee':
            return 0
        return self.palettes_non_conformes

    def get_status_display_color(self):
        """Retourne la classe CSS Bootstrap pour l'affichage du statut"""
        status_colors = {
            'en_attente': 'warning',
            'traitee': 'success',
            'partiel': 'info',
            'rejetee': 'danger',
            'conforme': 'success'
        }
        return status_colors.get(self.statut_palette_nc, 'secondary')
    
    def get_efficiency_score(self):
        """Calcule un score d'efficacité basé sur la production et la qualité"""
        if self.palettes_produites == 0:
            return 0
        
        # Score basé sur les palettes conformes vs temps
        base_score = self.palettes_conformes()
        
        # Pénalité pour les arrêts
        if self.duree_arret_minutes > 0:
            penalty = min(self.duree_arret_minutes * 0.1, base_score * 0.3)
            base_score -= penalty
        
        return max(0, round(base_score, 2))

    # Validation et sauvegarde
def clean(self):
    """Validation des données avant sauvegarde"""
    from django.core.exceptions import ValidationError
    
    # Validation des palettes
    if self.palettes_non_conformes > self.palettes_produites:
        raise ValidationError({
            'palettes_non_conformes': 'Le nombre de palettes non conformes ne peut pas dépasser le nombre de palettes produites.'
        })
    
    # ✅ CORRECTION - vérifier d'abord si operateur existe
    if self.operateur and hasattr(self.operateur, 'userprofile'):
        profile = self.operateur.userprofile
        if profile.horaire_equipe and self.equipe:
            if profile.horaire_equipe != self.equipe.horaire:
                raise ValidationError({
                    'equipe': f'L\'équipe ne correspond pas à l\'horaire de l\'opérateur ({profile.get_horaire_equipe_display()})'
                })
    elif not self.operateur:
        # Gérer le cas où aucun opérateur n'est assigné
        raise ValidationError({
            'operateur': 'Un opérateur doit être assigné à cet enregistrement.'
        })

    def save(self, *args, **kwargs):
        """Logique de sauvegarde avec mise à jour automatique du statut NC"""
        # Mettre à jour le statut NC automatiquement pour les nouveaux enregistrements
        if not self.pk:  # Si nouvel enregistrement
            if self.palettes_non_conformes == 0:
                self.statut_palette_nc = 'conforme'
            else:
                self.statut_palette_nc = 'en_attente'
        
        # Calcul automatique des boîtes produites si non renseigné
        if self.boites_produites == 0 and self.palettes_produites > 0:
            # Estimation : 1 palette ≈ 72 boîtes (selon votre logique métier)
            self.boites_produites = self.palettes_produites * 72
        
        # Validation avant sauvegarde
        self.full_clean()
        
        super().save(*args, **kwargs)


class Alerte(models.Model):
    """Modèle pour gérer les alertes de production"""
    TYPE_CHOICES = [
        ('arret', 'Arrêt de production'),
        ('dechets', 'Niveau de déchets élevé'),
        ('qualite', 'Problème qualité'),
        ('maintenance', 'Maintenance requise'),
        ('conformite', 'Non-conformité'),
        ('performance', 'Performance dégradée'),
        ('other', 'Autre'),
    ]
    
    PRIORITE_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('critical', 'Critique'),
    ]
    
    production_record = models.ForeignKey(
        ProductionRecord, 
        on_delete=models.CASCADE, 
        related_name='alertes',
        verbose_name="Enregistrement de production"
    )
    type_alerte = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='other',
        verbose_name="Type d'alerte"
    )
    priorite = models.CharField(
        max_length=10,
        choices=PRIORITE_CHOICES,
        default='medium',
        verbose_name="Priorité"
    )
    message = models.TextField(verbose_name="Message d'alerte")
    date_creation = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, verbose_name="Résolu")
    date_resolution = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resolved_alerts',
        verbose_name="Résolu par"
    )
    commentaire_resolution = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Commentaire de résolution"
    )
    
    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['is_resolved', '-date_creation']),
            models.Index(fields=['type_alerte', '-date_creation']),
            models.Index(fields=['priorite', '-date_creation']),
        ]
    
    def __str__(self):
        status = "✅ Résolue" if self.is_resolved else "⚠️ Active"
        return f"{self.get_type_alerte_display()} - {status} - {self.get_priorite_display()}"
    
    def get_age_hours(self):
        """Retourne l'âge de l'alerte en heures"""
        if self.is_resolved and self.date_resolution:
            delta = self.date_resolution - self.date_creation
        else:
            delta = timezone.now() - self.date_creation
        
        return round(delta.total_seconds() / 3600, 1)
    
    def get_priority_color(self):
        """Retourne la classe CSS Bootstrap pour la priorité"""
        colors = {
            'low': 'info',
            'medium': 'warning', 
            'high': 'danger',
            'critical': 'dark'
        }
        return colors.get(self.priorite, 'secondary')
    
    def resolve(self, user, commentaire=None):
        """Marque l'alerte comme résolue"""
        self.is_resolved = True
        self.date_resolution = timezone.now()
        self.resolved_by = user
        if commentaire:
            self.commentaire_resolution = commentaire
        self.save()


# =======================================================
# SIGNAUX POUR CRÉATION AUTOMATIQUE DES PROFILS
# =======================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal pour créer automatiquement un profil utilisateur"""
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Signal pour sauvegarder le profil utilisateur"""
    if not instance.is_superuser and hasattr(instance, 'userprofile'):
        instance.userprofile.save()


# =======================================================
# FONCTIONS UTILITAIRES
# =======================================================

def get_current_shift():
    """Fonction utilitaire pour déterminer l'équipe active actuelle"""
    current_hour = datetime.now().hour
    
    if 6 <= current_hour < 14:
        return '6-14'
    elif 14 <= current_hour < 22:
        return '14-22'
    else:
        return '22-6'


def get_active_operators():
    """Retourne la liste des opérateurs pouvant accéder maintenant"""
    active_profiles = []
    for profile in UserProfile.objects.filter(is_active=True).select_related('user'):
        if profile.can_access_now():
            active_profiles.append(profile)
    return active_profiles