# ticketing/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URLs pour les spectateurs
    path('', views.liste_programmes, name='liste_programmes'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('reservation/<int:programme_id>/', views.ReservationView.as_view(), name='reservation'),
    path('historique/', views.historique_reservations, name='historique_reservations'),
    
    # URLs pour le processus de paiement
    path('paiement/<int:reservation_id>/', views.page_paiement, name='page_paiement'),
    path('create-payment-intent/<int:reservation_id>/', views.create_payment_intent, name='create_payment_intent'),
    path('payment-success/<int:reservation_id>/', views.payment_success, name='payment_success'),

    # URLs pour les gestionnaires (protégées)
    path('programme/creer/', views.creer_programme, name='creer_programme'),
]