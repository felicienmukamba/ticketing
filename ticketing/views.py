from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from .models import Programme, Reservation, Paiement, CustomUser
from .forms import ProgrammeForm, ReservationForm, PaiementForm, CustomUserCreationForm, CustomUserChangeForm

import stripe
import os
import json

# Assurez-vous d'avoir configuré vos clés Stripe dans settings.py
stripe.api_key = settings.STRIPE_SECRET_KEY

# Vues pour l'authentification et l'enregistrement
# ---

def user_login(request):
    """
    Vue de connexion de l'utilisateur.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, {username} !")
                # Redirection basée sur le rôle
                # Redirection prioritaire vers "next" si fourni (relatif pour sécurité)
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)

                # Redirection basée sur les rôles du CustomUser
                # Utiliser getattr pour éviter AttributeError si l'attribut n'existe pas
                if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
                    # Admin/Staff -> page de gestion des agents (ou tableau de bord admin)
                    return redirect('agent_list')
                if getattr(user, 'is_agent', False):
                    # Agent -> liste des programmes/gestion
                    return redirect('programme_list')
                if getattr(user, 'is_spectateur', False):
                    # Spectateur -> page d'accueil publique
                    return redirect('home')

                # Fallback : utiliser LOGIN_REDIRECT_URL si défini, sinon 'home'
                return redirect(getattr(settings, 'LOGIN_REDIRECT_URL', 'home'))
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    """
    Vue pour déconnecter un utilisateur.
    """
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')

def user_signup(request):
    """
    Vue pour la création d'un compte Spectateur.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_spectateur = True
            user.save()
            messages.success(request, 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# Vues pour les Spectateurs
# ---

def home(request):
    """
    Vue de la page d'accueil, affichant la liste des programmes.
    """
    programmes = Programme.objects.all().order_by('date')
    return render(request, 'ticket_app/home.html', {'programmes': programmes})

@login_required
def reservation_create(request, programme_id):
    """
    Vue pour créer une réservation.
    Accessible uniquement aux utilisateurs connectés.
    """
    programme = get_object_or_404(Programme, pk=programme_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.spectateur = request.user
            reservation.programme = programme
            reservation.save()
            messages.success(request, 'Votre réservation a été créée avec succès.')
            return redirect('reservation_history')
    else:
        form = ReservationForm()
    return render(request, 'ticket_app/reservation_form.html', {'form': form, 'programme': programme})

@login_required
def reservation_history(request):
    """
    Vue pour afficher l'historique des réservations de l'utilisateur.
    """
    reservations = Reservation.objects.filter(spectateur=request.user).order_by('-date_reservation')
    return render(request, 'ticket_app/reservation_history.html', {'reservations': reservations})


# Vues pour les Agents (CRUD pour Programme et Réservation)
# ---

@login_required
@permission_required('app_name.add_programme', raise_exception=True)
def programme_create(request):
    """
    Vue pour créer un nouveau programme (match).
    Accessible uniquement aux agents.
    """
    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme = form.save(commit=False)
            programme.agent = request.user
            programme.save()
            return JsonResponse({'message': 'Le programme a été créé avec succès.', 'status': 'success'})
        return JsonResponse({'message': 'Erreur de formulaire.', 'errors': form.errors, 'status': 'error'})
    # This is the correct way to handle a GET request
    else:
        form = ProgrammeForm()
    return render(request, 'ticket_app/programme_form.html', {'form': form})


@login_required
@permission_required('app_name.change_programme', raise_exception=True)
def programme_update(request, programme_id):
    """
    Vue pour mettre à jour un programme existant.
    Accessible uniquement aux agents.
    """
    programme = get_object_or_404(Programme, pk=programme_id)
    if request.method == 'POST':
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Le programme a été mis à jour avec succès.', 'status': 'success'})
        return JsonResponse({'message': 'Erreur de formulaire.', 'errors': form.errors, 'status': 'error'})
    # Added form instantiation for GET requests
    else:
        form = ProgrammeForm(instance=programme)
    return render(request, 'ticket_app/programme_form.html', {'form': form})

@login_required
@permission_required('app_name.delete_programme', raise_exception=True)
@require_POST
def programme_delete(request, programme_id):
    """
    Vue pour supprimer un programme.
    Accessible uniquement aux agents.
    """
    try:
        programme = get_object_or_404(Programme, pk=programme_id)
        programme.delete()
        return JsonResponse({'message': 'Le programme a été supprimé avec succès.', 'status': 'success'})
    except Exception as e:
        return JsonResponse({'message': f'Erreur lors de la suppression : {e}', 'status': 'error'})

@login_required
@permission_required('app_name.view_reservation', raise_exception=True)
def reservation_management(request):
    """
    Vue pour la gestion des réservations par l'agent.
    """
    reservations = Reservation.objects.all().order_by('-date_reservation')
    return render(request, 'ticket_app/reservation_management.html', {'reservations': reservations})

# Vues pour l'Admin
# ---
@login_required
@permission_required('auth.add_user', raise_exception=True)
def agent_create(request):
    """
    Vue pour créer un compte Agent (accessible par un Admin).
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_agent = True
            user.is_staff = True
            user.save()
            return JsonResponse({'message': 'Le compte de l\'agent a été créé avec succès.', 'status': 'success'})
        return JsonResponse({'message': 'Erreur de formulaire.', 'errors': form.errors, 'status': 'error'})
    # This is the correct way to handle a GET request
    else:
        form = CustomUserCreationForm()
    return render(request, 'ticket_app/agent_form.html', {'form': form})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def agent_list(request):
    """
    Vue pour lister tous les agents.
    """
    agents = CustomUser.objects.filter(is_agent=True)
    return render(request, 'ticket_app/agent_list.html', {'agents': agents})

@login_required
@permission_required('auth.change_user', raise_exception=True)
def agent_update(request, pk):
    """
    Vue pour mettre à jour un agent.
    """
    agent = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'L\'agent a été mis à jour avec succès.', 'status': 'success'})
        return JsonResponse({'message': 'Erreur de formulaire.', 'errors': form.errors, 'status': 'error'})
    # Added form instantiation for GET requests
    else:
        form = CustomUserChangeForm(instance=agent)
    return render(request, 'ticket_app/agent_form.html', {'form': form, 'agent': agent})

@login_required
@permission_required('auth.delete_user', raise_exception=True)
@require_POST
def agent_delete(request, pk):
    """
    Vue pour supprimer un agent.
    """
    try:
        agent = get_object_or_404(CustomUser, pk=pk)
        agent.delete()
        return JsonResponse({'message': 'L\'agent a été supprimé avec succès.', 'status': 'success'})
    except Exception as e:
        return JsonResponse({'message': f'Erreur lors de la suppression : {e}', 'status': 'error'})

def programme_list(request):
    """
    Vue pour lister les programmes (accessible aux agents).
    """
    programmes = Programme.objects.all().order_by('-date')
    return render(request, 'ticket_app/programme_list.html', {'programmes': programmes})

# Vues de paiement
# ---

@login_required
def create_checkout_session(request, reservation_id):
    """
    Vue pour créer une session de paiement Stripe.
    Cette vue remplace paiement_create.
    """
    reservation = get_object_or_404(Reservation, pk=reservation_id, spectateur=request.user)
    programme = reservation.programme
    
    # Calcule le prix total en fonction du type de réservation
    if reservation.type_reservation == 'A':
        prix_unitaire = programme.prix_a
    else:
        prix_unitaire = programme.prix_b

    # Convertit le prix en centimes, car Stripe travaille avec des entiers
    total_amount = int(prix_unitaire * reservation.nombre_billet * 100)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': total_amount,
                        'product_data': {
                            'name': f'Billet pour {programme.nom_equipe1} vs {programme.nom_equipe2}',
                            'description': f'Réservation pour {reservation.nombre_billet} billet(s) en section {reservation.type_reservation}',
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'reservation_id': reservation.id_reservation
            },
            mode='payment',
            success_url=request.build_absolute_uri('/paiement/succes/'),
            cancel_url=request.build_absolute_uri('/paiement/echec/'),
        )
        return redirect(checkout_session.url)
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de la création de la session de paiement: {e}")
        return redirect('reservation_history')

def stripe_success(request):
    """
    Vue affichée après un paiement réussi.
    """
    messages.success(request, "Paiement réussi ! Votre réservation a été confirmée.")
    return render(request, 'ticket_app/paiement_status.html', {'status': 'success'})

def stripe_cancel(request):
    """
    Vue affichée en cas d'annulation du paiement.
    """
    messages.error(request, "Paiement annulé. Vous pouvez réessayer à tout moment.")
    return render(request, 'ticket_app/paiement_status.html', {'status': 'cancel'})

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Vue pour gérer les webhooks de Stripe et confirmer les paiements.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Gérer les événements de paiement
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        reservation_id = session.get('metadata', {}).get('reservation_id')

        if reservation_id:
            try:
                reservation = Reservation.objects.get(pk=int(reservation_id))
                montant_total = session['amount_total'] / 100 # Convertir en dollars
                
                # Créer une nouvelle instance de Paiement
                Paiement.objects.create(
                    reservation=reservation,
                    mode_paiement='Stripe',
                    montant=montant_total
                )
                
                # Optionnel : marquer la réservation comme payée
                # reservation.is_paid = True
                # reservation.save()

            except Reservation.DoesNotExist:
                return HttpResponse(status=404)
        
    return HttpResponse(status=200)

def paiement_list(request):
    """
    Vue pour lister tous les paiements.
    """
    paiements = Paiement.objects.all().order_by('-date_paiement')
    return render(request, 'ticket_app/paiement_list.html', {'paiements': paiements})

@require_POST
def paiement_delete(request, pk):
    """
    Vue pour supprimer un paiement.
    """
    try:
        paiement = get_object_or_404(Paiement, pk=pk)
        paiement.delete()
        return JsonResponse({'message': 'Le paiement a été supprimé avec succès.', 'status': 'success'})
    except Exception as e:
        return JsonResponse({'message': f'Erreur lors de la suppression : {e}', 'status': 'error'})
