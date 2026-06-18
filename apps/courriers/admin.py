from django.contrib import admin
from .models import Courrier, Destinataire, Expediteur, LienCourrier, PieceJointe
@admin.register(Courrier)
class CourrierAdmin(admin.ModelAdmin):
    list_display = ('numero','objet','sens','statut','priorite','service_destinataire','date_reception','est_en_retard')
    list_filter = ('sens','statut','priorite','service_destinataire')
    search_fields = ('numero','objet')
    readonly_fields = ('numero','date_enregistrement','cree_le','modifie_le')
    date_hierarchy = 'date_reception'
admin.site.register(Expediteur); admin.site.register(Destinataire)
admin.site.register(LienCourrier); admin.site.register(PieceJointe)
