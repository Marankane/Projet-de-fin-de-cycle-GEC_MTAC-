from django.db import migrations


def create_services(apps, schema_editor):
    Service = apps.get_model('organisations', 'Service')
    names = [
        'DGC/TR', 'DC/SR', 'DTR', 'DMU',
        'DGTF/M/F', 'DTF', 'DTM/F', 'DL/TM',
        'DEP', 'DRFM', 'DRH', 'DS/I', 'DL', 'DAID/RP', 'DNM', 'DMP/DSP',
        'ANAC', 'ASECNA', 'AANN', 'ANISER', 'CNUT', 'CNTPS', 'CFTTR', 'SOTRUNI', 'NSH', 'NWA',
    ]
    for name in names:
        Service.objects.get_or_create(code=name, defaults={'nom': name, 'actif': True})


def reverse_services(apps, schema_editor):
    Service = apps.get_model('organisations', 'Service')
    Service.objects.filter(code__in=[
        'DGC/TR', 'DC/SR', 'DTR', 'DMU',
        'DGTF/M/F', 'DTF', 'DTM/F', 'DL/TM',
        'DEP', 'DRFM', 'DRH', 'DS/I', 'DL', 'DAID/RP', 'DNM', 'DMP/DSP',
        'ANAC', 'ASECNA', 'AANN', 'ANISER', 'CNUT', 'CNTPS', 'CFTTR', 'SOTRUNI', 'NSH', 'NWA',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_services, reverse_services),
    ]
