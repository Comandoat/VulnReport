# CLAUDE.md - VulnReport

## Projet

**VulnReport** est une application web securisee de generation de rapports de pentest et base de connaissance offensive, developpee dans le cadre du module UE7 DevSecOps (B2 Guardia Cybersecurity School).

- **Periode** : 23 mars - 10 avril 2026
- **Equipe** : Noa B. (Chef de Projet), Diego D. (Frontend), Raphael L. (Backend), Antoine C. (Securite/DevOps)
- **Depot** : GitLab.com (prive)

---

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | React (SPA) |
| **Backend / API** | Django + Django REST Framework |
| **Base de donnees** | PostgreSQL |
| **Reverse Proxy** | Nginx (optionnel) |
| **Conteneurisation** | Docker + docker-compose |
| **CI/CD** | GitLab CI/CD |
| **Hashage MDP** | Argon2id (django-argon2) |

---

## Architecture

### Conteneurs Docker
```
[React SPA] <--REST API--> [Django + DRF] <--ORM--> [PostgreSQL]
     |                          |
  (port 3000)            (port 8000)
     |                          |
  [Nginx reverse proxy - optionnel]
```

### Modele de donnees (6 tables)

| Table | Description |
|-------|-------------|
| **User** | id, username, email, password_hash, role (Viewer/Pentester/Admin), is_active, created_at |
| **Report** | id, title, context, executive_summary, status (Brouillon/En cours/Finalise/Publie), created_at, updated_at, owner_id (FK User) |
| **Finding** | id, title, description, proof, impact, recommendation, references, severity, cvss_score, report_id (FK Report), kb_entry_id (FK KBEntry nullable) |
| **KBEntry** | id, name, description, recommendation, references, severity_default, category, created_at, updated_at |
| **Resource** | id, title, url, description, category |
| **AuditLog** | id, actor_id (FK User), action, object_type, object_id, timestamp, metadata (JSON) |

---

## RBAC - Roles et Permissions

| Role | Permissions |
|------|-------------|
| **Viewer** | Lecture seule : KB + rapports au statut Publie |
| **Pentester** | CRUD ses propres rapports, ajout findings (KB ou custom), consultation KB. Ne voit pas les rapports d'autrui (sauf Publie) |
| **Admin** | Acces complet : gestion utilisateurs (roles, activation), CRUD KB, lecture/suppression tous rapports, dashboard, audit log |

### Regles d'acces critiques
- Un Pentester ne modifie que SES rapports (ownership verification cote serveur)
- Les rapports d'autrui sont en lecture seule (sauf Admin)
- KB : lecture pour tous, ecriture reservee Admin
- Audit log : visible par Admin uniquement

---

## Modules Fonctionnels

### Module Rapports
- Creer un rapport : Titre (oblig.), Contexte/Objectifs, Resume executif (optionnel), Date creation (auto), Statut (Brouillon/En cours/Finalise/Publie)
- Gerer les findings :
  - Depuis KB : pre-remplissage automatique (Description, Impact, Recommandation, References, Severite par defaut)
  - Custom : Titre, Description, Preuve/PoC (texte/URL), Impact, Recommandation, References (OWASP/CWE/CVE), Severite (L/M/H/Critique), Score (CVSS simplifie optionnel)
- Modifier/Supprimer un finding, reordonner par severite
- Sauvegarder/Editer/Supprimer rapport (proprietaire/Admin)
- Rechercher/Filtrer par titre, auteur, periode, severite findings
- Export PDF (optionnel)

### Module Base de Connaissance (KB)
- Fiches vulnerabilites : Nom, Description, Recommandation, References (OWASP/CWE), Severite par defaut, Categorie (Injection, Auth, XSS, CSRF, etc.)
- Consultation : tous roles
- Gestion CRUD : Admin uniquement
- Integration : copier vers rapport -> creer un finding pre-rempli

### Module Ressources
- Pages statiques : liens academiques (PortSwigger, WebGoat, Juice Shop, TryHackMe), cheatsheets OWASP, guide redaction PoC

### Audit Log
- Journalise : login, creation/edition/suppression rapport, ajout/modif finding, modifs KB, changement role/statut utilisateur
- Champs : acteur, action, type d'objet, id, timestamp, metadonnees non sensibles

### Dashboard
- Compteurs : # rapports, # findings par severite, rapports recemment modifies
- Vue Admin = globale / Vue Pentester = ses rapports

---

## Exigences de Securite (Security by Design)

### Authentification & Sessions
- Systeme natif Django (django.contrib.auth)
- Hashage mots de passe : **Argon2id** (django-argon2)
- Sessions serveur (base de donnees Django)
- Cookies : `HttpOnly=True`, `Secure=True`, `SameSite=Strict`
- SESSION_COOKIE_AGE = 3600s (1h)
- Mot de passe : minimum 8 caracteres, 12+ recommande

### Protection OWASP Top 10
| Menace | Mesures |
|--------|---------|
| **SQLi (A03)** | Requetes parametrees via ORM Django, validation stricte entrees, moindre privilege sur compte DB |
| **XSS (A03)** | Echappement auto Django/React, Content-Security-Policy (CSP), sanitisation champs libres |
| **Broken Access Control (A01)** | RBAC strict, verification ownership cote serveur a chaque requete |
| **Vol de session** | Cookies HttpOnly + Secure + SameSite=Strict, HTTPS obligatoire, expiration 1h |
| **Exposition donnees (A02)** | Argon2id, chiffrement secrets via env vars, pas de donnees sensibles dans les logs |
| **CSRF (A01 adj.)** | Token CSRF Django actif sur tous formulaires, SameSite=Strict |
| **Mauvaise config (A05)** | Headers HTTP securite (X-Frame-Options, HSTS, X-Content-Type-Options), secrets hors code source |
| **Supply chain (A06)** | SCA automatise (Safety + Trivy) en CI/CD, versions epinglees dans requirements.txt |

### Headers HTTP de Securite
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store (pages sensibles)
```

### Validation des entrees
- Toujours valider cote serveur (ne jamais faire confiance au client)
- Utiliser les serializers DRF avec validation stricte
- Whitelister les valeurs autorisees
- Encoder la sortie selon le contexte (HTML, JS, URL)

---

## Pipeline CI/CD GitLab

### Stages
```yaml
stages:
  - lint        # flake8 / ruff — conformite PEP8
  - sast        # Bandit + Semgrep — analyse statique securite
  - sca         # Safety + Trivy — analyse dependances
  - build       # Docker build — image validee
  - dast        # OWASP ZAP (Sprint 3) — test dynamique boite noire
  - secrets     # TruffleHog — detection secrets dans le code
  - deploy      # Deploiement (manuel, branche main uniquement)
```

### Outils de securite
| Type | Outil | Usage |
|------|-------|-------|
| **SAST** | Bandit, Semgrep | Analyse statique du code Python |
| **SCA** | Safety, Trivy, OWASP Dependency-Check, Snyk | Vulnerabilites dans les dependances |
| **DAST** | OWASP ZAP | Tests dynamiques en boite noire |
| **Secrets** | TruffleHog | Detection de secrets dans le repo |
| **Lint** | flake8, ruff | Qualite et conformite du code |

### Artefacts
- Tous les rapports SAST/SCA/DAST/secrets sont conserves comme artefacts GitLab CI/CD
- Format : JSON et/ou HTML selon l'outil

---

## Analyse des Risques

### Matrice (P x I)
| Risque | P | I | Score | Criticite |
|--------|---|---|-------|-----------|
| Injection SQL | 3 | 3 | **9** | Eleve |
| XSS | 3 | 2 | **6** | Eleve |
| Broken Access Control | 2 | 3 | **6** | Eleve |
| Vol de session | 2 | 3 | **6** | Eleve |
| Exposition donnees sensibles | 2 | 3 | **6** | Eleve |
| CSRF | 2 | 2 | **4** | Moyen |
| Mauvaise config securite | 2 | 2 | **4** | Moyen |
| Compromission supply chain | 1 | 3 | **3** | Faible |
| Alteration audit log | 1 | 3 | **3** | Faible |
| DoS | 1 | 2 | **2** | Faible |

### Risques residuels
- Broken Access Control (complexite des regles d'ownership)
- Supply chain (dependances tierces non auditees en profondeur)
- Reevaluation prevue apres resultats SAST/SCA/DAST Sprint 3

---

## Conventions Git

| Prefixe | Usage | Exemple |
|---------|-------|---------|
| `feature/` | Nouvelle fonctionnalite metier | `feature/4-creation-rapport` |
| `fix/` | Correction bug fonctionnel | `fix/15-erreur-affichage-dashboard` |
| `sec/` | Mesure Security by Design ou correction vuln | `sec/8-ajout-headers-http` |
| `ops/` / `ci/` | Infrastructure Docker, pipeline CI/CD | `ops/2-creation-dockerfile` |
| `docs/` | README, rapport securite, fiches KB | `docs/25-redaction-rapport-architecture` |
| `refactor/` | Refactoring sans changement de comportement | `refactor/11-nettoyage-auth` |

**Regle** : 1 issue GitLab = 1 branche = 1 Merge Request (MR)

---

## Planning (3 Sprints)

### Sprint 1 — Fondations (23/03 - 29/03)
- [x] Initialisation depot GitLab (structure, branches, board)
- [ ] Dockerfile de base + docker-compose
- [ ] Structure base de donnees (migrations)
- [ ] Authentification securisee (cookies HttpOnly, Secure, SameSite, headers HTTP)
- [ ] RBAC strict (Viewer, Pentester, Admin)
- [ ] Fondations Security by Design

### Sprint 2 — Coeur Fonctionnel (30/03 - 05/04)
- [ ] Module KB — CRUD Admin
- [ ] Module Rapports — creation, ajout findings (KB ou custom), statuts
- [ ] Audit log (tracabilite actions sensibles)
- [ ] Validation rigoureuse entrees (anti-SQLi, anti-XSS)
- [ ] Dashboard (compteurs)

### Sprint 3 — Pipeline & Finalisation (06/04 - 10/04)
- [ ] Configuration pipeline CI/CD GitLab complet
- [ ] Integration SAST, SCA, DAST — artefacts
- [ ] Feature freeze 08/04 : correction vulnerabilites detectees
- [ ] README (variables env, comptes seed, commandes Docker)
- [ ] Rapport de securite final (8-10 pages)

### Jalons
| Jalon | Date | Livrables |
|-------|------|-----------|
| J1 | 29/03 | Depot GitLab, Dockerfile, auth + RBAC |
| J2 | 05/04 | Modules Rapports, KB, Audit log. Protections SQLi/XSS |
| J3 | 08/04 | Feature freeze. Pipeline CI/CD. Artefacts SAST/SCA/DAST |
| J4 | 10/04 | README, Rapport securite, app dockerisee testable |

---

## Rendus Attendus

1. **Code GitLab** (issues, branches, MR)
2. **Dockerfile** (et docker-compose si BD) ; execution par `docker run` / `docker compose up`
3. **CI/CD** avec SAST/SCA/DAST actifs (artefacts disponibles)
4. **README** : setup, variables d'env, comptes seed (Admin, Pentester, Viewer), commandes Docker
5. **Rapport securite** :
   - Architecture
   - Mesures OWASP
   - Resultats SAST/SCA/DAST + corrections
   - Risques residuels & ameliorations

---

## Ateliers Pratiques (Travail Preparatoire)

### Atelier 1 — Pipeline CI/CD GitLab
- Pipeline 4 stages (build, test, integration, deploy)
- Gestion artefacts, `allow_failure`, job manuel
- Detection secrets avec TruffleHog
- Controle conditionnel et variables

### Atelier 2 — SCA + SAST
- **SCA** : OWASP Dependency-Check (local + CI), Snyk (cloud + CI)
- **SAST** : Bandit (local + CI)
- **DAST** : OWASP ZAP sur DVWA + Juice Shop (pipeline complet)
- Detection secrets avec TruffleHog
- Patch management des dependances

### Atelier 3 — Tests DAST + Securite Applicative
- OWASP ZAP sur DVWA et Juice Shop
- Pipeline CI/CD complet avec DAST
- Gestion des secrets dans le pipeline

---

## Structure Projet Cible

```
vulnreport/
├── .gitlab-ci.yml              # Pipeline CI/CD
├── docker-compose.yml          # Orchestration conteneurs
├── Dockerfile                  # Image Docker principale
├── README.md                   # Setup, env vars, comptes seed, commandes
├── requirements.txt            # Dependances Python (versions epinglees)
├── .env.example                # Template variables d'environnement
├── .dockerignore
├── .gitignore
│
├── backend/                    # Django + DRF
│   ├── manage.py
│   ├── vulnreport/             # Settings Django
│   │   ├── settings.py         # Config securisee (Argon2id, cookies, headers, CSP)
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── accounts/               # App auth + RBAC
│   │   ├── models.py           # User avec role
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py      # IsAdmin, IsPentester, IsOwner, etc.
│   │   └── middleware.py       # Security headers middleware
│   │
│   ├── reports/                # App rapports + findings
│   │   ├── models.py           # Report, Finding
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── permissions.py      # Ownership checks
│   │
│   ├── kb/                     # App base de connaissance
│   │   ├── models.py           # KBEntry, Resource
│   │   ├── serializers.py
│   │   └── views.py
│   │
│   └── audit/                  # App audit log
│       ├── models.py           # AuditLog
│       ├── signals.py          # Auto-logging
│       └── views.py
│
├── frontend/                   # React SPA
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/           # API calls
│   │   └── utils/
│   └── Dockerfile
│
├── nginx/                      # Config Nginx (optionnel)
│   └── nginx.conf
│
└── docs/
    └── rapport-securite.pdf    # Rapport final 8-10 pages
```

---

## Comptes Seed (README)

| Role | Username | Email | Password |
|------|----------|-------|----------|
| Admin | admin | admin@vulnreport.local | (env var) |
| Pentester | pentester1 | pentester@vulnreport.local | (env var) |
| Viewer | viewer1 | viewer@vulnreport.local | (env var) |

Les mots de passe seed sont definis via variables d'environnement, jamais en dur dans le code.

---

## Variables d'Environnement

```env
# Django
DJANGO_SECRET_KEY=          # Cle secrete Django (generer avec get_random_secret_key())
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Base de donnees
DB_NAME=vulnreport
DB_USER=vulnreport_user
DB_PASSWORD=                # Secret - jamais en clair dans le code
DB_HOST=db
DB_PORT=5432

# Securite
CSRF_TRUSTED_ORIGINS=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Comptes seed
ADMIN_PASSWORD=             # Mot de passe admin initial
PENTESTER_PASSWORD=         # Mot de passe pentester initial
VIEWER_PASSWORD=            # Mot de passe viewer initial
```

---

## Regles pour Claude (Skill Secure-DEV)

Lors du developpement, appliquer systematiquement :

1. **Defense in depth** : ne jamais s'appuyer sur un seul controle de securite
2. **Fail securely** : en cas d'erreur, refuser l'acces (deny by default)
3. **Least privilege** : permissions minimales necessaires
4. **Input validation** : valider TOUT cote serveur, ne jamais faire confiance au client
5. **Output encoding** : encoder selon le contexte (HTML, JS, URL, CSS)
6. **Requetes parametrees** : ORM Django exclusivement, jamais de SQL brut avec concatenation
7. **RBAC strict** : verifier role ET ownership a chaque endpoint
8. **Pas de secrets dans le code** : utiliser les variables d'environnement
9. **Headers securite** : HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
10. **Audit log** : tracer toutes les actions sensibles (login, CRUD, changements de role)

### Checklist avant chaque endpoint
- [ ] Authentification verifiee
- [ ] Autorisation verifiee (role)
- [ ] Ownership verifiee (si applicable)
- [ ] Entrees validees et sanitisees
- [ ] Sortie encodee selon le contexte
- [ ] Action loguee dans l'audit log
- [ ] Pas de donnees sensibles dans la reponse d'erreur

---

## Bareme Evaluation (100 pts -> /20)

### Savoirs - Connaissances (30 pts)
- Analyse projet, perimetre, risques : 6pts
- Architecture technique, schema BD, RBAC : 6pts
- Analyse risques OWASP, CIA, mesures : 6pts
- Bonnes pratiques Security by Design : 5pts
- Chaine DevSecOps (SAST/SCA/DAST, CI/CD) : 4pts
- Structure rapport de pentest : 3pts

### Savoirs - Faire (50 pts)
- BDD coherente, relations, index : 5pts
- Auth & RBAC (sessions, hash, cookies, permissions, ownership) : 8pts
- Module Rapports (CRUD, statut, edition, tri) : 6pts
- Module Findings (KB, custom, PoC, impact, reco, severite) : 7pts
- Module KB (consultation + gestion Admin) : 4pts
- Module Admin (users, roles, activation, audit log) : 4pts
- CI/CD DevSecOps (pipeline, SAST, SCA, corrections) : 8pts
- Gestion de projet (Kanban, progression) : 4pts
- Respect jalons et qualite livrables : 4pts

### Savoirs - Etre (20 pts)
- Travail en equipe : 8pts
- Creativite et initiative : 4pts
- Communication (MR, documentation) : 4pts
- Soutenance finale : 4pts
