from django.db import models

class MouvementCourrier(models.Model):
    ACTIONS = [
        ('CREATION','Enregistrement'),('SCAN','Scan document'),
        ('DISPATCH','Dispatch service'),('AFFECTATION','Affectation agent'),
        ('INSTRUCTION','Instruction chef'),('CONSULTATION','Consultation'),
        ('COMMENTAIRE','Commentaire'),('VALIDATION','Validation'),
        ('CLOTURE','Clôture'),('PJ_AJOUT','PJ ajoutée'),
        ('PJ_SUPPR','PJ supprimée'),('LIEN_CREE','Lien créé'),('AUTRE','Autre'),
    ]
    courrier = models.ForeignKey('courriers.Courrier', on_delete=models.CASCADE, related_name='mouvements')
    utilisateur = models.ForeignKey('accounts.Utilisateur', on_delete=models.PROTECT, related_name='mouvements')
    service = models.ForeignKey('organisations.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='mouvements')
    action = models.CharField(max_length=50, choices=ACTIONS, default='AUTRE')
    commentaire = models.TextField(blank=True)
    statut_avant = models.CharField(max_length=20, blank=True)
    statut_apres = models.CharField(max_length=20, blank=True)
    date_mouvement = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_mouvement']
        indexes = [models.Index(fields=['courrier','date_mouvement']), models.Index(fields=['utilisateur','date_mouvement'])]

    def __str__(self): return f"{self.courrier.numero} – {self.get_action_display()} – {self.date_mouvement:%d/%m/%Y %H:%M}"

    def save(self, *args, **kwargs):
        if self.pk: raise PermissionError("Les mouvements sont immuables.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs): raise PermissionError("Les mouvements ne peuvent pas être supprimés.")
