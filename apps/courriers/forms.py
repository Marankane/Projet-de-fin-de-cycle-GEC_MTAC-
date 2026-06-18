from datetime import date
from django import forms
from django.db.models import Count
from apps.accounts.models import Role
from apps.organisations.models import Service
from django.db.models import Q
from apps.parametrage.models import Priorite, StatutCourrier, TypeCourrier
from .models import Courrier, Destinataire, Expediteur, LienCourrier, PieceJointe

_fc=lambda ph='': forms.TextInput(attrs={'class':'form-control','placeholder':ph})
_fa=lambda r=3: forms.Textarea(attrs={'class':'form-control','rows':r})
_fs=lambda: forms.Select(attrs={'class':'form-select'})
_fd=lambda: forms.DateInput(attrs={'class':'form-control','type':'date'},format='%Y-%m-%d')
_fsm=lambda: forms.SelectMultiple(attrs={'class':'form-select select2-multiple'})
_fck=lambda: forms.CheckboxInput(attrs={'class':'form-check-input'})

# Définition des structures pour la logique de classification automatique
DIRECTIONS_APPUI = ['DEP', 'DRFM', 'DRH', 'DS/I', 'DL', 'DAID/RP', 'DNM', 'DMP', 'DSP']
AUTRES_STRUCTURES = ['ANAC', 'ASECNA', 'AANN', 'ANISER', 'CNUT', 'CNTPS', 'CFTTR', 'SOTRUNI', 'NSH', 'NWA']

POUR_CHOICES = [
    ('Suite à donner','Suite à donner'),
    ("M'en parler","M'en parler"),
    ('Y prendre part','Y prendre part'),
    ('Prendre RDV','Prendre RDV'),
    ('Information','Information'),
    ('Élaborer TDR','Élaborer TDR'),
    ('Élaborer Plan d’Action','Élaborer Plan d’Action'),
    ('Préparer Projet de Budget','Préparer Projet de Budget'),
    ('Dispositions à prendre','Dispositions à prendre'),
    ('Attribution','Attribution'),
    ('Préparation projet de réponse','Préparation projet de réponse'),
    ('Large diffusion','Large diffusion'),
    ('Classement','Classement'),
    ('Garder en Instance','Garder en Instance'),
    ('Préparer réunion de partage','Préparer réunion de partage'),
    ('Études et Observations','Études et Observations'),
]

class DisambiguatedModelChoiceField(forms.ModelChoiceField):
    """
    Un ModelChoiceField qui ajoute le type de l'objet à son libellé
    si plusieurs objets ont le même nom dans le queryset.
    """
    def __init__(self, *args, duplicate_names=None, **kwargs):
        self.duplicate_names = duplicate_names if duplicate_names is not None else set()
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if obj.nom in self.duplicate_names:
            return f"{obj.nom} ({obj.get_type_display()})"
        return obj.nom

class ExpéditeurForm(forms.ModelForm):
    class Meta:
        model=Expediteur; fields=['nom','type','adresse','telephone','email','pays']
        widgets={'nom':_fc(),'type':_fs(),'adresse':_fa(2),'telephone':_fc(),'email':forms.EmailInput(attrs={'class':'form-control'}),'pays':_fc('Niger')}

class DestinataireForm(forms.ModelForm):
    class Meta:
        model=Destinataire; fields=['nom','type','adresse','telephone','email']
        widgets={'nom':_fc(),'type':_fs(),'adresse':_fa(2),'telephone':_fc(),'email':forms.EmailInput(attrs={'class':'form-control'})}

class EnregistrementForm(forms.ModelForm):
    class Meta:
        model=Courrier
        fields=['sens','type_courrier','priorite','date_reception','numero_lettre','date_sortie','objet','expediteur','destinataire','service_destinataire','services_original','services_copie','confidentiel','observations']
        labels={
            'date_reception': 'Date de réception',
            'numero_lettre': 'N° de la lettre / Réf.',
            'date_sortie': 'Date de sortie',
            'service_destinataire': 'Direction Responsable',
            'services_original': 'Imputation (Original)',
            'services_copie': 'Imputation (Copie)',
        }
        widgets={
            'sens': forms.HiddenInput(), # Devient automatique
            'type_courrier':_fs(),
            'priorite':_fs(),
            'date_reception':_fd(),
            'numero_lettre':_fc(),
            'date_sortie':_fd(),
            'objet':forms.Textarea(attrs={'class':'form-control','rows':3, 'placeholder': 'Résumé succinct de l\'objet du courrier...'}),
            # 'expediteur':_fs(), # Ces champs seront remplacés dans __init__
            # 'destinataire':_fs(), # Ces champs seront remplacés dans __init__
            'service_destinataire':_fs(),
            'services_original':_fsm(),
            'services_copie':_fsm(),
            'confidentiel':_fck(),
            'observations':_fa(2),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        if 'sens' in self.fields:
            self.fields['sens'].required = False

        # Créer automatiquement les Expediteur de type 'SERVICE' à partir des Services actifs
        # s'ils n'existent pas déjà
        for service in Service.objects.filter(actif=True):
            exp_name = f"{service.code} - {service.nom}"
            Expediteur.objects.get_or_create(
                nom=exp_name,
                defaults={'type': 'SERVICE', 'pays': 'Niger'}
            )
        
        # Afficher uniquement les Expediteurs de type 'SERVICE'
        self.fields['expediteur'] = forms.ModelChoiceField(
            queryset=Expediteur.objects.filter(type='SERVICE').order_by('nom'),
            label="Service / Direction (Expéditeur)",
            widget=_fs(),
            empty_label="Sélectionner un service..."
        )
        self.fields['destinataire'] = forms.ModelChoiceField(
            queryset=Destinataire.objects.order_by('nom').distinct('nom'),
            label="Destinataire",
            widget=_fs(),
            required=False
        )
        self.fields['type_courrier'].queryset=TypeCourrier.objects.filter(actif=True).order_by('ordre')
        self.fields['priorite'].queryset=Priorite.objects.all().order_by('ordre')
        self.fields['service_destinataire'].queryset=Service.objects.filter(actif=True).order_by('nom')
        self.fields['services_original'].queryset=Service.objects.filter(actif=True).order_by('nom')
        self.fields['services_copie'].queryset=Service.objects.filter(actif=True).order_by('nom')
        self.fields['destinataire'].required=False
        self.fields['services_original'].required=False
        self.fields['services_copie'].required=False

        # Set defaults
        if not self.instance.pk:
            try:
                self.fields['type_courrier'].initial = TypeCourrier.objects.get(libelle='Lettre')
            except TypeCourrier.DoesNotExist:
                pass
            try:
                self.fields['priorite'].initial = Priorite.objects.get(libelle='Normal')
            except Priorite.DoesNotExist:
                pass

    def clean(self):
        cd=super().clean()
        exp = cd.get('expediteur')
        dest_serv = cd.get('service_destinataire')
        
        # Logique de détermination automatique du SENS
        if exp and dest_serv:
            def is_interne(name):
                return any(code in name.upper() for code in DIRECTIONS_APPUI)
            def is_externe(name):
                return any(code in name.upper() for code in AUTRES_STRUCTURES)

            exp_is_int = is_interne(exp.nom) or exp.type == 'SERVICE'
            dest_is_int = is_interne(dest_serv.nom)
            
            exp_is_ext = is_externe(exp.nom) or exp.type != 'SERVICE'
            dest_is_ext = is_externe(dest_serv.nom)

            if exp_is_int and dest_is_int:
                cd['sens'] = 'INT'
            elif exp_is_int and dest_is_ext:
                cd['sens'] = 'SOR'
            elif exp_is_ext and dest_is_int:
                cd['sens'] = 'ENT'
            elif exp_is_ext and dest_is_ext:
                raise forms.ValidationError("Action impossible : L'expéditeur et le destinataire ne peuvent pas être tous les deux externes.")
            else:
                cd['sens'] = 'INT' # Par défaut

        # Validations de dates
        recep=cd.get('date_reception')
        if recep and recep>date.today(): self.add_error('date_reception',"La date de réception ne peut pas être dans le futur.")
        date_sortie = cd.get('date_sortie')
        if recep and date_sortie and date_sortie < recep:
            self.add_error('date_sortie', "La date de sortie doit être postérieure ou égale à la date de réception.")
        return cd

    def save(self, commit=True, cree_par=None):
        c=super().save(commit=False)
        from apps.parametrage.models import StatutCourrier
        try:
            c.statut=StatutCourrier.objects.get(code='ENR')
        except StatutCourrier.DoesNotExist as exc:
            raise forms.ValidationError("Le statut initial ENR est absent du paramétrage.") from exc
        if cree_par: c.cree_par=cree_par
        if commit:
            c.save()
            self.save_m2m()
        return c

class PieceJointeForm(forms.ModelForm):
    class Meta:
        model=PieceJointe; fields=['fichier','est_scan']
        widgets={'fichier':forms.ClearableFileInput(attrs={'class':'form-control'}),'est_scan':_fck()}

    def clean_fichier(self):
        f=self.cleaned_data.get('fichier')
        if f:
            if f.size>20*1024*1024: raise forms.ValidationError("Fichier trop volumineux. Maximum : 20 Mo.")
            ext=f.name.rsplit('.',1)[-1].lower() if '.' in f.name else ''
            if ext not in ['pdf','doc','docx','xls','xlsx','jpg','jpeg','png','tiff']:
                raise forms.ValidationError("Extension non autorisée.")
        return f

class DispatchForm(forms.Form):
    destinataire=forms.ModelChoiceField(queryset=Destinataire.objects.all().order_by('nom'),label="Destinataire",widget=forms.RadioSelect(),required=False)
    service_destinataire=forms.ModelChoiceField(queryset=Service.objects.filter(actif=True).order_by('nom'),label="Direction / Service",widget=forms.RadioSelect())
    pour=forms.CharField(label="Pour / Suite à donner", required=False, widget=forms.TextInput(attrs={'class':'form-control','list':'pour-options'}))
    agent=forms.ModelChoiceField(queryset=None,label="Affecter à un agent (optionnel)",required=False,widget=_fs())
    commentaire=forms.CharField(label="Instruction / Commentaire",required=False,widget=_fa(3))
    observations=forms.CharField(label="Observations (réservé SGA/SG/Ministre)",required=False,widget=_fa(3))

    def __init__(self,*args, user=None, courrier=None, **kwargs):
        self.user = user
        self.courrier = courrier
        super().__init__(*args,**kwargs)
        from apps.accounts.models import Utilisateur
        self.fields['agent'].queryset=Utilisateur.objects.filter(role=Role.AGENT,is_active=True).select_related('service').order_by('nom')
        if user and user.role == Role.AGENT:
            self.fields['observations'].widget.attrs['readonly'] = 'readonly'
            self.fields['observations'].help_text = "Réservé au SGA / SG / Ministre"
            
            # Restriction des destinataires pour l'Agent Courrier
            # L'agent ne peut envoyer que au Ministre, SG, SGA ou au destinataire original du courrier
            filter_q = Q(code__in=['SGA', 'SG', 'MIN'], actif=True)
            if courrier and courrier.service_destinataire:
                filter_q |= Q(pk=courrier.service_destinataire.pk)
            
            self.fields['service_destinataire'].queryset = Service.objects.filter(filter_q).order_by('nom')
            if courrier and courrier.destinataire:
                self.fields['destinataire'].queryset = Destinataire.objects.filter(pk=courrier.destinataire.pk)
            else:
                self.fields['destinataire'].queryset = Destinataire.objects.none()

        if not user or user.role == Role.SECRETAIRE:
            self.fields['observations'].widget.attrs['readonly'] = 'readonly'
            self.fields['observations'].help_text = "Réservé au SGA / SG / Ministre"
        if user and user.role in [Role.CHEF_SERVICE, Role.DIRECTEUR] and user.service and user.service.code in ['SGA','SG','MIN','DG']:
            self.fields['observations'].widget.attrs.pop('readonly', None)
            self.fields['observations'].help_text = "Observation autorisée pour votre chaîne"
        if courrier:
            self.fields['destinataire'].initial = courrier.destinataire
            self.fields['service_destinataire'].initial = courrier.service_destinataire
            self.fields['agent'].initial = courrier.agent_responsable
            self.fields['observations'].initial = courrier.observations
            self.fields['pour'].initial = courrier.pour


class InstructionForm(forms.Form):
    instruction=forms.CharField(label="Instruction / Décision",widget=_fa(4))
    nouveau_statut=forms.ModelChoiceField(queryset=StatutCourrier.objects.none(),label="Changer le statut vers",required=False,widget=_fs())

    def __init__(self, courrier, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.courrier = courrier
        self.user = user
        allowed_codes = self._get_allowed_statuts()
        self.fields['nouveau_statut'].queryset = StatutCourrier.objects.filter(code__in=allowed_codes).order_by('ordre')

    def _get_allowed_statuts(self):
        statut = self.courrier.statut.code
        role = self.user.role
        service = self.user.service

        # Define roles
        is_agent = role == 'AGENT'
        is_sga = service and service.code == 'SGA'
        is_sg = service and service.code == 'SG'
        is_ministre = service and service.code in ['MIN', 'DG']

        allowed = []

        if is_agent:
            if statut == 'ENR':
                allowed = ['SGA', 'SG', 'MIN', 'DIS']
            elif statut in ['ACC', 'REJ']:
                allowed = ['CLO', 'RET']
        
        elif is_sga and statut == 'SGA':
            allowed = ['ENR', 'REJ']
            
        elif is_sg and statut == 'SG':
            allowed = ['ENR', 'REJ']
            
        elif is_ministre and statut == 'MIN':
            allowed = ['ACC', 'REJ']

        # Un administrateur peut tout forcer (optionnel)
        if role == 'ADMIN':
            allowed = list(StatutCourrier.objects.values_list('code', flat=True))

        # On s'assure de ne pas proposer le statut actuel
        if statut in allowed:
            allowed.remove(statut)
            
        return list(set(allowed))

class LienForm(forms.ModelForm):
    class Meta:
        model=LienCourrier; fields=['courrier_cible','type_lien','note']
        widgets={'courrier_cible':_fs(),'type_lien':_fs(),'note':_fa(2)}
    def __init__(self,courrier_source,*args,**kwargs):
        self.courrier_source=courrier_source; super().__init__(*args,**kwargs)
        self.fields['courrier_cible'].queryset=Courrier.objects.exclude(pk=courrier_source.pk).order_by('-date_enregistrement')

class RechercheForm(forms.Form):
    q=forms.CharField(label="Recherche",required=False,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Numéro, objet, expéditeur…'}))
    sens=forms.ChoiceField(label="Sens",required=False,choices=[('','Tous')]+Courrier.SENS,widget=_fs())
    type_courrier=forms.ModelChoiceField(label="Type",required=False,queryset=TypeCourrier.objects.filter(actif=True),empty_label="Tous les types",widget=_fs())
    statut=forms.ModelChoiceField(label="Statut",required=False,queryset=StatutCourrier.objects.all().order_by('ordre'),empty_label="Tous les statuts",widget=_fs())
    priorite=forms.ModelChoiceField(label="Priorité",required=False,queryset=Priorite.objects.all().order_by('ordre'),empty_label="Toutes",widget=_fs())
    service=forms.ModelChoiceField(label="Service",required=False,queryset=Service.objects.filter(actif=True),empty_label="Tous les services",widget=_fs())
    date_debut=forms.DateField(label="Du",required=False,widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    date_fin=forms.DateField(label="Au",required=False,widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    en_retard=forms.BooleanField(label="En retard uniquement",required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))


class FichierTransmissionForm(forms.ModelForm):
    class Meta:
        model = Courrier
        fields = [
            'pour', 'services_original', 'services_copie',
            'date_entree_sga', 'date_sortie_sga', 'avis_sga_positif', 'avis_sga',
            'date_entree_sg', 'date_sortie_sg', 'avis_sg_positif', 'avis_sg',
            'date_entree_min', 'date_sortie_min', 'decision_min_positif', 'decision_min',
        ]
        labels = {
            'pour': 'Pour / suite à donner',
            'services_original': 'Destinataires / directions en original',
            'services_copie': 'Directions en copie',
            'avis_sga_positif': 'Avis favorable SGA',
            'avis_sg_positif': 'Avis favorable SG',
            'decision_min_positif': 'Décision favorable Ministre',
        }
        widgets = {
            'pour': forms.TextInput(attrs={'class': 'form-control', 'list': 'pour-options'}),
            'services_original': _fsm(),
            'services_copie': _fsm(),
            'date_entree_sga': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_sortie_sga': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_entree_sg': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_sortie_sg': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_entree_min': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_sortie_min': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'avis_sga_positif': _fck(),
            'avis_sg_positif': _fck(),
            'decision_min_positif': _fck(),
            'avis_sga': _fa(2),
            'avis_sg': _fa(2),
            'decision_min': _fa(2),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Service.objects.filter(actif=True).order_by('nom')
        self.fields['services_original'].queryset = qs
        self.fields['services_copie'].queryset = qs