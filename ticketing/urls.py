# ticketing/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Racine du site (redirige vers le dashboard si connecté)
    path('', views.index, name='index'),

    # ===== DASHBOARD =====
    path('dashboard/', views.DashboardHomeView.as_view(), name='dashboard_home'),

    # --- URLs Spectateur ---
    path('dashboard/programmes/', views.ProgrammeListView.as_view(), name='dashboard_programme_list'),
    path('dashboard/reservations/', views.ReservationHistoryView.as_view(), name='dashboard_reservation_history'),
    path('dashboard/reserver/<int:programme_id>/', views.ReservationCreateView.as_view(), name='reservation_create'),

    # Le processus de paiement reste le même
    path('paiement/<int:reservation_id>/', views.page_paiement, name='page_paiement'),
    path('create-payment-intent/<int:reservation_id>/', views.create_payment_intent, name='create_payment_intent'),
    path('payment-success/<int:reservation_id>/', views.payment_success, name='payment_success'),

    # --- URLs Gestionnaire (CRUD) ---
    # CRUD pour les Programmes
    path('dashboard/manager/programmes/', views.ProgrammeManagerListView.as_view(), name='dashboard_manager_programmes'),
    path('dashboard/manager/programmes/creer/', views.ProgrammeCreateView.as_view(), name='dashboard_manager_programme_create'),
    path('dashboard/manager/programmes/modifier/<int:pk>/', views.ProgrammeUpdateView.as_view(), name='dashboard_manager_programme_update'),
    path('dashboard/manager/programmes/supprimer/<int:pk>/', views.ProgrammeDeleteView.as_view(), name='dashboard_manager_programme_delete'),

    # CRUD pour les Réservations
    path('dashboard/manager/reservations/', views.ReservationManagerListView.as_view(), name='dashboard_manager_reservations'),
    path('dashboard/manager/reservations/modifier/<int:pk>/', views.ReservationUpdateView.as_view(), name='dashboard_manager_reservation_update'),

    # Historique des billets vendus
    path('dashboard/manager/billets/', views.TicketHistoryView.as_view(), name='dashboard_manager_tickets'),
]