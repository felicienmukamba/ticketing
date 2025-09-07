from django.urls import path
from . import views

urlpatterns = [
    # URLs pour l'authentification
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='signup'),

    # URLs pour les spectateurs
    path('', views.home, name='home'),
    path('programmes/<int:programme_id>/reserver/', views.reservation_create, name='reservation_create'),
    path('reservations/historique/', views.reservation_history, name='reservation_history'),

    # URLs pour les agents (CRUD Programme)
    path('programmes/', views.programme_list, name='programme_list'),
    path('programmes/creer/', views.programme_create, name='programme_create'),
    path('programmes/modifier/<int:programme_id>/', views.programme_update, name='programme_update'),
    path('programmes/supprimer/<int:programme_id>/', views.programme_delete, name='programme_delete'),

    # URLs pour la gestion des réservations par l'agent
    path('reservations/gestion/', views.reservation_management, name='reservation_management'),

    # URLs pour la gestion des utilisateurs (Admin)
    path('agents/', views.agent_list, name='agent_list'),
    path('agents/creer/', views.agent_create, name='agent_create'),
    path('agents/modifier/<int:pk>/', views.agent_update, name='agent_update'),
    path('agents/supprimer/<int:pk>/', views.agent_delete, name='agent_delete'),
    
    # URLs pour la gestion des paiements
    # path('paiements/creer/', views.paiement_create, name='paiement_create'),
    path('paiements/', views.paiement_list, name='paiement_list'),
    path('paiements/supprimer/<int:pk>/', views.paiement_delete, name='paiement_delete'),


    path('paiement/<int:reservation_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('paiement/succes/', views.stripe_success, name='stripe_success'),
    path('paiement/echec/', views.stripe_cancel, name='stripe_cancel'),
    path('paiement/webhook/', views.stripe_webhook, name='stripe_webhook'),
]