# GED Courriers – MINTRANSPORT Niger

Gestion Électronique des Courriers pour le Ministère du Transport et de la Navigation Civile du Niger.

## Prérequis

- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (optionnel, pour Celery)

## Installation rapide

```bash
# 1. Cloner / dézipper le projet
cd ged_courrier

# 2. Lancer le script d'installation
bash setup.sh
```

## Installation manuelle

```bash
# 1. Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 2. Dépendances
pip install -r requirements.txt

# 3. Configuration
cp .env.example .env
# Éditez .env avec vos paramètres

# 4. Base de données PostgreSQL
createdb ged_courrier
createuser ged_user

# 5. Migrations
python manage.py makemigrations
python manage.py migrate

# 6. Données initiales
python manage.py loaddata fixtures/services.json
python manage.py loaddata fixtures/parametrage.json

# 7. Superutilisateur
python manage.py createsuperuser

# 8. Démarrage
python manage.py runserver
```

## URLs

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | Application principale |
| http://127.0.0.1:8000/admin/ | Interface d'administration Django |
| http://127.0.0.1:8000/api/v1/ | API REST (JSON) |

## Rôles utilisateurs

| Rôle | Description |
|------|-------------|
| Agent Courrier | Enregistrement, scan, dispatch |
| Secrétaire | Consultation, répartition, suivi délais |
| Chef de Service | Instructions, validation, tableau de bord |
| Directeur Général | Vision globale, statistiques |
| Administrateur | Gestion complète du système |

## Workflow de traitement des courriers

### Acteurs et ordre de traitement

1. **Agent de courrier** :
   - Assure la réception physique du courrier entrant
   - Procède au scan des documents papier et à leur enregistrement dans le système
   - Affecte les courriers aux services destinataires
   - Ajoute un fichier récapitulatif du courrier pour le transmettre au SGA

2. **SGA (Secrétaire Général Adjoint)** :
   - Consulte, vérifie et donne son avis (rejeter/accepter avec description)
   - Retourne au "Agent de courrier"

3. **Agent de courrier** :
   - Si avis positif du SGA : transmet au SG
   - Sinon : retourne à l'expéditeur

4. **SG (Secrétaire Général)** :
   - Consulte, vérifie et donne son avis (rejeter/accepter avec description)
   - Retourne au "Agent de courrier"

5. **Agent de courrier** :
   - Si avis positif du SG : transmet au Ministre
   - Sinon : retourne à l'expéditeur

6. **Ministre** :
   - Consulte, vérifie et donne son avis (rejeter/accepter avec décision)
   - Retourne au "Agent de courrier"

7. **Agent de courrier** :
   - Si avis positif du Ministre : transmet au Destinataire
   - Sinon : retourne à l'expéditeur

### Statuts du workflow

Les statuts suivants sont utilisés pour suivre l'avancement :
- ENR : Enregistré
- SGA : Soumis au SGA
- SG : Soumis au SG
- MIN : Soumis au Ministre
- ACC : Accepté
- REJ : Rejeté
- CLO : Clôturé

## Structure du projet

```
ged_courrier/
├── apps/
│   ├── accounts/       # Authentification, utilisateurs
│   ├── courriers/      # Courriers entrants/sortants
│   ├── dashboard/      # Tableaux de bord par rôle
│   ├── mouvements/     # Journal de traçabilité
│   ├── organisations/  # Services et structure
│   ├── parametrage/    # Configuration métier
│   └── notifications/  # Alertes et e-mails
├── config/             # Settings, URLs
├── core/               # Permissions partagées
├── fixtures/           # Données initiales
├── static/             # CSS, JS
├── templates/          # HTML
└── media/              # Fichiers uploadés
```

## API REST

Authentification JWT :
```bash
curl -X POST http://127.0.0.1:8000/api/v1/accounts/connexion/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mintransport.ne","mot_de_passe":"votre_mdp"}'
```

Endpoints principaux :
- `GET /api/v1/courriers/` — Liste des courriers
- `POST /api/v1/courriers/` — Créer un courrier
- `POST /api/v1/courriers/{id}/dispatcher/` — Dispatcher
- `POST /api/v1/courriers/{id}/valider/` — Valider
- `GET /api/v1/courriers/statistiques/` — Statistiques
