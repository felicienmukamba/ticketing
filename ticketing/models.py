from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class CustomUser(AbstractUser):
    """
    Un modèle d'utilisateur personnalisé qui sert de base pour tous les rôles.
    Il remplace les modèles 'Agent' et 'Spectateur' pour une gestion simplifiée.
    """
    # Champ spécifique au Spectateur
    num_phone = models.CharField(max_length=15, blank=True, null=True)
    ville_spect = models.CharField(max_length=100, blank=True, null=True)

    # Nous utiliserons les permissions et les groupes de Django pour différencier
    # les rôles, mais ces champs sont utiles pour un accès rapide.
    # 'is_staff' de AbstractUser peut être utilisé pour les agents.
    is_spectateur = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)
    
    # Renommer les champs 'related_name' pour éviter les conflits
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.username

class Programme(models.Model):
    """
    Cette classe représente un match ou un programme d'événement.
    """
    id_programme = models.AutoField(primary_key=True)
    nom_equipe1 = models.CharField(max_length=100)
    nom_equipe2 = models.CharField(max_length=100)
    stadium = models.CharField(max_length=200)
    date = models.DateField()
    version = models.CharField(max_length=50)
    division = models.CharField(max_length=50)
    prix_a = models.DecimalField(max_digits=10, decimal_places=2)
    prix_b = models.DecimalField(max_digits=10, decimal_places=2)
    
    # La relation est maintenant vers le modèle CustomUser
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='programmes_crees'
    )

    def __str__(self):
        return f"{self.nom_equipe1} vs {self.nom_equipe2}"

class Reservation(models.Model):
    """
    Cette classe représente une réservation de billet.
    """
    id_reservation = models.AutoField(primary_key=True)
    date_reservation = models.DateField(auto_now_add=True)
    type_reservation = models.CharField(max_length=50)
    nombre_billet = models.IntegerField()
    
    # La relation est maintenant vers le modèle CustomUser
    spectateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    programme = models.ForeignKey(
        'Programme', 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )

    def __str__(self):
        return f"Réservation {self.id_reservation} par {self.spectateur.username}"

class Paiement(models.Model):
    """
    Cette classe représente un paiement effectué pour une réservation.
    """
    id_paiement = models.AutoField(primary_key=True)
    mode_paiement = models.CharField(max_length=50)
    date_paiement = models.DateField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Relation vers Réservation
    reservation = models.OneToOneField(
        'Reservation', 
        on_delete=models.CASCADE, 
        related_name='paiement'
    )
    
    def __str__(self):
        return f"Paiement {self.id_paiement} pour réservation {self.reservation.id_reservation}"
