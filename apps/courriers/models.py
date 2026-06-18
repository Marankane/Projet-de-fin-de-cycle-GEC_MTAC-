import os
from datetime import date
from django.core.exceptions import ValidationError
from django.db import models, transaction

def _chemin_pj(instance, filename):
    today = date.today()
    return f"courriers/{today.year}/{today.month:02d}/{instance.courrier.numero}/{filename}"

def _generer_numero(sens):
    prefix = {'ENT':'ENT','SOR':'SOR','INT':'INT'}.get(sens,'CRR')
    annee = date.today().year
    n = Courrier.objects.filter(sens=sens, date_enregistrement__year=annee).count() + 1
    return f"{prefix}-{annee}-{n:05d}"

class Expediteur(models.Model):
    TYPES = [('PERSONNE','Personne physique'),('SOCIETE','Société'),('INSTITUTION','Institution'),('AMBASSADE','Ambassade'),('SERVICE','Service interne')]
    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPES, default='INSTITUTION')
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    pays = models.CharField(max_length=100, default='Niger')
    class Meta: ordering = ['nom']
    def __str__(self): return f"{self.nom} ({self.get_type_display()})"
    def __str__(self): return self.nom
    def __str__(self): return self.nom

class Destinataire(models.Model):
    TYPES = [('PERSONNE','Personne'),('SERVICE','Service'),('INSTITUTION','Institution'),('SOCIETE','Société')]
    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPES, default='SERVICE')
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    class Meta: ordering = ['nom']
    def __str__(self): return self.nom

class Courrier(models.Model):
    SENS = [('ENT','Entrant'),('SOR','Sortant'),('INT','Interne')]
    IMP = [('ORIGINAL','Original'),('COPIE','Copie')]

    numero = models.CharField(max_length=30, unique=True, editable=False)
    date_enregistrement = models.DateField(auto_now_add=True)
    date_reception = models.DateField()
    numero_lettre = models.CharField(max_length=100, blank=True)
    date_sortie = models.DateField(null=True, blank=True)
    objet = models.TextField()
    sens = models.CharField(max_length=3, choices=SENS)
    imp = models.CharField(max_length=10, choices=IMP, default='ORIGINAL')
    confidentiel = models.BooleanField(default=False)
    observations = models.TextField(blank=True)
    pour = models.CharField(max_length=150, blank=True)

    # Champs pour le Fichier de Transmission / Workflow
    date_entree_sga = models.DateTimeField(null=True, blank=True)
    date_sortie_sga = models.DateTimeField(null=True, blank=True)
    avis_sga = models.TextField(blank=True, verbose_name="Observations SGA")
    avis_sga_positif = models.BooleanField(null=True, blank=True)
    date_entree_sg = models.DateTimeField(null=True, blank=True)
    date_sortie_sg = models.DateTimeField(null=True, blank=True)
    avis_sg = models.TextField(blank=True, verbose_name="Observations SG")
    avis_sg_positif = models.BooleanField(null=True, blank=True)
    date_entree_min = models.DateTimeField(null=True, blank=True)
    date_sortie_min = models.DateTimeField(null=True, blank=True)
    decision_min = models.TextField(blank=True, verbose_name="Décision du Ministre")
    decision_min_positif = models.BooleanField(null=True, blank=True)

    type_courrier = models.ForeignKey('parametrage.TypeCourrier', on_delete=models.PROTECT, related_name='courriers')
    priorite = models.ForeignKey('parametrage.Priorite', on_delete=models.PROTECT, related_name='courriers')
    statut = models.ForeignKey('parametrage.StatutCourrier', on_delete=models.PROTECT, related_name='courriers')

    expediteur = models.ForeignKey(Expediteur, on_delete=models.PROTECT, related_name='courriers_expedies')
    destinataire = models.ForeignKey(Destinataire, on_delete=models.SET_NULL, null=True, blank=True)
    service_destinataire = models.ForeignKey('organisations.Service', on_delete=models.PROTECT, related_name='courriers_recus')
    services_original = models.ManyToManyField('organisations.Service', blank=True, related_name='courriers_original')
    services_copie = models.ManyToManyField('organisations.Service', blank=True, related_name='courriers_copie')
    agent_responsable = models.ForeignKey('accounts.Utilisateur', on_delete=models.SET_NULL, null=True, blank=True, related_name='courriers_en_charge')
    cree_par = models.ForeignKey('accounts.Utilisateur', on_delete=models.PROTECT, related_name='courriers_crees')

    date_echeance = models.DateField(null=True, blank=True)
    date_cloture = models.DateField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_enregistrement', '-cree_le']
        indexes = [models.Index(fields=['numero']), models.Index(fields=['sens','statut']), models.Index(fields=['service_destinataire','statut']), models.Index(fields=['date_echeance'])]

    def __str__(self): return f"{self.numero} – {self.objet[:60]}"

    def save(self, *args, **kwargs):
        if not self.numero: self.numero = _generer_numero(self.sens)
        super().save(*args, **kwargs)

    @property
    def est_en_retard(self):
        return bool(self.date_echeance and not self.statut.est_final and date.today() > self.date_echeance)

    @property
    def jours_restants(self):
        if self.date_echeance and not self.statut.est_final:
            return (self.date_echeance - date.today()).days
        return None

    @property
    def nb_pieces_jointes(self): return self.pieces_jointes.count()

    @transaction.atomic
    def changer_statut(self, code, utilisateur, commentaire=''):
        if self.statut.est_final: raise ValueError("Ce courrier est clôturé. Aucune modification possible.")
        from apps.parametrage.models import StatutCourrier
        from apps.mouvements.models import MouvementCourrier
        ancien = self.statut.code
        try:
            self.statut = StatutCourrier.objects.get(code=code)
        except StatutCourrier.DoesNotExist as exc:
            raise ValueError(f"Le statut « {code} » n'existe pas dans le paramétrage.") from exc
        if self.statut.est_final: self.date_cloture = date.today()
        self.save(update_fields=['statut','date_cloture','modifie_le'])
        MouvementCourrier.objects.create(
            courrier=self, utilisateur=utilisateur, service=utilisateur.service,
            action='AUTRE', commentaire=commentaire, statut_avant=ancien, statut_apres=code,
        )

    @transaction.atomic
    def affecter_agent(self, agent, par, commentaire=''):
        from apps.mouvements.models import MouvementCourrier
        self.agent_responsable = agent
        self.save(update_fields=['agent_responsable','modifie_le'])
        MouvementCourrier.objects.create(
            courrier=self, utilisateur=par, service=par.service,
            action='AFFECTATION', commentaire=commentaire or f"Affecté à {agent.nom_complet}",
        )

class PieceJointe(models.Model):
    courrier = models.ForeignKey(Courrier, on_delete=models.CASCADE, related_name='pieces_jointes')
    fichier = models.FileField(upload_to=_chemin_pj)
    nom_fichier = models.CharField(max_length=255)
    type_mime = models.CharField(max_length=100, blank=True)
    taille_ko = models.FloatField(default=0)
    est_scan = models.BooleanField(default=False)
    uploade_par = models.ForeignKey('accounts.Utilisateur', on_delete=models.SET_NULL, null=True)
    uploade_le = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-uploade_le']
    def __str__(self): return self.nom_fichier
    def save(self, *args, **kwargs):
        if self.fichier and not self.nom_fichier: self.nom_fichier = os.path.basename(self.fichier.name)
        if self.fichier: self.taille_ko = round(self.fichier.size / 1024, 1)
        super().save(*args, **kwargs)
    @property
    def extension(self): return os.path.splitext(self.nom_fichier)[1].lower().lstrip('.')
    @property
    def icone(self):
        return {'pdf':'bi-file-earmark-pdf-fill','doc':'bi-file-earmark-word-fill','docx':'bi-file-earmark-word-fill','xls':'bi-file-earmark-excel-fill','xlsx':'bi-file-earmark-excel-fill','jpg':'bi-file-earmark-image-fill','jpeg':'bi-file-earmark-image-fill','png':'bi-file-earmark-image-fill'}.get(self.extension,'bi-file-earmark-fill')

class LienCourrier(models.Model):
    TYPES = [('REPONSE_A','Réponse à'),('RELANCE','Relance de'),('ANNULATION','Annulation de'),('SUITE_A','Suite à'),('REFERENCE','Référence à')]
    courrier_source = models.ForeignKey(Courrier, on_delete=models.CASCADE, related_name='liens_source')
    courrier_cible = models.ForeignKey(Courrier, on_delete=models.CASCADE, related_name='liens_cible')
    type_lien = models.CharField(max_length=20, choices=TYPES)
    note = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey('accounts.Utilisateur', on_delete=models.SET_NULL, null=True)
    class Meta: unique_together = [('courrier_source','courrier_cible','type_lien')]
    def clean(self):
        if self.courrier_source_id == self.courrier_cible_id:
            raise ValidationError("Un courrier ne peut pas être lié à lui-même.")
    def __str__(self): return f"{self.courrier_source.numero} [{self.get_type_lien_display()}] {self.courrier_cible.numero}"
