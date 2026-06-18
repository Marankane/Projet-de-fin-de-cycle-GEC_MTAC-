from celery import shared_task
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from apps.accounts.models import Utilisateur
from apps.courriers.models import Courrier
from .models import Notification

@shared_task
def envoyer_notifications_courrier(courrier_id, utilisateurs_ids):
    """
    Tâche asynchrone Celery pour envoyer les notifications et emails
    à tous les utilisateurs concernés par un nouveau courrier.
    """
    try:
        courrier = Courrier.objects.get(id=courrier_id)
        utilisateurs = Utilisateur.objects.filter(
            id__in=utilisateurs_ids,
            is_active=True,
            notifier_par_email=True
        )
        
        emails_to_send = []
        
        for utilisateur in utilisateurs:
            # Créer la notification en BD
            Notification.objects.get_or_create(
                utilisateur=utilisateur,
                courrier=courrier,
                type='COURRIER_ASSIGNE',
                defaults={
                    'titre': f"Nouveau courrier : {courrier.numero}",
                    'message': f"Un nouveau courrier vous concerne : {courrier.objet}",
                    'lien': f"/courriers/{courrier.id}/",
                }
            )
            
            # Préparer l'email
            if utilisateur.email:
                context = {
                    'courrier': courrier,
                    'utilisateur': utilisateur,
                    'agent': utilisateur,  # Pour compatibilité template
                }
                
                message_txt = render_to_string('emails/nouveau_courrier.txt', context)
                message_html = render_to_string('emails/nouveau_courrier.html', context)
                
                subject = f"🔔 Nouveau courrier : {courrier.numero}"
                
                emails_to_send.append((
                    subject,
                    message_txt,
                    settings.DEFAULT_FROM_EMAIL,
                    [utilisateur.email],
                    message_html,
                ))
        
        # Envoyer tous les emails en une seule requête
        if emails_to_send:
            send_mass_mail(
                [(e[0], e[1], e[2], e[3]) for e in emails_to_send],
                fail_silently=False
            )
            
            # Bonus : Envoyer aussi les HTML
            for subject, message_txt, from_email, recipient_list, html_message in emails_to_send:
                from django.core.mail import EmailMultiAlternatives
                msg = EmailMultiAlternatives(
                    subject,
                    message_txt,
                    from_email,
                    recipient_list
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send(fail_silently=False)
        
        return f"✅ Notifications envoyées à {utilisateurs.count()} utilisateur(s)"
        
    except Courrier.DoesNotExist:
        return f"❌ Courrier {courrier_id} non trouvé"
    except Exception as e:
        return f"❌ Erreur lors de l'envoi des notifications : {str(e)}"


@shared_task
def envoyer_rappel_courriers_echus():
    """
    Tâche asynchrone Celery pour envoyer des rappels
    sur les courriers échus (deadline dépassée).
    """
    from datetime import date
    from django.db.models import Q
    
    # Récupérer tous les courriers échus non clôturés
    courriers_echus = Courrier.objects.filter(
        date_echeance__lt=date.today(),
        statut__est_final=False
    )
    
    for courrier in courriers_echus:
        # Notifier l'agent responsable
        if courrier.agent_responsable and courrier.agent_responsable.notifier_par_email:
            # Créer notification
            Notification.objects.get_or_create(
                utilisateur=courrier.agent_responsable,
                courrier=courrier,
                type='COURRIER_ECHU',
                defaults={
                    'titre': f"Courrier échu : {courrier.numero}",
                    'message': f"Le courrier {courrier.numero} a dépassé sa date limite",
                    'lien': f"/courriers/{courrier.id}/",
                }
            )
            
            # Envoyer email
            context = {
                'courrier': courrier,
                'utilisateur': courrier.agent_responsable,
                'jours_retard': (date.today() - courrier.date_echeance).days,
            }
            
            subject = f"⚠️ COURRIER ÉCHU : {courrier.numero}"
            message_txt = render_to_string('emails/courrier_echu.txt', context)
            message_html = render_to_string('emails/courrier_echu.html', context)
            
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(
                subject,
                message_txt,
                settings.DEFAULT_FROM_EMAIL,
                [courrier.agent_responsable.email]
            )
            msg.attach_alternative(message_html, "text/html")
            msg.send(fail_silently=True)
    
    return f"✅ {courriers_echus.count()} rappel(s) envoyé(s)"
