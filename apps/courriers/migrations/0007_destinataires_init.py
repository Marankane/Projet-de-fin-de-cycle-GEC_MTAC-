from django.db import migrations


def create_destinataires(apps, schema_editor):
    Destinataire = apps.get_model('courriers', 'Destinataire')
    names = [
        'Secrétaire Général',
        'DRMT/AC',
        'Chef de Cabinet',
        'Conseillers Techniques',
        'Secrétaire Général Adj.',
        'Projet/Programme',
        'Attaché de Protocole',
        'IGS',
        'Chef Bureau d’Ordre',
        'Attaché de Presse',
        'Inspecteurs de Services',
    ]
    for name in names:
        Destinataire.objects.get_or_create(nom=name, defaults={'type': 'SERVICE'})


def reverse_destinataires(apps, schema_editor):
    Destinataire = apps.get_model('courriers', 'Destinataire')
    Destinataire.objects.filter(nom__in=[
        'Secrétaire Général',
        'DRMT/AC',
        'Chef de Cabinet',
        'Conseillers Techniques',
        'Secrétaire Général Adj.',
        'Projet/Programme',
        'Attaché de Protocole',
        'IGS',
        'Chef Bureau d’Ordre',
        'Attaché de Presse',
        'Inspecteurs de Services',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('courriers', '0006_courrier_service_copie_courrier_service_original'),
    ]

    operations = [
        migrations.RunPython(create_destinataires, reverse_destinataires),
    ]
