#!/usr/bin/env python
"""Test script to submit a courrier form"""
import os
import django
import unittest
from django.contrib.auth import get_user_model

if __name__ != "__main__":
    raise unittest.SkipTest("Script manuel: exécuter directement avec python test_courrier_submit.py")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from apps.courriers.models import Courrier, Expediteur
from apps.organisations.models import Service

# Create a test client
client = Client()

# Login first
login_success = client.login(email='admin@mintransport.ne', password='Admin123456')
print(f"Login success: {login_success}")

# Get CSRF token
response = client.get('/courriers/enregistrement/')
csrf_token = response.cookies.get('csrftoken', '')
print(f"Got CSRF token: {csrf_token[:20]}...")

# Prepare data
data = {
    'csrfmiddlewaretoken': csrf_token,
    'numero_lettre': '2024/TEST001',
    'destinataire': '10',  # Attaché de Presse
    'date_reception': '2026-05-06',
    'objet': 'Test de soumission de courrier',
    'expediteur': '1',  # First expediteur
    'type_courrier': '1',  # Lettre
    'priorite': '1',  # Normal (15j)
    'service_destinataire': '1',  # First service
    'confidentiel': False,
}

print("\nData to submit:")
for k, v in data.items():
    if k != 'csrfmiddlewaretoken':
        print(f"  {k}: {v}")

# Submit the form
print("\nSubmitting form...")
response = client.post('/courriers/enregistrement/', data, follow=True)

print(f"Response status: {response.status_code}")
print(f"Response URL: {response.request['PATH_INFO']}")

# Check if there were any form errors
if hasattr(response.context, '__getitem__'):
    form = response.context.get('form')
    if form and form.errors:
        print("\nForm errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    else:
        print("\nNo form errors - Success!")
        
        # Check if courrier was created
        try:
            courrier = Courrier.objects.get(numero_lettre='2024/TEST001')
            print(f"\nCourrier créé avec succès!")
            print(f"ID: {courrier.id}")
            print(f"Numéro: {courrier.numero_lettre}")
            print(f"Objet: {courrier.objet}")
        except Courrier.DoesNotExist:
            print("\nCourrier non créé mais pas d'erreur du formulaire...")
else:
    print("\nContext non disponible")
    
# Also check raw response content for errors
if 'error' in response.content.decode().lower():
    print("\nPotential errors in response:")
    print(response.content.decode()[-500:])
