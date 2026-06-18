from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import JournalConnexion, TokenReinit, Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    ordering = ('nom',)
    list_display = ('email','nom','prenom','role','service','is_active','date_joined')
    list_filter = ('role','service','is_active')
    search_fields = ('email','nom','prenom')
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Identité', {'fields': ('nom','prenom','telephone','avatar')}),
        ('Rôle & Org', {'fields': ('role','service')}),
        ('Paramètres', {'fields': ('notifier_par_email',)}),
        ('Permissions', {'classes': ('collapse',),'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
        ('Dates', {'fields': ('last_login','date_joined')}),
    )
    add_fieldsets = ((None,{'classes':('wide',),'fields':('email','nom','prenom','role','service','password1','password2')}),)
    readonly_fields = ('date_joined','last_login')

@admin.register(JournalConnexion)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('email_tente','resultat','adresse_ip','date_heure')
    list_filter = ('resultat',)
    readonly_fields = ('utilisateur','email_tente','adresse_ip','resultat','date_heure')
    def has_add_permission(self, r): return False
    def has_change_permission(self, r, o=None): return False
