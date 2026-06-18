from datetime import date, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView
from apps.accounts.models import Role, Utilisateur
from apps.courriers.models import Courrier
from apps.mouvements.models import MouvementCourrier
from apps.organisations.models import Service

class AccueilView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        m = {'AGENT':'dashboard/agent.html','SECRETAIRE':'dashboard/secretaire.html','CHEF_SERVICE':'dashboard/chef_service.html','DIRECTEUR':'dashboard/directeur.html','ADMIN':'dashboard/admin.html'}
        return [m.get(self.request.user.role, 'dashboard/base_db.html')]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user; today = date.today()
        ctx['today'] = today
        r = user.role
        if r == Role.AGENT: ctx.update(self._agent(user, today))
        elif r == Role.SECRETAIRE: ctx.update(self._secretaire(user, today))
        elif r == Role.CHEF_SERVICE: ctx.update(self._chef(user, today))
        elif r == Role.DIRECTEUR: ctx.update(self._directeur(today))
        elif r == Role.ADMINISTRATEUR: ctx.update(self._admin(today))
        return ctx

    def _agent(self, user, today):
        qs = Courrier.objects.filter(Q(agent_responsable=user)|Q(cree_par=user)).select_related('statut','priorite')
        return {
            'total': qs.count(), 'en_cours': qs.filter(statut__code='DIS').count(),
            'en_retard': qs.filter(date_echeance__lt=today, statut__est_final=False).count(),
            'clotures_semaine': qs.filter(date_cloture__gte=today-timedelta(days=7)).count(),
            'courriers_en_cours': qs.filter(statut__est_final=False).order_by('date_echeance')[:10],
            'courriers_urgents': qs.filter(priorite__code__in=['URG','TRES_URG'], statut__est_final=False).order_by('date_echeance')[:5],
            'activite': MouvementCourrier.objects.filter(utilisateur=user).select_related('courrier').order_by('-date_mouvement')[:8],
        }

    def _secretaire(self, user, today):
        qs = Courrier.objects.filter(service_destinataire=user.service).select_related('statut','priorite','agent_responsable')
        return {
            'total_service': qs.count(),
            'non_affectes': qs.filter(agent_responsable__isnull=True, statut__est_final=False).count(),
            'en_retard': qs.filter(date_echeance__lt=today, statut__est_final=False).count(),
            'traites_mois': qs.filter(date_cloture__year=today.year, date_cloture__month=today.month).count(),
            'courriers_non_affectes': qs.filter(agent_responsable__isnull=True, statut__est_final=False).order_by('date_reception')[:10],
            'courriers_retard': qs.filter(date_echeance__lt=today, statut__est_final=False).order_by('date_echeance')[:5],
            'agents': Utilisateur.objects.filter(service=user.service, role=Role.AGENT, is_active=True).annotate(nb=Count('courriers_en_charge', filter=Q(courriers_en_charge__statut__est_final=False))).order_by('nom'),
        }

    def _chef(self, user, today):
        qs = Courrier.objects.filter(service_destinataire=user.service).select_related('statut','priorite','agent_responsable')
        return {
            'total': qs.count(),
            'a_instruire': qs.filter(statut__code='DIS').count(),
            'a_valider': qs.filter(statut__code='ACC').count(),
            'en_retard': qs.filter(date_echeance__lt=today, statut__est_final=False).count(),
            'par_statut': list(qs.values('statut__code','statut__libelle','statut__couleur').annotate(total=Count('id')).order_by('statut__ordre')),
            'a_traiter': qs.filter(statut__est_final=False).order_by('date_echeance','-priorite__ordre')[:10],
            'en_retard_list': qs.filter(date_echeance__lt=today, statut__est_final=False).order_by('date_echeance')[:5],
            'agents': Utilisateur.objects.filter(service=user.service, role=Role.AGENT, is_active=True).annotate(nb=Count('courriers_en_charge', filter=Q(courriers_en_charge__statut__est_final=False))),
        }

    def _directeur(self, today):
        tous = Courrier.objects.select_related('statut','priorite','service_destinataire')
        return {
            'total': tous.count(),
            'ouverts': tous.filter(statut__est_final=False).count(),
            'en_retard': tous.filter(date_echeance__lt=today, statut__est_final=False).count(),
            'clotures_mois': tous.filter(date_cloture__year=today.year, date_cloture__month=today.month).count(),
            'recus_mois': tous.filter(date_enregistrement__year=today.year, date_enregistrement__month=today.month).count(),
            'par_service': list(tous.filter(statut__est_final=False).values('service_destinataire__nom','service_destinataire__code').annotate(total=Count('id'), retard=Count('id', filter=Q(date_echeance__lt=today))).order_by('-total')[:10]),
            'par_sens': list(tous.values('sens').annotate(total=Count('id'))),
            'importants': tous.filter(priorite__code__in=['URG','TRES_URG','CONF'], statut__est_final=False).order_by('date_echeance')[:10],
            'activite': MouvementCourrier.objects.select_related('courrier','utilisateur','service').order_by('-date_mouvement')[:15],
        }

    def _admin(self, today):
        ctx = self._directeur(today)
        ctx.update({
            'nb_users': Utilisateur.objects.filter(is_active=True).count(),
            'nb_services': Service.objects.filter(actif=True).count(),
            'par_role': list(Utilisateur.objects.filter(is_active=True).values('role').annotate(total=Count('id'))),
            'derniers_users': Utilisateur.objects.order_by('-date_joined')[:5],
        })
        return ctx
