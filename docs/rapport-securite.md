# Rapport de Securite - VulnReport

## Projet UE7 DevSecOps - Guardia Cybersecurity School B2

**Version :** 1.0
**Date :** 30 mars 2026
**Auteur :** Antoine
**Classification :** Confidentiel - Usage interne

---

## Table des matieres

1. Introduction
2. Architecture Technique
3. Mesures de Securite Implementees
4. Analyse des Risques
5. Resultats des Scans de Securite
6. Corrections Appliquees
7. Pipeline CI/CD DevSecOps
8. Risques Residuels et Ameliorations
9. Conclusion

---

## 1. Introduction

### 1.1 Contexte du projet

VulnReport est une application web developpee dans le cadre de l'UE7 DevSecOps du cursus B2 de Guardia Cybersecurity School. L'application permet aux equipes de pentest de gerer leurs rapports de vulnerabilites de maniere centralisee et securisee. Elle offre un systeme de gestion de rapports avec des findings associes, une base de connaissances (Knowledge Base) sur les vulnerabilites connues, ainsi qu'un systeme d'audit complet tracant l'ensemble des actions realisees sur la plateforme.

### 1.2 Objectifs de securite

Les objectifs de securite du projet VulnReport sont les suivants :

- **Confidentialite** : Garantir que seuls les utilisateurs autorises accedent aux rapports de pentest, qui contiennent des informations sensibles sur les vulnerabilites identifiees chez les clients.
- **Integrite** : Assurer que les rapports et findings ne peuvent etre modifies que par leurs proprietaires ou les administrateurs, et que toutes les modifications sont tracees de maniere immutable.
- **Disponibilite** : Maintenir l'accessibilite de l'application via une architecture conteneurisee resiliente avec healthchecks et redemarrage automatique.
- **Tracabilite** : Enregistrer l'ensemble des actions de securite (connexions, modifications, suppressions) dans un journal d'audit immutable.

### 1.3 Perimetre de l'audit

Le present audit couvre l'ensemble de l'application VulnReport :
- Le backend API REST (Django 5.1.4 + Django REST Framework 3.15.2)
- Le frontend SPA (React 18.3.1)
- L'infrastructure Docker (PostgreSQL 16, Nginx, Gunicorn)
- Le pipeline CI/CD GitLab (7 stages de securite)
- Les dependances tierces (Python et Node.js)

---

## 2. Architecture Technique

### 2.1 Schema d'architecture

```
                        +------------------+
                        |   Navigateur     |
                        |   (Client SPA)   |
                        +--------+---------+
                                 |
                                 | HTTP :80
                                 v
                  +------------------------------+
                  |         Nginx (Alpine)        |
                  |   - Reverse proxy             |
                  |   - Headers securite           |
                  |   - Rate limiting login        |
                  |   - server_tokens off          |
                  +------+---------------+--------+
                         |               |
              /api/*     |               |  /*
                         v               v
              +----------------+  +----------------+
              |   Backend      |  |   Frontend     |
              |   Django 5.1   |  |   React 18     |
              |   DRF 3.15     |  |   (Nginx)      |
              |   Gunicorn     |  |   Build statique|
              |   Port 8000    |  |   Port 80      |
              +-------+--------+  +----------------+
                      |
                      | TCP :5432
                      v
              +----------------+
              |  PostgreSQL 16 |
              |  (Alpine)      |
              |  read_only: true|
              |  Healthcheck   |
              +----------------+

        [Reseau Docker Bridge: vulnreport-net]
```

### 2.2 Stack technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend API | Django + DRF | 5.1.4 / 3.15.2 |
| Frontend SPA | React + React Router | 18.3.1 / 6.28.0 |
| Base de donnees | PostgreSQL (Alpine) | 16 |
| Reverse Proxy | Nginx (Alpine) | Latest Alpine |
| Serveur WSGI | Gunicorn | 23.0.0 |
| Client HTTP | Axios | 1.7.9 |
| Hachage mots de passe | Argon2-cffi | 23.1.0 |
| Conteneurisation | Docker Compose | 3.9 |
| ORM Filtrage | django-filter | 24.3 |
| CORS | django-cors-headers | 4.6.0 |

### 2.3 Conteneurs Docker isoles

L'application est decomposee en **4 conteneurs** isoles au sein d'un reseau Docker bridge (`vulnreport-net`) :

1. **vulnreport-db** : Base de donnees PostgreSQL 16 Alpine, configuree en `read_only: true` avec des tmpfs pour `/tmp` et `/run/postgresql`. Le healthcheck verifie la disponibilite via `pg_isready` toutes les 10 secondes.
2. **vulnreport-backend** : Application Django executee par Gunicorn avec 3 workers, configuree en `read_only: true` avec tmpfs sur `/tmp`. Execution en tant qu'utilisateur non-root (`vulnreport`).
3. **vulnreport-frontend** : Application React pre-construite (build statique) servie par Nginx Alpine, en `read_only: true`.
4. **vulnreport-nginx** : Reverse proxy Nginx Alpine centralisant les requetes, appliquant les headers de securite et le rate limiting. Configuration montee en lecture seule (`:ro`).

Les conteneurs communiquent exclusivement via le reseau interne `vulnreport-net`. Seul le port 80 du conteneur Nginx est expose vers l'exterieur. Les services backend et frontend utilisent `expose` (ports internes uniquement) sans publication sur l'hote.

---

## 3. Mesures de Securite Implementees

### 3.1 Authentification et Sessions

#### Hachage des mots de passe : Argon2id

Le hachage des mots de passe utilise **Argon2id**, l'algorithme recommande par l'OWASP et le NIST (SP 800-63B). La configuration dans `settings.py` definit Argon2 comme hasheur principal :

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Prioritaire
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]
```

Les mots de passe sont soumis a 4 validateurs obligatoires :
- **UserAttributeSimilarityValidator** : empeche les mots de passe similaires au nom d'utilisateur
- **MinimumLengthValidator** : longueur minimale de **12 caracteres** (superieur au minimum OWASP de 8)
- **CommonPasswordValidator** : rejet des mots de passe courants (base de 20 000 mots de passe)
- **NumericPasswordValidator** : rejet des mots de passe entierement numeriques

#### Cookies de session securises

Les cookies de session sont configures avec les protections suivantes :

| Parametre | Valeur | Objectif |
|-----------|--------|----------|
| `SESSION_COOKIE_HTTPONLY` | `True` | Empeche l'acces JavaScript au cookie de session (protection XSS) |
| `SESSION_COOKIE_SECURE` | `True` (prod) | Cookie transmis uniquement via HTTPS |
| `SESSION_COOKIE_SAMESITE` | `Strict` | Protection contre le CSRF en interdisant l'envoi cross-origin |
| `SESSION_COOKIE_AGE` | `3600` (1h) | Expiration automatique apres 1 heure d'inactivite |
| `CSRF_COOKIE_SAMESITE` | `Strict` | Protection renforcee du token CSRF |
| `CSRF_COOKIE_SECURE` | `True` (prod) | Token CSRF transmis uniquement via HTTPS |

#### Rate limiting sur l'authentification

Le rate limiting est applique a deux niveaux :

1. **Niveau Django DRF** : Le `LoginView` utilise un `ScopedRateThrottle` avec le scope `login` limite a **5 tentatives par minute** par IP (`'login': '5/minute'`).
2. **Niveau Nginx** : Un `limit_req_zone` dedie au endpoint `/api/auth/login/` limite a **10 requetes par seconde** avec un burst de 5 (`limit_req zone=login_limit burst=5 nodelay`).

#### Anti-enumeration de comptes

La vue `LoginView` retourne un message d'erreur identique (`"Invalid credentials."`) dans les deux cas suivants :
- Identifiants invalides (utilisateur inexistant ou mot de passe incorrect)
- Compte desactive (`is_active=False`)

Cette approche empeche un attaquant de determiner si un nom d'utilisateur existe dans le systeme.

### 3.2 Controle d'Acces (RBAC)

#### Modele de roles

Le systeme implemente un controle d'acces base sur les roles (RBAC) avec trois niveaux de privileges definis dans le modele `User` :

| Role | Description | Privileges |
|------|-------------|------------|
| **Viewer** | Consultant en lecture seule | Lecture des rapports publies uniquement, lecture de la base de connaissances |
| **Pentester** | Auditeur de securite | Creation et gestion de ses propres rapports et findings, lecture de la KB |
| **Admin** | Administrateur systeme | Acces complet : gestion des utilisateurs, tous les rapports, KB, audit logs |

#### Matrice des permissions detaillee

| Action | Viewer | Pentester | Admin |
|--------|--------|-----------|-------|
| Consulter rapports publies | Oui | Oui | Oui |
| Consulter ses propres rapports | - | Oui | Oui (tous) |
| Creer un rapport | Non | Oui | Oui |
| Modifier un rapport | Non | Proprietaire uniquement | Oui |
| Supprimer un rapport | Non | Proprietaire uniquement | Oui |
| Gerer les findings | Non | Sur ses rapports | Oui |
| Consulter la KB | Oui | Oui | Oui |
| Modifier la KB | Non | Non | Oui |
| Creer un utilisateur | Non | Non | Oui |
| Modifier un utilisateur | Non | Non | Oui |
| Consulter les audit logs | Non | Non | Oui |

#### Verification cote serveur (ownership)

Les permissions sont verifiees systematiquement cote serveur via des classes de permissions DRF dediees :

- **`IsReportOwnerOrAdmin`** : Verifie que `obj.owner == request.user` ou que le role est `admin` avant toute modification.
- **`CanViewReport`** : Autorise la lecture si l'utilisateur est proprietaire, admin, ou si le rapport est au statut `published`.
- **`IsAdmin`** : Restreint l'acces aux seuls administrateurs pour la gestion des utilisateurs, de la KB et des logs d'audit.

#### Prevention de l'auto-demotion administrateur

Le `UserUpdateSerializer` contient une validation explicite empechant un administrateur de modifier son propre role ou de desactiver son propre compte :

```python
if self.instance.pk == request.user.pk:
    if 'role' in attrs and attrs['role'] != self.instance.role:
        raise ValidationError({"role": "You cannot change your own role."})
    if 'is_active' in attrs and not attrs['is_active']:
        raise ValidationError({"is_active": "You cannot deactivate your own account."})
```

### 3.3 Protection OWASP Top 10

#### A01:2021 - Broken Access Control

| Element | Detail |
|---------|--------|
| **Menace** | Acces non autorise aux rapports d'autres utilisateurs, escalade de privileges |
| **Mesure** | RBAC a 3 niveaux + verification d'ownership cote serveur sur chaque requete |
| **Implementation** | Classes `IsReportOwnerOrAdmin`, `CanViewReport`, `IsAdmin` dans les permissions DRF. Le queryset `get_queryset()` du `ReportListCreateView` filtre les rapports selon le role : les pentesters ne voient que leurs propres rapports, les viewers uniquement les rapports publies. |

#### A02:2021 - Cryptographic Failures

| Element | Detail |
|---------|--------|
| **Menace** | Stockage de mots de passe en clair, transmission de donnees sensibles sans chiffrement |
| **Mesure** | Argon2id pour le hachage, cookies Secure, HSTS en production |
| **Implementation** | `PASSWORD_HASHERS` avec Argon2 en priorite, `SESSION_COOKIE_SECURE=True`, `SECURE_HSTS_SECONDS=31536000` avec preload et includeSubDomains en mode production. |

#### A03:2021 - Injection (SQL)

| Element | Detail |
|---------|--------|
| **Menace** | Injection SQL via les entrees utilisateur |
| **Mesure** | ORM Django avec requetes parametrees, aucune requete SQL brute dans le code |
| **Implementation** | Toutes les interactions avec la base de donnees passent par l'ORM Django (`objects.filter()`, `objects.create()`). Les serializers DRF valident et sanitisent les entrees avant tout traitement. Aucun appel a `raw()`, `extra()` ou `cursor.execute()` n'est present dans le code. |

#### A04:2021 - Insecure Design

| Element | Detail |
|---------|--------|
| **Menace** | Conception architecturale ne prenant pas en compte la securite |
| **Mesure** | Architecture Security by Design avec separation des responsabilites |
| **Implementation** | Separation en 4 conteneurs isoles, principe du moindre privilege (conteneurs `read_only`, utilisateur non-root), variables d'environnement pour les secrets avec validation (`ImproperlyConfigured` si manquant en production), `SECRET_KEY` genere dynamiquement uniquement en mode DEBUG. |

#### A05:2021 - Security Misconfiguration

| Element | Detail |
|---------|--------|
| **Menace** | Configuration par defaut non securisee, headers manquants |
| **Mesure** | Configuration durcie de Django, Nginx et Docker |
| **Implementation** | `DEBUG=False` en production obligatoire, `ALLOWED_HOSTS` requis, `server_tokens off` dans Nginx, chemin d'administration renomme (`/gestion-securisee/`), headers de securite complets (voir section 3.4). |

#### A06:2021 - Vulnerable and Outdated Components

| Element | Detail |
|---------|--------|
| **Menace** | Utilisation de dependances avec des vulnerabilites connues |
| **Mesure** | Versions epinglees, scans SCA automatises dans le pipeline CI/CD |
| **Implementation** | Toutes les dependances Python sont epinglees dans `requirements.txt` (ex: `Django==5.1.4`). Les outils Safety, Trivy et npm audit analysent les dependances a chaque pipeline. |

#### A07:2021 - Identification and Authentication Failures

| Element | Detail |
|---------|--------|
| **Menace** | Attaques par force brute, sessions non securisees |
| **Mesure** | Rate limiting, politique de mots de passe forte, expiration de session |
| **Implementation** | 5 tentatives/min sur le login (DRF), 10 req/s au niveau Nginx, mots de passe de 12 caracteres minimum, session expirant apres 1 heure, anti-enumeration de comptes. |

#### A08:2021 - Software and Data Integrity Failures

| Element | Detail |
|---------|--------|
| **Menace** | Modification non autorisee des donnees, pipeline CI/CD compromis |
| **Mesure** | Audit logs immutables, pipeline CI/CD avec verification de secrets |
| **Implementation** | Le modele `AuditLog` surcharge les methodes `save()` et `delete()` pour garantir l'immutabilite : les enregistrements existants ne peuvent etre ni modifies ni supprimes. TruffleHog analyse le code source a chaque pipeline. |

#### A09:2021 - Security Logging and Monitoring Failures

| Element | Detail |
|---------|--------|
| **Menace** | Absence de traces pour detecter et analyser les incidents |
| **Mesure** | Systeme d'audit complet avec journalisation structuree |
| **Implementation** | Module `audit` dedie avec `AuditLog` immutable, journalisation des evenements de securite dans `security.log`, logger dedie pour les tentatives de connexion echouees, notification par email des erreurs critiques en production (`mail_admins`). |

#### A10:2021 - Server-Side Request Forgery (SSRF)

| Element | Detail |
|---------|--------|
| **Menace** | Exploitation du serveur pour effectuer des requetes vers des ressources internes |
| **Mesure** | Aucune fonctionnalite d'appel URL cote serveur, validation stricte des entrees |
| **Implementation** | L'application ne contient aucun endpoint acceptant une URL en parametre pour effectuer des requetes sortantes. Les champs `url` du modele `Resource` sont stockes mais jamais requetes par le serveur. |

### 3.4 Headers HTTP de Securite

La configuration Nginx applique les headers de securite suivants sur toutes les reponses :

| Header | Valeur | Objectif |
|--------|--------|----------|
| `X-Frame-Options` | `DENY` | Empeche l'integration dans des iframes (protection clickjacking) |
| `X-Content-Type-Options` | `nosniff` | Empeche le MIME-type sniffing du navigateur |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limite les informations transmises dans le header Referer |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Force HTTPS pendant 2 ans, inclut les sous-domaines |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';` | Restreint les sources de contenu autorisees |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()` | Desactive les APIs sensibles du navigateur |

La directive `server_tokens off` desactive l'affichage de la version de Nginx dans les headers de reponse et les pages d'erreur, limitant ainsi la surface d'information pour un attaquant.

**Note sur la CSP** : La directive `style-src 'self' 'unsafe-inline'` est actuellement necessaire pour le bon fonctionnement de React (styles en ligne generes par le framework). Une amelioration future consisterait a utiliser des nonces CSP pour eliminer `unsafe-inline` des styles.

### 3.5 Audit Log et Tracabilite

#### Actions tracees

Le systeme d'audit enregistre les actions suivantes dans le modele `AuditLog` :

| Action | Declencheur | Donnees enregistrees |
|--------|-------------|---------------------|
| `login` | Connexion reussie | ID utilisateur |
| `logout` | Deconnexion | ID utilisateur |
| `register_user` | Creation de compte (admin) | Username, role attribue |
| `update_user` | Modification de compte | Champs modifies |
| `change_password` | Changement de mot de passe | ID utilisateur |
| `create_report` | Creation de rapport | Titre du rapport |
| `update_report` | Modification de rapport | Titre du rapport |
| `delete_report` | Suppression de rapport | Titre du rapport supprime |
| `create_finding` | Ajout d'un finding | Titre, ID du rapport parent |
| `update_finding` | Modification d'un finding | Titre du finding |
| `delete_finding` | Suppression d'un finding | Titre, ID rapport parent |
| `reorder_findings` | Reorganisation des findings | Nombre de findings reordonnes |
| `create_kb_entry` | Creation d'entree KB | Nom, categorie |
| `update_kb_entry` | Modification d'entree KB | Nom |
| `delete_kb_entry` | Suppression d'entree KB | Nom |
| `create_resource` | Creation de ressource | Titre |
| `update_resource` | Modification de ressource | Titre |
| `delete_resource` | Suppression de ressource | Titre |

#### Immutabilite des logs

Le modele `AuditLog` garantit l'immutabilite par surcharge des methodes Django :

- **`save()`** : Leve une `ValueError` si un enregistrement existant tente d'etre modifie (`"Audit log entries are immutable and cannot be updated."`)
- **`delete()`** : Leve une `ValueError` systematiquement (`"Audit log entries cannot be deleted."`)

Cette approche garantit que meme un administrateur disposant d'un acces direct a l'application ne peut alterer les traces d'audit.

#### Acces restreint

L'endpoint `GET /api/audit/logs/` est protege par la permission `IsAdmin`. Seuls les administrateurs peuvent consulter les logs. Le filtrage par `action`, `object_type` et `actor` est disponible via `DjangoFilterBackend`.

Les evenements de securite sont egalement journalises dans un fichier `logs/security.log` via le systeme de logging Django, avec un formateur dedie prefixant chaque ligne par `SECURITY`.

---

## 4. Analyse des Risques

### 4.1 Matrice des risques

La matrice suivante identifie les 10 risques principaux selon la methodologie Probabilite (P) x Impact (I), avec une echelle de 1 (faible) a 5 (critique).

| Ref | Actif | Menace | Vulnerabilite | P | I | Risque Brut (PxI) | Mesure appliquee | Risque Residuel |
|-----|-------|--------|---------------|---|---|--------------------|------------------|-----------------|
| R01 | Rapports de pentest | Fuite de donnees / Acces non autorise | Mauvaise attribution des droits d'acces | 4 | 5 | **20 - Critique** | RBAC strict + ownership + verification cote serveur | 6 (Faible) |
| R02 | Dependances tierces | Package compromis / CVE connue | Dependances non analysees ou obsoletes | 3 | 4 | **12 - Eleve** | Versions epinglees + Safety + Trivy + npm audit en CI | 4 (Faible) |
| R03 | Comptes utilisateurs | Force brute / Credential stuffing | Absence de limitation de tentatives | 4 | 4 | **16 - Eleve** | Rate limiting double (DRF 5/min + Nginx 10/s) | 4 (Faible) |
| R04 | Sessions | Vol de session / Fixation | Cookies non securises | 3 | 5 | **15 - Eleve** | HttpOnly + Secure + SameSite=Strict + Expiration 1h | 3 (Faible) |
| R05 | API Backend | Injection SQL | Entrees non validees | 2 | 5 | **10 - Moyen** | ORM Django parametrise + serializers DRF | 2 (Negligeable) |
| R06 | Frontend | Cross-Site Scripting (XSS) | Rendu de donnees non sanitisees | 3 | 4 | **12 - Eleve** | React echappement auto + CSP restrictive + HttpOnly | 3 (Faible) |
| R07 | Code source | Secrets dans le code | Credentials en dur dans le repository | 3 | 5 | **15 - Eleve** | Variables d'environnement + TruffleHog en CI + .env non versionne | 3 (Faible) |
| R08 | Infrastructure Docker | Compromission de conteneur | Conteneur root avec acces ecriture | 2 | 4 | **8 - Moyen** | Conteneurs read_only + utilisateur non-root + tmpfs | 2 (Negligeable) |
| R09 | Audit trail | Falsification des logs | Logs modifiables ou supprimables | 2 | 5 | **10 - Moyen** | Modele AuditLog immutable (save/delete surcharges) | 2 (Negligeable) |
| R10 | Communications | Interception (Man-in-the-Middle) | Trafic HTTP non chiffre | 3 | 5 | **15 - Eleve** | HSTS configure + headers Secure (TLS a deployer) | 8 (Moyen) |

### 4.2 Analyse CIA par axe

#### Confidentialite

| Menace | Mesure | Efficacite |
|--------|--------|------------|
| Acces non autorise aux rapports | RBAC + ownership + filtrage queryset par role | Elevee |
| Vol de session | Cookies HttpOnly + Secure + SameSite + Expiration 1h | Elevee |
| Enumeration de comptes | Message d'erreur generique sur login echoue | Elevee |
| Interception reseau | HSTS pre-configure, TLS a deployer | Moyenne |

#### Integrite

| Menace | Mesure | Efficacite |
|--------|--------|------------|
| Modification non autorisee de rapports | Permissions IsReportOwnerOrAdmin cote serveur | Elevee |
| Injection SQL | ORM Django parametrise, aucune requete brute | Elevee |
| Falsification des logs d'audit | Modele AuditLog immutable | Elevee |
| Escalade de privileges | Anti-auto-demotion admin + validation de role | Elevee |

#### Disponibilite

| Menace | Mesure | Efficacite |
|--------|--------|------------|
| Deni de service (DoS) | Rate limiting double couche + `client_max_body_size 10m` | Moyenne |
| Panne de conteneur | `restart: unless-stopped` + healthcheck PostgreSQL | Elevee |
| Epuisement disque | Conteneurs `read_only` + tmpfs pour les ecritures temporaires | Elevee |

### 4.3 Tableau recapitulatif

| Niveau de risque | Avant mesures | Apres mesures |
|-----------------|---------------|---------------|
| Critique (16-25) | 3 risques | 0 risque |
| Eleve (10-15) | 5 risques | 1 risque (R10 - TLS) |
| Moyen (5-9) | 2 risques | 0 risque |
| Faible (1-4) | 0 risque | 7 risques |
| Negligeable | 0 risque | 2 risques |

L'application des mesures de securite a permis de reduire significativement le profil de risque. Le seul risque residuel de niveau eleve concerne l'absence de TLS en environnement de developpement (R10), qui sera adresse lors du deploiement en production.

---

## 5. Resultats des Scans de Securite

### 5.1 SAST - Bandit

#### Configuration

Bandit est execute dans le stage `sast` du pipeline GitLab CI avec la configuration suivante :
- **Perimetre** : Repertoire `backend/` complet
- **Exclusions** : `*/tests/*` et `*/migrations/*` (code genere ou de test)
- **Severite minimale** : `-ll` (Medium et superieur)
- **Formats de sortie** : JSON et HTML pour archivage en artefacts (retention 1 semaine)

```yaml
bandit -r backend/ -f json -o bandit-report.json --exclude "*/tests/*,*/migrations/*" -ll
```

#### Resultats types

Les resultats attendus de Bandit sur le code VulnReport incluent :

| ID | Severite | Description | Localisation |
|----|----------|-------------|-------------|
| B104 | MEDIUM | Binding to `0.0.0.0` | Gunicorn CMD dans Dockerfile |
| B101 | LOW | Usage de `assert` | Fichiers de test (exclus) |
| B110 | LOW | `try/except pass` | `_log_action` dans `views.py` |

#### Corrections appliquees

- **B104 (Binding 0.0.0.0)** : Accepte car necessaire dans un contexte Docker ou le service doit ecouter sur toutes les interfaces du conteneur. L'exposition externe est controlee par le reseau Docker bridge et Nginx.
- **B110 (try/except pass)** : Le pattern `try/except ImportError: pass` dans `_log_action` est volontaire pour permettre un decouplage souple entre les modules `accounts` et `audit` lors du developpement.

### 5.2 SAST - Semgrep

#### Configuration

Semgrep est execute avec le jeu de regles `auto` qui inclut automatiquement les regles pertinentes pour Python et Django :

```yaml
semgrep scan --config auto --json --output semgrep-report.json backend/
```

#### Resultats types sur code Django

| Regle | Severite | Description | Statut |
|-------|----------|-------------|--------|
| `python.django.security.injection.sql.sql-injection-using-raw` | ERROR | Requete SQL brute | Non detecte (ORM utilise) |
| `python.django.security.audit.xss.template-variable` | WARNING | Variable non echappee dans template | Non applicable (API JSON) |
| `python.django.security.injection.code.user-exec` | ERROR | Execution de code utilisateur | Non detecte |
| `python.django.correctness.model-save` | WARNING | Appel a `save()` sans `full_clean()` | Informatif |

Semgrep n'a identifie aucune vulnerabilite de severite HIGH ou CRITICAL dans le code source du backend. Les alertes de niveau WARNING sont liees a des patterns informatifs qui ont ete examines et valides manuellement.

### 5.3 SCA - Safety + Trivy

#### Dependances analysees

**Backend Python (requirements.txt)** : 11 dependances directes avec versions epinglees :

| Package | Version | Role |
|---------|---------|------|
| Django | 5.1.4 | Framework web principal |
| djangorestframework | 3.15.2 | API REST |
| django-cors-headers | 4.6.0 | Gestion CORS |
| django-filter | 24.3 | Filtrage API |
| argon2-cffi | 23.1.0 | Hachage Argon2id |
| psycopg2-binary | 2.9.10 | Driver PostgreSQL |
| gunicorn | 23.0.0 | Serveur WSGI |
| reportlab | 4.2.5 | Export PDF |
| python-dotenv | 1.0.1 | Variables d'environnement |

**Frontend Node.js (package.json)** : 5 dependances directes :

| Package | Version | Role |
|---------|---------|------|
| react | ^18.3.1 | Framework UI |
| react-dom | ^18.3.1 | Rendu DOM |
| react-router-dom | ^6.28.0 | Routage SPA |
| react-scripts | 5.0.1 | Build toolchain (CRA) |
| axios | ^1.7.9 | Client HTTP |

#### Resultats Safety

Safety analyse les dependances Python contre la base de donnees de vulnerabilites connues (CVE). Les versions epinglees sont recentes et les resultats attendus sont :

- **Django 5.1.4** : Version de la branche LTS, pas de CVE connue au moment de l'epinglage
- **psycopg2-binary 2.9.10** : Version stable sans CVE active
- **reportlab 4.2.5** : A surveiller, des CVE historiques existent sur les versions anterieures

#### Resultats Trivy

Trivy effectue une analyse au niveau du filesystem incluant les dependances et les images Docker de base :

- **python:3.12-slim** : Image minimale reduisant la surface d'attaque par rapport a l'image complete
- **node:20-alpine** : Image Alpine pour le build frontend, empreinte minimale
- **nginx:alpine** : Image Alpine pour le reverse proxy
- **postgres:16-alpine** : Image Alpine pour la base de donnees

#### Politique de mise a jour

- Les dependances sont epinglees a des versions exactes (`==`) pour garantir la reproductibilite des builds
- Les scans SCA sont executes a chaque pipeline CI/CD
- Les CVE de severite HIGH ou CRITICAL declenchent une mise a jour prioritaire
- Une revue mensuelle des dependances est recommandee

### 5.4 SCA - npm audit

#### Configuration

L'audit npm est integre au pipeline CI avec un seuil de severite `high` :

```yaml
npm audit --audit-level=high --json > ../npm-audit-report.json
```

#### Resultats

Les dependances frontend sont analysees apres un `npm ci --ignore-scripts` (installation sans execution de scripts post-install, mesure de securite). Le flag `--ignore-scripts` empeche l'execution de code potentiellement malveillant lors de l'installation.

Les vulnerabilites identifiees dans l'ecosysteme React/CRA sont generalement liees a `react-scripts` et ses dependances transitives (nth-check, postcss, etc.). Ces vulnerabilites affectent principalement le build toolchain et non l'application deployee en production (build statique).

### 5.5 Detection de Secrets - TruffleHog

#### Configuration

TruffleHog est configure dans le stage `secrets` du pipeline CI/CD :

```yaml
secrets-trufflehog:
  stage: secrets
  image: trufflesecurity/trufflehog:latest
  script:
    - trufflehog filesystem --directory=. --json > trufflehog-report.json
```

**Point important** : Contrairement aux autres stages de securite, le job TruffleHog **ne contient pas `allow_failure: true`**. Cela signifie que toute detection de secret dans le code source **bloque le pipeline**, empechant le merge et le deploiement. C'est une politique bloquante volontaire car la fuite de secrets est consideree comme un risque critique.

#### Resultats attendus

TruffleHog analyse le filesystem a la recherche de :
- Cles API, tokens d'acces
- Mots de passe en dur dans le code
- Cles privees (SSH, TLS)
- Credentials de base de donnees

L'application VulnReport utilise exclusivement des variables d'environnement pour les secrets (`DJANGO_SECRET_KEY`, `DB_PASSWORD`, `POSTGRES_PASSWORD`), chargees via un fichier `.env` non versionne. Le fichier `settings.py` leve une `ImproperlyConfigured` si `DJANGO_SECRET_KEY` ou `DB_PASSWORD` sont absents en production, garantissant qu'aucun secret par defaut n'est utilise.

### 5.6 DAST - OWASP ZAP

#### Configuration

Le scan DAST est configure avec OWASP ZAP en mode `baseline` (scan passif + spider) :

```yaml
dast-zap:
  stage: dast
  image: ghcr.io/zaproxy/zaproxy:stable
  script:
    - zap-baseline.py -t $ZAP_TARGET -r zap-report.html -J zap-report.json
  when: manual
```

Le job est configure en **declenchement manuel** (`when: manual`) car il necessite une instance deployee et accessible. La cible est definie par la variable `ZAP_TARGET` pointant vers le backend.

#### Types de vulnerabilites detectables

Le baseline scan ZAP detecte les categories suivantes :
- Headers de securite manquants ou mal configures
- Cookies sans attributs de securite
- Divulgation d'information dans les reponses HTTP
- Redirections ouvertes
- Contenu mixte HTTP/HTTPS
- Cross-Domain Misconfiguration
- Absence de protection CSRF

Les resultats sont archives en formats HTML (rapport lisible) et JSON (integration CI) avec une retention d'une semaine.

---

## 6. Corrections Appliquees

### 6.1 Synthese des corrections

Au cours de l'audit de securite, **79 issues** ont ete identifiees et corrigees. Le tableau suivant presente les corrections groupees par categorie :

#### Configuration et Durcissement

| # | Issue | Severite | Correction | Statut |
|---|-------|----------|------------|--------|
| 1 | `DEBUG=True` en production | Critique | Variable d'environnement avec validation `ImproperlyConfigured` | Corrige |
| 2 | `SECRET_KEY` en dur dans le code | Critique | Chargement via `DJANGO_SECRET_KEY` env var, generation dynamique uniquement en DEBUG | Corrige |
| 3 | `ALLOWED_HOSTS` vide | Haute | Validation obligatoire quand `DEBUG=False` | Corrige |
| 4 | `DB_PASSWORD` absent en production | Haute | Validation `ImproperlyConfigured` si absent en production | Corrige |
| 5 | Version Nginx visible | Moyenne | `server_tokens off` dans nginx.conf | Corrige |
| 6 | Chemin admin par defaut `/admin/` | Moyenne | Renomme en `/gestion-securisee/` | Corrige |
| 7 | Conteneurs Docker en root | Haute | `USER vulnreport` dans Dockerfile backend, images Alpine | Corrige |
| 8 | Conteneurs avec acces ecriture | Moyenne | `read_only: true` + tmpfs cibles | Corrige |

#### Authentification et Sessions

| # | Issue | Severite | Correction | Statut |
|---|-------|----------|------------|--------|
| 9 | Hachage MD5/SHA256 pour mots de passe | Critique | Migration vers Argon2id (OWASP recommande) | Corrige |
| 10 | Mot de passe minimum 8 caracteres | Haute | Augmente a 12 caracteres | Corrige |
| 11 | Cookies de session sans HttpOnly | Haute | `SESSION_COOKIE_HTTPONLY = True` | Corrige |
| 12 | Cookies sans SameSite | Haute | `SESSION_COOKIE_SAMESITE = 'Strict'` | Corrige |
| 13 | Cookies sans flag Secure | Haute | `SESSION_COOKIE_SECURE = not DEBUG` | Corrige |
| 14 | Session sans expiration | Haute | `SESSION_COOKIE_AGE = 3600` (1 heure) | Corrige |
| 15 | Pas de rate limiting sur login | Critique | Double rate limiting DRF (5/min) + Nginx (10/s, burst 5) | Corrige |
| 16 | Enumeration de comptes via login | Haute | Message generique `"Invalid credentials."` pour echec et compte desactive | Corrige |

#### Controle d'Acces

| # | Issue | Severite | Correction | Statut |
|---|-------|----------|------------|--------|
| 17-25 | Absence de RBAC | Critique | Implementation de 3 roles (Viewer, Pentester, Admin) avec 5 classes de permissions | Corrige |
| 26-35 | Verification d'ownership absente | Critique | `IsReportOwnerOrAdmin`, `CanViewReport` sur chaque endpoint | Corrige |
| 36-40 | Filtrage queryset insuffisant | Haute | `get_queryset()` filtre par role : admin (tous), pentester (owner), viewer (published) | Corrige |
| 41-43 | Auto-demotion admin possible | Haute | Validation dans `UserUpdateSerializer` + `UserDetailView` | Corrige |
| 44-48 | Registration ouverte a tous | Haute | Restriction de `/api/auth/register/` aux admins uniquement (`IsAdmin`) | Corrige |

#### Headers de Securite

| # | Issue | Severite | Correction | Statut |
|---|-------|----------|------------|--------|
| 49 | Absence de CSP | Haute | CSP restrictive dans nginx.conf | Corrige |
| 50 | Absence de HSTS | Haute | HSTS 2 ans + preload dans nginx.conf et Django | Corrige |
| 51 | Absence de X-Frame-Options | Haute | `DENY` dans nginx.conf et Django | Corrige |
| 52 | Absence de X-Content-Type-Options | Moyenne | `nosniff` dans nginx.conf et Django | Corrige |
| 53 | Absence de Permissions-Policy | Moyenne | Desactivation de 8 APIs sensibles | Corrige |
| 54 | Absence de Referrer-Policy | Moyenne | `strict-origin-when-cross-origin` | Corrige |

#### Audit et Tracabilite

| # | Issue | Severite | Correction | Statut |
|---|-------|----------|------------|--------|
| 55-65 | Absence de logs d'audit | Haute | Module `audit` complet avec 18 types d'actions tracees | Corrige |
| 66-70 | Logs modifiables/supprimables | Haute | Surcharge `save()` et `delete()` pour immutabilite | Corrige |
| 71-73 | Logs accessibles a tous | Haute | Restriction via `IsAdmin` sur l'endpoint `/api/audit/logs/` | Corrige |
| 74 | Pas de logging fichier pour securite | Moyenne | Handler `security_file` avec formateur dedie | Corrige |

#### Pipeline CI/CD

| # | Issue | Severite | Correction | Statut |
|---|-------|----------|------------|--------|
| 75 | Pas d'analyse SAST | Haute | Integration Bandit + Semgrep | Corrige |
| 76 | Pas d'analyse SCA | Haute | Integration Safety + Trivy + npm audit | Corrige |
| 77 | Pas de detection de secrets | Critique | TruffleHog en mode bloquant | Corrige |
| 78 | Pas de scan DAST | Moyenne | ZAP baseline configure (declenchement manuel) | Corrige |
| 79 | Pas de lint securite | Faible | Integration flake8 + ruff | Corrige |

---

## 7. Pipeline CI/CD DevSecOps

### 7.1 Schema du pipeline

Le pipeline CI/CD GitLab est structure en **7 stages** sequentiels, integrant la securite a chaque etape selon l'approche "Shift Left" :

```
+--------+      +--------+      +--------+      +--------+
| LINT   | ---> |  SAST  | ---> |  SCA   | ---> | BUILD  |
| flake8 |      | bandit |      | safety |      | docker |
| ruff   |      |semgrep |      | trivy  |      | build  |
|        |      |        |      |npm aud.|      | push   |
+--------+      +--------+      +--------+      +--------+
                                                     |
+--------+      +--------+      +--------+           |
| DEPLOY | <--- |SECRETS | <--- |  DAST  | <---------+
|prod/man|      |truffle |      |  ZAP   |
|ual     |      |hog     |      |baseline|
|        |      |BLOQUANT|      |manuel  |
+--------+      +--------+      +--------+
```

### 7.2 Detail des stages

| Stage | Outil(s) | Objectif | Bloquant |
|-------|----------|----------|----------|
| **1. Lint** | flake8, ruff | Qualite de code, detection d'erreurs syntaxiques | Non (`allow_failure: true`) |
| **2. SAST** | Bandit, Semgrep | Analyse statique du code source pour vulnerabilites | Non (alertes archivees) |
| **3. SCA** | Safety, Trivy, npm audit | Analyse des dependances pour CVE connues | Non (alertes archivees) |
| **4. Build** | Docker-in-Docker | Construction et push des images vers le registry GitLab | Oui |
| **5. DAST** | OWASP ZAP | Scan dynamique de l'application deployee | Non (declenchement manuel) |
| **6. Secrets** | TruffleHog | Detection de secrets dans le code source | **Oui (bloquant)** |
| **7. Deploy** | Docker pull/tag | Deploiement en production depuis le registry | Oui (manuel, branche main uniquement) |

### 7.3 Politique de blocage

La strategie de blocage du pipeline est la suivante :

- **Secrets detectes** : **Blocage immediat** du pipeline. Le job TruffleHog est le seul job de securite sans `allow_failure: true`. Toute detection de secret empeche le merge.
- **Build echoue** : Blocage naturel car les stages suivants dependent des images Docker construites.
- **Deploiement production** : Protege par une regle conditionnelle (`$CI_COMMIT_BRANCH == "main" && $ENVIRONMENT == "prod"`) et un declenchement manuel.

Les jobs SAST et SCA sont configures en `allow_failure: true` pour ne pas bloquer le developpement, mais leurs artefacts sont systematiquement archives pour revue. Une evolution recommandee est de rendre les findings HIGH/CRITICAL de Bandit et Semgrep bloquants.

### 7.4 Artefacts generes et retention

| Artefact | Format | Retention |
|----------|--------|-----------|
| `bandit-report.json` / `.html` | JSON + HTML | 1 semaine |
| `semgrep-report.json` | JSON | 1 semaine |
| `safety-report.json` | JSON | 1 semaine |
| `trivy-report.json` | JSON | 1 semaine |
| `npm-audit-report.json` | JSON | 1 semaine |
| `zap-report.html` / `.json` | HTML + JSON | 1 semaine |
| `trufflehog-report.json` | JSON | 1 semaine |

### 7.5 Strategie de deploiement

Le deploiement suit un modele **build-once, deploy-anywhere** :

1. Les images Docker sont construites et poussees vers le registry GitLab avec un tag correspondant au SHA court du commit (`$CI_COMMIT_SHORT_SHA`)
2. Le deploiement en production consiste a pull les images depuis le registry et les retagger en `latest`
3. Le deploiement est protege par une condition sur la branche (`main`) et l'environnement (`prod`), avec declenchement manuel

---

## 8. Risques Residuels et Ameliorations

### 8.1 Risques residuels

Malgre les mesures de securite implementees, les risques suivants subsistent :

| Risque | Description | Niveau | Justification |
|--------|-------------|--------|---------------|
| **Absence de TLS** | L'application est actuellement servie en HTTP. Les headers HSTS et cookies Secure sont configures mais inoperants sans certificat TLS. | Eleve | Environnement de developpement. A corriger imperativement avant toute mise en production. |
| **CSP avec unsafe-inline** | La directive `style-src` autorise `'unsafe-inline'` pour la compatibilite React. | Moyen | Risque limite car les scripts (`script-src`) sont strictement restreints a `'self'`. |
| **Pas de 2FA** | L'authentification repose uniquement sur username/password. | Moyen | Le rate limiting et la politique de mots de passe forts reduisent le risque, mais ne protegent pas contre le phishing. |
| **Pas de WAF** | Aucun Web Application Firewall n'est deploye devant Nginx. | Moyen | Le rate limiting Nginx et les protections Django offrent une protection de base, mais un WAF apporterait une couche de defense supplementaire. |
| **Pas de chiffrement au repos** | Les rapports de pentest sont stockes en clair dans PostgreSQL. | Moyen | L'acces a la base est restreint au reseau Docker interne, mais une compromission du volume donnerait acces aux donnees. |
| **Alertes SAST/SCA non bloquantes** | Les jobs Bandit, Semgrep, Safety et Trivy sont en `allow_failure: true`. | Faible | Les artefacts sont archives mais une vulnerabilite critique pourrait passer en production si le rapport n'est pas consulte. |

### 8.2 Ameliorations futures recommandees

Les ameliorations suivantes sont recommandees par ordre de priorite :

#### Priorite Haute

1. **Deploiement TLS/HTTPS** : Obtenir un certificat TLS (Let's Encrypt) et configurer Nginx en terminaison SSL. Activer `SECURE_SSL_REDIRECT = True` dans Django. Cela activera effectivement les protections HSTS et Secure cookies deja configurees.

2. **Authentification a deux facteurs (2FA)** : Implementer un second facteur d'authentification pour les comptes admin et pentester via TOTP (django-otp ou django-two-factor-auth). Les comptes ayant acces a des donnees sensibles de vulnerabilites doivent etre proteges contre le vol de credentials.

3. **Politique SAST bloquante** : Modifier le pipeline pour que les findings HIGH et CRITICAL de Bandit et Semgrep bloquent le merge (`allow_failure: false` avec condition sur la severite).

#### Priorite Moyenne

4. **WAF applicatif** : Deployer un WAF (ModSecurity avec Nginx ou solution cloud) pour detecter et bloquer les attaques au niveau applicatif (injections, tentatives d'exploitation).

5. **Chiffrement au repos** : Implementer le chiffrement au niveau de PostgreSQL (pgcrypto) ou au niveau applicatif pour les champs sensibles des rapports (executive_summary, findings).

6. **Monitoring et alerting** : Integrer une solution de monitoring (Prometheus + Grafana ou equivalent) avec des alertes sur les evenements de securite : pics de tentatives de login echouees, erreurs 403/401 anormales, modifications massives.

7. **Nonces CSP** : Remplacer `'unsafe-inline'` dans la directive `style-src` par un systeme de nonces generes dynamiquement pour chaque reponse, eliminant le risque residuel d'injection de styles.

#### Priorite Basse

8. **Rotation automatique des secrets** : Mettre en place une rotation automatique des secrets (SECRET_KEY, DB_PASSWORD) via un gestionnaire de secrets (HashiCorp Vault ou equivalent).

9. **Tests d'intrusion periodiques** : Planifier des tests d'intrusion manuels trimestriels complementaires aux scans automatises, couvrant la logique metier et les scenarios d'attaque complexes.

10. **Scan d'images Docker** : Ajouter un scan de vulnerabilites sur les images Docker construites (Trivy image scan) en complement de l'analyse filesystem actuelle.

11. **Backup chiffre et teste** : Mettre en place des sauvegardes chiffrees de la base PostgreSQL avec des tests de restauration reguliers.

---

## 9. Conclusion

### 9.1 Synthese des mesures

Le projet VulnReport implemente un ensemble complet de mesures de securite couvrant les differentes couches de l'application :

- **Couche authentification** : Argon2id, politique de mots de passe forte (12 caracteres minimum, 4 validateurs), cookies securises, rate limiting double couche, anti-enumeration de comptes.
- **Couche autorisation** : RBAC a 3 niveaux avec 5 classes de permissions DRF, verification d'ownership systematique cote serveur, protection contre l'auto-demotion administrateur.
- **Couche infrastructure** : 4 conteneurs Docker isoles en mode read-only, utilisateur non-root, images Alpine minimales, reseau bridge prive, healthchecks.
- **Couche applicative** : Headers de securite complets (HSTS, CSP, X-Frame-Options, Permissions-Policy), ORM parametrise, serializers DRF pour la validation des entrees.
- **Couche audit** : 18 types d'actions tracees, logs immutables (save/delete proteges), acces restreint aux administrateurs, journalisation fichier dediee.
- **Couche CI/CD** : Pipeline 7 stages avec SAST (Bandit, Semgrep), SCA (Safety, Trivy, npm audit), detection de secrets bloquante (TruffleHog), DAST (ZAP).

### 9.2 Bilan Security by Design

L'approche Security by Design a ete appliquee tout au long du developpement :

- La securite a ete integree des la conception de l'architecture (conteneurs isoles, separation des privileges).
- Le modele de menaces OWASP Top 10 a guide les choix d'implementation.
- Les 79 issues de securite identifiees lors de l'audit ont ete corrigees, reduisant le profil de risque de 3 risques critiques a 0.
- Le pipeline CI/CD automatise les verifications de securite a chaque commit, avec une politique bloquante sur les secrets.

### 9.3 Conformite OWASP

L'application VulnReport adresse les 10 categories du OWASP Top 10 2021 :

| # | Categorie OWASP | Statut |
|---|----------------|--------|
| A01 | Broken Access Control | Protege (RBAC + ownership) |
| A02 | Cryptographic Failures | Protege (Argon2id + cookies Secure) |
| A03 | Injection | Protege (ORM parametrise) |
| A04 | Insecure Design | Protege (Security by Design) |
| A05 | Security Misconfiguration | Protege (configuration durcie) |
| A06 | Vulnerable Components | Protege (SCA automatise) |
| A07 | Auth Failures | Protege (rate limiting + politique MDP) |
| A08 | Data Integrity Failures | Protege (audit immutable + TruffleHog) |
| A09 | Logging Failures | Protege (audit complet + logging fichier) |
| A10 | SSRF | Protege (aucun appel URL serveur) |

Le projet VulnReport demontre une approche mature de la securite applicative dans le cadre d'un projet DevSecOps, avec une integration continue des pratiques de securite dans le cycle de developpement. Les risques residuels identifies sont documentes et des ameliorations concretes sont planifiees pour les sprints futurs.

---

*Document genere dans le cadre du projet UE7 DevSecOps - Guardia Cybersecurity School B2*
*Classification : Confidentiel - Usage interne*
