from django.db import models

COULEURS = [
    ('primary','Bleu'),('success','Vert'),('warning','Orange'),
    ('danger','Rouge'),('secondary','Gris'),('info','Cyan'),('dark','Noir'),
]

class TypeCourrier(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveSmallIntegerField(default=0)
    class Meta:
        verbose_name = 'type de courrier'
        ordering = ['ordre', 'libelle']
    def __str__(self): return self.libelle

class StatutCourrier(models.Model):
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    couleur = models.CharField(max_length=20, choices=COULEURS, default='secondary')
    est_final = models.BooleanField(default=False)
    ordre = models.PositiveSmallIntegerField(default=0)
    class Meta:
        verbose_name = 'statut de courrier'
        ordering = ['ordre']
    def __str__(self): return f"{self.code} – {self.libelle}"

class Priorite(models.Model):
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=100)
    delai_jours = models.PositiveSmallIntegerField(default=15)
    couleur = models.CharField(max_length=20, choices=COULEURS, default='secondary')
    ordre = models.PositiveSmallIntegerField(default=0)
    class Meta:
        verbose_name = 'priorité'
        ordering = ['ordre']
    def __str__(self): return f"{self.libelle} ({self.delai_jours}j)"
