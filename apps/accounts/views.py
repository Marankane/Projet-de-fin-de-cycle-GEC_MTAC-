from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from core.permissions import AdminMixin
from .forms import ChangeMDPForm, ConnexionForm, CreationUtilisateurForm, DemandeReinitForm, EditionProfilForm, EditionUtilisateurForm, NouveauMDPForm
from .models import JournalConnexion, TokenReinit, Utilisateur

def _ip(req):
    x = req.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0] if x else req.META.get('REMOTE_ADDR')

def _journal(req, email, resultat, user=None):
    JournalConnexion.objects.create(utilisateur=user, email_tente=email, adresse_ip=_ip(req), resultat=resultat)

class InfoProjetView(View):
    template_name = 'project_info.html'
    def get(self, request):
        return render(request, self.template_name)

class ConnexionView(View):
    template_name = 'accounts/connexion.html'
    def get(self, request):
        if request.user.is_authenticated: return redirect('dashboard:accueil')
        return render(request, self.template_name, {'form': ConnexionForm()})
    def post(self, request):
        form = ConnexionForm(request, data=request.POST)
        email = request.POST.get('email', '')
        if form.is_valid():
            u = form.get_utilisateur()
            login(request, u)
            if not form.cleaned_data.get('se_souvenir'): request.session.set_expiry(0)
            _journal(request, email, 'OK', u)
            messages.success(request, f"Bienvenue, {u.nom_complet} !")
            return redirect(request.GET.get('next', 'dashboard:accueil'))
        _journal(request, email, 'ERR')
        return render(request, self.template_name, {'form': form})

class DeconnexionView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        messages.info(request, "Vous êtes déconnecté(e).")
        return redirect('accounts:connexion')

class ProfilView(LoginRequiredMixin, View):
    template_name = 'accounts/profil.html'
    def get(self, request):
        return render(request, self.template_name, {'form': EditionProfilForm(instance=request.user), 'form_mdp': ChangeMDPForm(request.user)})
    def post(self, request):
        action = request.POST.get('action')
        if action == 'profil':
            form = EditionProfilForm(request.POST, request.FILES, instance=request.user)
            form_mdp = ChangeMDPForm(request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profil mis à jour.")
                return redirect('accounts:profil')
        else:
            form = EditionProfilForm(instance=request.user)
            form_mdp = ChangeMDPForm(request.user, request.POST)
            if form_mdp.is_valid():
                form_mdp.sauvegarder()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Mot de passe mis à jour.")
                return redirect('accounts:profil')
        return render(request, self.template_name, {'form': form, 'form_mdp': form_mdp})

class ListeUtilisateursView(AdminMixin, ListView):
    model = Utilisateur
    template_name = 'accounts/utilisateurs_liste.html'
    context_object_name = 'utilisateurs'
    paginate_by = 20
    def get_queryset(self):
        qs = Utilisateur.objects.select_related('service').order_by('nom')
        q = self.request.GET.get('q','')
        role = self.request.GET.get('role','')
        if q: qs = qs.filter(Q(nom__icontains=q)|Q(prenom__icontains=q)|Q(email__icontains=q))
        if role: qs = qs.filter(role=role)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['roles'] = Utilisateur.role.field.choices
        ctx['q'] = self.request.GET.get('q','')
        ctx['role_filtre'] = self.request.GET.get('role','')
        return ctx

class CreerUtilisateurView(AdminMixin, CreateView):
    model = Utilisateur
    form_class = CreationUtilisateurForm
    template_name = 'accounts/utilisateur_form.html'
    success_url = reverse_lazy('accounts:liste_utilisateurs')
    def form_valid(self, form):
        messages.success(self.request, f"Utilisateur {form.instance.nom_complet} créé.")
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'titre': "Créer un utilisateur"}

class ModifierUtilisateurView(AdminMixin, UpdateView):
    model = Utilisateur
    form_class = EditionUtilisateurForm
    template_name = 'accounts/utilisateur_form.html'
    success_url = reverse_lazy('accounts:liste_utilisateurs')
    def form_valid(self, form):
        messages.success(self.request, "Utilisateur mis à jour.")
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'titre': f"Modifier – {self.object.nom_complet}"}

class ToggleUtilisateurView(AdminMixin, View):
    def post(self, request, pk):
        u = get_object_or_404(Utilisateur, pk=pk)
        if u == request.user:
            messages.error(request, "Impossible de désactiver votre propre compte.")
        else:
            u.is_active = not u.is_active
            u.save(update_fields=['is_active'])
            messages.success(request, f"Compte {'activé' if u.is_active else 'désactivé'}.")
        return redirect('accounts:liste_utilisateurs')

class DemandeReinitView(View):
    def get(self, request): return render(request, 'accounts/reinit_demande.html', {'form': DemandeReinitForm()})
    def post(self, request):
        form = DemandeReinitForm(request.POST)
        if form.is_valid():
            u = form.get_utilisateur()
            if u:
                token = TokenReinit.creer(u)
                lien = request.build_absolute_uri(f"/reinitialisation/{token.token}/")
                from django.core.mail import send_mail
                send_mail("[GED] Réinitialisation de mot de passe",
                    f"Bonjour {u.nom_complet},\n\nLien : {lien}\n\nExpire dans 24h.",
                    'noreply@mintransport.ne', [u.email], fail_silently=True)
            messages.info(request, "Si cet e-mail est enregistré, vous recevrez un lien de réinitialisation.")
            return redirect('accounts:connexion')
        return render(request, 'accounts/reinit_demande.html', {'form': form})

class ReinitMDPView(View):
    def _t(self, t):
        try:
            obj = TokenReinit.objects.select_related('utilisateur').get(token=t)
            return obj if obj.est_valide() else None
        except TokenReinit.DoesNotExist: return None
    def get(self, request, token):
        if not self._t(token):
            messages.error(request, "Lien invalide ou expiré.")
            return redirect('accounts:demande_reinit')
        return render(request, 'accounts/reinit_mdp.html', {'form': NouveauMDPForm(), 'token': token})
    def post(self, request, token):
        obj = self._t(token)
        if not obj:
            messages.error(request, "Lien invalide ou expiré.")
            return redirect('accounts:demande_reinit')
        form = NouveauMDPForm(request.POST)
        if form.is_valid():
            obj.utilisateur.set_password(form.cleaned_data['mdp1'])
            obj.utilisateur.save(update_fields=['password'])
            obj.utilise = True; obj.save(update_fields=['utilise'])
            messages.success(request, "Mot de passe réinitialisé.")
            return redirect('accounts:connexion')
        return render(request, 'accounts/reinit_mdp.html', {'form': form, 'token': token})
