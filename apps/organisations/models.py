from django.db import models

class Service(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'service'
        verbose_name_plural = 'services'
        ordering = ['nom']

    def __str__(self):
        return f"{self.code} – {self.nom}"

    @property
    def chef(self):
        return self.utilisateurs.filter(role='CHEF_SERVICE', is_active=True).first()
