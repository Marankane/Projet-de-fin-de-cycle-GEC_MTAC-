import secrets
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

class Role(models.TextChoices):
    AGENT = 'AGENT', 'Agent Courrier'
    SECRETAIRE = 'SECRETAIRE', 'Secrétaire'
    CHEF_SERVICE = 'CHEF_SERVICE', 'Chef de Service'
    DIRECTEUR = 'DIRECTEUR', 'Directeur Général'
    ADMINISTRATEUR = 'ADMIN', 'Administrateur'

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email: raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        extra.setdefault('role', Role.AGENT)
        extra.setdefault('is_active', True)
        u = self.model(email=email, **extra)
        u.set_password(password)
        u.save(using=self._db)
        return u
    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('role', Role.ADMINISTRATEUR)
        return self.create_user(email, password, **extra)

class Utilisateur(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AGENT)
    service = models.ForeignKey('organisations.Service', null=True, blank=True,
                                on_delete=models.SET_NULL, related_name='utilisateurs')
    telephone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    notifier_par_email = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']
    objects = UtilisateurManager()

    class Meta:
        verbose_name = 'utilisateur'
        ordering = ['nom', 'prenom']

    def __str__(self): return f"{self.prenom} {self.nom} ({self.get_role_display()})"

    @property
    def nom_complet(self): return f"{self.prenom} {self.nom}"
    @property
    def initiales(self): return f"{self.prenom[:1]}{self.nom[:1]}".upper()
    @property
    def est_agent(self): return self.role == Role.AGENT
    @property
    def est_secretaire(self): return self.role == Role.SECRETAIRE
    @property
    def est_chef_service(self): return self.role == Role.CHEF_SERVICE
    @property
    def est_directeur(self): return self.role == Role.DIRECTEUR
    @property
    def est_admin(self): return self.role == Role.ADMINISTRATEUR
    @property
    def peut_dispatcher(self): return self.role in [Role.AGENT, Role.SECRETAIRE, Role.ADMINISTRATEUR]
    @property
    def peut_valider(self): return self.role in [Role.CHEF_SERVICE, Role.ADMINISTRATEUR]
    @property
    def peut_voir_tout(self): return self.role in [Role.DIRECTEUR, Role.ADMINISTRATEUR]

class JournalConnexion(models.Model):
    RESULTAT = [('OK','Succès'),('ERR','Échec'),('BLQ','Bloqué')]
    utilisateur = models.ForeignKey(Utilisateur, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='journaux')
    email_tente = models.EmailField()
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    resultat = models.CharField(max_length=3, choices=RESULTAT)
    date_heure = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-date_heure']
    def __str__(self): return f"{self.email_tente} – {self.resultat}"

class TokenReinit(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=64, unique=True)
    expire_le = models.DateTimeField()
    utilise = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    @classmethod
    def creer(cls, utilisateur, heures=24):
        cls.objects.filter(utilisateur=utilisateur, utilise=False).delete()
        return cls.objects.create(
            utilisateur=utilisateur,
            token=secrets.token_urlsafe(48),
            expire_le=timezone.now() + timedelta(hours=heures),
        )
    def est_valide(self): return not self.utilise and timezone.now() < self.expire_le
