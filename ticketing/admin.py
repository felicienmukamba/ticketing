from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Programme, Reservation, Paiement
from .forms import CustomUserCreationForm, CustomUserChangeForm

# --- Personnalisation de l'interface d'administration ---

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuration de l'interface d'administration pour le modèle CustomUser.
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_spectateur', 'is_agent')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_spectateur', 'is_agent')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('num_phone', 'ville_spect', 'is_spectateur', 'is_agent')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('num_phone', 'ville_spect', 'is_spectateur', 'is_agent')}),
    )
    search_fields = ('username', 'email', 'num_phone')
    ordering = ('username',)

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    """
    Configuration pour le modèle Programme.
    """
    list_display = ('nom_equipe1', 'nom_equipe2', 'date', 'stadium', 'agent')
    list_filter = ('date', 'division')
    search_fields = ('nom_equipe1', 'nom_equipe2', 'stadium')
    date_hierarchy = 'date'
    ordering = ('-date',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Configuration pour le modèle Reservation.
    """
    list_display = ('spectateur', 'programme', 'nombre_billet', 'date_reservation')
    list_filter = ('date_reservation', 'type_reservation')
    search_fields = ('spectateur__username', 'programme__nom_equipe1', 'programme__nom_equipe2')
    ordering = ('-date_reservation',)

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    """
    Configuration pour le modèle Paiement.
    """
    list_display = ('id_paiement', 'reservation', 'montant', 'mode_paiement', 'date_paiement')
    list_filter = ('mode_paiement', 'date_paiement')
    search_fields = ('reservation__id_reservation', 'mode_paiement')
    ordering = ('-date_paiement',)
