# VulnReport

Assistant de generation de rapports de Pentest & Base de Connaissance Offensive.

**Projet UE7 DevSecOps** - Guardia Cybersecurity School (B2/GCS2)

## Equipe

| Membre | Role | Responsabilites |
|--------|------|-----------------|
| Noa B. | Chef de Projet | Coordination, gestion board GitLab, suivi jalons |
| Diego D. | Frontend | Interfaces React, integration backend, UX |
| Raphael L. | Backend | Django/DRF, auth, RBAC, modules metier |
| Antoine C. | Securite/DevOps | CI/CD, Docker, SAST/SCA, headers securite |

## Stack Technique

- **Backend** : Django 5.1 + Django REST Framework
- **Frontend** : React 18 (SPA)
- **Base de donnees** : PostgreSQL 16
- **Conteneurisation** : Docker + docker-compose
- **CI/CD** : GitLab CI/CD (SAST, SCA, DAST, Secrets)
- **Securite** : Argon2id, RBAC, CSP, HSTS, cookies securises

## Demarrage Rapide

### Prerequis

- Docker et Docker Compose installes
- Git

### Installation

```bash
# 1. Cloner le depot
git clone <URL_DU_DEPOT>
cd vulnreport

# 2. Copier le fichier d'environnement
cp .env.example .env

# 3. Modifier les variables d'environnement dans .env
# (notamment les mots de passe)

# 4. Lancer l'application
docker compose up --build -d

# 5. L'application est accessible sur :
#    - Frontend : http://localhost:3000
#    - API Backend : http://localhost:8000/api/
#    - Admin Django : http://localhost:8000/admin/
#    - Nginx (reverse proxy) : http://localhost:80
```

### Commandes Utiles

```bash
# Voir les logs
docker compose logs -f

# Voir les logs d'un service specifique
docker compose logs -f backend

# Arreter l'application
docker compose down

# Arreter et supprimer les volumes (reset DB)
docker compose down -v

# Relancer les migrations
docker compose exec backend python manage.py migrate

# Relancer le seed
docker compose exec backend python manage.py seed_data

# Creer un superuser manuellement
docker compose exec backend python manage.py createsuperuser

# Lancer les tests
docker compose exec backend python manage.py test
```

## Comptes Seed

L'application cree automatiquement 3 comptes au demarrage :

| Role | Username | Email | Mot de passe par defaut |
|------|----------|-------|------------------------|
| **Admin** | admin | admin@vulnreport.local | `Admin@VulnReport2026!` |
| **Pentester** | pentester1 | pentester@vulnreport.local | `Pentester@VulnReport2026!` |
| **Viewer** | viewer1 | viewer@vulnreport.local | `Viewer@VulnReport2026!` |

> Les mots de passe par defaut peuvent etre modifies via les variables d'environnement `ADMIN_PASSWORD`, `PENTESTER_PASSWORD`, `VIEWER_PASSWORD`.

## Variables d'Environnement

| Variable | Description | Defaut |
|----------|-------------|--------|
| `DJANGO_SECRET_KEY` | Cle secrete Django | (requis) |
| `DJANGO_DEBUG` | Mode debug | `False` |
| `DJANGO_ALLOWED_HOSTS` | Hotes autorises | `localhost,127.0.0.1` |
| `DB_NAME` | Nom de la base | `vulnreport` |
| `DB_USER` | Utilisateur DB | `vulnreport_user` |
| `DB_PASSWORD` | Mot de passe DB | (requis) |
| `DB_HOST` | Hote DB | `db` |
| `DB_PORT` | Port DB | `5432` |
| `CSRF_TRUSTED_ORIGINS` | Origines CSRF | `http://localhost:3000` |
| `CORS_ALLOWED_ORIGINS` | Origines CORS | `http://localhost:3000` |
| `ADMIN_PASSWORD` | MDP admin seed | `Admin@VulnReport2026!` |
| `PENTESTER_PASSWORD` | MDP pentester seed | `Pentester@VulnReport2026!` |
| `VIEWER_PASSWORD` | MDP viewer seed | `Viewer@VulnReport2026!` |

## Architecture

```
                   +------------------+
                   |    Nginx :80     |
                   |  (reverse proxy) |
                   +--------+---------+
                            |
               +------------+------------+
               |                         |
      +--------v--------+     +---------v--------+
      | Frontend :3000   |     | Backend :8000    |
      | (React SPA)      |     | (Django + DRF)   |
      +-----------------+     +--------+---------+
                                       |
                              +--------v--------+
                              | PostgreSQL :5432 |
                              | (Donnees)        |
                              +-----------------+
```

## RBAC (Roles et Permissions)

| Action | Viewer | Pentester | Admin |
|--------|:------:|:---------:|:-----:|
| Consulter KB | X | X | X |
| Consulter rapports publies | X | X | X |
| Creer un rapport | | X | X |
| Editer ses rapports | | X | X |
| Supprimer ses rapports | | X | X |
| Voir tous les rapports | | | X |
| Supprimer tout rapport | | | X |
| Gerer la KB (CRUD) | | | X |
| Gerer les utilisateurs | | | X |
| Consulter l'audit log | | | X |
| Voir le dashboard | | X (ses donnees) | X (global) |

## Pipeline CI/CD

Le pipeline GitLab CI/CD comporte 7 stages :

1. **Lint** : flake8 + ruff (conformite PEP8)
2. **SAST** : Bandit + Semgrep (analyse statique securite)
3. **SCA** : Safety + Trivy (vulnerabilites des dependances)
4. **Build** : Construction de l'image Docker
5. **DAST** : OWASP ZAP (test dynamique - manuel)
6. **Secrets** : TruffleHog (detection de secrets)
7. **Deploy** : Deploiement (manuel, branche main + ENVIRONMENT=prod)

Tous les artefacts (rapports JSON/HTML) sont conserves 1 semaine.

## Mesures de Securite

- **Authentification** : Argon2id (hashage mots de passe)
- **Sessions** : Cookies HttpOnly, Secure, SameSite=Strict, expiration 1h
- **RBAC** : Verification role + ownership cote serveur sur chaque endpoint
- **Anti-SQLi** : ORM Django (requetes parametrees exclusivement)
- **Anti-XSS** : Echappement automatique Django/React + CSP
- **Anti-CSRF** : Tokens CSRF Django + SameSite=Strict
- **Headers** : HSTS, X-Frame-Options DENY, X-Content-Type-Options nosniff
- **Secrets** : Variables d'environnement, jamais dans le code source
- **Audit** : Journalisation de toutes les actions sensibles

## Structure du Projet

```
vulnreport/
├── .gitlab-ci.yml          # Pipeline CI/CD
├── docker-compose.yml      # Orchestration Docker
├── .env.example            # Template variables d'env
├── README.md               # Ce fichier
├── CLAUDE.md               # Specifications techniques
│
├── backend/                # Django + DRF
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── vulnreport/         # Config Django (settings, urls, wsgi)
│   ├── accounts/           # Auth, RBAC, gestion utilisateurs
│   ├── reports/            # Rapports + Findings
│   ├── kb/                 # Base de Connaissance + Ressources
│   └── audit/              # Audit Log
│
├── frontend/               # React SPA
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── components/     # Navbar, ProtectedRoute
│       ├── context/        # AuthContext
│       ├── pages/          # Login, Dashboard, Reports, KB, Admin
│       └── services/       # API client Axios
│
└── nginx/                  # Reverse proxy
    └── nginx.conf
```

## Licence

Projet academique - Guardia Cybersecurity School 2025-2026.

## Contributeurs

- Noa B. — Chef de Projet
- Diego D. — Responsable Frontend
- Raphael L. — Responsable Backend
- Antoine C. — Responsable Securite / DevOps

## Gestion de Projet

Le projet est gere via le board GitLab avec 3 sprints et 25 issues.
Voir docs/usage-gitlab.md pour le detail de l'utilisation de GitLab.
