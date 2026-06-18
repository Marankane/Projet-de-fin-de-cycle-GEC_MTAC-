from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from apps.accounts.models import Role
from apps.mouvements.models import MouvementCourrier
from apps.parametrage.models import Priorite
from core.permissions import AgentMixin, ChefMixin, DispatchMixin, ValidationMixin
from .forms import DispatchForm, EnregistrementForm, FichierTransmissionForm, InstructionForm, LienForm, PieceJointeForm, RechercheForm, ExpéditeurForm, DestinataireForm
from .models import Courrier, LienCourrier, PieceJointe


def _agent_courrier_auto(createur):
    from apps.accounts.models import Utilisateur

    if createur.role == Role.AGENT and createur.is_active:
        return createur

    return (
        Utilisateur.objects
        .filter(role=Role.AGENT, is_active=True)
        .annotate(nb_ouverts=Count('courriers_en_charge', filter=Q(courriers_en_charge__statut__est_final=False)))
        .order_by('nb_ouverts', 'nom', 'prenom')
        .first()
    )

def _acces_autorise(user):
    """Vérifie si l'utilisateur a accès complet (même aux courriers confidentiels)."""
    if not user.is_authenticated: 
        return False
    # Agent courrier, SGA, SG, Ministre peuvent voir tous les courriers y compris les confidentiels
    if user.role == Role.AGENT: 
        return True
    service_code = getattr(user.service, 'code', '')
    return service_code in ['SGA', 'SG', 'MIN', 'CABINET']

def _qs(user):
    qs = Courrier.objects.select_related('statut','priorite','type_courrier','expediteur','service_destinataire','agent_responsable','cree_par').prefetch_related('pieces_jointes')
    # L'Agent Courrier, SGA, SG, Ministre voient tout le flux y compris les courriers confidentiels
    if user.peut_voir_tout or _acces_autorise(user): 
        return qs
    
    if user.role in [Role.CHEF_SERVICE, Role.SECRETAIRE]: 
        return qs.filter(service_destinataire=user.service)
    return qs.filter(Q(service_destinataire=user.service)|Q(agent_responsable=user)|Q(cree_par=user))

def _acces(user, courrier):
    # Accès total pour la direction et l'agent courrier (outrepasse le flag confidentiel)
    if user.peut_voir_tout or _acces_autorise(user): 
        return True
    
    if courrier.confidentiel: 
        return False
    if user.role in [Role.CHEF_SERVICE, Role.SECRETAIRE]: 
        return courrier.service_destinataire == user.service
    return courrier.service_destinataire == user.service or courrier.agent_responsable == user or courrier.cree_par == user

def _peut_fichier_transmission(user):
    # Seul l'agent courrier peut gérer le fichier de transmission
    return user.est_admin or user.role == Role.AGENT

class ListeCourrierView(AgentMixin, ListView):
    template_name = 'courriers/liste.html'
    context_object_name = 'courriers'
    paginate_by = 25

    def get_queryset(self):
        # Seuls les agents courriers voient tous les courriers
        qs = Courrier.objects.select_related('statut','priorite','type_courrier','expediteur','service_destinataire','agent_responsable','cree_par').prefetch_related('pieces_jointes')
        f = RechercheForm(self.request.GET)
        if f.is_valid():
            d = f.cleaned_data
            if d.get('q'): qs = qs.filter(Q(numero__icontains=d['q'])|Q(objet__icontains=d['q'])|Q(expediteur__nom__icontains=d['q']))
            if d.get('sens'): qs = qs.filter(sens=d['sens'])
            if d.get('type_courrier'): qs = qs.filter(type_courrier=d['type_courrier'])
            if d.get('statut'): qs = qs.filter(statut=d['statut'])
            if d.get('priorite'): qs = qs.filter(priorite=d['priorite'])
            if d.get('service'): qs = qs.filter(service_destinataire=d['service'])
            if d.get('date_debut'): qs = qs.filter(date_reception__gte=d['date_debut'])
            if d.get('date_fin'): qs = qs.filter(date_reception__lte=d['date_fin'])
            if d.get('en_retard'): qs = qs.filter(date_echeance__lt=date.today(), statut__est_final=False)
        return qs.order_by('-date_enregistrement')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_recherche'] = RechercheForm(self.request.GET)
        ctx['total'] = self.get_queryset().count()
        return ctx

class EnregistrementView(AgentMixin, View):
    template_name = 'courriers/enregistrement.html'
    def _ctx(self, form=None, form_pj=None):
        return {'form': form or EnregistrementForm(), 'form_pj': form_pj or PieceJointeForm(), 'priorites_delais': {str(p.pk): p.delai_jours for p in Priorite.objects.all()}}
    def get(self, request): return render(request, self.template_name, self._ctx())
    def post(self, request):
        form = EnregistrementForm(request.POST)
        form_pj = PieceJointeForm(request.POST, request.FILES)
        if form.is_valid():
            agent_courrier = _agent_courrier_auto(request.user)
            if not agent_courrier:
                form.add_error(None, "Aucun agent courrier actif n'est disponible pour recevoir ce courrier.")
                return render(request, self.template_name, self._ctx(form, form_pj))

            courrier = form.save(cree_par=request.user)
            courrier.agent_responsable = agent_courrier
            courrier.save(update_fields=['agent_responsable','modifie_le'])
            MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=request.user.service, action='CREATION', commentaire="Enregistrement du courrier", statut_apres='ENR')
            MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=agent_courrier.service, action='AFFECTATION', commentaire=f"Envoyé automatiquement à l'agent courrier {agent_courrier.nom_complet}.")
            if form_pj.is_valid() and request.FILES.get('fichier'):
                pj = form_pj.save(commit=False)
                pj.courrier = courrier; pj.uploade_par = request.user
                pj.nom_fichier = request.FILES['fichier'].name; pj.type_mime = request.FILES['fichier'].content_type
                pj.save()
                MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=request.user.service, action='PJ_AJOUT', commentaire=f"Fichier : {pj.nom_fichier}")
            messages.success(request, f"Courrier {courrier.numero} enregistré et envoyé à l'agent courrier {agent_courrier.nom_complet}.")
            return redirect('courriers:detail', pk=courrier.pk)
        return render(request, self.template_name, self._ctx(form, form_pj))

class DetailCourrierView(AgentMixin, View):
    def get(self, request, pk):
        # Seuls les agents courriers peuvent ouvrir les courriers
        courrier = get_object_or_404(Courrier.objects.select_related('statut','priorite','type_courrier','expediteur','destinataire','service_destinataire','cree_par','agent_responsable').prefetch_related('pieces_jointes','mouvements__utilisateur'), pk=pk)
        ctx = {
            'courrier': courrier,
            'mouvements': courrier.mouvements.select_related('utilisateur','service').order_by('-date_mouvement'),
            'form_pj': PieceJointeForm(), 'form_lien': LienForm(courrier),
            'liens_source': courrier.liens_source.select_related('courrier_cible').all(),
            'liens_cible': courrier.liens_cible.select_related('courrier_source').all(),
            'peut_dispatcher': request.user.peut_dispatcher, 'peut_valider': request.user.peut_valider,
            'peut_fichier_transmission': _peut_fichier_transmission(request.user),
            'est_chef': request.user.est_chef_service, 'est_admin': request.user.est_admin,
            'peut_voir_complet': _acces_autorise(request.user),  # Agent, SGA, SG, Ministre voient tout y compris confidentiel
        }
        return render(request, 'courriers/detail.html', ctx)

class ModifierCourrierView(AgentMixin, View):
    def get(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        if courrier.statut.est_final: messages.error(request, "Impossible de modifier un courrier clôturé."); return redirect('courriers:detail', pk=pk)
        return render(request, 'courriers/modifier.html', {'form': EnregistrementForm(instance=courrier), 'courrier': courrier})
    def post(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        if courrier.statut.est_final: messages.error(request, "Impossible de modifier un courrier clôturé."); return redirect('courriers:detail', pk=pk)
        form = EnregistrementForm(request.POST, instance=courrier)
        if form.is_valid():
            form.save()
            MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=request.user.service, action='AUTRE', commentaire="Modification de la fiche courrier.")
            messages.success(request, "Courrier mis à jour."); return redirect('courriers:detail', pk=pk)
        return render(request, 'courriers/modifier.html', {'form': form, 'courrier': courrier})


class FichierTransmissionView(AgentMixin, View):
    template_name = 'courriers/fichier_transmission.html'

    def _courrier(self, pk):
        return get_object_or_404(
            Courrier.objects.select_related(
                'statut', 'priorite', 'type_courrier', 'expediteur',
                'destinataire', 'service_destinataire', 'cree_par', 'agent_responsable',
            ).prefetch_related('services_original', 'services_copie'),
            pk=pk,
        )

    def get(self, request, pk):
        # Seuls les agents courriers peuvent gérer le fichier de transmission
        courrier = self._courrier(pk)
        return render(request, self.template_name, {
            'courrier': courrier,
            'form': FichierTransmissionForm(instance=courrier),
        })

    def post(self, request, pk):
        # Seuls les agents courriers peuvent gérer le fichier de transmission
        courrier = self._courrier(pk)
        form = FichierTransmissionForm(request.POST, instance=courrier)
        if form.is_valid():
            form.save()
            MouvementCourrier.objects.create(
                courrier=courrier,
                utilisateur=request.user,
                service=request.user.service,
                action='COMMENTAIRE',
                commentaire="Fichier de transmission mis à jour.",
            )
            messages.success(request, "Fichier de transmission mis à jour.")
            return redirect('courriers:fichier_transmission', pk=courrier.pk)
        return render(request, self.template_name, {'courrier': courrier, 'form': form})

class AjouterPJView(AgentMixin, View):
    def post(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        form = PieceJointeForm(request.POST, request.FILES)
        if form.is_valid():
            pj = form.save(commit=False); pj.courrier = courrier; pj.uploade_par = request.user
            pj.nom_fichier = request.FILES['fichier'].name; pj.type_mime = request.FILES['fichier'].content_type; pj.save()
            MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=request.user.service, action='PJ_AJOUT', commentaire=f"Fichier : {pj.nom_fichier}")
            messages.success(request, f"Pièce jointe « {pj.nom_fichier} » ajoutée.")
        else: messages.error(request, "Fichier invalide ou trop volumineux.")
        return redirect('courriers:detail', pk=pk)

class SupprimerPJView(AgentMixin, View):
    def post(self, request, pk, pj_pk):
        pj = get_object_or_404(PieceJointe, pk=pj_pk, courrier_id=pk)
        nom = pj.nom_fichier; pj.fichier.delete(save=False); pj.delete()
        MouvementCourrier.objects.create(courrier_id=pk, utilisateur=request.user, service=request.user.service, action='PJ_SUPPR', commentaire=f"PJ supprimée : {nom}")
        messages.success(request, f"Pièce jointe « {nom} » supprimée.")
        return redirect('courriers:detail', pk=pk)

class DispatchView(DispatchMixin, View):
    def get(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        return render(request, 'courriers/dispatch.html', {'courrier': courrier, 'form': DispatchForm(user=request.user, courrier=courrier)})
    def post(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        form = DispatchForm(request.POST, user=request.user, courrier=courrier)
        if form.is_valid():
            d = form.cleaned_data
            courrier.destinataire = d.get('destinataire')
            courrier.service_destinataire = d['service_destinataire']
            courrier.pour = d.get('pour','')
            if d.get('agent'): courrier.agent_responsable = d['agent']
            if request.user.role in [Role.CHEF_SERVICE, Role.DIRECTEUR] and request.user.service and request.user.service.code in ['SGA','SG','MIN','DG']:
                courrier.observations = d.get('observations','')
            courrier.save(update_fields=['destinataire','service_destinataire','agent_responsable','pour','observations','modifie_le'])
            try:
                courrier.changer_statut('DIS', request.user, commentaire=d.get('commentaire') or f"Dispatché vers {d['service_destinataire'].nom}")
            except ValueError as exc:
                messages.warning(request, str(exc))
            MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=d['service_destinataire'], action='DISPATCH', commentaire=d.get('commentaire',''))
            messages.success(request, f"Courrier dispatché vers {d['service_destinataire'].nom}.")
            return redirect('courriers:detail', pk=pk)
        return render(request, 'courriers/dispatch.html', {'courrier': courrier, 'form': form})

class BulkDispatchView(DispatchMixin, View):
    def get(self, request):
        ids = request.GET.get('ids', '').split(',')
        courriers = Courrier.objects.filter(pk__in=ids).select_related('statut','priorite','type_courrier','expediteur','service_destinataire')
        if not courriers: messages.error(request, "Aucun courrier sélectionné."); return redirect('courriers:liste')
        return render(request, 'courriers/bulk_dispatch.html', {'courriers': courriers, 'form': DispatchForm(user=request.user)})
    def post(self, request):
        ids = request.POST.getlist('courrier_ids')
        courriers = Courrier.objects.filter(pk__in=ids)
        form = DispatchForm(request.POST, user=request.user)
        if form.is_valid():
            d = form.cleaned_data
            count = 0
            for courrier in courriers:
                courrier.service_destinataire = d['service_destinataire']
                courrier.pour = d.get('pour','')
                if d.get('agent'): courrier.agent_responsable = d['agent']
                if request.user.role in [Role.CHEF_SERVICE, Role.DIRECTEUR] and request.user.service and request.user.service.code in ['SGA','SG','MIN','DG']:
                    courrier.observations = d.get('observations','')
                courrier.save(update_fields=['service_destinataire','agent_responsable','pour','observations','modifie_le'])
                try:
                    courrier.changer_statut('DIS', request.user, commentaire=d.get('commentaire') or f"Dispatché vers {d['service_destinataire'].nom}")
                except ValueError as exc:
                    messages.warning(request, f"{courrier.numero}: {exc}")
                MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=d['service_destinataire'], action='DISPATCH', commentaire=d.get('commentaire',''))
                count += 1
            messages.success(request, f"{count} courrier(s) dispatché(s) vers {d['service_destinataire'].nom}.")
            return redirect('courriers:liste')
        return render(request, 'courriers/bulk_dispatch.html', {'courriers': courriers, 'form': form})

class InstructionView(ChefMixin, View):
    def get(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        return render(request, 'courriers/instruction.html', {'courrier': courrier, 'form': InstructionForm(courrier, request.user)})
    def post(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        form = InstructionForm(courrier, request.user, request.POST)
        if form.is_valid():
            d = form.cleaned_data; avant = courrier.statut.code
            if d.get('nouveau_statut'): courrier.statut = d['nouveau_statut']; courrier.save(update_fields=['statut','modifie_le'])
            MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=request.user.service, action='INSTRUCTION', commentaire=d['instruction'], statut_avant=avant, statut_apres=d['nouveau_statut'].code if d.get('nouveau_statut') else avant)
            messages.success(request, "Instruction enregistrée."); return redirect('courriers:detail', pk=pk)
        return render(request, 'courriers/instruction.html', {'courrier': courrier, 'form': form})

class ValiderView(ValidationMixin, View):
    def post(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        try: courrier.changer_statut('ACC', request.user, commentaire=request.POST.get('commentaire','Réponse validée.')); messages.success(request, f"Courrier {courrier.numero} validé.")
        except ValueError as e: messages.error(request, str(e))
        return redirect('courriers:detail', pk=pk)

class CloturerView(LoginRequiredMixin, View):
    def post(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        if not (request.user.peut_valider or request.user == courrier.agent_responsable): raise PermissionDenied
        try: courrier.changer_statut('CLO', request.user, commentaire=request.POST.get('commentaire','Clôture du dossier.')); messages.success(request, f"Courrier {courrier.numero} clôturé.")
        except ValueError as e: messages.error(request, str(e))
        return redirect('courriers:detail', pk=pk)

class AjouterLienView(LoginRequiredMixin, View):
    def post(self, request, pk):
        courrier = get_object_or_404(Courrier, pk=pk)
        form = LienForm(courrier, request.POST)
        if form.is_valid():
            lien = form.save(commit=False); lien.courrier_source = courrier; lien.cree_par = request.user; lien.save()
            MouvementCourrier.objects.create(courrier=courrier, utilisateur=request.user, service=request.user.service, action='LIEN_CREE', commentaire=f"[{lien.get_type_lien_display()}] → {lien.courrier_cible.numero}")
            messages.success(request, "Lien créé.")
        else: messages.error(request, "Impossible de créer ce lien.")
        return redirect('courriers:detail', pk=pk)

class ExpéditeurCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = ExpéditeurForm(request.POST)
        if form.is_valid(): exp = form.save(); messages.success(request, f"Expéditeur « {exp.nom} » créé.")
        else: messages.error(request, "Données expéditeur invalides.")
        return redirect(request.META.get('HTTP_REFERER','courriers:enregistrement'))

class DestinataireCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = DestinataireForm(request.POST)
        if form.is_valid(): d = form.save(); messages.success(request, f"Destinataire « {d.nom} » créé.")
        else: messages.error(request, "Données destinataire invalides.")
        return redirect(request.META.get('HTTP_REFERER','courriers:enregistrement'))

class RegistreEnregistrementView(LoginRequiredMixin, ListView):
    """Registre d'enregistrement officiel des courriers de l'année en cours."""
    model = Courrier
    template_name = 'courriers/registre.html'
    context_object_name = 'courriers'
    paginate_by = 100

    def get_queryset(self):
        return _qs(self.request.user).filter(
            date_enregistrement__year=date.today().year
        ).order_by('numero')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = f"Registre Annuel - {date.today().year}"
        return ctx
    