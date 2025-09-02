# ticketing/views.py
from django.shortcuts import render, redirect
from django.views import View

from ticketing.forms import ProgrammeForm, SpectateurCreationForm
from .models import Programme, Reservation, Paiement, Spectateur
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required



# ticketing/views.py (à ajouter)
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Reservation, Paiement

stripe.api_key = settings.STRIPE_SECRET_KEY

def page_paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    # Calculer le montant (exemple simple)
    montant_total = reservation.nombre_billets * reservation.programme.prix_a

    return render(request, 'ticketing/paiement.html', {
        'reservation': reservation,
        'montant_total': montant_total,
        'montant_total_cents': int(montant_total * 100),
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

def create_payment_intent(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    montant_total = reservation.nombre_billets * reservation.programme.prix_a

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(montant_total * 100), # Montant en centimes
            currency='eur',
            metadata={'reservation_id': reservation.id}
        )
        return JsonResponse({'clientSecret': intent.client_secret})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)

def payment_success(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    # Créer l'objet Paiement pour garder une trace
    Paiement.objects.create(
        reservation=reservation,
        montant=reservation.nombre_billets * reservation.programme.prix_a,
        mode_paiement='Google Pay via Stripe',
        # Idéalement, stocker ici l'ID de la transaction Stripe
    )
    return render(request, 'ticketing/payment_success.html')

# Vue pour afficher tous les programmes
def liste_programmes(request):
    programmes = Programme.objects.all().order_by('date')
    return render(request, 'ticketing/liste_programmes.html', {'programmes': programmes})

@login_required
@permission_required('ticketing.add_programme', raise_exception=True)
def creer_programme(request):
    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme = form.save(commit=False)
            # Associer l'agent connecté comme créateur
            programme.agent_createur = request.user.agent
            programme.save()
            return redirect('liste_programmes')
    else:
        form = ProgrammeForm()
    return render(request, 'ticketing/creer_programme.html', {'form': form})

# Vue pour le processus de réservation (Exemple simple)
class ReservationView(LoginRequiredMixin, View):
    def get(self, request, programme_id):
        programme = Programme.objects.get(id=programme_id)
        return render(request, 'ticketing/reservation.html', {'programme': programme})

    def post(self, request, programme_id):
        # Logique pour créer la réservation et préparer le paiement
        programme = Programme.objects.get(id=programme_id)
        spectateur = request.user.spectateur
        nb_billets = int(request.POST.get('nombre_billets'))
        
        # Créer une réservation en attente de paiement
        reservation = Reservation.objects.create(
            spectateur=spectateur,
            programme=programme,
            nombre_billets=nb_billets
        )
        
        # Rediriger vers la page de paiement avec l'ID de la réservation
        return redirect('page_paiement', reservation_id=reservation.id)
    


# ticketing/views.py

@login_required
def historique_reservations(request):
    # S'assurer que l'utilisateur est un spectateur
    try:
        spectateur = request.user.spectateur
        reservations = Reservation.objects.filter(spectateur=spectateur).order_by('-date_reservation')
        return render(request, 'ticketing/historique_reservations.html', {'reservations': reservations})
    except Spectateur.DoesNotExist:
        # Gérer le cas où un gestionnaire ou admin connecté irait sur cette page
        return render(request, 'ticketing/historique_reservations.html', {'reservations': []})