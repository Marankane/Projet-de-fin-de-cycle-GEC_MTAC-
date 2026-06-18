#!/bin/bash
# ════════════════════════════════════════════════════════
#  GED Courriers – MINTRANSPORT Niger
#  Script d'installation automatique v1.0
#  Usage : bash setup.sh
# ════════════════════════════════════════════════════════
set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${BLUE}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   GED Courriers – MINTRANSPORT Niger     ║"
echo "  ║   Installation automatique               ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Vérification Python ──
python3 --version >/dev/null 2>&1 || { echo -e "${RED}Python 3 requis.${NC}"; exit 1; }
echo -e "${GREEN}✓ Python OK${NC}"

# ── Environnement virtuel ──
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Création du venv...${NC}"
    python3 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN}✓ Venv activé${NC}"

# ── Dépendances ──
echo -e "${YELLOW}Installation des dépendances...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dépendances installées${NC}"

# ── Fichier .env ──
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠  Fichier .env créé. Éditez-le avec vos paramètres DB avant de continuer.${NC}"
    echo ""
    echo -e "${BLUE}Paramètres à configurer dans .env :${NC}"
    echo "  DB_NAME=ged_courrier"
    echo "  DB_USER=ged_user"
    echo "  DB_PASSWORD=votre_mot_de_passe"
    echo ""
    read -p "Appuyez sur Entrée une fois .env configuré..."
fi
echo -e "${GREEN}✓ .env configuré${NC}"

# ── PostgreSQL ──
echo -e "${YELLOW}Création de la base PostgreSQL (si nécessaire)...${NC}"
source .env 2>/dev/null || true
DB_NAME=${DB_NAME:-ged_courrier}
DB_USER=${DB_USER:-ged_user}
DB_PASSWORD=${DB_PASSWORD:-}

psql -U postgres -tc "SELECT 1 FROM pg_user WHERE usename='$DB_USER'" 2>/dev/null | grep -q 1 || \
    psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true

psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null | grep -q 1 || \
    psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING='UTF8';" 2>/dev/null || true

echo -e "${GREEN}✓ Base de données prête${NC}"

# ── Migrations ──
echo -e "${YELLOW}Application des migrations...${NC}"
python manage.py makemigrations --no-input
python manage.py migrate --no-input
echo -e "${GREEN}✓ Migrations appliquées${NC}"

# ── Données initiales ──
echo -e "${YELLOW}Chargement des données initiales...${NC}"
python manage.py loaddata fixtures/services.json
python manage.py loaddata fixtures/parametrage.json
echo -e "${GREEN}✓ Données chargées${NC}"

# ── Superutilisateur ──
echo ""
echo -e "${BLUE}Créer le compte administrateur :${NC}"
python manage.py createsuperuser

# ── Statiques ──
echo -e "${YELLOW}Collecte des fichiers statiques...${NC}"
python manage.py collectstatic --no-input --clear >/dev/null 2>&1
echo -e "${GREEN}✓ Statiques collectés${NC}"

# ── Résumé ──
echo ""
echo -e "${GREEN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   Installation terminée avec succès !   ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  Démarrer le serveur :"
echo -e "  ${BLUE}source venv/bin/activate && python manage.py runserver${NC}"
echo ""
echo -e "  Accès : ${BLUE}http://127.0.0.1:8000${NC}"
echo -e "  Admin : ${BLUE}http://127.0.0.1:8000/admin/${NC}"
echo ""
