from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # AUTHENTIFICATION
    # ==========================================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==========================================
    # DASHBOARDS
    # ==========================================
    path('dashboard/', views.operator_dashboard, name='operator_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('operateur-login/', views.operateur_login_view, name='operateur_login'),

    # ==========================================
    # GESTION DES RELEVÉS DE PRODUCTION
    # ==========================================
    path('nouveau-releve/', views.add_production_record, name='add_production_record'),
    path('historique/', views.production_history, name='production_history'),
    path('modifier-releve/<int:record_id>/', views.edit_production_record, name='edit_production_record'),
    
    # ==========================================
    # TRAITEMENT DES PALETTES NON CONFORMES
    # ==========================================
    path('palette-nc-details/<int:record_id>/', views.palette_nc_details, name='palette_nc_details'),
    path('traiter-palette-nc/<int:record_id>/', views.traiter_palette_nc, name='traiter_palette_nc'),
    # Sécurité
    path('shift-blocked/', views.shift_blocked, name='shift_blocked'),
    
    # ==========================================
    # APIs ET DONNÉES EN TEMPS RÉEL
    # ==========================================
    path('api/production-data/', views.api_production_data, name='api_production_data'),
    path('api/system-health/', views.api_system_health, name='api_system_health'),
    
    # ==========================================
    # GESTION DES ALERTES
    # ==========================================
    path('resolve-alert/<int:alert_id>/', views.resolve_alert, name='resolve_alert'),
]
