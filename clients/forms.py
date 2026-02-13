from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Client

class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On force le champ email à ne jamais être désactivé
        self.fields['email'].disabled = False

    class Meta:
        model = Client
        fields = ['nom', 'email', 'telephone', 'piece_identite', 'adresse', 'solde']
        widgets = {
            'piece_identite': ClearableFileInput(),
        }
