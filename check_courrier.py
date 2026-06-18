#!/usr/bin/env python
"""Check if courrier was created"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.courriers.models import Courrier

# Check recent courriers
courriers = Courrier.objects.all().order_by('-id')[:5]
print(f"Total courriers: {Courrier.objects.count()}")
print("\nRecent courriers:")
for c in courriers:
    print(f"  - {c.id}: {c.numero_lettre} ({c.objet})")

# Check specifically for our test courrier
test_numbers = ['2024/TEST001', '2024/TEST002', '2024/TEST003']
for num in test_numbers:
    try:
        test = Courrier.objects.get(numero_lettre=num)
        print(f"\n✓ Test courrier {num} found!")
        print(f"  ID: {test.id}")
        print(f"  Objet: {test.objet}")
    except Courrier.DoesNotExist:
        pass

print("\nDone")
