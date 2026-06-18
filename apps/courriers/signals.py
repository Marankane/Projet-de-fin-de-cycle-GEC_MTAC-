from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Courrier
from apps.notifications.models import Notification
from apps.notifications.tasks import envoyer_notifications_courrier

@receiver(post_save, sender=Courrier)
def notifier_nouveau_courrier(sender, instance, created, **kwargs):
    """
    Signal envoyé après la création/modification d'un courrier.
    Notifie tous les utilisateurs concernés (agent responsable + services).
    """
    if created:
        # Collecter tous les utilisateurs à notifier
        utilisateurs_a_notifier = set()
        
        # 1. Agent responsable
        if instance.agent_responsable:
            utilisateurs_a_notifier.add(instance.agent_responsable.id)
        
        # 2. Utilisateurs du service destinataire principal
        if instance.service_destinataire:
            utilisateurs_service = instance.service_destinataire.utilisateurs.filter(
                is_active=True, 
                notifier_par_email=True
            ).values_list('id', flat=True)
            utilisateurs_a_notifier.update(utilisateurs_service)
        
        # 3. Utilisateurs des services en original
        for service in instance.services_original.all():
            utilisateurs_service = service.utilisateurs.filter(
                is_active=True, 
                notifier_par_email=True
            ).values_list('id', flat=True)
            utilisateurs_a_notifier.update(utilisateurs_service)
        
        # 4. Utilisateurs des services en copie
        for service in instance.services_copie.all():
            utilisateurs_service = service.utilisateurs.filter(
                is_active=True, 
                notifier_par_email=True
            ).values_list('id', flat=True)
            utilisateurs_a_notifier.update(utilisateurs_service)
        
        # Créer les notifications et envoyer les emails
        if utilisateurs_a_notifier:
            # Lancer la tâche asynchrone Celery
            envoyer_notifications_courrier.delay(instance.id, list(utilisateurs_a_notifier))