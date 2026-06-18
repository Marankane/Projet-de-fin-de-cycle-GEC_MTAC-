from django.contrib import admin
from .models import MouvementCourrier
@admin.register(MouvementCourrier)
class MouvAdmin(admin.ModelAdmin):
    list_display = ('courrier','action','utilisateur','date_mouvement')
    list_filter = ('action',)
    readonly_fields = ('courrier','utilisateur','service','action','commentaire','statut_avant','statut_apres','date_mouvement')
    def has_add_permission(self, r): return False
    def has_change_permission(self, r, o=None): return False
    def has_delete_permission(self, r, o=None): return False
