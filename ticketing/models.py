# ticketing/models.py
from django.db import models
from django.contrib.auth.models import User

# On étend le modèle User de Django pour ajouter des rôles
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Ajout d'un champ pour distinguer les rôles (Admin, Gestionnaire)
    SERVICE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('GESTION', 'Gestionnaire'),
    ]
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    # Les autres champs comme nomAgent, prenomAgent sont déjà dans le modèle User
    # (first_name, last_name)

    def __str__(self):
        return self.user.username

class Spectateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ville = models.CharField(max_length=100)
    num_phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Programme(models.Model):
    nom_equipe1 = models.CharField(max_length=100)
    nom_equipe2 = models.CharField(max_length=100)
    stadium = models.CharField(max_length=100)
    date = models.DateTimeField()
    division = models.CharField(max_length=50)
    prix_a = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix pour la catégorie A")
    prix_b = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix pour la catégorie B")
    # Relation : Un programme est ajouté par un Agent (Gestionnaire)
    agent_createur = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, related_name='programmes_crees')

    def __str__(self):
        return f"{self.nom_equipe1} vs {self.nom_equipe2} le {self.date.strftime('%d/%m/%Y')}"

class Reservation(models.Model):
    spectateur = models.ForeignKey(Spectateur, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    date_reservation = models.DateTimeField(auto_now_add=True)
    nombre_billets = models.PositiveIntegerField()
    # Le type de réservation peut être déduit du prix choisi lors du paiement

    def __str__(self):
        return f"Réservation de {self.spectateur.user.username} pour {self.programme}"

class Paiement(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=50, default='Google Pay')
    payment_token = models.CharField(max_length=255, help_text="ID de transaction retourné par le processeur de paiement")
    
    def __str__(self):
        return f"Paiement de {self.montant} pour {self.reservation}"