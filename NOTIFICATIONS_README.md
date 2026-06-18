# 📧 Système de Notifications par Email - GED Courrier

## Vue d'ensemble

Le système de notifications par email de GED Courrier envoie automatiquement des emails à tous les utilisateurs concernés quand :
1. **Un nouveau courrier arrive** (assigné à leur service ou en copie)
2. **Un courrier dépasse sa date limite** (rappels automatiques)

---

## 🎯 Qui reçoit les notifications ?

### Pour un NOUVEAU courrier :
✅ **Agent responsable** (si assigné)  
✅ **Tous les utilisateurs du service destinataire** (actifs + email activé)  
✅ **Tous les utilisateurs des services en original**  
✅ **Tous les utilisateurs des services en copie**  

### Pour un courrier ÉCHU :
✅ **Agent responsable** uniquement  

---

## ⚙️ Configuration Requise

### 1. Variables d'environnement (.env)

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com                    # ou votre serveur SMTP
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
DEFAULT_FROM_EMAIL=GED Courriers <noreply@mintransport.ne>

# Redis (pour Celery)
REDIS_URL=redis://localhost:6379/0
```

### 2. Installations requises

```bash
# Celery (tâches asynchrones)
pip install celery redis

# Si pas déjà installé
pip install django-celery-beat
pip install django-celery-results
```

### 3. Démarrer Celery

```bash
# Terminal 1 - Worker Celery
celery -A config worker -l info

# Terminal 2 - Beat (planificateur)
celery -A config beat -l info
```

---

## 🔄 Flux d'envoi des emails

```
Création du courrier
        ↓
Signal Django post_save
        ↓
Collecte des utilisateurs concernés
        ↓
Lancement tâche Celery (asynchrone)
        ↓
Création notifications en BD
        ↓
Préparation des emails (HTML + texte)
        ↓
Envoi massif via SMTP
```

---

## 📝 Templates d'Email

Deux templates disponibles :

### 1. Nouveau Courrier (`nouveau_courrier.html/txt`)
- Informations du courrier
- Détails expéditeur/type/priorité
- Bouton d'action "Consulter"
- Informations sur les délais

### 2. Courrier Échu (`courrier_echu.html/txt`)
- Alerte rouge de dépassement
- Nombre de jours de retard
- Informations du courrier
- Appel à action urgent

---

## 🛠️ Utilisation

### Envoyer notification manuellement

```python
from apps.notifications.tasks import envoyer_notifications_courrier
from apps.accounts.models import Utilisateur

courrier_id = 123
utilisateurs_ids = list(Utilisateur.objects.values_list('id', flat=True))

# Asynchrone (recommandé)
envoyer_notifications_courrier.delay(courrier_id, utilisateurs_ids)

# Synchrone (test)
envoyer_notifications_courrier(courrier_id, utilisateurs_ids)
```

### Envoyer rappels courriers échus

```python
from apps.notifications.tasks import envoyer_rappel_courriers_echus

# Lancer manuellement
envoyer_rappel_courriers_echus()

# Ou via Celery Beat (automatique)
```

---

## 📊 Contrôle par Utilisateur

Chaque utilisateur peut contrôler ses notifications via son profil :

```html
<!-- Dans le profil utilisateur -->
<label>
  <input type="checkbox" name="notifier_par_email" value="true">
  Recevoir les notifications par email
</label>
```

**Condition dans le code** :
- `notifier_par_email=True` → reçoit les emails
- `notifier_par_email=False` → pas d'emails
- `is_active=False` → pas d'emails

---

## 🗄️ Modèle de Données - Notification

```python
class Notification(models.Model):
    TYPES = [
        ('COURRIER_ASSIGNE', 'Courrier assigné'),
        ('COURRIER_ECHU', 'Courrier échu'),
        ('COURRIER_RETOURNE', 'Courrier retourné'),
        ('RAPPEL', 'Rappel'),
    ]
    
    utilisateur = ForeignKey(Utilisateur)
    type = CharField(choices=TYPES)
    titre = CharField(max_length=200)
    message = TextField()
    lien = URLField()
    courrier = ForeignKey(Courrier)
    lue = BooleanField(default=False)
    cree_le = DateTimeField(auto_now_add=True)
```

---

## 🧪 Tests

### Tester l'envoi d'email en console

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Les emails s'affichent dans le terminal au lieu d'être envoyés.

### Envoyer un email test

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test',
    message='Hello World',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['test@example.com'],
)
```

---

## 🚨 Dépannage

### Les emails ne sont pas envoyés

**Vérifier :**
1. ✅ Celery est-il démarré ? (`celery -A config worker`)
2. ✅ Redis est-il en cours d'exécution ? (`redis-cli ping`)
3. ✅ Les credentials EMAIL sont-ils corrects ?
4. ✅ L'utilisateur a-t-il `notifier_par_email=True` ?
5. ✅ L'utilisateur est-il `is_active=True` ?

### Les notifications n'apparaissent pas en BD

**Vérifier :**
1. ✅ Les migrations sont-elles appliquées ?
2. ✅ Le signal Django est-il enregistré ? (voir `apps.py`)
3. ✅ Y a-t-il une tâche Celery bloquée ? (voir logs)

### Les emails arrivent en spam

**Solutions :**
1. Configurer SPF/DKIM pour votre domaine
2. Utiliser un service email professionnel (SendGrid, Mailgun, etc.)
3. Ajouter un template Unsubscribe

---

## 📧 Services Email Recommandés

Pour la production, utiliser un service professionnel :

```env
# Gmail SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Attention: pas le mot de passe normal

# SendGrid
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG...

# Mailgun
EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
ANYMAIL_MAILGUN_API_KEY=key-...
```

---

## 🔔 Notifications en BD vs Email

| Source | Via Email | Via BD | Temps |
|--------|-----------|--------|-------|
| Nouveau courrier | ✅ | ✅ | Instant |
| Courrier échu | ✅ | ✅ | Chaque jour (Beat) |
| Commentaire | ❌ | ✅ | Instant |
| Validation | ❌ | ✅ | Instant |

---

## 📞 Support

Pour des questions sur le système de notifications :
1. Vérifier les logs Celery : `celery -A config worker --loglevel=debug`
2. Vérifier les logs Django : `python manage.py runserver --verbosity 3`
3. Consulter le fichier `CHANGELOG.md` pour les dernières mises à jour

---

**Version** : 1.0  
**Dernière mise à jour** : 3 Juin 2026  
**Statut** : ✅ Production Ready
