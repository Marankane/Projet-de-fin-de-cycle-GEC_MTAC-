from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from apps.courriers.models import Courrier
from apps.notifications.tasks import envoyer_notifications_courrier, envoyer_rappel_courriers_echus
from apps.accounts.models import Utilisateur

class Command(BaseCommand):
    help = 'Tester l\'envoi de notifications pour les courriers'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['nouveau', 'echu', 'list'],
            help='Action à effectuer: nouveau (tester nouveau courrier), echu (tester rappel échu), list (lister les courriers)'
        )
        parser.add_argument(
            '--courrier-id',
            type=int,
            help='ID du courrier à traiter (pour action "nouveau")'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Envoyer de manière asynchrone via Celery'
        )

    def handle(self, *args, **options):
        action = options['action']
        is_async = options.get('async', False)

        if action == 'list':
            self.lister_courriers()
        elif action == 'nouveau':
            self.tester_nouveau_courrier(options.get('courrier_id'), is_async)
        elif action == 'echu':
            self.tester_rappel_echu(is_async)

    def lister_courriers(self):
        """Liste tous les courriers"""
        courriers = Courrier.objects.all().order_by('-cree_le')[:10]
        
        self.stdout.write(self.style.SUCCESS('\n📋 Derniers courriers :\n'))
        
        for c in courriers:
            print(f"  ID: {c.id} | {c.numero} | {c.objet[:50]}")
            print(f"     Agent: {c.agent_responsable}")
            print(f"     Service: {c.service_destinataire}\n")

    def tester_nouveau_courrier(self, courrier_id, is_async):
        """Tester l'envoi de notification pour un nouveau courrier"""
        
        if not courrier_id:
            # Prendre le dernier courrier
            courrier = Courrier.objects.order_by('-cree_le').first()
            if not courrier:
                self.stdout.write(self.style.ERROR('❌ Aucun courrier trouvé'))
                return
        else:
            try:
                courrier = Courrier.objects.get(id=courrier_id)
            except Courrier.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Courrier ID {courrier_id} introuvable'))
                return
        
        # Collecter les utilisateurs
        utilisateurs_ids = set()
        
        if courrier.agent_responsable:
            utilisateurs_ids.add(courrier.agent_responsable.id)
        
        if courrier.service_destinataire:
            utilisateurs_ids.update(
                courrier.service_destinataire.utilisateurs.filter(
                    is_active=True, notifier_par_email=True
                ).values_list('id', flat=True)
            )
        
        for service in courrier.services_original.all():
            utilisateurs_ids.update(
                service.utilisateurs.filter(
                    is_active=True, notifier_par_email=True
                ).values_list('id', flat=True)
            )
        
        for service in courrier.services_copie.all():
            utilisateurs_ids.update(
                service.utilisateurs.filter(
                    is_active=True, notifier_par_email=True
                ).values_list('id', flat=True)
            )
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Teste d\'envoi pour le courrier :'))
        self.stdout.write(f'  Numéro: {courrier.numero}')
        self.stdout.write(f'  Objet: {courrier.objet[:50]}')
        self.stdout.write(f'  Destinataires: {len(utilisateurs_ids)} utilisateur(s)\n')
        
        if not utilisateurs_ids:
            self.stdout.write(self.style.WARNING('⚠️  Aucun utilisateur à notifier'))
            return
        
        # Afficher les utilisateurs
        utilisateurs = Utilisateur.objects.filter(id__in=utilisateurs_ids)
        for u in utilisateurs:
            self.stdout.write(f'  📧 {u.nom_complet} ({u.email})')
        
        # Envoyer notifications
        if is_async:
            self.stdout.write('\n🔄 Envoi asynchrone via Celery...')
            result = envoyer_notifications_courrier.delay(courrier.id, list(utilisateurs_ids))
            self.stdout.write(self.style.SUCCESS(f'✅ Tâche lancée (ID: {result.id})'))
        else:
            self.stdout.write('\n🔄 Envoi synchrone...')
            result = envoyer_notifications_courrier(courrier.id, list(utilisateurs_ids))
            self.stdout.write(self.style.SUCCESS(f'✅ {result}'))

    def tester_rappel_echu(self, is_async):
        """Tester l'envoi de rappels pour courriers échus"""
        from datetime import date
        
        courriers_echus = Courrier.objects.filter(
            date_echeance__lt=date.today(),
            statut__est_final=False
        )
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Test d\'envoi de rappels :'))
        self.stdout.write(f'  Courriers échus: {courriers_echus.count()}\n')
        
        if courriers_echus.count() == 0:
            self.stdout.write(self.style.WARNING('ℹ️  Aucun courrier échu trouvé'))
            return
        
        for c in courriers_echus[:5]:
            self.stdout.write(f'  ⚠️  {c.numero} | {c.objet[:40]}')
        
        if is_async:
            self.stdout.write('\n🔄 Envoi asynchrone via Celery...')
            result = envoyer_rappel_courriers_echus.delay()
            self.stdout.write(self.style.SUCCESS(f'✅ Tâche lancée (ID: {result.id})'))
        else:
            self.stdout.write('\n🔄 Envoi synchrone...')
            result = envoyer_rappel_courriers_echus()
            self.stdout.write(self.style.SUCCESS(f'✅ {result}'))

    def afficher_help(self):
        self.stdout.write(self.style.SUCCESS('\n📧 COMMANDES DISPONIBLES :\n'))
        self.stdout.write('  python manage.py test_notifications list')
        self.stdout.write('    → Affiche les 10 derniers courriers\n')
        self.stdout.write('  python manage.py test_notifications nouveau [--courrier-id=123] [--async]')
        self.stdout.write('    → Teste l\'envoi pour un courrier\n')
        self.stdout.write('  python manage.py test_notifications echu [--async]')
        self.stdout.write('    → Teste les rappels pour courriers échus\n')
