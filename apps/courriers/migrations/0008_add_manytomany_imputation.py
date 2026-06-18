# Generated migration to add ManyToMany fields for services_original and services_copie

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courriers', '0007_destinataires_init'),
        ('organisations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courrier',
            name='services_original',
            field=models.ManyToManyField(blank=True, related_name='courriers_original', to='organisations.service'),
        ),
        migrations.AddField(
            model_name='courrier',
            name='services_copie',
            field=models.ManyToManyField(blank=True, related_name='courriers_copie', to='organisations.service'),
        ),
    ]
