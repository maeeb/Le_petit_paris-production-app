from django.contrib import admin
from .models import Produit, LigneProduction, Equipe, ProductionRecord, Alerte

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']
    search_fields = ['nom']

@admin.register(LigneProduction)
class LigneProductionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nom']
    ordering = ['numero']

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'horaire', 'operateur']
    list_filter = ['horaire']

@admin.register(ProductionRecord)
class ProductionRecordAdmin(admin.ModelAdmin):
    list_display = ['date_heure', 'ligne_production', 'operateur', 'palettes_produites', 'cause_non_conformite',  'dechets_boites', 'duree_arret_minutes']
    list_filter = ['ligne_production', 'date_heure', 'operateur']
    search_fields = ['operateur__username', 'cause_arret', 'cause_non_conformite'] 
    date_hierarchy = 'date_heure'

@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ['date_creation', 'type_alerte', 'is_resolved', 'production_record']
    list_filter = ['type_alerte', 'is_resolved', 'date_creation']
    fields = (
        'date_heure', 'ligne_production', 'produit', 'equipe', 'operateur',
        'palettes_produites', 'palettes_non_conformes', 'cause_non_conformite',
        'boites_produites', 'dechets_boites',
        'duree_arret_minutes', 'cause_arret',
        'is_active', 'commentaires'
    )
    from django.contrib import admin
from .models import UserProfile, ProductionRecord, LigneProduction, Produit, Equipe

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'horaire_equipe', 'get_can_access_now')
    list_filter = ('horaire_equipe',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    
    def get_can_access_now(self, obj):
        return obj.can_access_now()
    get_can_access_now.short_description = 'Peut accéder maintenant'
    get_can_access_now.boolean = True