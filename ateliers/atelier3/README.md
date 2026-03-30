# Atelier 3 - SAST, DAST, Detection de Secrets et Patch Management

## Introduction

Cet atelier couvre les quatre piliers de la securite applicative automatisee :
1. **SAST** (Static Application Security Testing) avec Bandit
2. **DAST** (Dynamic Application Security Testing) avec OWASP ZAP
3. **Detection de secrets** avec TruffleHog
4. **Patch Management** des dependances avec des outils automatises

L'objectif est d'integrer ces outils dans un pipeline CI/CD GitLab pour obtenir une couverture de securite complete.

---

## Partie 1 - Analyse SAST avec Bandit

### 1.1 Qu'est-ce que le SAST ?

Le SAST (Static Application Security Testing) est une methode d'analyse de securite qui examine le code source **sans l'executer**. L'outil parcourt le code a la recherche de patterns connus comme vulnerables : utilisation de fonctions dangereuses, secrets en dur, configurations insecurees, etc.

**Avantages du SAST :**
- Detection precoce des vulnerabilites (shift-left)
- Pas besoin d'environnement d'execution
- Couverture de tout le code, meme le code mort
- Rapide a executer dans un pipeline CI/CD

**Limites du SAST :**
- Faux positifs frequents
- Ne detecte pas les vulnerabilites a l'execution (runtime)
- Specifique a un langage (Bandit = Python uniquement)
- Ne comprend pas le contexte metier

### 1.2 Installation et utilisation locale de Bandit

#### Installation

```bash
pip install bandit
```

Verification de l'installation :

```bash
bandit --version
```

#### Commande d'analyse locale

```bash
# Analyse basique sur le dossier backend
bandit -r backend/ -f json -o bandit-report.json -ll

# Analyse avec rapport HTML
bandit -r backend/ -f html -o bandit-report.html -ll

# Analyse en excluant les tests et migrations
bandit -r backend/ -f json -o bandit-report.json -ll \
  --exclude "*/tests/*,*/migrations/*,*/node_modules/*"
```

**Explication des options :**
- `-r backend/` : analyse recursive du dossier backend
- `-f json` : format de sortie JSON
- `-o bandit-report.json` : fichier de sortie
- `-ll` : affiche uniquement les severites MEDIUM et HIGH (filtre le bruit)
- `--exclude` : exclut les dossiers non pertinents

#### Interpretation des resultats

Bandit classe les resultats par :
- **Severite** : LOW, MEDIUM, HIGH
- **Confiance** : LOW, MEDIUM, HIGH
- **Test ID** : identifiant unique du type de vulnerabilite (ex: B105, B602)

### 1.3 Types de vulnerabilites detectees par Bandit

#### B104 - Binding sur 0.0.0.0

```python
# VULNERABLE - ecoute sur toutes les interfaces
app.run(host='0.0.0.0', port=5000)

# CORRIGE - ecoute uniquement en local
app.run(host='127.0.0.1', port=5000)
```

**Risque :** Exposer le service sur toutes les interfaces reseau, y compris les interfaces publiques, peut permettre un acces non autorise.

#### B602 - Utilisation de subprocess avec shell=True

```python
# VULNERABLE - injection de commande possible
import subprocess
subprocess.call("ls " + user_input, shell=True)

# CORRIGE - utiliser une liste d'arguments
subprocess.call(["ls", user_input], shell=False)
```

**Risque :** L'utilisation de `shell=True` avec des entrees utilisateur permet l'injection de commandes systeme.

#### B101 - Utilisation de assert pour la securite

```python
# VULNERABLE - assert desactive en mode optimise (-O)
def delete_user(user, admin):
    assert user.is_admin, "Not admin"
    user.delete()

# CORRIGE - utiliser une vraie verification
def delete_user(user, admin):
    if not user.is_admin:
        raise PermissionError("Not admin")
    user.delete()
```

**Risque :** Les instructions `assert` sont supprimees quand Python est execute en mode optimise (`python -O`), ce qui desactive les verifications de securite.

#### B105 / B106 - Mots de passe en dur

```python
# VULNERABLE - mot de passe en dur dans le code
DB_PASSWORD = "admin@123"
connection = psycopg2.connect(password="secret123")

# CORRIGE - utiliser des variables d'environnement
import os
DB_PASSWORD = os.environ.get("DB_PASSWORD")
connection = psycopg2.connect(password=os.environ["DB_PASSWORD"])
```

**Risque :** Les secrets en dur dans le code sont exposes dans le depot Git et visibles par tous les developpeurs.

#### B108 - Utilisation de /tmp

```python
# VULNERABLE - fichier temporaire previsible
f = open('/tmp/my_app_data.txt', 'w')

# CORRIGE - utiliser tempfile
import tempfile
f = tempfile.NamedTemporaryFile(delete=False)
```

**Risque :** Les fichiers dans `/tmp` sont accessibles a tous les utilisateurs du systeme, ce qui peut mener a des attaques de type symlink ou race condition.

### 1.4 Exemples de findings typiques sur un projet Django

Sur un projet Django classique, Bandit detecte generalement :

| Test ID | Description | Severite | Exemple |
|---------|-------------|----------|---------|
| B104 | Binding 0.0.0.0 | MEDIUM | `runserver 0.0.0.0:8000` |
| B105 | Hardcoded password | LOW | `SECRET_KEY = "abc123"` dans settings.py |
| B110 | try/except/pass | LOW | Exceptions silencieuses |
| B303 | Utilisation de MD5/SHA1 | MEDIUM | Hashage faible pour les mots de passe |
| B608 | SQL injection | MEDIUM | Requetes SQL construites par concatenation |
| B703 | Jinja2 autoescape off | HIGH | Templates sans echappement automatique |

### 1.5 Integration dans GitLab CI/CD

Le job Bandit dans le pipeline (voir `.gitlab-ci.yml`) :

```yaml
sast-bandit:
  stage: sast
  image: python:3.12-slim
  before_script:
    - pip install bandit
  script:
    - bandit -r . -f json -o bandit-report.json --exclude "*/tests/*,*/migrations/*,*/node_modules/*" -ll
    - bandit -r . -f html -o bandit-report.html --exclude "*/tests/*,*/migrations/*,*/node_modules/*" -ll
  artifacts:
    paths:
      - bandit-report.json
      - bandit-report.html
    when: always
    expire_in: 1 week
```

**Points cles de la configuration :**
- `when: always` pour les artefacts : le rapport est conserve meme si Bandit trouve des vulnerabilites (exit code != 0)
- Exclusion des dossiers de tests et migrations qui generent du bruit
- Double rapport JSON (pour traitement automatise) + HTML (pour lecture humaine)
- `expire_in: 1 week` : nettoyage automatique des rapports

---

## Partie 2 - Tests DAST avec OWASP ZAP

### 2.1 Qu'est-ce que le DAST ?

Le DAST (Dynamic Application Security Testing) teste une application **en cours d'execution**. Contrairement au SAST qui analyse le code source, le DAST envoie des requetes HTTP et analyse les reponses pour detecter des vulnerabilites.

**Avantages du DAST :**
- Teste l'application dans son contexte reel
- Independant du langage de programmation
- Detecte les problemes de configuration serveur
- Peu de faux positifs par rapport au SAST

**Limites du DAST :**
- Necessite une application deployee et fonctionnelle
- Ne couvre que les endpoints decouverts
- Plus lent que le SAST
- Ne peut pas identifier la ligne de code a corriger

### 2.2 Test local sur DVWA

#### Lancement de DVWA

DVWA (Damn Vulnerable Web Application) est une application web volontairement vulnerable, ideale pour tester les outils DAST.

```bash
# Lancement de DVWA via Docker
docker run -d -p 80:80 vulnerables/web-dvwa

# Verification
curl http://localhost:80
```

**Acces :** http://localhost avec les identifiants `admin` / `password`

#### Configuration de ZAP en mode GUI

1. **Telecharger et installer** OWASP ZAP depuis https://www.zaproxy.org/
2. **Lancer ZAP** et configurer le proxy sur `localhost:8080`
3. **Configurer le navigateur** pour utiliser le proxy ZAP
4. **Naviguer** vers DVWA pour que ZAP decouvre les pages

#### Scan de base (Spider + Active Scan)

1. **Spider (exploration)** : ZAP parcourt automatiquement les liens de l'application
   - Clic droit sur le site dans l'arbre > Spider > Start Scan
   - Le spider decouvre toutes les pages accessibles

2. **Active Scan** : ZAP envoie des payloads d'attaque sur chaque parametre
   - Clic droit sur le site > Active Scan > Start Scan
   - ZAP teste les injections SQL, XSS, etc.

#### Resultats typiques sur DVWA

| Vulnerabilite | Severite | Description |
|---------------|----------|-------------|
| SQL Injection | HIGH | Parametres injectables dans les formulaires |
| XSS (Reflected) | HIGH | Scripts injectes reflechis dans les reponses |
| XSS (Stored) | HIGH | Scripts stockes en base de donnees |
| CSRF | MEDIUM | Absence de tokens anti-CSRF |
| Session Management | MEDIUM | Cookies sans flags Secure/HttpOnly |
| Directory Listing | LOW | Repertoires accessibles sans index |
| Information Disclosure | LOW | Headers serveur revelant les versions |

### 2.3 Pipeline complet sur Juice Shop

#### Presentation de OWASP Juice Shop

OWASP Juice Shop est une application Node.js volontairement vulnerable, plus moderne que DVWA. Elle contient plus de 100 challenges de securite couvrant le OWASP Top 10.

#### Fork et import sur GitLab

```bash
# Cloner le repository
git clone https://github.com/juice-shop/juice-shop.git

# Ajouter le remote GitLab
cd juice-shop
git remote add gitlab https://gitlab.com/<votre-namespace>/juice-shop.git
git push gitlab main
```

#### Pipeline CI/CD avec ZAP

Le pipeline complet est defini dans le fichier `.gitlab-ci.yml` de cet atelier. Les etapes cles sont :

1. **Pull de l'image Juice Shop** : utilisation de l'image Docker officielle `bkimminich/juice-shop`
2. **Lancement comme service** : Juice Shop tourne comme un service GitLab CI accessible via l'alias `juice-shop` sur le port 3000
3. **Scan ZAP** : execution de `zap-baseline.py` en mode headless contre le service
4. **Generation des rapports** : rapports HTML et JSON conserves comme artefacts

```yaml
dast-zap-juice-shop:
  stage: dast
  image: ghcr.io/zaproxy/zaproxy:stable
  services:
    - name: bkimminich/juice-shop
      alias: juice-shop
  variables:
    ZAP_TARGET: "http://juice-shop:3000"
  script:
    - mkdir -p /zap/wrk
    - sleep 30  # Attendre le demarrage de Juice Shop
    - zap-baseline.py -t $ZAP_TARGET -r zap-report.html -J zap-report.json -I
    - cp /zap/wrk/zap-report.html . 2>/dev/null || true
    - cp /zap/wrk/zap-report.json . 2>/dev/null || true
  artifacts:
    paths:
      - zap-report.html
      - zap-report.json
    when: always
```

**Points importants :**
- `sleep 30` : Juice Shop met du temps a demarrer, il faut attendre
- `-I` : ignore les warnings pour ne pas faire echouer le pipeline
- `allow_failure: true` : le pipeline continue meme si ZAP trouve des vulnerabilites
- `when: manual` : le scan DAST est declenche manuellement car il est long

### 2.4 Questions d'analyse - Reponses completes

#### Question 1 : Quelles categories de vulnerabilites sont detectees par le DAST ?

Le DAST detecte principalement les vulnerabilites suivantes :

1. **Headers HTTP manquants ou mal configures :**
   - Absence de `X-Content-Type-Options: nosniff`
   - Absence de `X-Frame-Options` (clickjacking)
   - Absence de `Content-Security-Policy` (CSP)
   - Absence de `Strict-Transport-Security` (HSTS)
   - Header `Server` revelant la version du serveur

2. **Cross-Site Scripting (XSS) :**
   - XSS reflechi : injection dans les parametres URL ou formulaires
   - XSS stocke : injection persistante via les champs de saisie
   - XSS base sur le DOM : manipulation du DOM cote client

3. **Injection SQL :**
   - Injection classique dans les parametres GET/POST
   - Injection aveugle (blind SQL injection)
   - Injection basee sur les erreurs

4. **Cross-Site Request Forgery (CSRF) :**
   - Formulaires sans token anti-CSRF
   - Actions sensibles accessibles sans verification d'origine

5. **Information Disclosure :**
   - Pages d'erreur detaillees (stack traces)
   - Fichiers de configuration accessibles
   - Commentaires HTML contenant des informations sensibles

6. **Cookies insecurises :**
   - Absence du flag `Secure`
   - Absence du flag `HttpOnly`
   - Absence du flag `SameSite`
   - Duree de vie excessive

7. **Directory Listing :**
   - Repertoires accessibles sans fichier index
   - Fichiers sensibles exposes (.git, .env, backup)

#### Question 2 : Quelles sont les limites d'une analyse DAST automatisee ?

Les limites majeures du DAST automatise sont :

1. **Couverture limitee aux endpoints decouverts :**
   - Le spider ne peut decouvrir que les pages liees par des liens HTML
   - Les API REST/GraphQL necessitent une specification OpenAPI/Swagger pour etre testees
   - Les pages protegees par authentification multi-facteur sont inaccessibles
   - Les applications SPA (Single Page Application) avec routing dynamique sont mal couvertes

2. **Pas de comprehension de la logique metier :**
   - Le DAST ne comprend pas les regles de gestion de l'application
   - Il ne peut pas tester si un utilisateur standard peut acceder aux fonctions admin
   - Les workflows complexes (panier -> paiement -> confirmation) ne sont pas testes de bout en bout

3. **Faux positifs :**
   - Certains mecanismes de protection sont interpretes comme des vulnerabilites
   - Les WAF (Web Application Firewalls) peuvent masquer les vraies vulnerabilites
   - Les reponses HTTP ambigues generent des alertes non pertinentes

4. **Vulnerabilites d'authentification complexe :**
   - Le DAST ne teste pas l'enumeration d'utilisateurs de maniere fiable
   - Les failles de logique d'authentification (ex: reset password) ne sont pas detectees
   - Les problemes de gestion de sessions complexes echappent au scan

5. **Dependance a l'environnement :**
   - L'application doit etre deployee et fonctionnelle
   - L'environnement de test doit etre representatif de la production
   - Les scans peuvent etre lents (plusieurs heures pour une application complexe)

6. **Impact sur l'application :**
   - Les scans actifs peuvent modifier les donnees (creation de comptes, commandes)
   - Risque de crash de l'application sous la charge des requetes
   - Necessite un environnement de test dedie

#### Question 3 : Quels types de vulnerabilites echappent au DAST ?

Les vulnerabilites suivantes ne sont generalement **pas detectees** par le DAST :

1. **Business Logic Flaws :**
   - Contournement des regles de gestion (prix negatif, quantite zero)
   - Escalade de privileges horizontale (acceder aux donnees d'un autre utilisateur)
   - Abus de fonctionnalites (envoi massif d'emails, brute force lent)

2. **Race Conditions :**
   - Conditions de concurrence sur les transactions
   - Double spending (double utilisation d'un bon de reduction)
   - Time-of-check to time-of-use (TOCTOU)

3. **Injection de code cote serveur non expose :**
   - Server-Side Request Forgery (SSRF) complexe
   - Remote Code Execution via deserialization
   - Template injection cote serveur (SSTI)

4. **Cryptographie faible :**
   - Utilisation de MD5/SHA1 pour le hashage des mots de passe
   - Cles de chiffrement faibles
   - Mauvaise implementation de TLS/SSL (sauf les headers)
   - Stockage de secrets en clair en base de donnees

5. **Deserialization insecurisee :**
   - Deserialization de donnees non fiables (Java, PHP, Python pickle)
   - Manipulation d'objets serialises pour executer du code

6. **Backdoors et code malveillant :**
   - Portes derobees dans le code source
   - Dependances compromises (supply chain attacks)
   - Code obfusque malveillant

7. **Problemes d'infrastructure :**
   - Mauvaise configuration des permissions de fichiers
   - Secrets dans les variables d'environnement
   - Segmentation reseau insuffisante

---

## Partie 3 - Gestion des Secrets

### 3.1 Pourquoi la detection de secrets est critique ?

La detection de secrets dans le code source est un enjeu de securite majeur pour plusieurs raisons :

1. **Prevention des fuites de credentials :**
   - Un secret commite dans Git est **permanent** dans l'historique, meme apres suppression
   - Les depots publics sont scannes en permanence par des bots malveillants
   - Un secret expose peut etre exploite en quelques minutes

2. **Protection contre les attaques de supply chain :**
   - Des credentials AWS/GCP/Azure exposes permettent de compromettre toute l'infrastructure cloud
   - Des tokens d'API permettent d'acceder aux services tiers (Stripe, Twilio, SendGrid)
   - Des cles SSH permettent de se connecter aux serveurs de production

3. **Conformite reglementaire :**
   - Le RGPD impose la protection des donnees personnelles (et les credentials d'acces)
   - PCI-DSS interdit le stockage de secrets en clair
   - SOC 2 exige des controles d'acces aux secrets
   - Les audits de securite verifient systematiquement la gestion des secrets

4. **Impact financier :**
   - Cles AWS exposees : minage de cryptomonnaie a vos frais (factures de dizaines de milliers d'euros)
   - Tokens Stripe : fraude aux paiements
   - Credentials de base de donnees : vol de donnees clients -> amendes RGPD

### 3.2 Fichier de configuration vulnerable

Le fichier `config.conf` de cet atelier contient volontairement des secrets en clair pour demontrer la detection :

```
DB_PASSWORD=admin@123
AWS_ACCESS_KEY_ID=Biencache123
AWS_SECRET_ACCESS_KEY=azerty@123
JWT_SECRET=myjwtsecret
```

**Problemes identifies :**
- Mots de passe faibles et previsibles
- Cles AWS en clair dans un fichier de configuration
- Secret JWT faible et hardcode

### 3.3 TruffleHog - Analyse locale et pipeline

#### Analyse locale

```bash
# Installation
# Via Docker (recommande)
docker run -it -v "$PWD:/pwd" trufflesecurity/trufflehog:latest filesystem --directory=/pwd

# Ou via pip
pip install trufflehog

# Scan du repertoire courant
trufflehog filesystem --directory=. --json > trufflehog-report.json

# Scan de l'historique Git
trufflehog git file://. --json > trufflehog-git-report.json
```

#### Integration dans le pipeline GitLab

```yaml
secrets-trufflehog:
  stage: secrets
  image: trufflesecurity/trufflehog:latest
  script:
    - trufflehog filesystem --directory=. --json > trufflehog-report.json
  artifacts:
    paths:
      - trufflehog-report.json
    when: always
    expire_in: 1 week
```

#### Resultats attendus

TruffleHog detecte dans le fichier `config.conf` :
- **AWS Access Key** : pattern `AKIA...` reconnu comme potentielle cle AWS
- **Mots de passe** : patterns de credentials dans les fichiers de configuration
- **JWT Secret** : detection de secrets generiques

### 3.4 Bonnes pratiques de gestion des secrets

| Pratique | Description | Outils |
|----------|-------------|--------|
| **Vault / Gestionnaire de secrets** | Stocker les secrets dans un vault centralise | HashiCorp Vault, AWS Secrets Manager, Azure Key Vault |
| **Variables CI/CD protegees** | Utiliser les variables protegees de GitLab CI/CD | GitLab CI/CD Settings > Variables (masked + protected) |
| **Rotation reguliere** | Changer les secrets periodiquement | Vault auto-rotation, scripts de rotation |
| **Fichier .gitignore** | Exclure les fichiers de secrets du depot | `.env`, `*.key`, `*.pem`, `config.conf` |
| **Pre-commit hooks** | Bloquer les commits contenant des secrets | `pre-commit` + `detect-secrets`, `gitleaks` |
| **Secret scanning** | Scanner les depots pour detecter les fuites | TruffleHog, GitLeaks, GitLab Secret Detection |
| **Principe du moindre privilege** | Chaque service n'a acces qu'aux secrets necessaires | IAM roles, service accounts |
| **Chiffrement au repos** | Les secrets sont chiffres en base de donnees | KMS, envelope encryption |

#### Exemple de .gitignore pour les secrets

```gitignore
# Fichiers de secrets
.env
.env.*
*.key
*.pem
*.p12
config.conf
secrets/
credentials.json

# IDE et systeme
.idea/
.vscode/
*.swp
.DS_Store
```

#### Exemple de pre-commit hook avec detect-secrets

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

---

## Partie 4 - Patch Management des Dependances

> Le document complet de l'etude de Patch Management est disponible dans le fichier `patch-management.md`.

### 4.1 Resume

Le patch management des dependances est essentiel pour :
- Corriger les vulnerabilites connues (CVE)
- Maintenir la compatibilite des librairies
- Respecter les exigences de conformite

### 4.2 Recommandation

Apres analyse comparative des outils du marche, la recommandation est :

1. **Renovate** pour la gestion automatisee des mises a jour (gratuit, natif GitLab, auto-MR)
2. **Trivy** pour les scans de vulnerabilites dans le pipeline CI/CD (gratuit, multi-scanner)

### 4.3 Architecture recommandee

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

## Resume du pipeline CI/CD

Le fichier `.gitlab-ci.yml` de cet atelier definit un pipeline complet en 4 stages :

```
build --> sast --> sca --> dast --> secrets
```

| Stage | Job | Outil | Description |
|-------|-----|-------|-------------|
| build | build-juice-shop | Docker | Pull de l'image Juice Shop |
| sast | sast-bandit | Bandit | Analyse statique du code Python |
| sca | *(extensible)* | Safety/Trivy | Analyse des dependances |
| dast | dast-zap-juice-shop | OWASP ZAP | Scan dynamique de Juice Shop |
| secrets | secrets-trufflehog | TruffleHog | Detection de secrets |

### Artefacts generes

- `bandit-report.json` / `bandit-report.html` : rapport SAST
- `zap-report.json` / `zap-report.html` : rapport DAST
- `trufflehog-report.json` : rapport de detection de secrets

---

## Conclusion

L'integration de SAST, DAST, detection de secrets et patch management dans un pipeline CI/CD permet de :

1. **Detecter les vulnerabilites tot** dans le cycle de developpement (shift-left)
2. **Automatiser** les verifications de securite a chaque commit
3. **Couvrir differents angles** d'attaque grace a la complementarite des outils
4. **Maintenir les dependances a jour** pour reduire la surface d'attaque
5. **Tracer** toutes les analyses via les artefacts et rapports

La combinaison SAST + DAST + Secrets + SCA offre une couverture de securite robuste, mais ne remplace pas les audits manuels et les tests de penetration pour les vulnerabilites de logique metier.
