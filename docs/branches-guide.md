# Guide des Branches — VulnReport

## Convention de nommage

Chaque branche suit le format : `prefixe/numero-issue-description`

Le prefixe identifie le type de travail :

| Prefixe | Signification | Couleur Board |
|---------|--------------|---------------|
| `feature/` | Nouvelle fonctionnalite metier | Bleu |
| `fix/` | Correction de bug | Rouge |
| `sec/` | Securite (Security by Design, corrections vulns) | Rouge vif |
| `ops/` | Infrastructure (Docker, serveur, config) | Vert |
| `ci/` | Pipeline CI/CD | Vert |
| `docs/` | Documentation (rapport, README) | Orange |
| `refactor/` | Refactoring sans changement fonctionnel | Violet |

---

## Branches du projet

### `main` — Branche principale

La branche protegee. Tout le code stable et valide est ici. Aucun push direct — uniquement des merges via Merge Request apres validation du pipeline CI/CD.

**Regles :**
- Pipeline CI/CD doit passer avant merge
- Branche source supprimee apres merge
- Contient la version deployable de l'application

---

### `feature/9-module-kb-crud`

**Issue liee** : #9 — Module Base de Connaissance (KB) - CRUD Admin
**Sprint** : Sprint 2 — Coeur Fonctionnel
**Responsable** : Raphael L. (Backend)
**MR** : !1

**Ce qui a ete fait :**
- Modele `KBEntry` : nom, description, recommandation, references OWASP/CWE, severite par defaut, categorie
- Modele `Resource` : liens pedagogiques (PortSwigger, TryHackMe, OWASP)
- API REST : `GET/POST /api/kb/entries/` et `GET/PATCH/DELETE /api/kb/entries/:id/`
- Permissions : lecture pour tous les roles, ecriture reservee a l'Admin
- Filtrage par categorie, recherche par nom/description
- 15 fiches KB pre-chargees couvrant l'OWASP Top 10
- 6 ressources pedagogiques (PortSwigger, HackTheBox, TryHackMe, OWASP, CWE)
- Audit log sur toutes les operations CRUD
- 18 tests unitaires (acces par role, CRUD admin-only)

**Fichiers modifies :**
```
backend/kb/models.py         — Modeles KBEntry et Resource
backend/kb/serializers.py    — Serializers avec validation
backend/kb/views.py          — Vues API avec permissions
backend/kb/urls.py           — Routes /entries/ et /resources/
backend/kb/tests.py          — 18 tests
```

---

### `feature/10-module-rapports`

**Issue liee** : #10 — Module Rapports + #11 — Module Findings
**Sprint** : Sprint 2 — Coeur Fonctionnel
**Responsable** : Raphael L. (Backend) + Diego D. (Frontend)
**MR** : !2

**Ce qui a ete fait :**
- Modele `Report` : titre, contexte, resume executif, statut (draft/in_progress/finalized/published), proprietaire
- Modele `Finding` : titre, description, preuve PoC, impact, recommandation, references, severite, score CVSS, lien KB optionnel
- Workflow de statut : draft → in_progress → finalized → published (admin pour publier)
- Ownership : un pentester ne voit et ne modifie que SES rapports
- Pre-remplissage des findings depuis la KB (severite, description, recommandation)
- Reordonnancement des findings (boutons haut/bas)
- Validation CVSS 0.0 - 10.0
- Frontend : pages liste, creation, detail avec modal KB et formulaire custom
- 27 tests unitaires (ownership, transitions statut, CVSS, findings)

**Fichiers modifies :**
```
backend/reports/models.py       — Modeles Report et Finding
backend/reports/serializers.py  — Serializers avec validation CVSS et transitions
backend/reports/views.py        — Vues API avec ownership check
backend/reports/permissions.py  — IsReportOwner, CanViewReport
backend/reports/urls.py         — Routes reports et findings
backend/reports/tests.py        — 27 tests
frontend/src/pages/ReportListPage.js
frontend/src/pages/ReportCreatePage.js
frontend/src/pages/ReportDetailPage.js
```

---

### `sec/8-headers-securite-http`

**Issue liee** : #6 — Headers HTTP de securite
**Sprint** : Sprint 1 — Fondations
**Responsable** : Antoine C. (Securite/DevOps)
**MR** : !3

**Ce qui a ete fait :**
- Configuration Nginx avec headers de securite :
  - `Strict-Transport-Security` (HSTS) : force HTTPS pendant 2 ans
  - `Content-Security-Policy` (CSP) : bloque les scripts inline et eval
  - `X-Frame-Options: DENY` : empeche le clickjacking
  - `X-Content-Type-Options: nosniff` : empeche le MIME sniffing
  - `Referrer-Policy: strict-origin-when-cross-origin` : limite les infos envoyees
  - `Permissions-Policy` : desactive camera, micro, geolocation
- Configuration Django settings.py :
  - `SECURE_BROWSER_XSS_FILTER = True`
  - `SECURE_CONTENT_TYPE_NOSNIFF = True`
  - `X_FRAME_OPTIONS = 'DENY'`
  - HSTS en production (31536000 secondes)

**Fichiers modifies :**
```
nginx/nginx.conf                   — Headers de securite Nginx
backend/vulnreport/settings.py     — Headers Django
```

**Pourquoi c'est important :**
Les headers HTTP sont la premiere ligne de defense. Ils instruisent le navigateur sur comment se comporter. Sans CSP, une XSS peut executer du JavaScript arbitraire. Sans HSTS, un attaquant peut intercepter le trafic via un downgrade HTTP.

---

### `ops/2-creation-dockerfile`

**Issue liee** : #2 — Creation Dockerfile et docker-compose
**Sprint** : Sprint 1 — Fondations
**Responsable** : Antoine C. (Securite/DevOps)
**MR** : !4

**Ce qui a ete fait :**
- `backend/Dockerfile` : image Python 3.12-slim, utilisateur non-root, installation dependances, Gunicorn
- `frontend/Dockerfile` : build multi-stage (Node 20 → Nginx Alpine)
- `docker-compose.yml` : 4 services orchestres
  - `db` : PostgreSQL 16 avec healthcheck et volume persistant
  - `backend` : Django + Gunicorn, migrations auto au demarrage
  - `frontend` : React build servi par Nginx
  - `nginx` : reverse proxy, seul port expose (80)
- Reseau Docker bridge isole (`vulnreport-net`)
- `.dockerignore` pour backend et frontend
- Commande de demarrage : migrations → seed data → Gunicorn

**Fichiers modifies :**
```
backend/Dockerfile
frontend/Dockerfile
docker-compose.yml
backend/.dockerignore
frontend/.dockerignore
nginx/nginx.conf
```

**Securite Docker :**
- Utilisateur non-root dans le conteneur backend
- Seul Nginx expose sur le port 80 (backend/frontend internes)
- Pas de credentials par defaut (docker-compose echoue si .env absent)
- `restart: unless-stopped` sur tous les services

---

### `sec/20-audit-securite-complet`

**Issue liee** : #20 — Audit securite complet
**Sprint** : Sprint 3 — Pipeline et Finalisation
**Responsable** : Antoine C. (Securite/DevOps)
**MR** : !5

**Ce qui a ete fait :**
Audit de securite exhaustif de tout le code, avec **79 vulnerabilites identifiees et corrigees** :

| Severite | Nombre | Exemples |
|----------|--------|----------|
| CRITICAL | 4 | SECRET_KEY nullable, credentials par defaut, pipeline non-bloquant |
| HIGH | 17 | Pas de rate limiting, password validators non appliques, CSP unsafe-inline |
| MEDIUM | 34 | Enumeration de comptes, CVSS non valide, admin path par defaut |
| LOW | 24 | Headers manquants, React anti-patterns |

**Corrections majeures :**
- Rate limiting sur le login (5 tentatives/minute)
- Anti-enumeration de comptes (meme message d'erreur partout)
- Password validators Django appliques (12 chars minimum)
- Session invalidation apres changement de mot de passe
- Audit log immutable (pas de modification ni suppression)
- CSP durci (suppression unsafe-inline et unsafe-eval)
- CVSS valide entre 0.0 et 10.0
- Transitions de statut controlees
- Admin ne peut pas se desactiver lui-meme

**Fichiers modifies :** 16 fichiers backend + frontend + infra

---

### `feature/15-tests-backend`

**Issue liee** : #15 — Tests backend
**Sprint** : Sprint 2 — Coeur Fonctionnel
**Responsable** : Raphael L. (Backend)
**MR** : !6

**Ce qui a ete fait :**
86 tests unitaires repartis sur 4 fichiers :

| Fichier | Tests | Ce qui est teste |
|---------|-------|-----------------|
| `accounts/tests.py` | 25 | Login, logout, anti-enumeration, RBAC, politique mots de passe, auto-demotion |
| `reports/tests.py` | 27 | Ownership, transitions statut, creation findings, CVSS, pre-remplissage KB |
| `kb/tests.py` | 18 | Lecture tous roles, CRUD admin-only, recherche, filtrage |
| `audit/tests.py` | 16 | Immutabilite, logging actions, acces admin-only |

**Exemples de tests critiques :**
- Un pentester ne peut PAS voir les rapports d'un autre pentester
- Un viewer ne peut PAS creer de rapport
- Un admin ne peut PAS se desactiver lui-meme
- Un mot de passe de 8 caracteres est REJETE (minimum 12)
- Un score CVSS de 11.0 est REJETE
- Un log d'audit ne peut PAS etre modifie apres creation

---

### `docs/21-rapport-securite`

**Issue liee** : #21 — Rapport de securite final
**Sprint** : Sprint 3 — Pipeline et Finalisation
**Responsable** : Antoine C. (Securite/DevOps)
**MR** : !7

**Ce qui a ete fait :**
Rapport de securite complet de 10 pages (`docs/rapport-securite.md`) :

1. **Introduction** : contexte, objectifs, perimetre
2. **Architecture technique** : schema, stack, conteneurs
3. **Mesures de securite** : authentification (Argon2id), RBAC, OWASP Top 10, headers, audit log
4. **Analyse des risques** : matrice 10 risques (P x I), analyse CIA
5. **Resultats des scans** : SAST (Bandit, Semgrep), SCA (Safety, Trivy), secrets (TruffleHog)
6. **Corrections appliquees** : 79 issues par categorie et severite
7. **Pipeline CI/CD** : 7 stages, politique de blocage
8. **Risques residuels** : TLS, 2FA, WAF, chiffrement au repos
9. **Conclusion** : bilan Security by Design

---

### `ci/17-pipeline-complet`

**Issue liee** : #17 — Pipeline CI/CD complet
**Sprint** : Sprint 3 — Pipeline et Finalisation
**Responsable** : Antoine C. (Securite/DevOps)
**MR** : !8

**Ce qui a ete fait :**
Pipeline GitLab CI/CD avec 7 stages et 8 jobs :

```
LINT → SAST → SCA → BUILD → SECRETS → DEPLOY
```

| Stage | Job | Outil | Resultat |
|-------|-----|-------|---------|
| Lint | lint-python | flake8 + ruff | OK |
| SAST | sast-bandit | Bandit | OK — rapports JSON + HTML |
| SAST | sast-semgrep | Semgrep | OK — rapport JSON |
| SCA | sca-safety | Safety | OK — CVE Python |
| SCA | sca-trivy | Trivy | Echec (allow_failure) |
| SCA | sca-npm-audit | npm audit | OK — CVE JavaScript |
| Build | build-backend | Docker | Echec (allow_failure) |
| Secrets | secrets-trufflehog | TruffleHog | OK — aucun secret detecte |

**Politique :**
- Les scans de secrets bloquent le pipeline si des secrets sont trouves
- Les autres scans sont en `allow_failure` pour ne pas bloquer le dev
- Le deploy est manuel et conditionne a `branch=main` + `ENVIRONMENT=prod`
- Tous les rapports sont conserves comme artefacts pendant 1 semaine

---

## Resume visuel

```
main ─────────────────────────────────────────────────────── (branche protegee)
  │
  ├── feature/9-module-kb-crud ──────── MR !1 ──→ merge
  ├── feature/10-module-rapports ────── MR !2 ──→ merge
  ├── feature/15-tests-backend ──────── MR !6 ──→ merge
  │
  ├── sec/8-headers-securite-http ───── MR !3 ──→ merge
  ├── sec/20-audit-securite-complet ─── MR !5 ──→ merge
  │
  ├── ops/2-creation-dockerfile ─────── MR !4 ──→ merge
  ├── ci/17-pipeline-complet ────────── MR !8 ──→ merge
  │
  └── docs/21-rapport-securite ──────── MR !7 ──→ merge
```
