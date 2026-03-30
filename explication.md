# Explication Complète du Projet VulnReport

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Stack technique et justifications](#2-stack-technique-et-justifications)
3. [Architecture du projet](#3-architecture-du-projet)
4. [Backend Django — Comment ça fonctionne](#4-backend-django--comment-ça-fonctionne)
5. [Frontend React — Comment ça fonctionne](#5-frontend-react--comment-ça-fonctionne)
6. [Sécurité — Tout ce qui a été mis en place](#6-sécurité--tout-ce-qui-a-été-mis-en-place)
7. [Docker — Conteneurisation](#7-docker--conteneurisation)
8. [Pipeline CI/CD GitLab](#8-pipeline-cicd-gitlab)
9. [Les Ateliers](#9-les-ateliers)
10. [Comment lancer le projet](#10-comment-lancer-le-projet)
11. [Structure complète des fichiers](#11-structure-complète-des-fichiers)

---

## 1. Vue d'ensemble

### C'est quoi VulnReport ?

VulnReport est une **application web sécurisée** qui permet aux pentesters (testeurs d'intrusion) de :

1. **Générer des rapports de pentest** : créer un rapport, y ajouter des vulnérabilités trouvées (appelées "findings"), les organiser par sévérité, et publier le rapport.
2. **Consulter une Base de Connaissance (KB)** : une bibliothèque de fiches sur les vulnérabilités connues (OWASP Top 10, CWE) avec des recommandations prêtes à l'emploi.

L'application gère **3 rôles** (RBAC) :
- **Viewer** : peut seulement lire la KB et les rapports publiés
- **Pentester** : peut créer et gérer ses propres rapports
- **Admin** : a accès à tout (gestion utilisateurs, KB, audit log)

### Pourquoi ce projet ?

C'est le projet du module **UE7 DevSecOps** à Guardia Cybersecurity School (B2). L'objectif pédagogique est d'apprendre à :
- Développer une application web **sécurisée dès la conception** (Security by Design)
- Intégrer la sécurité dans le cycle de développement (SAST, SCA, DAST)
- Conteneuriser avec Docker
- Mettre en place un pipeline CI/CD

---

## 2. Stack technique et justifications

### Backend : Django 5.1 + Django REST Framework

**Django** est un framework Python "batteries included". On l'a choisi parce que :
- **Sécurité native** : protection CSRF, échappement des templates, gestion des sessions, tout est intégré
- **ORM (Object-Relational Mapping)** : on écrit du Python, pas du SQL brut. Ça prévient les injections SQL automatiquement
- **Système d'authentification complet** : gestion des utilisateurs, hashage des mots de passe, sessions — tout est prêt
- **Admin intégré** : interface d'administration auto-générée (utile pour le debug)
- **Migrations** : le schéma de la base de données est versionné et appliqué automatiquement

**Django REST Framework (DRF)** ajoute par-dessus :
- Des **serializers** (transforment les objets Python en JSON et inversement, avec validation)
- Des **vues API** avec permissions intégrées
- De la **pagination** et du **filtrage** automatiques
- L'**authentification par session** pour notre SPA React

### Frontend : React 18

**React** est une bibliothèque JavaScript pour construire des interfaces utilisateur :
- **SPA (Single Page Application)** : l'application se charge une fois, puis tout se passe sans rechargement de page
- **Composants** : l'interface est découpée en morceaux réutilisables (Navbar, ProtectedRoute, pages)
- **React Router** : gère la navigation entre les pages côté client
- **Axios** : fait les appels API vers le backend Django
- **Context API** : partage l'état d'authentification entre tous les composants

### Base de données : PostgreSQL 16

- **SGBD robuste** et conforme ACID (les transactions sont fiables)
- **Supérieur à SQLite** pour le multi-utilisateurs
- Supporte les **JSONField** (pour les métadonnées de l'audit log)
- **Contraintes d'intégrité** fortes (clés étrangères, NOT NULL, UNIQUE)

### Conteneurisation : Docker + docker-compose

- **Reproductibilité** : l'application fonctionne de la même façon partout
- **Isolation** : chaque service tourne dans son propre conteneur
- **Simplicité** : une seule commande (`docker compose up`) pour tout lancer

### Reverse Proxy : Nginx

- **Point d'entrée unique** : seul Nginx est exposé au réseau
- **Headers de sécurité** : HSTS, CSP, X-Frame-Options ajoutés à chaque réponse
- **Rate limiting** : limite les tentatives de connexion (anti brute-force)
- **Séparation** : le frontend et le backend ne sont pas directement accessibles

---

## 3. Architecture du projet

### Schéma d'architecture

```
Internet / Navigateur
        │
        ▼
┌─────────────────────────┐
│     Nginx (port 80)     │  ← Seul point d'entrée
│   - Reverse proxy       │
│   - Headers sécurité    │
│   - Rate limiting       │
│   - CSP                 │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────────┐
│Frontend│  │   Backend    │
│ React  │  │ Django + DRF │
│(port80)│  │ (port 8000)  │
└────────┘  └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ PostgreSQL   │
            │ (port 5432)  │
            └──────────────┘
```

### Comment une requête circule

1. L'utilisateur tape `http://localhost` dans son navigateur
2. **Nginx** reçoit la requête
3. Si l'URL commence par `/api/` ou `/gestion-securisee/` → Nginx redirige vers **Django** (port 8000)
4. Sinon → Nginx sert le **frontend React** (fichiers HTML/JS/CSS statiques)
5. Django traite la requête API : vérifie l'authentification, les permissions, exécute la logique métier, interroge **PostgreSQL**, et renvoie du JSON
6. React reçoit le JSON et met à jour l'interface

### Réseau Docker

Tous les conteneurs sont sur un réseau Docker isolé (`vulnreport-net`). Ils communiquent entre eux par leurs noms de service (ex: `backend:8000`, `db:5432`). **Seul Nginx est exposé** sur le port 80 de la machine hôte.

---

## 4. Backend Django — Comment ça fonctionne

### Les 4 applications Django

Django organise le code en "apps", chacune responsable d'un domaine :

#### App `accounts` — Authentification et RBAC

**Fichiers clés :**
- `models.py` : Modèle `User` personnalisé (étend AbstractUser) avec un champ `role` (viewer/pentester/admin)
- `views.py` : Endpoints login, logout, register, me, users, change-password
- `permissions.py` : Classes de permission (`IsAdmin`, `IsPentester`, `IsOwnerOrAdmin`)
- `serializers.py` : Validation des données (mots de passe 12 chars min, email unique, password validators Django)

**Comment le login fonctionne :**
```
1. POST /api/auth/login/ { username, password }
2. Django vérifie le username/password avec authenticate()
3. Le mot de passe est comparé au hash Argon2id stocké en base
4. Si OK → Django crée une session serveur et envoie un cookie de session
5. Le cookie a les flags HttpOnly, Secure, SameSite=Strict
6. L'action est loguée dans l'audit log
7. Réponse : { user: { id, username, role }, csrf_token }
```

**Comment le RBAC fonctionne :**
```python
# Dans chaque vue, on déclare les permissions requises :
class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    # → Seul un admin authentifié peut accéder à cette vue

# Pour les rapports, on vérifie aussi l'ownership :
class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    # GET : CanViewReport (propriétaire, admin, ou rapport publié)
    # PATCH/DELETE : IsReportOwnerOrAdmin (propriétaire ou admin)
```

#### App `reports` — Rapports et Findings

**Modèles :**
- `Report` : titre, contexte, résumé exécutif, statut (draft→in_progress→finalized→published), propriétaire
- `Finding` : titre, description, preuve (PoC), impact, recommandation, sévérité (low/medium/high/critical), score CVSS, lié à un rapport et optionnellement à une entrée KB

**Comment la création d'un finding depuis la KB fonctionne :**
```
1. Pentester consulte la KB, trouve "SQL Injection"
2. Clique "Utiliser dans le rapport"
3. POST /api/reports/5/findings/ { title: "SQLi", kb_entry: 3 }
4. Le serializer détecte kb_entry=3
5. Il va chercher la KBEntry et pré-remplit les champs vides :
   - description ← KB.description
   - recommendation ← KB.recommendation
   - references ← KB.references
   - severity ← KB.severity_default
6. Le pentester peut ensuite modifier ces champs pour son cas spécifique
```

**Transitions de statut :**
```
draft → in_progress → finalized → published
                                      ↑
                              (admin uniquement)
```
Un pentester ne peut PAS publier directement — il doit passer par les étapes intermédiaires, et seul un admin peut mettre en "published".

#### App `kb` — Base de Connaissance

**Modèles :**
- `KBEntry` : fiches vulnérabilités avec nom, description, recommandation, références OWASP/CWE, sévérité par défaut, catégorie
- `Resource` : liens pédagogiques (PortSwigger, TryHackMe, OWASP)

**15 fiches pré-chargées** couvrant l'OWASP Top 10 : SQL Injection, XSS (Reflected + Stored), IDOR, Privilege Escalation, CSRF, SSRF, Security Misconfiguration, Sensitive Data Exposure, Broken Auth, XXE, Insecure Deserialization, Supply Chain, Logging & Monitoring, Path Traversal.

#### App `audit` — Journal d'Audit

**Modèle :** `AuditLog` avec acteur, action, type d'objet, ID objet, timestamp, métadonnées (JSON).

**Particularités :**
- **Immutable** : la méthode `save()` est overridée pour empêcher les modifications des entrées existantes
- **Non-supprimable** : la méthode `delete()` lève une erreur
- **Actions tracées** : login, logout, création/modification/suppression de rapports, findings, KB entries, changements de rôle

```python
# Exemple d'utilisation dans une vue :
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

### Les 86 tests

Chaque app a un fichier `tests.py` qui vérifie :
- **accounts** (25 tests) : login/logout, anti-énumération, RBAC, politique mots de passe
- **reports** (27 tests) : ownership, transitions de statut, CVSS validation, findings depuis KB
- **kb** (18 tests) : lecture pour tous, écriture admin-only
- **audit** (16 tests) : immutabilité, logging, accès admin-only

---

## 5. Frontend React — Comment ça fonctionne

### Architecture du frontend

```
frontend/src/
├── index.js            ← Point d'entrée, monte App dans le DOM
├── App.js              ← Routes et navigation
├── App.css             ← Styles globaux (thème dark cybersécurité)
├── context/
│   └── AuthContext.js  ← État d'authentification partagé
├── services/
│   └── api.js          ← Client HTTP Axios (appels API)
├── components/
│   ├── Navbar.js       ← Barre de navigation (liens selon le rôle)
│   └── ProtectedRoute.js ← Garde de route (auth + rôle)
└── pages/
    ├── LoginPage.js
    ├── Dashboard.js
    ├── ReportListPage.js
    ├── ReportCreatePage.js
    ├── ReportDetailPage.js
    ├── KBListPage.js
    ├── KBDetailPage.js
    ├── UserManagementPage.js  (admin)
    └── AuditLogPage.js        (admin)
```

### Comment l'authentification fonctionne côté frontend

```
1. Au chargement de l'app, AuthContext appelle GET /api/auth/me/
2. Si la session est valide → on récupère l'objet user { username, role }
3. Si 401 → l'utilisateur n'est pas connecté, on redirige vers /login

4. À la connexion : POST /api/auth/login/ { username, password }
5. Django crée la session et envoie le cookie
6. AuthContext stocke l'utilisateur dans le state React
7. Les composants lisent isAdmin, isPentester, isViewer pour adapter l'UI
```

### Comment la protection CSRF fonctionne avec React

Le problème : React est une SPA, les formulaires ne sont pas rendus par Django (qui injecte normalement le token CSRF). Solution :

```javascript
// api.js — On lit le cookie CSRF et on l'envoie dans le header X-CSRFToken
function getCookie(name) {
    // Parse document.cookie pour trouver 'csrftoken'
}

const api = axios.create({
    baseURL: '/api',
    withCredentials: true,  // Envoie les cookies à chaque requête
});

api.interceptors.request.use(config => {
    // Pour POST/PUT/PATCH/DELETE, on ajoute le header X-CSRFToken
    config.headers['X-CSRFToken'] = getCookie('csrftoken');
    return config;
});
```

Django vérifie que le header `X-CSRFToken` correspond au cookie `csrftoken`. Comme le cookie est `SameSite=Strict`, un site malveillant ne peut pas le lire.

### Les pages et leur fonctionnement

**Dashboard** : Affiche des compteurs différents selon le rôle :
- Admin : nombre total de rapports, findings par sévérité, activité récente
- Pentester : ses rapports, ses findings par sévérité
- Viewer : rapports publiés, entrées KB

**ReportDetailPage** : La page la plus complexe :
- Affiche les détails du rapport (titre, contexte, résumé, statut)
- Liste les findings avec badges de sévérité colorés
- Boutons pour ajouter un finding (depuis KB ou custom)
- Modal de sélection KB avec pré-remplissage
- Formulaire inline pour findings custom
- Boutons haut/bas pour réordonner les findings
- Changement de statut (dropdown)
- Suppression (avec confirmation)

---

## 6. Sécurité — Tout ce qui a été mis en place

### Audit de sécurité réalisé

On a fait un audit complet du code et trouvé **79 vulnérabilités** qu'on a corrigées :

| Sévérité | Nombre | Exemples |
|----------|--------|----------|
| CRITICAL | 4 | SECRET_KEY nullable, credentials par défaut, pipeline non-bloquant |
| HIGH | 17 | Pas de rate limiting, password validators non appliqués, CSP avec unsafe-inline |
| MEDIUM | 34 | Enumération de comptes, CVSS non validé, admin path par défaut |
| LOW | 24 | Headers manquants, useEffect mal placé, dépendances |

### Mesures de sécurité par catégorie

#### Authentification
| Mesure | Détail |
|--------|--------|
| Hashage MDP | **Argon2id** (recommandé OWASP/NIST), résistant aux attaques GPU/ASIC |
| Politique MDP | 12 caractères minimum + validators Django (similarité, commun, numérique) |
| Sessions | Côté serveur (en base), cookie HttpOnly + Secure + SameSite=Strict |
| Expiration | 1 heure d'inactivité |
| Rate limiting | 5 tentatives de login par minute (anti brute-force) |
| Anti-énumération | Même message d'erreur pour user inexistant, mauvais MDP, ou compte désactivé |

#### Contrôle d'accès (RBAC)
| Mesure | Détail |
|--------|--------|
| Vérification côté serveur | Chaque endpoint vérifie le rôle ET l'ownership |
| Pas de confiance au client | Le frontend masque les boutons, mais le backend est la vraie barrière |
| Anti self-demotion | Un admin ne peut pas se désactiver ou changer son propre rôle |
| Transitions de statut | draft→in_progress→finalized→published, publish = admin only |

#### Protection OWASP Top 10
| Risque | Protection |
|--------|-----------|
| **A01 - Broken Access Control** | RBAC strict, ownership vérifiée à chaque requête |
| **A02 - Cryptographic Failures** | Argon2id, secrets en env vars, HTTPS-ready |
| **A03 - Injection (SQLi)** | ORM Django uniquement, requêtes paramétrées, jamais de SQL brut |
| **A03 - XSS** | Échappement auto React + CSP sans unsafe-inline |
| **A04 - Insecure Design** | Security by Design dès la conception, audit log |
| **A05 - Security Misconfiguration** | Headers HTTP complets, admin URL obfusquée, DEBUG=False en prod |
| **A06 - Vulnerable Components** | SCA automatisé (Safety, Trivy, npm audit) dans le pipeline |
| **A07 - Auth Failures** | Rate limiting, anti-énumération, password policy forte |
| **A08 - Data Integrity** | Audit log immutable, CSRF tokens, SameSite cookies |
| **A09 - Logging Failures** | Audit log complet, actions sensibles tracées |
| **A10 - SSRF** | Pas de fonctionnalité de fetch d'URL côté serveur |

#### Headers HTTP (via Nginx)
```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## 7. Docker — Conteneurisation

### docker-compose.yml — 4 services

```yaml
services:
  db:         # PostgreSQL 16
  backend:    # Django (construit depuis backend/Dockerfile)
  frontend:   # React (construit depuis frontend/Dockerfile, multi-stage)
  nginx:      # Reverse proxy (seul port exposé : 80)
```

### Comment ça démarre

```
1. docker compose up --build
2. PostgreSQL démarre et attend les connexions (healthcheck)
3. Le backend attend que PostgreSQL soit healthy (depends_on)
4. Le backend exécute :
   a. python manage.py migrate --noinput  → crée les tables
   b. python manage.py seed_data          → insère les données initiales
   c. gunicorn vulnreport.wsgi ...        → lance le serveur API
5. Le frontend est construit (npm run build) et servi par Nginx interne
6. Nginx démarre et route les requêtes
```

### Sécurité Docker
- Conteneurs en `read_only: true` (écriture uniquement dans les tmpfs)
- Pas de ports exposés sauf Nginx (backend/frontend = `expose` interne)
- Pas de credentials par défaut (docker-compose échoue si .env manquant)
- `restart: unless-stopped` sur tous les services

---

## 8. Pipeline CI/CD GitLab

### Les 7 stages

```
┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌─────────┐   ┌────────┐
│ Lint │ → │ SAST │ → │ SCA  │ → │Build │ → │ DAST │ → │ Secrets │ → │ Deploy │
└──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └─────────┘   └────────┘
 flake8     Bandit     Safety     Docker      ZAP       TruffleHog    Registry
 ruff       Semgrep    Trivy      build       (manuel)  (BLOQUANT)    (manuel)
                       npm audit
```

### Ce que chaque outil fait

| Outil | Type | Ce qu'il détecte |
|-------|------|-----------------|
| **flake8/ruff** | Lint | Erreurs de style Python, code non conforme PEP8 |
| **Bandit** | SAST | Vulnérabilités dans le code Python (exec, eval, binding 0.0.0.0, hardcoded passwords) |
| **Semgrep** | SAST | Patterns de code dangereux (règles communautaires auto) |
| **Safety** | SCA | CVE connues dans les dépendances Python (requirements.txt) |
| **Trivy** | SCA | CVE dans les dépendances + l'image Docker |
| **npm audit** | SCA | CVE dans les dépendances JavaScript (package.json) |
| **OWASP ZAP** | DAST | Vulnérabilités en boîte noire (XSS, SQLi, headers manquants) |
| **TruffleHog** | Secrets | Mots de passe, clés API, tokens dans le code source |

### Politique de blocage

- **TruffleHog** : bloque le pipeline si des secrets sont trouvés (pas de `allow_failure`)
- **Bandit** : bloque si des vulnérabilités HIGH sont trouvées (pas de `|| true`)
- **Autres** : alertent mais ne bloquent pas (pour ne pas ralentir le développement)
- **Deploy** : uniquement sur branche `main` + variable `ENVIRONMENT=prod` + action manuelle

---

## 9. Les Ateliers

### Atelier 2 — Pipeline CI/CD + SCA

**Dossier** : `ateliers/atelier2/`

**Ce qu'on y trouve :**
- Un pipeline GitLab avec les 7 exercices demandés (4 stages, artefacts, allow_failure, job manuel, secrets, variables conditionnelles)
- L'intégration OWASP Dependency-Check (SCA local + CI)
- L'intégration Snyk (SCA cloud + CI)
- Un `config.conf` avec des secrets en clair (pour tester TruffleHog)
- Un `package.json` avec des dépendances vulnérables (lodash 3.0.0, jquery 3.2.1, minimist 0.0.8)
- Réponses complètes à toutes les questions théoriques

### Atelier 3 — SAST + DAST + Secrets + Patch Management

**Dossier** : `ateliers/atelier3/`

**Ce qu'on y trouve :**
- Bandit : analyse SAST locale et en pipeline
- OWASP ZAP : tests DAST sur DVWA (local) et Juice Shop (pipeline)
- TruffleHog : détection de secrets
- **Document Patch Management** (`patch-management.md`) :
  - Benchmark de 6 outils (Dependabot, Renovate, Snyk, OWASP Dep-Check, Safety, Trivy)
  - Recommandation : Renovate (auto-MR) + Trivy (scans CI)
  - Architecture de gestion automatisée des dépendances
  - Configuration Renovate pour GitLab

---

## 10. Comment lancer le projet

### Prérequis
- Docker et Docker Compose installés
- Git

### Lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/Comandoat/VulnReport.git
cd VulnReport

# 2. Créer le fichier d'environnement
cp .env.example .env
# Modifier les mots de passe dans .env (DJANGO_SECRET_KEY, DB_PASSWORD)

# 3. Lancer
docker compose up --build -d

# 4. Accéder à l'application
# → http://localhost (via Nginx)
```

### Comptes de test

| Rôle | Login | Mot de passe |
|------|-------|-------------|
| Admin | admin | Admin@VulnReport2026! |
| Pentester | pentester1 | Pentester@VulnReport2026! |
| Viewer | viewer1 | Viewer@VulnReport2026! |

### Commandes utiles

```bash
# Voir les logs
docker compose logs -f backend

# Relancer les migrations
docker compose exec backend python manage.py migrate

# Lancer les tests
docker compose exec backend python manage.py test

# Créer un superuser
docker compose exec backend python manage.py createsuperuser

# Arrêter tout
docker compose down

# Reset complet (supprime la base)
docker compose down -v
```

---

## 11. Structure complète des fichiers

```
VulnReport/                          # 84 fichiers, ~12 000 lignes
│
├── CLAUDE.md                        # Spécifications techniques pour Claude
├── README.md                        # Documentation utilisateur
├── explication.md                   # Ce fichier
├── .env.example                     # Template variables d'environnement
├── .gitignore                       # Fichiers ignorés par Git
├── docker-compose.yml               # Orchestration 4 conteneurs
├── .gitlab-ci.yml                   # Pipeline CI/CD 7 stages
│
├── backend/                         # Django 5.1 + DRF
│   ├── Dockerfile                   # Image Python 3.12, non-root user
│   ├── requirements.txt             # 12 dépendances Python épinglées
│   ├── manage.py                    # CLI Django
│   ├── .dockerignore
│   │
│   ├── vulnreport/                  # Configuration Django
│   │   ├── settings.py              # Sécurité, DB, CORS, throttling, logging
│   │   ├── urls.py                  # Routage principal → 4 apps
│   │   └── wsgi.py                  # Point d'entrée Gunicorn
│   │
│   ├── accounts/                    # Auth + RBAC
│   │   ├── models.py                # User (role: viewer/pentester/admin)
│   │   ├── serializers.py           # Login, Register, UserUpdate, ChangePassword
│   │   ├── views.py                 # 7 endpoints API
│   │   ├── permissions.py           # IsAdmin, IsPentester, IsOwnerOrAdmin
│   │   ├── urls.py                  # /api/auth/...
│   │   ├── admin.py                 # Interface admin Django
│   │   ├── tests.py                 # 25 tests
│   │   └── management/commands/
│   │       └── seed_data.py         # Données initiales (users, KB, rapports)
│   │
│   ├── reports/                     # Rapports + Findings
│   │   ├── models.py                # Report, Finding
│   │   ├── serializers.py           # CRUD + validation CVSS + transitions statut
│   │   ├── views.py                 # List, Detail, Findings, Reorder
│   │   ├── permissions.py           # IsReportOwner, CanViewReport
│   │   ├── urls.py                  # /api/reports/...
│   │   ├── admin.py
│   │   └── tests.py                 # 27 tests
│   │
│   ├── kb/                          # Base de Connaissance
│   │   ├── models.py                # KBEntry, Resource
│   │   ├── serializers.py           # KBEntry, KBEntryList, Resource
│   │   ├── views.py                 # CRUD (lecture tous, écriture admin)
│   │   ├── urls.py                  # /api/kb/...
│   │   ├── admin.py
│   │   └── tests.py                 # 18 tests
│   │
│   └── audit/                       # Journal d'audit
│       ├── models.py                # AuditLog (immutable)
│       ├── serializers.py           # Lecture seule, actor imbriqué
│       ├── views.py                 # Liste (admin only)
│       ├── utils.py                 # log_action() helper
│       ├── urls.py                  # /api/audit/...
│       ├── admin.py                 # Lecture seule dans admin
│       └── tests.py                 # 16 tests
│
├── frontend/                        # React 18 SPA
│   ├── Dockerfile                   # Multi-stage (Node build → Nginx serve)
│   ├── package.json                 # React, react-router-dom, axios
│   ├── nginx.conf                   # Config Nginx pour SPA (try_files)
│   ├── .dockerignore
│   │
│   ├── public/
│   │   └── index.html               # Shell HTML5
│   │
│   └── src/
│       ├── index.js                 # Point d'entrée React
│       ├── App.js                   # Routes + Navigation
│       ├── App.css                  # Thème dark cybersécurité
│       ├── context/
│       │   └── AuthContext.js       # État auth partagé (user, rôle, login/logout)
│       ├── services/
│       │   └── api.js               # Client Axios (CSRF, interceptors, validation ID)
│       ├── components/
│       │   ├── Navbar.js            # Navigation adaptée au rôle
│       │   └── ProtectedRoute.js    # Garde d'authentification + rôle
│       └── pages/
│           ├── LoginPage.js         # Formulaire login
│           ├── Dashboard.js         # Compteurs par rôle
│           ├── ReportListPage.js    # Liste rapports (filtres, recherche)
│           ├── ReportCreatePage.js  # Nouveau rapport
│           ├── ReportDetailPage.js  # Détail + findings + KB modal
│           ├── KBListPage.js        # Liste KB (filtres)
│           ├── KBDetailPage.js      # Détail KB + "Utiliser dans rapport"
│           ├── UserManagementPage.js # Gestion users (admin)
│           └── AuditLogPage.js      # Logs d'audit (admin)
│
├── nginx/
│   └── nginx.conf                   # Reverse proxy + headers sécurité + rate limiting
│
├── docs/
│   └── rapport-securite.md          # Rapport de sécurité 10 pages
│
├── ateliers/
│   ├── atelier2/                    # CI/CD + SCA
│   │   ├── README.md                # Réponses complètes exercices + théorie
│   │   ├── .gitlab-ci.yml           # Pipeline 7 exercices
│   │   ├── config.conf              # Secrets en clair (test TruffleHog)
│   │   └── package.json             # Dépendances vulnérables (test SCA)
│   │
│   └── atelier3/                    # SAST + DAST + Secrets + Patch Mgmt
│       ├── README.md                # Documentation complète
│       ├── .gitlab-ci.yml           # Pipeline Bandit + ZAP + TruffleHog
│       ├── config.conf              # Secrets en clair (test)
│       └── patch-management.md      # Benchmark outils + architecture recommandée
│
└── VulnReport_Atelier1.md           # Livrable Atelier 1 (Plan de dev, DAT, Risques)
```

---

## Récapitulatif

| Élément | Statut | Détail |
|---------|--------|--------|
| Sprint 1 — Fondations | Fait | Auth, RBAC, Docker, pipeline CI/CD |
| Sprint 2 — Coeur Fonctionnel | Fait | KB, Rapports, Findings, Audit, Dashboard, 86 tests |
| Sprint 3 — Finalisation | Fait | Rapport sécurité, hardening, artefacts CI/CD |
| Atelier 1 — Présentation | Fait | VulnReport_Atelier1.md |
| Atelier 2 — CI/CD + SCA | Fait | Pipeline, OWASP Dep-Check, Snyk, questions |
| Atelier 3 — SAST+DAST+Secrets | Fait | Bandit, ZAP, TruffleHog, patch management |
| Audit sécurité | Fait | 79 issues trouvées et corrigées |
| Tests | Fait | 86 tests backend (auth, RBAC, ownership, findings, KB, audit) |
