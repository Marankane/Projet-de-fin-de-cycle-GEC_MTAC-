from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'type', 'titre', 'lue', 'cree_le']
    list_filter = ['type', 'lue', 'cree_le']
    search_fields = ['utilisateur__nom_complet', 'titre', 'message']