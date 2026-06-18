# Installation du Scanner IA pour GED Courriers

Le système de scanner et d'analyse IA des documents a été intégré à l'application.

## Prérequis

### 1. pytesseract (OCR Python)
Déjà ajouté à `requirements.txt`. À installer avec :
```bash
pip install -r requirements.txt
```

### 2. Tesseract-OCR (Moteur OCR système)

Cette bibliothèque **requiert l'installation de Tesseract-OCR** sur votre système d'exploitation.

#### Sur Windows :
1. Télécharger l'installateur depuis : https://github.com/UB-Mannheim/tesseract/wiki
2. Installer avec les paramètres par défaut (par exemple : `C:\Program Files\Tesseract-OCR`)
3. Définir la variable d'environnement `PYTESSERACT_PATH` ou mettre à jour le code dans `ai_service.py` :

```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

#### Sur Linux (Ubuntu/Debian) :
```bash
sudo apt-get install tesseract-ocr
```

### Backends IA alternatifs
Par défaut, le système utilise plusieurs backends en cascade : `tesseract`, `ocr_space` et `azure_vision`. Si le premier échoue, le suivant prend automatiquement le relais.

- Pour utiliser OCR.space, définissez la clé API :
  - `OCR_SPACE_API_KEY=your_key`
- Pour utiliser Azure Computer Vision, définissez :
  - `AZURE_COMPUTER_VISION_ENDPOINT=https://<votre-endpoint>.cognitiveservices.azure.com`
  - `AZURE_COMPUTER_VISION_KEY=your_key`
- Pour modifier l'ordre des backends, utilisez :
  - `AI_BACKENDS=tesseract,ocr_space,azure_vision`

Vous pouvez ajouter d'autres backends dans `apps/courriers/ai_service.py` si nécessaire.

#### Sur macOS :
```bash
brew install tesseract
```

## Fonctionnalités

### 1. **Scanner / Import de Documents**
- **Glisser-déposer** : Déposer un fichier sur la zone de scan
- **Parcourir** : Cliquer pour sélectionner un fichier
- **Formats acceptés** : JPG, PNG, GIF, PDF (max 20 Mo)

### 2. **Analyse IA**
En cliquant sur "Analyser avec IA", le système :
- Extrait le texte du document via OCR
- Tente l'analyse avec plusieurs backends IA en cascade
- Analyse le texte pour détecter :
  - **Objet** : Le sujet/titre du courrier
  - **Expéditeur** : Qui envoie le courrier
  - **Date** : La date d'envoi/réception
  - **Référence** : Numéro/référence du courrier
  - **Résumé** : Un aperçu du contenu

### 3. **Mécanisme de bascule (fallback)**
Le traitement utilise plusieurs API / services dans l'ordre configuré :
- `tesseract` (OCR local via `pytesseract`)
- `ocr_space` (OCR Cloud via l'API OCR.space)

Si le premier backend échoue, le deuxième prend le relais automatiquement.

### 4. **Remplissage Automatique**
Les champs détectés remplissent automatiquement le formulaire :
- Objet du courrier
- Date de réception
- Référence externe

### 5. **Validation**
L'utilisateur peut modifier les données extraites avant validation.

### 3. **Remplissage Automatique**
Les champs détectés remplissent automatiquement le formulaire :
- Objet du courrier
- Date de réception
- Référence externe

### 4. **Validation**
L'utilisateur peut modifier les données extraites avant validation.

## Architecture Technique

### Fichiers Ajoutés/Modifiés

1. **`apps/courriers/ai_service.py`** : Service d'analyse des documents
   - `DocumentAnalyzer.extract_text_from_image()` : OCR
   - `DocumentAnalyzer.extract_metadata()` : Extraction métadonnées
   - `DocumentAnalyzer.analyze_document()` : Analyse complète

2. **`apps/courriers/api.py`** : API REST
   - `POST /courriers/api/process-document/` : Endpoint d'analyse

3. **`static/js/scanner.js`** : Interface utilisateur
   - Gestion du drag & drop
   - Appel API
   - Remplissage automatique du formulaire

4. **`static/css/ged.css`** : Styles du scanner

5. **`templates/courriers/enregistrement.html`** : Template mise à jour

6. **`apps/courriers/urls.py`** : Route API

## Utilisation

1. Aller à `/courriers/enregistrement/`
2. Dans la section "Scanner ou importer un document" :
   - Glisser un document ou cliquer pour parcourir
   - Cliquer sur "Analyser avec IA"
3. Vérifier les résultats affichés
4. Les champs principaux se remplissent automatiquement
5. Continuer avec le formulaire normal et valider

## Modifications Futures Possibles

- **Support PDF avancé** : Utiliser `pdf2image` + OCR
- **Amélioration IA** : Intégrer OpenAI Vision API pour analyse sémantique
- **Traitement batch** : Scanner plusieurs documents à la fois
- **Correction automatique** : Apprentissage des corrections utilisateur
- **Multilangues** : Support de plusieurs langues (actuellement français uniquement)

## Dépannage

### Erreur "Tesseract is not installed"
- Installer Tesseract-OCR pour votre système (voir ci-dessus)
- Vérifier le chemin dans `ai_service.py`

### OCR retourne du texte vide
- Document de mauvaise qualité ou trop sombre
- Essayer avec une image plus claire

### Analyse très lente
- Réduire la résolution de l'image
- Convertir en noir et blanc avant d'envoyer
