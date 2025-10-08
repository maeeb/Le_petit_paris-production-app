# production/forms.py
from django import forms
from .models import ProductionRecord, Produit, LigneProduction

class ProductionForm(forms.ModelForm):
    class Meta:
        model = ProductionRecord
        fields = [
            'ligne_production', 'produit', 'palettes_produites', 'palettes_non_conformes', 'cause_non_conformite',
            'dechets_boites', 'duree_arret_minutes', 'cause_arret', 'commentaires'
        ]
        widgets = {
            'ligne_production': forms.Select(attrs={
                'class': 'form-control form-select',
                'required': True
            }),
            'produit': forms.Select(attrs={
                'class': 'form-control form-select',
                'required': True
            }),
            'palettes_produites': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'required': True,
                'placeholder': 'Nombre de palettes produites'
            }),
            'palettes_non_conformes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Palettes non conformes',
                'id': 'id_palettes_non_conformes'
            }),
            'dechets boites': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.1',
                'placeholder': '0.0'
            }),
            'duree_arret_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0',
                'id': 'id_duree_arret_minutes'
            }),
            'cause_arret': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Décrire la cause de l\'arrêt si applicable...',
                'id': 'id_cause_arret'
            }),
            'commentaires': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '2',
                'placeholder': 'Observations particulières (optionnel)...'
            }),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ligne_production'].queryset = LigneProduction.objects.all().order_by('numero')
        self.fields['produit'].queryset = Produit.objects.all().order_by('nom')
        
        # Champs obligatoires
        self.fields['ligne_production'].required = True
        self.fields['produit'].required = True
        self.fields['palettes_produites'].required = True
        
        # Labels personnalisés
        self.fields['palettes_non_conformes'].label = "Palettes Non Conformes"

    def clean(self):
        cleaned_data = super().clean()
        duree_arret = cleaned_data.get('duree_arret_minutes', 0)
        cause_arret = cleaned_data.get('cause_arret', '').strip()
        palettes_produites = cleaned_data.get('palettes_produites', 0)
        palettes_non_conformes = cleaned_data.get('palettes_non_conformes', 0)
        cause_non_conformite = cleaned_data.get('cause_non_conformite', '').strip()
        
        # Validation arrêts
        if duree_arret > 0 and not cause_arret:
            raise forms.ValidationError(
                "Veuillez spécifier la cause de l'arrêt si la durée est supérieure à 0 minutes."
            )
        
        # Validation palettes non conformes
        if palettes_non_conformes > palettes_produites:
            raise forms.ValidationError(
                "Le nombre de palettes non conformes ne peut pas dépasser le nombre total de palettes produites."
            )
        
        # Validations générales
        if palettes_produites < 0:
            raise forms.ValidationError("Le nombre de palettes ne peut pas être négatif.")
        
        if palettes_non_conformes < 0:
            raise forms.ValidationError("Le nombre de palettes non conformes ne peut pas être négatif.")
        
        if cleaned_data.get('dechets_boites', 0) < 0:
            raise forms.ValidationError("Le poids des déchets ne peut pas être négatif.")
            
        if duree_arret < 0:
            raise forms.ValidationError("La durée d'arrêt ne peut pas être négative.")
        
        return cleaned_data

# Formulaire pour filtrer les relevés
class ProductionFilterForm(forms.Form):
    """Formulaire pour filtrer les relevés de production dans l'historique"""
    
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de début"
    )
    
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de fin"
    )
    
    ligne_production = forms.ModelChoiceField(
        queryset=LigneProduction.objects.all().order_by('numero'),
        required=False,
        empty_label="Toutes les lignes",
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        label="Ligne de production"
    )
    
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all().order_by('nom'),
        required=False,
        empty_label="Tous les produits",
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        label="Produit"
    )