from django import forms
from .models import Reservation
from clients.models import Client
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, Div

class ReservationForm(forms.ModelForm):
    # Champs pour le client
    nom_client = forms.CharField(label="Nom du client", max_length=100)
    email_client = forms.EmailField(label="E-mail du client", required=False)
    telephone_client = forms.CharField(label="Téléphone du client", max_length=20)
    adresse_client = forms.CharField(label="Adresse du client", widget=forms.Textarea(attrs={'rows': 3}), required=False)
    piece_identite_client = forms.ImageField(label="Pièce d'identité", required=False)

    class Meta:
        model = Reservation
        fields = ['chambre', 'nationalite', 'numero_identite', 'date_expiration_visa', 'date_naissance', 'date_debut', 'date_fin', 'statut', 'mode_paiement', 'cash']
        widgets = {
            'nationalite': forms.TextInput(attrs={'placeholder': 'Ex: Française, Sénégalaise, etc.'}),
            'numero_identite': forms.TextInput(attrs={'placeholder': 'Numéro de passeport ou CNI'}),
            'date_expiration_visa': forms.DateInput(attrs={'type': 'date'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si on est en mode "modification" (instance existante)
        if self.instance and self.instance.pk:
            client = self.instance.client
            # Initialiser les champs avec les données du client
            self.fields['nom_client'].initial = client.nom
            self.fields['email_client'].initial = client.email
            self.fields['telephone_client'].initial = client.telephone
            self.fields['adresse_client'].initial = client.adresse

            # Pour les champs DateField, il faut les re-formater pour l'input HTML
            if self.instance.date_debut:
                self.initial['date_debut'] = self.instance.date_debut.strftime('%Y-%m-%d')
            if self.instance.date_fin:
                self.initial['date_fin'] = self.instance.date_fin.strftime('%Y-%m-%d')
        
        # Filtrer les chambres disponibles si les dates sont fournies dans les données initiales
        if 'data' in kwargs:
            data = kwargs['data']
            date_debut = data.get('date_debut')
            date_fin = data.get('date_fin')
            
            if date_debut and date_fin:
                # Filtrer les chambres disponibles pour ces dates
                from .models import Reservation
                from rooms.models import Room
                
                # Convertir les dates en objets date
                from datetime import datetime
                try:
                    date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
                    date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
                    
                    # Trouver les chambres déjà réservées pour ces dates
                    chambres_occupees = Reservation.objects.filter(
                        date_debut__lt=date_fin_obj,
                        date_fin__gt=date_debut_obj,
                        statut__in=['en_attente', 'confirmee', 'active']
                    ).values_list('chambre_id', flat=True)
                    
                    # Filtrer les chambres disponibles (non occupées, statut disponible et statut de nettoyage inspectée)
                    chambres_disponibles = Room.objects.filter(
                        statut='disponible',
                        cleaning_status='inspectee'
                    ).exclude(
                        id__in=chambres_occupees
                    )
                    
                    # Mettre à jour le queryset du champ chambre
                    self.fields['chambre'].queryset = chambres_disponibles
                    
                except (ValueError, TypeError):
                    # En cas d'erreur de format de date, on garde toutes les chambres
                    pass

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('nom_client', css_class='form-group col-md-6 mb-0'),
                Column('nationalite', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('numero_identite', css_class='form-group col-md-6 mb-0'),
                Column('date_expiration_visa', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('piece_identite_client', css_class='form-group col-md-6 mb-0'),
                Column('date_naissance', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('email_client', css_class='form-group col-md-6 mb-0'),
                Column('telephone_client', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('date_debut', css_class='form-group col-md-6 mb-0'),
                Column('date_fin', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('chambre', css_class='form-group col-md-6 mb-0'),
                Column('statut', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Row(
                Column('mode_paiement', css_class='form-group col-md-6 mb-0'),
                Column('cash', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            'adresse_client'
        )

    def save(self, commit=True):
        # Si on est en mode "création", on crée le client
        if not self.instance.pk:
            email = self.cleaned_data['email_client']
            telephone = self.cleaned_data['telephone_client']
            
            # Si l'email est fourni, on l'utilise comme identifiant
            if email:
                client, created = Client.objects.get_or_create(
                    email=email,
                    defaults={
                        'nom': self.cleaned_data['nom_client'],
                        'telephone': telephone,
                        'adresse': self.cleaned_data['adresse_client'],
                        'piece_identite': self.cleaned_data.get('piece_identite_client')
                    }
                )
            else:
                # Si pas d'email, on crée un nouveau client avec le téléphone comme identifiant
                # On vérifie d'abord si un client existe avec ce téléphone
                client, created = Client.objects.get_or_create(
                    telephone=telephone,
                    defaults={
                        'nom': self.cleaned_data['nom_client'],
                        'email': email,
                        'adresse': self.cleaned_data['adresse_client'],
                        'piece_identite': self.cleaned_data.get('piece_identite_client')
                    }
                )
            
            self.instance.client = client
        else:
            # En mode modification, on met à jour le client existant
            client = self.instance.client
            client.nom = self.cleaned_data['nom_client']
            client.email = self.cleaned_data['email_client']
            client.telephone = self.cleaned_data['telephone_client']
            client.adresse = self.cleaned_data['adresse_client']
            if self.cleaned_data.get('piece_identite_client'):
                client.piece_identite = self.cleaned_data['piece_identite_client']
            client.save()
        
        return super().save(commit)
