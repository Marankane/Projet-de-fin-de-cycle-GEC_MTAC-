from django.contrib import admin
from .models import Priorite, StatutCourrier, TypeCourrier

@admin.register(TypeCourrier)
class TypeCourrierAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'actif', 'ordre')
    list_editable = ('actif', 'ordre')

@admin.register(StatutCourrier)
class StatutAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'couleur', 'est_final', 'ordre')
    list_editable = ('ordre',)

@admin.register(Priorite)
class PrioriteAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'delai_jours', 'couleur', 'ordre')
    list_editable = ('ordre',)
