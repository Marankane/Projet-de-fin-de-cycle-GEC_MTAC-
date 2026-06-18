# 📢 Cloche de Notifications - Guide d'Intégration

## 📋 Vue d'ensemble

La cloche de notifications affiche en temps réel les notifications non lues avec:
- **Tri par urgence** : Les notifications urgentes apparaissent toujours en premier
- **Tri par date**: Les plus récentes viennent après les urgentes
- **Mise à jour automatique** : Toutes les 30 secondes
- **Interface moderne** : Couleurs Niger (Orange #E85D04 et Vert #1B4332)

## 🎯 Fonctionnalités

### ✅ Fonctionnalités Actuelles
- Badge de compteur avec nombre de notifications (99+ si > 99)
- Animation de la cloche lors de nouvelles notifications
- Dropdown avec liste des notifications
- Clic sur notification = marque comme lue + redirection
- Bouton "Tout marquer comme lu"
- Formatage du temps relatif (Il y a 5m, Il y a 2h, etc.)
- Types de notifications avec icônes personnalisées:
  - 🔴 URGENCE (rouge)
  - 📧 COURRIER ASSIGNÉ (orange)
  - ⚠️ COURRIER ÉCHU (rouge)
  - 🔄 COURRIER RETOURNÉ (jaune)
  - 🔔 RAPPEL (bleu)

### 🎨 Interface
- Responsive : Mobile, Tablette, Desktop
- Dark mode ready
- Animations fluides
- Dégradé Nigeria en fond

## 🔧 Configuration Technique

### 1. Fichiers Créés/Modifiés

#### Nouveaux Fichiers
- `static/js/notification-bell.js` - Composant JavaScript principal (350+ lignes)
- `static/css/notification-bell.css` - Styles de la cloche (300+ lignes)
- `templates/includes/notification_bell.html` - Template réutilisable

#### Fichiers Modifiés
- `templates/base.html` 
  - Ajout du lien CSS notification-bell.css dans `<head>`
  - Remplacement du dropdown notifications par le composant `notification_bell.html`
  - Ajout du script `notification-bell.js` avant `</body>`

### 2. Endpoints API Requis

La cloche utilise ces endpoints (déjà implémentés):
- `GET /api/notifications/unread/?limit=8` - Récupère les 8 dernières notifications non lues
- `POST /api/notifications/<id>/read/` - Marque une notification comme lue
- `POST /api/notifications/read-all/` - Marque toutes les notifications comme lues
- `GET /api/notifications/count/` - Compte les notifications non lues

### 3. Classe JavaScript: `NotificationBell`

#### Initialisation
```javascript
new NotificationBell({
    apiUrl: '/api/notifications/unread/',
    updateInterval: 30000,  // ms
    notificationLimit: 8
});
```

#### Méthodes Principales
- `init()` - Initialise les event listeners
- `loadNotifications()` - Charge les notifications depuis l'API
- `renderNotifications(notifications)` - Rend la liste des notifications
- `markAsRead(notificationId, reload)` - Marque une notification comme lue
- `markAllAsRead()` - Marque toutes comme lues
- `updateBadge(count)` - Met à jour le badge de compteur

## 📦 Dépendances

### Logicielles
- Django 5.0.6+
- Django REST Framework
- PostgreSQL (ou autre DB supportée)
- Redis 6+ (pour Celery)
- Celery 5.4.0+

### Frontend
- Bootstrap 5.3+
- Bootstrap Icons (bi-bell, bi-envelope, etc.)
- Vanilla JavaScript (ES6+)

### Backend Services
- Email backend configuré (SMTP ou console)
- Celery worker en exécution
- Task `envoyer_notifications_courrier` disponible

## 🚀 Installation & Configuration

### 1. Vérifier que l'API est Fonctionnelle

```bash
# Tester les endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/notifications/count/
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/notifications/unread/?limit=8
```

### 2. Vérifier que les Notifications sont Créées

Les notifications doivent être créées par le système lorsqu'un courrier est assigné:

```python
# apps/notifications/models.py
class Notification(models.Model):
    utilisateur = ForeignKey(User)
    courrier = ForeignKey(Courrier)
    titre = CharField()
    message = TextField()
    lue = BooleanField(default=False)
    type = CharField(choices=[...])  # COURRIER_ASSIGNE, COURRIER_ÉCHU, etc.
    cree_le = DateTimeField(auto_now_add=True)
```

### 3. Vérifier que Celery est Actif

```bash
# Terminal 1: Démarrer Redis
redis-server

# Terminal 2: Démarrer Celery Worker
celery -A config worker -l info

# Terminal 3: Démarrer le serveur Django
python manage.py runserver
```

### 4. S'Assurer que les Tâches d'Email Fonctionnent

```bash
# Test depuis Django shell
python manage.py shell
>>> from apps.notifications.tasks import envoyer_notifications_courrier
>>> envoyer_notifications_courrier.delay(courrier_id=1, utilisateurs_ids=[1,2,3])
```

## 🧪 Tests

### Test Manuel

1. **Créer un courrier** via l'interface
2. **Vérifier la BD** que des Notification objects ont été créés
3. **Aller au dashboard** et voir la cloche s'animer
4. **Cliquer sur la cloche** pour voir le dropdown
5. **Cliquer sur une notification** pour la marquer comme lue
6. **Cliquer "Tout marquer comme lu"** pour marquer toutes comme lues

### Test API

```bash
# Lister les notifications
GET /api/notifications/unread/?limit=8

# Response
{
  "count": 3,
  "notifications": [
    {
      "id": 1,
      "titre": "Courrier assigné",
      "message": "Un courrier t'a été assigné",
      "type": "COURRIER_ASSIGNE",
      "lue": false,
      "is_urgent": true,
      "cree_le": "2024-01-15T10:30:00Z",
      "courrier_numero": "CR-2024-001",
      "lien": "/courriers/1/detail/"
    }
  ]
}

# Marquer comme lue
POST /api/notifications/1/read/
Headers: X-CSRFToken: xxx

# Response
{"status": "success"}
```

## 🎨 Personnalisation

### Changer les Couleurs

Modifier `static/css/notification-bell.css`:
```css
/* Actuellement: Orange (#E85D04) et Vert (#1B4332) Niger */

#notification-bell-icon {
    color: #E85D04;  /* Couleur primaire */
}

#notification-count-badge {
    background: linear-gradient(135deg, #E85D04 0%, #c53030 100%);
}
```

### Changer l'Intervalle de Mise à Jour

Modifier `static/js/notification-bell.js`:
```javascript
new NotificationBell({
    updateInterval: 15000,  // Au lieu de 30000ms (15 secondes)
});
```

### Ajouter Plus de Notifications par Défaut

```javascript
new NotificationBell({
    notificationLimit: 15,  // Au lieu de 8
});
```

## 🐛 Débogage

### La Cloche n'Apparaît Pas

1. Vérifier que `templates/includes/notification_bell.html` est chargé
2. Vérifier que `{% load static %}` est dans base.html
3. Vérifier les erreurs du navigateur (F12 → Console)

```javascript
// Dans la console navigateur
const bell = new NotificationBell();
console.log(bell.bellContainer);  // Doit afficher l'élément DOM
```

### Les Notifications ne se Chargent Pas

1. Vérifier l'URL API dans JavaScript: `apiUrl: '/api/notifications/unread/'`
2. Vérifier le token d'authentification
3. Vérifier dans le Network tab (F12 → Network) les appels API

```bash
# Vérifier l'endpoint
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/notifications/unread/
```

### Le Badge ne Se Mets Pas à Jour

1. Vérifier que les notifications sont créées en base
2. Vérifier que `updateInterval` est correctement configuré
3. Vérifier les erreurs JavaScript dans la console

```javascript
// Debug
setInterval(() => {
    fetch('/api/notifications/count/').then(r => r.json()).then(console.log);
}, 5000);
```

## 📊 Architecture

```
notification-bell.js
  ├── NotificationBell (classe)
  │   ├── init() - Initialisation
  │   ├── loadNotifications() - Fetch API
  │   ├── renderNotifications() - Render DOM
  │   ├── markAsRead() - API POST
  │   └── updateBadge() - Badge count
  │
notification-bell.css
  ├── #notification-bell-container
  ├── #notification-bell-icon
  ├── #notification-count-badge
  ├── #notification-dropdown-menu
  └── .notification-item-btn

notification_bell.html
  ├── Bell icon button
  ├── Count badge
  ├── Dropdown menu
  └── Notifications list

API Endpoints
  ├── GET /api/notifications/unread/?limit=8
  ├── POST /api/notifications/<id>/read/
  ├── POST /api/notifications/read-all/
  └── GET /api/notifications/count/
```

## 📝 Logs

Les erreurs JavaScript sont loggées dans la console du navigateur:
```
Erreur chargement notifications: ...
Erreur marquage notification: ...
```

Les erreurs Django/API sont loggées dans les logs Django:
```bash
tail -f logs/django.log | grep -i notification
```

## 🔄 Amélioration Future

- [ ] Push notifications (WebSocket)
- [ ] Son de notification
- [ ] Grouper par type de notification
- [ ] Filtrer les notifications
- [ ] Chercher dans les notifications
- [ ] Mark as unread
- [ ] Delete notification
- [ ] Notification settings par utilisateur
- [ ] Email digest au lieu d'immédiat

## 📞 Support

Pour des problèmes:
1. Vérifier les logs Django/JavaScript
2. Tester les endpoints API directement
3. Vérifier que Celery/Redis sont actifs
4. Consulter la documentation de Django REST Framework
