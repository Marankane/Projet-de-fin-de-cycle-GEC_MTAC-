#!/usr/bin/env python
"""Test script to submit a courrier form via HTTP - using urllib"""
import urllib.request
import urllib.parse
import http.cookiejar
import unittest
from html.parser import HTMLParser

if __name__ != "__main__":
    raise unittest.SkipTest("Script manuel: exécuter directement avec python test_http_submit.py")

BASE_URL = 'http://127.0.0.1:8000'

# Setup cookie jar to persist sessions
cookiejar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))

# Parse HTML to extract fields
class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.csrf_token = None
        self.in_form = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'form':
            self.in_form = True
        if self.in_form and tag == 'input' and attrs_dict.get('name') == 'csrfmiddlewaretoken':
            self.csrf_token = attrs_dict.get('value')
    
    def handle_endtag(self, tag):
        if tag == 'form':
            self.in_form = False

# Login first
print("Logging in...")
login_url = f'{BASE_URL}/connexion/'
response = opener.open(login_url)
html = response.read().decode('utf-8')

# Extract CSRF token
parser = FormParser()
parser.feed(html)
csrf_token = parser.csrf_token

if csrf_token:
    print(f"✓ Got CSRF token: {csrf_token[:20]}...")
else:
    print("✗ Could not find CSRF token")
    exit(1)

# Login
login_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf_token,
    'email': 'admin@mintransport.ne',
    'password': 'Admin123456',
}).encode('utf-8')

try:
    response = opener.open(login_url, login_data)
    print(f"✓ Login successful (status: {response.status})")
except urllib.error.HTTPError as e:
    print(f"✗ Login failed (status: {e.code})")
    print(e.read().decode()[:500])
    exit(1)

# Get the courrier form page
print("\nGetting courrier form page...")
form_url = f'{BASE_URL}/courriers/enregistrement/'
try:
    response = opener.open(form_url)
    html = response.read().decode('utf-8')
    print(f"✓ Form page loaded (status: {response.status})")
except urllib.error.HTTPError as e:
    print(f"✗ Form page failed (status: {e.code})")
    print(e.read().decode()[:500])
    exit(1)

# Extract CSRF token from form page
parser = FormParser()
parser.feed(html)
csrf_token = parser.csrf_token

if csrf_token:
    print(f"✓ Got new CSRF token: {csrf_token[:20]}...")
else:
    print("✗ Could not find CSRF token in form page")
    exit(1)

# Prepare data for submission
form_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf_token,
    'numero_lettre': '2024/TEST003',
    'destinataire': '10',  # Attaché de Presse
    'date_reception': '2026-05-06',
    'objet': 'Test de soumission via urllib',
    'expediteur': '1',  # First expediteur
    'type_courrier': '1',  # Lettre
    'priorite': '1',  # Normal (15j)
    'service_destinataire': '1',  # First service
    'confidentiel': 'off',
}).encode('utf-8')

# Submit the form
print("\nSubmitting form...")
try:
    response = opener.open(form_url, form_data)
    html = response.read().decode('utf-8')
    print(f"✓ Form submitted (status: {response.status})")
    print(f"  Response URL: {response.geturl()}")
    
    # Check for errors
    if 'class="alert' in html or 'error' in html.lower():
        print("\n⚠ Response may contain errors")
        # Extract a snippet
        if 'alert-danger' in html:
            print("  Found danger alert in response")
    else:
        print("\n✓ No obvious errors detected")
        
    print(f"\nResponse preview (first 300 chars):")
    print(html[:300])
    
except urllib.error.HTTPError as e:
    print(f"✗ Form submission failed (status: {e.code})")
    html = e.read().decode('utf-8')
    print(f"Error page preview: {html[:500]}")
    exit(1)
