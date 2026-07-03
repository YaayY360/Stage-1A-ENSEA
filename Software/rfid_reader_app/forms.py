from django import forms
from .models import Component

class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = '__all__'  # Ou spécifie une liste : ['name', 'reference', 'quantity', ...]
        # Optionnel : Ajoute des classes Bootstrap pour le style
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            # Fais de même pour les autres champs si nécessaire
        }