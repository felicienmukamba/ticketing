from django import forms
from .models import CustomUser, Programme, Reservation, Paiement
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# --- Formulaires pour les modèles ---

class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire de création d'utilisateur personnalisé.
    Inclut les champs de CustomUser et utilise le style Bootstrap.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'num_phone', 'ville_spect', 'is_spectateur', 'is_agent'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'num_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'ville_spect': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomUserChangeForm(UserChangeForm):
    """
    Formulaire de modification d'utilisateur pour l'interface d'administration.
    """
    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'num_phone', 'ville_spect', 'is_spectateur', 'is_agent'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'num_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'ville_spect': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProgrammeForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier un programme.
    """
    class Meta:
        model = Programme
        fields = '__all__'
        widgets = {
            'nom_equipe1': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_equipe2': forms.TextInput(attrs={'class': 'form-control'}),
            'stadium': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'division': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_a': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_b': forms.NumberInput(attrs={'class': 'form-control'}),
            # Pour le champ agent, nous utilisons un champ texte pour le datalist
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Créez une liste de noms d'utilisateurs pour le datalist.
        # Note : Le datalist est une fonctionnalité front-end qui n'est pas gérée par le widget standard de Django.
        # Vous devrez créer le <datalist> dans votre template HTML.
        self.fields['agent'].choices = [(user.pk, user.username) for user in CustomUser.objects.filter(is_agent=True)]

class ReservationForm(forms.ModelForm):
    """
    Formulaire pour créer une réservation.
    """
    class Meta:
        model = Reservation
        fields = '__all__'
        widgets = {
            'type_reservation': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_billet': forms.NumberInput(attrs={'class': 'form-control'}),
            # Utilisation de champs texte pour le datalist
            'spectateur': forms.TextInput(attrs={'class': 'form-control', 'list': 'spectateur_list'}),
            'programme': forms.TextInput(attrs={'class': 'form-control', 'list': 'programme_list'}),
        }

class PaiementForm(forms.ModelForm):
    """
    Formulaire pour enregistrer un paiement.
    """
    class Meta:
        model = Paiement
        fields = '__all__'
        widgets = {
            'mode_paiement': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'reservation': forms.TextInput(attrs={'class': 'form-control', 'list': 'reservation_list'}),
        }
