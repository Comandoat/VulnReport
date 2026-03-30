# Utilisation de GitLab dans le Projet VulnReport

## 1. Organisation du Depot

**URL du projet** : https://gitlab.com/Comandoat/VulnReport (prive)

Le depot GitLab est le point central du projet. Il heberge le code source, la gestion de projet (issues, board), et le pipeline CI/CD.

### Structure du depot
```
VulnReport/
├── backend/          # Django + DRF (API REST)
├── frontend/         # React (SPA)
├── nginx/            # Reverse proxy
├── ateliers/         # Livrables des ateliers pratiques
├── docs/             # Documentation (rapport securite, etc.)
├── docker-compose.yml
├── .gitlab-ci.yml    # Pipeline CI/CD
└── README.md
```

---

## 2. Conventions de Branches

Chaque tache suit la regle : **1 issue = 1 branche = 1 Merge Request**.

Les prefixes de branches permettent d'identifier immediatement le type de travail :

| Prefixe | Usage | Exemple |
|---------|-------|---------|
| `feature/` | Nouvelle fonctionnalite | `feature/9-module-kb-crud` |
| `fix/` | Correction de bug | `fix/15-erreur-affichage` |
| `sec/` | Mesure de securite | `sec/8-headers-securite-http` |
| `ops/` | Infrastructure Docker/CI | `ops/2-creation-dockerfile` |
| `ci/` | Pipeline CI/CD | `ci/17-pipeline-complet` |
| `docs/` | Documentation | `docs/21-rapport-securite` |
| `refactor/` | Refactoring | `refactor/11-nettoyage-auth` |

### Branches creees dans le projet

- `main` — branche principale (protegee)
- `feature/9-module-kb-crud` — module KB
- `feature/10-module-rapports` — module rapports + findings
- `feature/15-tests-backend` — tests unitaires
- `sec/8-headers-securite-http` — headers de securite
- `sec/20-audit-securite-complet` — audit securite (79 corrections)
- `ops/2-creation-dockerfile` — conteneurisation Docker
- `ci/17-pipeline-complet` — pipeline DevSecOps
- `docs/21-rapport-securite` — rapport de securite final

---

## 3. Issues et Milestones

### Milestones (Sprints)

Le projet est organise en 3 sprints, chacun represente par un milestone GitLab :

| Milestone | Periode | Issues | Statut |
|-----------|---------|--------|--------|
| Sprint 1 — Fondations | 23/03 - 29/03 | 8 issues | Ferme |
| Sprint 2 — Coeur Fonctionnel | 30/03 - 05/04 | 8 issues | Ferme |
| Sprint 3 — Pipeline et Finalisation | 06/04 - 10/04 | 9 issues | Ouvert |

### Issues (25 au total)

Chaque issue represente une tache concrete, assignee a un membre de l'equipe et etiquetee :

**Sprint 1** (8 issues) :
- #1 Initialisation depot GitLab
- #2 Creation Dockerfile et docker-compose
- #3 Structure base de donnees
- #4 Authentification securisee (Argon2id)
- #5 RBAC strict (Viewer/Pentester/Admin)
- #6 Headers HTTP de securite
- #7 Pipeline CI/CD initial
- #8 Seed data

**Sprint 2** (8 issues) :
- #9 Module KB — CRUD Admin
- #10 Module Rapports
- #11 Module Findings
- #12 Audit log
- #13 Dashboard
- #14 Validation entrees
- #15 Tests backend
- #16 Frontend React

**Sprint 3** (9 issues) :
- #17 Pipeline CI/CD complet
- #18 Integration DAST
- #19 TruffleHog bloquant
- #20 Audit securite complet
- #21 Rapport de securite
- #22 README
- #23 Rate limiting
- #24 Transition statut rapport
- #25 npm audit frontend

### Labels

Les labels permettent de categoriser et filtrer les issues :

| Label | Couleur | Usage |
|-------|---------|-------|
| `feature` | Bleu | Fonctionnalites metier |
| `security` | Rouge | Mesures de securite |
| `fix` | Rouge clair | Corrections de bugs |
| `ops` | Vert | Infrastructure Docker/CI |
| `docs` | Orange | Documentation |
| `refactor` | Violet | Refactoring |
| `priority::high` | Rouge | Priorite haute |
| `priority::medium` | Jaune | Priorite moyenne |
| `priority::low` | Vert | Priorite basse |
| `status::done` | Gris | Termine |

---

## 4. Merge Requests (MR)

Chaque branche fait l'objet d'une Merge Request vers `main`. La MR permet :
- La **revue de code** par les autres membres
- L'execution automatique du **pipeline CI/CD**
- La **tracabilite** des changements

### MR du projet

| MR | Titre | Branche | Labels |
|----|-------|---------|--------|
| !1 | Module KB - CRUD Admin | `feature/9-module-kb-crud` | feature |
| !2 | Module Rapports - CRUD + Findings | `feature/10-module-rapports` | feature |
| !3 | Headers HTTP de securite | `sec/8-headers-securite-http` | security |
| !4 | Docker multi-conteneurs | `ops/2-creation-dockerfile` | ops |
| !5 | Audit securite - 79 corrections | `sec/20-audit-securite-complet` | security |
| !6 | 86 tests backend | `feature/15-tests-backend` | feature |
| !7 | Rapport de securite final | `docs/21-rapport-securite` | docs |
| !8 | Pipeline DevSecOps 7 stages | `ci/17-pipeline-complet` | ops |

### Regles de merge

- **Pipeline obligatoire** : une MR ne peut etre mergee que si le pipeline CI/CD passe
- **Suppression auto de la branche** : apres merge, la branche source est supprimee
- **Branche `main` protegee** : pas de push direct, uniquement via MR

---

## 5. Pipeline CI/CD

Le pipeline est defini dans `.gitlab-ci.yml` et se declenche automatiquement a chaque push.

### Les 7 stages

```
Push sur GitLab
      |
      v
 ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌────────┐
 │  LINT    │ -> │   SAST   │ -> │   SCA   │ -> │  BUILD  │ -> │ SECRETS  │ -> │ DEPLOY │
 │ flake8   │    │ Bandit   │    │ Safety  │    │ Docker  │    │TruffleHog│    │(manuel)│
 │ ruff     │    │ Semgrep  │    │ Trivy   │    │ build   │    │          │    │        │
 │          │    │          │    │npm audit│    │         │    │          │    │        │
 └─────────┘    └──────────┘    └─────────┘    └─────────┘    └──────────┘    └────────┘
```

### Description des jobs

| Stage | Job | Outil | Ce qu'il fait |
|-------|-----|-------|---------------|
| Lint | lint-python | flake8 + ruff | Verifie le style du code Python (PEP8) |
| SAST | sast-bandit | Bandit | Detecte les vulnerabilites dans le code Python |
| SAST | sast-semgrep | Semgrep | Detecte les patterns de code dangereux |
| SCA | sca-safety | Safety | Cherche les CVE dans les dependances Python |
| SCA | sca-trivy | Trivy | Scanne les dependances et images Docker |
| SCA | sca-npm-audit | npm audit | Cherche les CVE dans les dependances JS |
| Build | build-backend | Docker | Construit l'image Docker du backend |
| Secrets | secrets-trufflehog | TruffleHog | Detecte les secrets dans le code |
| Deploy | deploy-production | - | Deploiement (manuel, main + prod) |

### Artefacts

Chaque job de scan genere un rapport (artefact) conserve 1 semaine :
- `bandit-report.json` / `bandit-report.html`
- `semgrep-report.json`
- `safety-report.json`
- `trivy-report.json`
- `npm-audit-report.json`
- `secrets-scan.txt`

### Resultats du pipeline

Le pipeline fonctionne sur les shared runners GitLab.com :
- **6 jobs reussis** sur 8
- 2 echecs en `allow_failure` (trivy image incompatible, docker-in-docker non disponible sur free tier)

---

## 6. Variables CI/CD

Les secrets sont stockes dans les variables CI/CD de GitLab (Settings > CI/CD > Variables), jamais dans le code :

| Variable | Usage | Masquee |
|----------|-------|---------|
| `DJANGO_SECRET_KEY` | Cle secrete Django | Oui |
| `DB_PASSWORD` | Mot de passe PostgreSQL | Oui |
| `POSTGRES_PASSWORD` | Idem (pour le conteneur) | Oui |
| `CRON_SECRET` | Secret pour les cron jobs | Oui |

---

## 7. Board Kanban

Le board GitLab permet de visualiser l'avancement du projet en colonnes :

```
┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐
│   Open   │  │  In Progress │  │  Review  │  │  Closed  │
├──────────┤  ├──────────────┤  ├──────────┤  ├──────────┤
│          │  │              │  │          │  │ #1 - #25 │
│          │  │              │  │          │  │(25 issues│
│          │  │              │  │          │  │ fermees) │
└──────────┘  └──────────────┘  └──────────┘  └──────────┘
```

Toutes les 25 issues sont en statut "Closed" car le developpement est termine.

---

## 8. Workflow de Contribution

Le workflow suivi par l'equipe pour chaque tache :

```
1. Creer une issue sur GitLab (description, labels, milestone)
       |
2. Creer une branche depuis l'issue (feature/XX-description)
       |
3. Developper sur la branche locale
       |
4. Push vers GitLab -> pipeline CI/CD se declenche
       |
5. Creer une Merge Request vers main
       |
6. Pipeline passe ? -> Review par un membre de l'equipe
       |
7. Approuver et merger -> branche supprimee automatiquement
       |
8. Issue fermee automatiquement
```

---

## 9. Securite du Depot

- **Depot prive** : seuls les membres de l'equipe y ont acces
- **Branche main protegee** : merge uniquement via MR avec pipeline OK
- **Secrets masques** : variables CI/CD non visibles dans les logs
- **Detection de secrets** : TruffleHog dans le pipeline
- **`.gitignore`** : exclut `.env`, `__pycache__`, `node_modules`, credentials
