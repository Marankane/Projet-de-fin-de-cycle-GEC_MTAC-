from datetime import date
from django.db.models import Count, Q
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.models import Role
from apps.mouvements.models import MouvementCourrier
from apps.organisations.models import Service
from core.permissions import PeutDispatchez, PeutValider, EstAgent
from .models import Courrier, Expediteur, PieceJointe


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

class ExpediteurSerializer(serializers.ModelSerializer):
    class Meta: model = Expediteur; fields = '__all__'

class CourrierListSerializer(serializers.ModelSerializer):
    statut_code=serializers.CharField(source='statut.code',read_only=True)
    statut_label=serializers.CharField(source='statut.libelle',read_only=True)
    statut_couleur=serializers.CharField(source='statut.couleur',read_only=True)
    priorite_code=serializers.CharField(source='priorite.code',read_only=True)
    priorite_label=serializers.CharField(source='priorite.libelle',read_only=True)
    type_label=serializers.CharField(source='type_courrier.libelle',read_only=True)
    sens_label=serializers.CharField(source='get_sens_display',read_only=True)
    service_nom=serializers.CharField(source='service_destinataire.nom',read_only=True)
    expediteur_nom=serializers.CharField(source='expediteur.nom',read_only=True)
    est_en_retard=serializers.BooleanField(read_only=True)
    jours_restants=serializers.IntegerField(read_only=True,allow_null=True)
    nb_pj=serializers.IntegerField(source='nb_pieces_jointes',read_only=True)
    class Meta:
        model=Courrier
        fields=['id','numero','objet','sens','sens_label','date_reception','date_enregistrement','date_echeance','statut_code','statut_label','statut_couleur','priorite_code','priorite_label','type_label','service_nom','expediteur_nom','confidentiel','nb_pj','est_en_retard','jours_restants']

class CourrierWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Courrier
        fields=['sens','type_courrier','priorite','statut','date_reception','date_echeance','objet','observations','expediteur','destinataire','service_destinataire','confidentiel']

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
    qs = Courrier.objects.select_related('statut','priorite','type_courrier','expediteur','service_destinataire')
    # Seuls les agents courriers voient tous les courriers
    if user.role in [Role.AGENT, 'ADMIN']: return qs
    if user.peut_voir_tout: return qs
    if user.role in [Role.CHEF_SERVICE, Role.SECRETAIRE]: return qs.filter(service_destinataire=user.service)
    return qs.filter(Q(service_destinataire=user.service)|Q(agent_responsable=user)|Q(cree_par=user))

class CourrierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, EstAgent]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero','objet','expediteur__nom']
    ordering = ['-date_enregistrement']

    def get_queryset(self):
        qs = _qs(self.request.user)
        p = self.request.query_params
        if p.get('sens'): qs = qs.filter(sens=p['sens'])
        if p.get('statut'): qs = qs.filter(statut__code=p['statut'])
        if p.get('service'): qs = qs.filter(service_destinataire_id=p['service'])
        if p.get('en_retard') == '1': qs = qs.filter(date_echeance__lt=date.today(), statut__est_final=False)
        return qs

    def get_serializer_class(self):
        if self.action in ['create','update','partial_update']: return CourrierWriteSerializer
        return CourrierListSerializer

    def perform_create(self, serializer):
        from apps.parametrage.models import StatutCourrier
        agent_courrier = _agent_courrier_auto(self.request.user)
        if not agent_courrier:
            raise serializers.ValidationError("Aucun agent courrier actif n'est disponible pour recevoir ce courrier.")
        courrier = serializer.save(cree_par=self.request.user, statut=StatutCourrier.objects.get(code='ENR'), agent_responsable=agent_courrier)
        MouvementCourrier.objects.create(courrier=courrier, utilisateur=self.request.user, service=self.request.user.service, action='CREATION', commentaire="Via API", statut_apres='ENR')
        MouvementCourrier.objects.create(courrier=courrier, utilisateur=self.request.user, service=agent_courrier.service, action='AFFECTATION', commentaire=f"Envoyé automatiquement à l'agent courrier {agent_courrier.nom_complet}.")

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PeutDispatchez])
    def dispatcher(self, request, pk=None):
        courrier = self.get_object()
        try:
            svc = Service.objects.get(pk=request.data.get('service_destinataire'))
        except (Service.DoesNotExist, TypeError, ValueError):
            return Response({'detail': 'Service destinataire invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        courrier.service_destinataire = svc
        if request.data.get('agent'):
            from apps.accounts.models import Utilisateur
            try:
                courrier.agent_responsable = Utilisateur.objects.get(pk=request.data['agent'])
            except (Utilisateur.DoesNotExist, TypeError, ValueError):
                return Response({'detail': 'Agent responsable invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        courrier.save(update_fields=['service_destinataire','agent_responsable','modifie_le'])
        try:
            courrier.changer_statut('DIS', request.user, commentaire=request.data.get('commentaire',''))
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CourrierListSerializer(courrier).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PeutValider])
    def valider(self, request, pk=None):
        courrier = self.get_object()
        try: courrier.changer_statut('ACC', request.user, commentaire=request.data.get('commentaire','Validé.'))
        except ValueError as e: return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CourrierListSerializer(courrier).data)

    @action(detail=True, methods=['post'])
    def cloturer(self, request, pk=None):
        courrier = self.get_object()
        try: courrier.changer_statut('CLO', request.user, commentaire=request.data.get('commentaire','Clôturé.'))
        except ValueError as e: return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CourrierListSerializer(courrier).data)

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        qs = _qs(request.user); today = date.today()
        return Response({
            'total': qs.count(),
            'ouverts': qs.filter(statut__est_final=False).count(),
            'en_retard': qs.filter(date_echeance__lt=today, statut__est_final=False).count(),
            'crees_ce_mois': qs.filter(date_enregistrement__year=today.year, date_enregistrement__month=today.month).count(),
            'par_statut': list(qs.values('statut__code','statut__libelle','statut__couleur').annotate(total=Count('id'))),
            'par_sens': list(qs.values('sens').annotate(total=Count('id'))),
            'par_priorite': list(qs.values('priorite__libelle','priorite__couleur').annotate(total=Count('id'))),
        })

    @action(detail=False, methods=['get'])
    def en_retard(self, request):
        qs = _qs(request.user).filter(date_echeance__lt=date.today(), statut__est_final=False)
        return Response(CourrierListSerializer(qs, many=True).data)

class ExpediteurViewSet(viewsets.ModelViewSet):
    queryset = Expediteur.objects.all().order_by('nom')
    serializer_class = ExpediteurSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'email']
