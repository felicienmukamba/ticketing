# ticketing/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Programme, Spectateur

# Formulaire d'inscription personnalisé pour inclure les champs du Spectateur
class SpectateurCreationForm(UserCreationForm):
    ville = forms.CharField(max_length=100, required=True)
    num_phone = forms.CharField(max_length=20, required=True, label="Numéro de téléphone")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Spectateur.objects.create(
                user=user,
                ville=self.cleaned_data.get('ville'),
                num_phone=self.cleaned_data.get('num_phone'),
            )
        return user


# Formulaire pour la création d'un programme par un gestionnaire
class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ['nom_equipe1', 'nom_equipe2', 'stadium', 'date', 'division', 'prix_a', 'prix_b']
        # Utiliser un widget pour faciliter la saisie de la date
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Surcharge pour que le champ date utilise le format HTML5
        self.fields['date'].input_formats = ('%Y-%m-%dT%H:%M',)