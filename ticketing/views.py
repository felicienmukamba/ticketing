# ticketing/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from .models import Programme, Reservation, Paiement, Spectateur
from .forms import SpectateurCreationForm, ProgrammeForm, ReservationManagerForm

# ... vues inscription, paiement, etc. déjà créées ...

def index(request):
    """ Redirige vers le dashboard si l'utilisateur est connecté, sinon vers la page de connexion. """
    if request.user.is_authenticated:
        return redirect('dashboard_home')
    return redirect('login')

# ========================
# VUES GÉNÉRIQUES DU DASHBOARD
# ========================

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard_base.html'

# ========================
# VUES DU SPECTATEUR
# ========================

class ProgrammeListView(LoginRequiredMixin, ListView):
    model = Programme
    template_name = 'dashboard/spectateur/programme_list.html'
    context_object_name = 'programmes'
    queryset = Programme.objects.order_by('date')

class ReservationHistoryView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'dashboard/spectateur/reservation_history.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        # Ne retourne que les réservations de l'utilisateur connecté
        return Reservation.objects.filter(spectateur=self.request.user.spectateur).order_by('-date_reservation')

# ========================
# VUES DU GESTIONNAIRE
# ========================

class ProgrammeManagerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Programme
    template_name = 'dashboard/manager/programme_list.html'
    context_object_name = 'programmes'
    permission_required = 'ticketing.view_programme'

class ProgrammeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Programme
    form_class = ProgrammeForm
    template_name = 'dashboard/manager/programme_form.html'
    success_url = reverse_lazy('dashboard_manager_programmes')
    permission_required = 'ticketing.add_programme'

    def form_valid(self, form):
        form.instance.agent_createur = self.request.user.agent
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = "Créer"
        return context

class ProgrammeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Programme
    form_class = ProgrammeForm
    template_name = 'dashboard/manager/programme_form.html'
    success_url = reverse_lazy('dashboard_manager_programmes')
    permission_required = 'ticketing.change_programme'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = "Modifier"
        return context

class ProgrammeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Programme
    template_name = 'dashboard/manager/programme_confirm_delete.html'
    success_url = reverse_lazy('dashboard_manager_programmes')
    permission_required = 'ticketing.delete_programme'


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    fields = ['nombre_billets']
    template_name = 'dashboard/spectateur/reservation_form.html'

    def form_valid(self, form):
        # Associer le programme et le spectateur à la réservation
        form.instance.programme = get_object_or_404(Programme, pk=self.kwargs['programme_id'])
        form.instance.spectateur = self.request.user.spectateur
        # Sauvegarder la réservation
        self.object = form.save()
        # Rediriger vers la page de paiement avec l'ID de la nouvelle réservation
        return redirect('page_paiement', reservation_id=self.object.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programme'] = get_object_or_404(Programme, pk=self.kwargs['programme_id'])
        return context
    
class ReservationManagerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Reservation
    template_name = 'dashboard/manager/reservation_list.html'
    context_object_name = 'reservations'
    permission_required = 'ticketing.view_reservation'

class ReservationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationManagerForm
    template_name = 'dashboard/manager/reservation_form.html'
    success_url = reverse_lazy('dashboard_manager_reservations')
    permission_required = 'ticketing.change_reservation'

class TicketHistoryView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Paiement
    template_name = 'dashboard/manager/ticket_history.html'
    context_object_name = 'paiements'
    permission_required = 'ticketing.view_paiement'