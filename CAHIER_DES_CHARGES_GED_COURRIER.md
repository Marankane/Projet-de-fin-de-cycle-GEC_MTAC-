# Cahier des Charges

## Projet : Plateforme de Gestion Electronique des Courriers

**Application :** GED Courriers  
**Contexte :** Gestion Electronique des Courriers pour une administration publique  
**Type de solution :** Application web Django avec interface utilisateur, tableaux de bord, API REST, gestion documentaire et analyse OCR/IA  
**Version du document :** 1.0  
**Date :** 18 mai 2026

---

## 1. Presentation Generale du Projet

### 1.1 Contexte

Les administrations publiques traitent quotidiennement un volume important de courriers entrants, sortants et internes. Ces courriers circulent entre plusieurs services, directions, secretariats et responsables hierarchiques. Une gestion manuelle ou semi-manuelle expose l'organisation a plusieurs difficultes : perte de documents, lenteur du traitement, absence de tracabilite, suivi incomplet des delais, doublons, erreurs d'affectation et manque de visibilite pour les responsables.

Le projet GED Courriers vise a mettre en place une plateforme web centralisee permettant d'enregistrer, numeriser, classer, affecter, suivre, traiter et archiver les courriers administratifs. L'application doit faciliter le travail des agents et offrir aux responsables une vision claire de l'activite courrier.

La solution repose sur Django, PostgreSQL, une interface web securisee, une API REST, un systeme de roles, un journal de mouvements et un module d'analyse automatique de documents par OCR/IA pour extraire certaines metadonnees depuis les images ou PDF.

### 1.2 Finalite du Projet

La finalite du projet est de fournir un outil fiable et evolutif pour la gestion complete du cycle de vie des courriers :

- reception ;
- enregistrement ;
- numerisation ;
- analyse automatique ;
- affectation a l'agent courrier ;
- dispatch vers les services ;
- instruction ;
- validation ;
- cloture ;
- archivage ;
- consultation ;
- suivi statistique.

### 1.3 Objectifs Generaux

Les objectifs generaux sont les suivants :

- centraliser tous les courriers dans une base unique ;
- permettre a tout utilisateur authentifie de creer un courrier ;
- affecter automatiquement chaque courrier cree a un agent courrier actif ;
- reduire les pertes et doublons de documents ;
- ameliorer la tracabilite des actions ;
- faciliter le suivi des delais ;
- produire des tableaux de bord par role ;
- rendre les documents accessibles selon les droits ;
- assurer la securite des donnees ;
- permettre une extension future vers des integrations externes.

---

## 2. Perimetre du Projet

### 2.1 Perimetre Fonctionnel Inclus

Le projet couvre les modules suivants :

- authentification et gestion des utilisateurs ;
- gestion des roles et permissions ;
- gestion des services administratifs ;
- parametrage des types de courriers ;
- parametrage des priorites ;
- parametrage des statuts ;
- creation des courriers par tout utilisateur connecte ;
- affectation automatique des courriers a un agent courrier ;
- enregistrement des courriers entrants, sortants et internes ;
- gestion des expediteurs ;
- gestion des destinataires ;
- ajout de pieces jointes ;
- analyse IA/OCR des images et PDF ;
- liste et recherche des courriers ;
- detail d'un courrier ;
- modification controlee ;
- dispatch simple ;
- dispatch en masse ;
- instruction par les responsables habilites ;
- validation ;
- cloture ;
- registre des courriers ;
- tableaux de bord ;
- notifications ;
- API REST securisee ;
- journalisation des mouvements ;
- gestion globale des erreurs.

### 2.2 Perimetre Fonctionnel Exclu

Les elements suivants ne sont pas obligatoires dans la premiere version :

- signature electronique qualifiee ;
- archivage legal certifie ;
- workflow BPMN avance ;
- messagerie instantanee integree ;
- application mobile native ;
- integration avec un systeme national d'identite ;
- reconnaissance manuscrite avancee ;
- conversion massive de lots de documents ;
- gestion de codes-barres physiques ;
- parapheur electronique complet.

Ces elements pourront faire l'objet d'une phase ulterieure.

### 2.3 Utilisateurs Concernes

Les profils utilisateurs prevus sont :

- Agent Courrier ;
- Secretaire ;
- Chef de Service ;
- Directeur General ;
- Administrateur ;
- tout autre utilisateur authentifie autorise a creer un courrier.

---

## 3. Description des Acteurs et Roles

### 3.1 Utilisateur Authentifie

Tout utilisateur connecte a l'application doit pouvoir creer un courrier. Apres creation, le courrier est automatiquement envoye a un agent courrier actif. L'utilisateur createur peut consulter les courriers qu'il a crees, dans la limite des regles de confidentialite.

Responsabilites :

- creer un courrier ;
- renseigner les informations principales ;
- ajouter une piece jointe si necessaire ;
- utiliser l'analyse IA si un document est disponible ;
- consulter le suivi de ses courriers.

### 3.2 Agent Courrier

L'agent courrier est le role central du circuit courrier. Il recoit automatiquement les courriers crees par les utilisateurs. Il peut ensuite verifier, completer, dispatcher ou affecter les courriers.

Responsabilites :

- recevoir automatiquement les courriers nouvellement crees ;
- verifier la qualite des informations saisies ;
- completer les metadonnees ;
- ajouter ou verifier les pieces jointes ;
- dispatcher vers une direction ou un service ;
- affecter a un agent responsable ;
- suivre les courriers en cours ;
- consulter le registre.

### 3.3 Secretaire

Le secretaire intervient dans le suivi operationnel d'un service ou d'une direction. Il peut consulter les courriers de son service et participer a la repartition.

Responsabilites :

- consulter les courriers du service ;
- suivre les courriers non affectes ;
- surveiller les retards ;
- assister le chef de service ;
- verifier l'avancement des traitements.

### 3.4 Chef de Service

Le chef de service est responsable de l'instruction et du traitement des courriers affectes a son service.

Responsabilites :

- consulter les courriers de son service ;
- donner des instructions ;
- valider certains traitements ;
- suivre les delais ;
- piloter l'activite du service ;
- consulter les indicateurs.

### 3.5 Directeur General

Le directeur dispose d'une vision globale ou strategique de l'activite courrier.

Responsabilites :

- consulter les statistiques globales ;
- suivre les volumes par service ;
- identifier les retards ;
- consulter les courriers importants ;
- superviser l'activite administrative.

### 3.6 Administrateur

L'administrateur gere la configuration du systeme, les utilisateurs, les roles et les referentiels.

Responsabilites :

- creer et modifier les utilisateurs ;
- activer ou desactiver les comptes ;
- configurer les services ;
- parametrer les types de courriers ;
- parametrer les priorites ;
- parametrer les statuts ;
- superviser le bon fonctionnement technique ;
- acceder aux fonctions avancees.

---

## 4. Fonctionnalites Attendues

### 4.1 Authentification

L'application doit proposer une authentification securisee par email et mot de passe. Les utilisateurs doivent pouvoir se connecter via une page dediee.

Fonctionnalites :

- connexion par email ;
- deconnexion securisee ;
- maintien de session ;
- option "se souvenir de moi" ;
- journalisation des connexions ;
- reinitialisation de mot de passe ;
- modification du profil ;
- modification du mot de passe.

Exigences :

- les mots de passe doivent etre haches ;
- les comptes desactives ne doivent pas pouvoir se connecter ;
- les tentatives de connexion doivent etre journalisees ;
- les liens de reinitialisation doivent expirer.

### 4.2 Gestion des Utilisateurs

L'administrateur doit pouvoir creer, modifier, activer ou desactiver les utilisateurs.

Champs utilisateur :

- nom ;
- prenom ;
- email ;
- role ;
- service ;
- telephone ;
- avatar ;
- statut actif/inactif ;
- preference de notification email.

Regles :

- l'email doit etre unique ;
- certains roles doivent etre rattaches a un service ;
- un utilisateur ne doit pas pouvoir desactiver son propre compte ;
- les permissions dependent du role.

### 4.3 Gestion des Services

Le systeme doit permettre de structurer l'organisation en services ou directions.

Champs service :

- nom ;
- code ;
- description ;
- statut actif ;
- date de creation.

Regles :

- le code service doit etre unique ;
- le nom service doit etre unique ;
- seuls les services actifs doivent etre proposes dans les formulaires ;
- un service peut avoir un chef.

### 4.4 Parametrage Metier

Le module de parametrage doit permettre d'adapter l'application au contexte de l'administration.

Parametres :

- types de courriers ;
- statuts de courriers ;
- priorites ;
- delais associes aux priorites ;
- couleurs d'affichage ;
- ordre d'affichage.

Exemples de statuts :

- ENR : Enregistre ;
- SGA : Soumis au SGA ;
- SG : Soumis au SG ;
- MIN : Soumis au Ministre ;
- ACC : Accepte ;
- REJ : Rejete ;
- DIS : Dispatche ;
- RET : Retourne a l'expediteur ;
- CLO : Cloture.

### 4.5 Creation d'un Courrier

Tout utilisateur authentifie doit pouvoir creer un courrier depuis l'interface web. Cette regle est fondamentale.

Champs principaux :

- sens du courrier ;
- type de courrier ;
- priorite ;
- date de reception ;
- numero de lettre ou reference ;
- date de sortie ;
- objet ;
- expediteur ;
- destinataire ;
- direction responsable ;
- services en original ;
- services en copie ;
- confidentialite ;
- observations.

Regles :

- le numero interne du courrier est genere automatiquement ;
- le statut initial doit etre ENR ;
- le createur est enregistre ;
- chaque courrier cree est automatiquement affecte a un agent courrier actif ;
- si le createur est lui-meme agent courrier, le courrier peut lui etre affecte ;
- si plusieurs agents courrier sont actifs, l'application doit pouvoir choisir un agent selon une regle de charge ou d'ordre ;
- si aucun agent courrier actif n'existe, la creation doit afficher une erreur claire.

### 4.6 Affectation Automatique a l'Agent Courrier

Lorsqu'un utilisateur cree un courrier, le systeme doit automatiquement identifier un agent courrier actif et lui affecter le courrier.

Regle d'affectation recommandee :

1. Si le createur est un agent courrier actif, affecter le courrier au createur.
2. Sinon, affecter au premier agent courrier actif ayant le moins de courriers ouverts.
3. Si aucun agent courrier actif n'est disponible, bloquer la creation avec un message explicite.

Effets attendus :

- champ `agent_responsable` renseigne automatiquement ;
- mouvement de creation enregistre ;
- mouvement d'affectation automatique enregistre ;
- notification possible vers l'agent courrier ;
- consultation immediate par l'agent courrier.

### 4.7 Pieces Jointes

L'utilisateur doit pouvoir ajouter une piece jointe lors de la creation ou apres creation.

Formats acceptes :

- PDF ;
- DOC ;
- DOCX ;
- XLS ;
- XLSX ;
- JPG ;
- JPEG ;
- PNG ;
- TIFF.

Regles :

- taille maximale : 20 Mo ;
- le nom du fichier doit etre conserve ;
- la taille doit etre calculee ;
- le type MIME doit etre conserve ;
- l'ajout doit etre journalise ;
- la suppression doit etre limitee au deposant ou a l'administrateur.

### 4.8 Analyse IA/OCR

La page d'enregistrement doit proposer une section d'analyse automatique permettant de deposer une image ou un PDF.

Formats acceptes pour analyse :

- JPEG ;
- PNG ;
- GIF ;
- WEBP ;
- TIFF ;
- PDF.

Fonctionnement :

- l'utilisateur depose ou selectionne un document ;
- le systeme affiche un apercu ;
- le bouton "Analyser le document" lance l'analyse ;
- l'image est analysee directement par OCR ;
- le PDF est converti en images puis analyse par OCR ;
- si le PDF contient du texte embarque, le systeme tente d'abord l'extraction texte ;
- les metadonnees detectees sont affichees ;
- les champs du formulaire peuvent etre remplis automatiquement.

Metadonnees attendues :

- objet ;
- expediteur ;
- date ;
- reference ;
- resume ;
- texte brut partiel.

Regles de robustesse :

- un document illisible ne doit pas faire planter la page ;
- une analyse impossible doit retourner un message clair ;
- les erreurs doivent etre affichees dans la section IA ;
- le serveur doit retourner du JSON stable ;
- les PDF avec MIME generique doivent etre acceptes.

### 4.9 Liste et Recherche des Courriers

L'application doit permettre de consulter les courriers selon les droits de l'utilisateur.

Filtres :

- recherche texte ;
- sens ;
- type de courrier ;
- statut ;
- priorite ;
- service ;
- date debut ;
- date fin ;
- courriers en retard.

Colonnes attendues :

- numero ;
- objet ;
- expediteur ;
- service destinataire ;
- statut ;
- priorite ;
- date de reception ;
- date d'echeance ;
- agent responsable ;
- actions.

Regles :

- un administrateur ou directeur peut voir un perimetre large ;
- un chef ou secretaire voit les courriers de son service ;
- un utilisateur standard voit ses courriers crees, affectes ou rattaches a son service ;
- les courriers confidentiels doivent etre proteges.

### 4.10 Detail d'un Courrier

La page detail doit fournir une vision complete du courrier.

Informations :

- identification ;
- objet ;
- expediteur ;
- destinataire ;
- service responsable ;
- statut ;
- priorite ;
- pieces jointes ;
- mouvements ;
- liens avec d'autres courriers ;
- actions disponibles selon le role.

Actions possibles :

- modifier ;
- ajouter piece jointe ;
- supprimer piece jointe ;
- dispatcher ;
- instruire ;
- valider ;
- cloturer ;
- ajouter un lien.

### 4.11 Dispatch Simple et Dispatch en Masse

Le dispatch permet d'orienter un ou plusieurs courriers vers un service ou un agent.

Champs :

- destinataire ;
- service destinataire ;
- agent ;
- instruction ;
- observations ;
- suite a donner.

Regles :

- seuls les profils autorises peuvent dispatcher ;
- un courrier finalise ne doit plus etre modifie ;
- le statut doit passer a DIS si le dispatch est effectue ;
- chaque dispatch doit creer un mouvement ;
- les erreurs de statut doivent etre affichees clairement.

### 4.12 Instruction, Validation et Cloture

Les responsables habilites doivent pouvoir instruire, valider ou cloturer les courriers.

Instruction :

- saisie d'une decision ou instruction ;
- changement de statut si autorise ;
- journalisation.

Validation :

- passage au statut ACC ;
- commentaire de validation ;
- journalisation.

Cloture :

- passage au statut CLO ;
- renseignement de la date de cloture ;
- interdiction de modification ulterieure.

### 4.13 Registre des Courriers

Le registre doit fournir une vue administrative des courriers.

Fonctionnalites :

- consultation des courriers ;
- filtrage par annee ;
- filtrage par mois ;
- pagination ;
- total des enregistrements ;
- respect des droits d'acces.

### 4.14 Tableaux de Bord

Chaque role doit disposer d'un tableau de bord adapte.

Agent Courrier :

- total des courriers ;
- courriers en cours ;
- courriers en retard ;
- courriers urgents ;
- activite recente.

Secretaire :

- total du service ;
- courriers non affectes ;
- courriers en retard ;
- traitements du mois ;
- charge des agents.

Chef de Service :

- courriers a instruire ;
- courriers a valider ;
- repartition par statut ;
- agents du service ;
- retards.

Directeur :

- volume global ;
- courriers ouverts ;
- retards ;
- clotures du mois ;
- repartition par service ;
- repartition par sens ;
- activite recente.

Administrateur :

- indicateurs globaux ;
- nombre d'utilisateurs ;
- nombre de services ;
- repartition par role ;
- derniers utilisateurs.

### 4.15 Notifications

Le systeme doit notifier les utilisateurs lors d'evenements importants.

Types :

- courrier assigne ;
- courrier echeant ou en retard ;
- courrier retourne ;
- rappel.

Regles :

- les notifications doivent etre consultables via l'interface ;
- un compteur doit afficher les notifications non lues ;
- l'indisponibilite du service notification ne doit pas casser l'interface ;
- les notifications doivent pouvoir etre marquees comme lues.

---

## 5. Workflow Cible

### 5.1 Creation par Tout Utilisateur

1. L'utilisateur se connecte.
2. Il ouvre la page d'enregistrement.
3. Il renseigne les informations du courrier.
4. Il ajoute eventuellement une piece jointe.
5. Il peut utiliser l'analyse IA/OCR.
6. Il valide la creation.
7. Le systeme genere le numero.
8. Le statut initial est ENR.
9. Le courrier est automatiquement affecte a un agent courrier actif.
10. Les mouvements CREATION et AFFECTATION sont enregistres.

### 5.2 Traitement par Agent Courrier

1. L'agent courrier consulte les courriers qui lui sont affectes.
2. Il verifie les informations.
3. Il corrige ou complete si necessaire.
4. Il dispatch vers le service concerne.
5. Le statut passe a DIS.
6. Le mouvement DISPATCH est enregistre.

### 5.3 Traitement par Service

1. Le service destinataire consulte le courrier.
2. Le chef ou responsable donne une instruction.
3. Le courrier est traite.
4. Il peut etre valide.
5. Il peut etre cloture.

### 5.4 Cloture

1. Le responsable habilite cloture le courrier.
2. Le statut passe a CLO.
3. La date de cloture est renseignee.
4. Les modifications sont bloquees.

---

## 6. Exigences Techniques

### 6.1 Architecture

L'application doit etre developpee avec une architecture modulaire Django.

Modules principaux :

- `accounts` : utilisateurs et authentification ;
- `courriers` : logique courrier ;
- `dashboard` : tableaux de bord ;
- `mouvements` : journal de tracabilite ;
- `notifications` : alertes ;
- `organisations` : services ;
- `parametrage` : referentiels ;
- `core` : permissions et gestion globale.

### 6.2 Technologies

Backend :

- Python 3.10+ ;
- Django 5 ;
- Django REST Framework ;
- PostgreSQL ;
- SimpleJWT ;
- django-filter ;
- django-environ.

Frontend :

- HTML ;
- CSS ;
- Bootstrap ;
- Bootstrap Icons ;
- JavaScript natif.

OCR / IA :

- pytesseract ;
- Tesseract OCR ;
- pypdfium2 pour les PDF ;
- backends optionnels OCR.space et Azure Vision.

Deploiement :

- Gunicorn ;
- Whitenoise ;
- Redis et Celery optionnels.

### 6.3 Base de Donnees

La base principale doit etre PostgreSQL.

Entites principales :

- Utilisateur ;
- Service ;
- Courrier ;
- Expediteur ;
- Destinataire ;
- PieceJointe ;
- LienCourrier ;
- MouvementCourrier ;
- TypeCourrier ;
- StatutCourrier ;
- Priorite ;
- Notification ;
- JournalConnexion ;
- TokenReinit.

### 6.4 API REST

L'application doit exposer une API REST securisee sous `/api/v1/`.

Endpoints principaux :

- authentification ;
- profil courant ;
- utilisateurs ;
- courriers ;
- dispatch ;
- validation ;
- cloture ;
- statistiques ;
- notifications ;
- parametrage.

Regles API :

- authentification obligatoire sauf login ;
- reponses JSON coherentes ;
- erreurs normalisees ;
- pagination ;
- recherche ;
- filtres ;
- permissions par role.

---

## 7. Exigences de Securite

### 7.1 Authentification

- authentification obligatoire pour acceder a l'application ;
- mot de passe hache ;
- reinitialisation par token temporaire ;
- journalisation des connexions ;
- gestion des comptes inactifs.

### 7.2 Autorisation

Les droits doivent etre controles par role.

Principes :

- un utilisateur ne voit que ce qu'il est autorise a voir ;
- les actions sensibles sont limitees ;
- les courriers confidentiels doivent etre proteges ;
- l'administration est reservee aux administrateurs ;
- les actions doivent etre verifiees cote serveur, pas seulement cote interface.

### 7.3 Protection des Fichiers

- limitation de taille ;
- controle d'extension ;
- stockage dans un dossier media ;
- suppression controlee ;
- conservation des metadonnees.

### 7.4 Gestion des Erreurs

Le systeme doit disposer d'une gestion globale des erreurs :

- page 400 ;
- page 403 ;
- page 404 ;
- page 500 ;
- reponses JSON pour les API ;
- journalisation des exceptions ;
- messages utilisateurs clairs ;
- aucun traceback affiche en production ;
- l'indisponibilite d'un module secondaire ne doit pas bloquer toute l'application.

---

## 8. Exigences d'Ergonomie

### 8.1 Interface

L'interface doit etre claire, professionnelle et adaptee a un usage administratif quotidien.

Principes :

- navigation laterale ;
- boutons explicites ;
- icones utiles ;
- formulaires lisibles ;
- messages d'erreur visibles ;
- tableaux filtrables ;
- actions disponibles selon le role ;
- design coherent.

### 8.2 Accessibilite

L'application doit respecter les principes de base :

- libelles de champs ;
- contrastes suffisants ;
- navigation clavier pour les zones importantes ;
- textes alternatifs pour images ;
- messages d'erreur explicites.

### 8.3 Performance Perçue

- chargement rapide des pages ;
- pagination des listes ;
- indicateur de chargement pour l'analyse IA ;
- messages de progression ;
- pas de blocage complet en cas d'erreur secondaire.

---

## 9. Contraintes et Regles de Gestion

### 9.1 Regles de Numerotation

Le numero du courrier doit etre genere automatiquement selon :

- le sens ;
- l'annee ;
- un compteur annuel.

Exemples :

- ENT-2026-00001 ;
- SOR-2026-00001 ;
- INT-2026-00001.

### 9.2 Regles de Statut

- un courrier cree commence a ENR ;
- un courrier dispatche passe a DIS ;
- un courrier valide passe a ACC ;
- un courrier cloture passe a CLO ;
- un statut final interdit les modifications.

### 9.3 Regles de Delai

Les priorites peuvent determiner un delai de traitement.

Exemples :

- Normal : 15 jours ;
- Moyenne : 10 jours ;
- Urgence : 3 jours.

Un courrier est en retard si :

- il a une date d'echeance ;
- son statut n'est pas final ;
- la date courante depasse la date d'echeance.

### 9.4 Regles de Tracabilite

Chaque action significative doit produire un mouvement.

Actions :

- creation ;
- scan ;
- dispatch ;
- affectation ;
- instruction ;
- consultation ;
- commentaire ;
- validation ;
- cloture ;
- ajout de piece jointe ;
- suppression de piece jointe ;
- creation de lien.

Les mouvements doivent etre immuables :

- pas de modification ;
- pas de suppression.

---

## 10. Exigences de Robustesse

### 10.1 Robustesse Applicative

L'application doit continuer a fonctionner meme si une fonctionnalite secondaire echoue.

Exemples :

- erreur notifications : la page doit rester utilisable ;
- erreur OCR : le formulaire doit rester utilisable ;
- fichier illisible : message clair ;
- statut absent : erreur metier lisible ;
- service invalide via API : reponse 400 propre ;
- agent indisponible : message clair.

### 10.2 Robustesse API

Toutes les API doivent retourner un format coherent.

Format d'erreur recommande :

```json
{
  "success": false,
  "status_code": 400,
  "error": "Message lisible",
  "details": {}
}
```

### 10.3 Journalisation

Les erreurs doivent etre journalisees cote serveur.

Informations utiles :

- chemin ;
- utilisateur si disponible ;
- type d'erreur ;
- message ;
- contexte technique ;
- date.

---

## 11. Livrables Attendus

### 11.1 Livrables Fonctionnels

- application web complete ;
- module authentification ;
- module utilisateurs ;
- module courriers ;
- module dispatch ;
- module registre ;
- module tableaux de bord ;
- module parametrage ;
- module notifications ;
- module OCR/IA ;
- API REST.

### 11.2 Livrables Techniques

- code source ;
- fichiers de configuration ;
- migrations ;
- fixtures initiales ;
- requirements ;
- documentation d'installation ;
- documentation OCR ;
- cahier des charges ;
- tests manuels ou automatises essentiels.

### 11.3 Documentation

La documentation doit couvrir :

- installation ;
- configuration `.env` ;
- base de donnees ;
- chargement fixtures ;
- creation superutilisateur ;
- lancement serveur ;
- configuration Tesseract ;
- utilisation de l'analyse IA ;
- roles et droits ;
- procedures d'exploitation.

---

## 12. Critères d'Acceptation

Le projet sera considere comme conforme si les criteres suivants sont remplis.

### 12.1 Authentification

- un utilisateur actif peut se connecter ;
- un utilisateur inactif est bloque ;
- un utilisateur peut modifier son profil ;
- l'administrateur peut gerer les utilisateurs.

### 12.2 Creation de Courrier

- tout utilisateur connecte peut acceder a la page d'enregistrement ;
- tout utilisateur connecte peut creer un courrier ;
- le courrier cree a un numero automatique ;
- le statut initial est ENR ;
- le createur est renseigne ;
- un agent courrier actif est affecte automatiquement ;
- un mouvement de creation est cree ;
- un mouvement d'affectation est cree.

### 12.3 Analyse IA

- une image peut etre analysee ;
- un PDF peut etre analyse ;
- les metadonnees detectees s'affichent ;
- les champs sont remplis automatiquement quand possible ;
- un document illisible affiche une erreur claire sans planter la page.

### 12.4 Dispatch

- un utilisateur autorise peut dispatcher un courrier ;
- le statut passe a DIS ;
- le mouvement est journalise ;
- le dispatch en masse fonctionne.

### 12.5 Suivi

- la liste affiche les courriers selon les droits ;
- les filtres fonctionnent ;
- le registre fonctionne ;
- les tableaux de bord affichent les indicateurs.

### 12.6 Securite

- les pages protegees exigent une connexion ;
- les permissions sont appliquees cote serveur ;
- les erreurs ne revelent pas de details sensibles en production ;
- les API retournent des erreurs JSON propres.

---

## 13. Evolutions Futures

Les evolutions suivantes peuvent etre envisagees :

- signature electronique ;
- parapheur numerique ;
- scan batch ;
- code-barres ou QR code courrier ;
- integration email entrant ;
- export Excel/PDF des registres ;
- statistiques avancees ;
- workflow configurable ;
- notifications email avancees ;
- archivage legal ;
- moteur de recherche plein texte ;
- reconnaissance OCR amelioree par modele IA ;
- application mobile ;
- audit de securite.

---

## 14. Conclusion

Le projet GED Courriers constitue une plateforme complete de gestion administrative des courriers. Il repond a des besoins essentiels de tracabilite, de rapidite, de securite et de pilotage.

La regle centrale du workflow cible est que tout utilisateur authentifie peut creer un courrier, et que tout courrier cree est automatiquement envoye a un agent courrier actif. Cette regle simplifie l'entree des demandes tout en maintenant un controle operationnel par le service courrier.

La solution doit rester robuste, claire et evolutive. Elle doit offrir une experience fluide aux utilisateurs tout en garantissant une gestion stricte des droits, des documents, des statuts et des mouvements.
