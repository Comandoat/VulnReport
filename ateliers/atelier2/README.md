# Atelier 2 - Pipeline CI/CD et Analyse SCA

## Table des matieres

1. [Partie 1 - Pipeline CI/CD GitLab](#partie-1---pipeline-cicd-gitlab)
2. [Questions theoriques](#questions-theoriques)
3. [Partie 2 - Analyse SCA](#partie-2---analyse-sca)

---

## Partie 1 - Pipeline CI/CD GitLab

### Exercice 1 - Pipeline avec 4 stages

**Objectif** : Creer un pipeline GitLab CI/CD compose de 4 etapes distinctes : `build`, `test`, `integration` et `deploy`.

**Explication** :

Le fichier `.gitlab-ci.yml` definit la structure du pipeline. Chaque stage represente une phase logique du cycle de vie du logiciel :

- **build** : Compilation du projet, installation des dependances.
- **test** : Execution des tests unitaires et des analyses statiques.
- **integration** : Tests d'integration entre les differents composants.
- **deploy** : Deploiement de l'application sur l'environnement cible.

Les stages s'executent sequentiellement dans l'ordre defini. Si un job echoue dans un stage, les stages suivants ne sont pas executes (sauf configuration contraire).

```yaml
stages:
  - build
  - test
  - integration
  - deploy
```

Chaque job est associe a un stage via le mot-cle `stage:`. Tous les jobs d'un meme stage s'executent en parallele, et le pipeline passe au stage suivant uniquement lorsque tous les jobs du stage courant ont reussi.

---

### Exercice 2 - Job d'integration avec artefact

**Objectif** : Creer un job dans le stage `integration` qui genere un fichier `output.txt` en tant qu'artefact.

**Explication** :

Les artefacts GitLab CI permettent de conserver des fichiers generes pendant l'execution d'un job. Ces fichiers sont stockes par GitLab et peuvent etre telecharges depuis l'interface web ou transmis aux jobs suivants.

```yaml
integration-job:
  stage: integration
  image: alpine:latest
  script:
    - echo "This is an output" > output.txt
    - echo "Integration testing..."
  artifacts:
    paths:
      - output.txt
    expire_in: 1 week
```

Le fichier `output.txt` est cree dans le script du job, puis declare comme artefact via `artifacts.paths`. Le parametre `expire_in` definit la duree de conservation de l'artefact sur le serveur GitLab (ici 1 semaine).

---

### Exercice 3 - Forcer une erreur et conserver l'artefact

**Objectif** : Introduire volontairement une erreur dans le job d'integration (`exit 1`) tout en s'assurant que l'artefact est quand meme genere et conserve.

**Explication** :

Par defaut, les artefacts ne sont sauvegardes que si le job reussit. Pour conserver les artefacts meme en cas d'echec, on utilise le parametre `artifacts:when: always`.

```yaml
integration-job:
  stage: integration
  image: alpine:latest
  script:
    - echo "This is an output" > output.txt
    - echo "Integration testing..."
    - exit 1  # Erreur forcee
  artifacts:
    paths:
      - output.txt
    when: always        # Sauvegarde l'artefact meme en cas d'echec
    expire_in: 1 week
```

Les trois valeurs possibles pour `artifacts:when` sont :

| Valeur        | Comportement                                          |
|---------------|-------------------------------------------------------|
| `on_success`  | (defaut) Artefact sauvegarde uniquement si le job reussit |
| `on_failure`  | Artefact sauvegarde uniquement si le job echoue       |
| `always`      | Artefact sauvegarde dans tous les cas                 |

Cela est particulierement utile pour conserver des rapports de tests ou des logs de diagnostic meme lorsque le job echoue, afin de faciliter le debogage.

---

### Exercice 4 - allow_failure sur le job d'integration

**Objectif** : Permettre au pipeline de continuer meme si le job d'integration echoue, en utilisant `allow_failure: true`.

**Explication** :

Le mot-cle `allow_failure: true` indique a GitLab que l'echec de ce job ne doit pas bloquer l'execution du pipeline. Le job sera marque avec un avertissement orange (au lieu du rouge d'echec), et les stages suivants continueront a s'executer.

```yaml
integration-job:
  stage: integration
  image: alpine:latest
  script:
    - echo "This is an output" > output.txt
    - echo "Integration testing..."
    - exit 1
  artifacts:
    paths:
      - output.txt
    when: always
    expire_in: 1 week
  allow_failure: true   # Le pipeline continue malgre l'echec
```

**Comportement observe** :

- Le job `integration-job` echoue (a cause de `exit 1`).
- L'artefact `output.txt` est quand meme sauvegarde (grace a `when: always`).
- Le pipeline continue vers le stage `deploy` (grace a `allow_failure: true`).
- Le job affiche une icone d'avertissement orange dans l'interface GitLab.
- Le pipeline global est marque comme "passed with warnings" au lieu de "failed".

---

### Exercice 5 - Job de deploiement manuel

**Objectif** : Configurer le job de deploiement pour qu'il necessite un declenchement manuel.

**Explication** :

Le mot-cle `when: manual` empeche l'execution automatique du job. Un bouton "Play" apparait dans l'interface GitLab, permettant a un utilisateur autorise de declencher le deploiement manuellement.

```yaml
deploy-job:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying to production..."
  when: manual
```

Cette approche est recommandee pour les deploiements en production car elle ajoute une validation humaine avant toute mise en production. C'est une bonne pratique de securite et de gouvernance.

**Remarque** : Un job manuel ne bloque pas le pipeline. Le pipeline est considere comme reussi meme si le job manuel n'a pas ete declenche.

---

### Exercice 6 - Detection de secrets avec TruffleHog

**Objectif** : Integrer TruffleHog dans le pipeline pour detecter les secrets commites accidentellement dans le code source.

**Explication** :

TruffleHog est un outil open source qui scanne les repositories Git a la recherche de secrets (cles API, mots de passe, tokens, etc.) en utilisant des expressions regulieres et l'entropie de Shannon.

#### Configuration du job dans le pipeline

```yaml
git-secrets:
  stage: test
  image: trufflesecurity/trufflehog:latest
  script:
    - trufflehog filesystem --directory=. --json > trufflehog-report.json
  artifacts:
    paths:
      - trufflehog-report.json
    when: always
    expire_in: 1 week
  allow_failure: true
```

#### Fichier de test (config.conf)

Pour tester la detection, on cree un fichier `config.conf` contenant des secrets volontairement exposes :

```
DB_PASSWORD=admin@123
AWS_ACCESS_KEY_ID=Biencache123
AWS_SECRET_ACCESS_KEY=azerty@123
JWT_SECRET=myjwtsecret
```

#### Resultats attendus

TruffleHog analyse le systeme de fichiers et produit un rapport JSON listant les secrets detectes. Pour chaque secret trouve, le rapport inclut :

- Le type de secret (cle AWS, mot de passe, token JWT, etc.)
- Le fichier source et la ligne concernee
- Le niveau de confiance de la detection (entropie)

#### Reponses aux questions de l'exercice 6

**Q : Pourquoi est-il dangereux de commiter des secrets dans un depot Git ?**

R : Les depots Git conservent l'historique complet de tous les fichiers. Meme si un secret est supprime dans un commit ulterieur, il reste accessible dans l'historique. Si le depot est public (ou le devient un jour), ces secrets sont exposes a tous. Un attaquant peut les utiliser pour acceder a des bases de donnees, des services cloud, ou d'autres ressources sensibles. De plus, les bots automatises scannent en permanence les depots publics a la recherche de secrets.

**Q : Comment remedier a un secret expose dans l'historique Git ?**

R : Il faut :
1. **Revoquer immediatement** le secret compromis (changer le mot de passe, regenerer la cle API).
2. **Supprimer le secret de l'historique Git** en utilisant des outils comme `git filter-branch` ou `BFG Repo-Cleaner`.
3. **Forcer le push** du depot nettoye (`git push --force`).
4. **Mettre en place des mesures preventives** : utiliser des fichiers `.gitignore`, des variables d'environnement, des gestionnaires de secrets (Vault, AWS Secrets Manager), et des hooks pre-commit.

**Q : Quelle est la difference entre detection par regex et detection par entropie ?**

R : La detection par **regex** (expressions regulieres) recherche des motifs connus correspondant a des formats de secrets specifiques (ex. `AKIA[0-9A-Z]{16}` pour les cles AWS). Elle est precise mais limitee aux formats connus. La detection par **entropie** mesure le desordre d'une chaine de caracteres : une chaine a haute entropie (comme un mot de passe ou une cle aleatoire) est potentiellement un secret. Cette methode est plus generique mais produit davantage de faux positifs.

---

### Exercice 7 - Variables conditionnelles et regles de deploiement

**Objectif** : Utiliser des variables d'environnement et des regles conditionnelles pour controler le deploiement.

**Explication** :

On definit une variable `ENVIRONMENT` avec la valeur par defaut `dev`. Le job de deploiement est configure pour ne s'executer que sur la branche `main` et uniquement lorsque `ENVIRONMENT` est egal a `prod`.

```yaml
variables:
  ENVIRONMENT: dev

deploy-job:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying to production..."
  rules:
    - if: '$CI_COMMIT_BRANCH == "main" && $ENVIRONMENT == "prod"'
      when: manual
```

#### Fonctionnement des regles

- `rules:if` evalue une expression booleenne basee sur des variables CI/CD.
- `$CI_COMMIT_BRANCH` est une variable predefinee GitLab contenant le nom de la branche du commit.
- `$ENVIRONMENT` est notre variable personnalisee.
- Le job ne sera visible et declenchable que si les deux conditions sont remplies simultanement.

#### Cas d'utilisation

| Branche | ENVIRONMENT | Deploiement disponible ? |
|---------|-------------|--------------------------|
| main    | prod        | Oui (manuel)             |
| main    | dev         | Non                      |
| develop | prod        | Non                      |
| develop | dev         | Non                      |

Pour declencher un deploiement en production, il faut modifier la variable `ENVIRONMENT` a `prod` dans les parametres CI/CD du projet GitLab (Settings > CI/CD > Variables) ou lors du declenchement manuel du pipeline.

---

## Questions theoriques

### 1. Qu'est-ce qu'un artefact dans un pipeline GitLab et quel est son role ?

Un **artefact** dans un pipeline GitLab CI/CD est un fichier ou un ensemble de fichiers generes par un job pendant son execution et conserves par GitLab apres la fin du job. Les artefacts remplissent plusieurs roles essentiels :

- **Conservation des resultats** : Ils permettent de sauvegarder les fichiers produits par un job (binaires compiles, rapports de tests, fichiers de couverture de code, logs, etc.) pour qu'ils puissent etre telecharges ou consultes ulterieurement.
- **Transmission inter-jobs** : Les artefacts peuvent etre transmis d'un job a un autre au sein du meme pipeline. Par exemple, un job de build peut produire un binaire compile qui sera utilise par un job de test ou de deploiement dans un stage ulterieur.
- **Tracabilite** : Ils fournissent une trace tangible de ce qui a ete produit par chaque execution du pipeline, ce qui est essentiel pour l'audit et le debogage.
- **Telechargement** : Les artefacts sont accessibles depuis l'interface web de GitLab et peuvent etre telecharges par les membres de l'equipe.

Les artefacts sont configures dans le fichier `.gitlab-ci.yml` via le mot-cle `artifacts` et peuvent avoir une duree de vie limitee grace a `expire_in`.

---

### 2. Que signifie allow_failure et dans quels cas est-ce utile ?

Le mot-cle `allow_failure: true` dans un job GitLab CI/CD indique que l'echec de ce job ne doit pas etre considere comme un echec du pipeline global. Concretement :

- Le job peut echouer sans bloquer les stages suivants.
- Le pipeline continue son execution normalement.
- Le job est marque avec un avertissement (icone orange) au lieu d'une erreur (icone rouge).
- Le pipeline global est marque comme "passed with warnings" au lieu de "failed".

**Cas d'utilisation courants** :

- **Outils d'analyse non bloquants** : Les scanners de securite (SAST, SCA, detection de secrets) peuvent trouver des vulnerabilites sans que cela ne doive bloquer le deploiement dans certains contextes (ex. environnement de developpement).
- **Tests instables (flaky tests)** : Certains tests peuvent echouer de maniere intermittente pour des raisons non liees au code (timeouts reseau, ressources indisponibles). On peut tolerer leur echec temporairement.
- **Jobs experimentaux** : Lors de l'introduction d'une nouvelle verification dans le pipeline, on peut vouloir l'observer sans impacter le flux de travail existant.
- **Jobs informatifs** : Certains jobs servent uniquement a fournir des metriques ou des rapports sans que leur echec ne soit critique.

---

### 3. Quelle est la difference entre un job en echec et un job en echec autorise (allow_failure) ?

| Aspect                          | Job en echec (failed)                    | Job en echec autorise (allow_failure)        |
|---------------------------------|------------------------------------------|----------------------------------------------|
| **Icone dans l'interface**      | Rouge (croix)                            | Orange (point d'exclamation)                 |
| **Impact sur le pipeline**      | Le pipeline est marque comme "failed"    | Le pipeline est marque comme "passed with warnings" |
| **Stages suivants**             | Les stages suivants ne s'executent PAS   | Les stages suivants s'executent normalement  |
| **Notification**                | Notification d'echec envoyee             | Pas de notification d'echec critique         |
| **Merge Request**               | Bloque le merge si "pipeline must succeed" est active | Ne bloque PAS le merge                      |
| **Artefacts (par defaut)**      | Non sauvegardes (sauf si `when: always`) | Non sauvegardes (sauf si `when: always`)     |

En resume, un job en echec est considere comme un probleme critique qui interrompt le pipeline, tandis qu'un job en echec autorise est un avertissement qui n'empeche pas la poursuite du processus.

---

### 4. Que se passe-t-il si le stage build echoue ?

Si un job dans le stage `build` echoue, les consequences sont les suivantes :

1. **Arret immediat du pipeline** : Les stages suivants (`test`, `integration`, `deploy`) ne seront **pas executes**. GitLab respecte l'ordre sequentiel des stages : si un stage echoue, tout ce qui suit est annule.

2. **Tous les jobs du stage build en parallele** : Si plusieurs jobs sont definis dans le stage `build`, ils s'executent en parallele. Si l'un d'entre eux echoue, les autres jobs du meme stage continuent leur execution (ils sont deja lances), mais le passage au stage suivant sera bloque.

3. **Pipeline marque comme "failed"** : Le pipeline global est marque en rouge comme ayant echoue.

4. **Notification d'echec** : Les membres du projet recoivent une notification d'echec (selon la configuration des notifications).

5. **Merge Request bloquee** : Si le projet a configure "Pipelines must succeed" dans les parametres de Merge Request, la MR ne pourra pas etre fusionnee.

**Exception** : Si le job de build qui echoue est configure avec `allow_failure: true`, le pipeline continuera normalement. Cependant, cette configuration n'est generalement pas recommandee pour le stage de build, car si la compilation echoue, les etapes suivantes n'ont pas de sens.

---

### 5. Pourquoi structurer un pipeline en plusieurs stages ?

La structuration d'un pipeline en plusieurs stages presente de nombreux avantages :

1. **Separation des responsabilites** : Chaque stage a un objectif clair et distinct (compiler, tester, deployer). Cela rend le pipeline plus lisible et maintenable.

2. **Fail-fast (echec rapide)** : Si la compilation echoue, il est inutile de lancer les tests ou le deploiement. Les stages sequentiels permettent de detecter les problemes au plus tot, economisant du temps et des ressources.

3. **Parallelisation** : Au sein d'un meme stage, tous les jobs s'executent en parallele. On peut ainsi lancer simultanement les tests unitaires, les tests de securite et l'analyse de qualite dans le stage `test`.

4. **Visibilite et debogage** : L'interface GitLab affiche clairement chaque stage et l'etat de ses jobs. En cas de probleme, on identifie immediatement a quelle etape l'erreur s'est produite.

5. **Controle du flux** : Les stages permettent de definir des points de controle (gates) dans le pipeline. Par exemple, le deploiement en production peut necessiter une validation manuelle (`when: manual`).

6. **Reutilisation des artefacts** : Les fichiers produits par un stage peuvent etre transmis aux stages suivants, creant une chaine de traitement coherente.

7. **Conformite et audit** : Une structure claire en stages documente le processus de livraison et facilite les audits de conformite (SOC 2, ISO 27001, etc.).

---

## Partie 2 - Analyse SCA (Software Composition Analysis)

L'analyse SCA (Software Composition Analysis) consiste a identifier les vulnerabilites connues dans les dependances tierces d'un projet. C'est un element essentiel de la securite de la chaine d'approvisionnement logicielle (supply chain security).

### Defi 1 - OWASP Dependency-Check

#### Presentation

OWASP Dependency-Check est un outil open source de la fondation OWASP qui identifie les vulnerabilites connues (CVE) dans les dependances d'un projet. Il fonctionne en analysant les fichiers de dependances (package.json, pom.xml, requirements.txt, etc.) et en les comparant avec la base de donnees NVD (National Vulnerability Database) du NIST.

#### Execution locale avec Docker

Pour lancer OWASP Dependency-Check localement a l'aide de Docker, on execute la commande suivante :

```bash
docker run --rm \
  -v $(pwd):/src \
  -v $(pwd)/dependency-check-report:/report \
  owasp/dependency-check:latest \
  --project "test-vuln" \
  --scan /src \
  --format HTML \
  --format JSON \
  --out /report
```

**Explication des parametres** :
- `--rm` : Supprime le conteneur apres l'execution.
- `-v $(pwd):/src` : Monte le repertoire courant comme source a analyser.
- `-v $(pwd)/dependency-check-report:/report` : Monte un repertoire local pour recevoir les rapports.
- `--project "test-vuln"` : Nom du projet pour le rapport.
- `--scan /src` : Repertoire a scanner.
- `--format HTML --format JSON` : Genere les rapports aux formats HTML et JSON.
- `--out /report` : Repertoire de sortie des rapports.

#### Analyse des resultats

Avec le fichier `package.json` de test contenant des dependances volontairement vulnerables (`lodash@3.0.0`, `jquery@3.2.1`, `minimist@0.0.8`), OWASP Dependency-Check detecte plusieurs vulnerabilites :

**lodash 3.0.0** :
- CVE-2018-3721 : Prototype Pollution (severite HAUTE)
- CVE-2018-16487 : Prototype Pollution (severite HAUTE)
- CVE-2019-1010266 : Consommation excessive de memoire via RegEx (severite MOYENNE)
- CVE-2019-10744 : Prototype Pollution via `defaultsDeep` (severite CRITIQUE)
- CVE-2020-8203 : Prototype Pollution via `zipObjectDeep` (severite HAUTE)
- CVE-2020-28500 : ReDoS (Regular Expression Denial of Service) (severite MOYENNE)
- CVE-2021-23337 : Injection de commandes via `template` (severite HAUTE)

**jquery 3.2.1** :
- CVE-2019-11358 : Prototype Pollution via `jQuery.extend` (severite MOYENNE)
- CVE-2020-11022 : Cross-Site Scripting (XSS) via `jQuery.html()` (severite MOYENNE)
- CVE-2020-11023 : Cross-Site Scripting (XSS) via `jQuery.htmlPrefilter()` (severite MOYENNE)

**minimist 0.0.8** :
- CVE-2020-7598 : Prototype Pollution (severite MOYENNE)
- CVE-2021-44906 : Prototype Pollution (severite CRITIQUE)

#### Integration dans le pipeline GitLab CI/CD

```yaml
oast-dependency-check:
  stage: test
  image: owasp/dependency-check:latest
  script:
    - /usr/share/dependency-check/bin/dependency-check.sh --project "test-vuln" --scan . --format HTML --format JSON --out dependency-check-report
  artifacts:
    paths:
      - dependency-check-report/
    when: always
    expire_in: 1 week
  allow_failure: true
```

Le job est place dans le stage `test` et configure avec `allow_failure: true` pour ne pas bloquer le pipeline (utile en phase d'adoption). Les rapports sont conserves en tant qu'artefacts pour consultation ulterieure.

---

### Defi 2 - Snyk

#### Presentation

Snyk est un outil commercial (avec un tier gratuit) de securite des applications qui se specialise dans la detection de vulnerabilites dans les dependances open source. Contrairement a OWASP Dependency-Check qui s'appuie uniquement sur la base NVD, Snyk maintient sa propre base de donnees de vulnerabilites, souvent plus a jour et enrichie par sa communaute de chercheurs en securite.

#### Installation et authentification

**Installation locale** :
```bash
# Via npm
npm install -g snyk

# Via l'executable direct (Linux)
wget -O /usr/local/bin/snyk https://static.snyk.io/cli/latest/snyk-linux
chmod +x /usr/local/bin/snyk
```

**Authentification** :
```bash
# Authentification interactive (ouvre le navigateur)
snyk auth

# Authentification par token (pour CI/CD)
snyk auth $SNYK_TOKEN
```

Pour obtenir un token, il faut creer un compte sur [snyk.io](https://snyk.io) et recuperer le token API dans les parametres du compte (Account Settings > API Token).

#### Execution de snyk test

```bash
# Installation des dependances
npm install

# Analyse des vulnerabilites
snyk test
```

**Resultats attendus avec notre package.json de test** :

Snyk detecte les memes categories de vulnerabilites que OWASP Dependency-Check, mais avec des informations supplementaires :

- **Chemin de dependance** : Snyk montre la chaine complete de dependances qui introduit la vulnerabilite (utile pour les dependances transitives).
- **Correctif disponible** : Snyk indique si une version corrigee existe et laquelle.
- **Score de priorite Snyk** : En plus du score CVSS, Snyk calcule un score de priorite base sur l'exploitabilite reelle de la vulnerabilite.
- **Recommandations de remediation** : Snyk propose des commandes pour corriger les vulnerabilites (`snyk fix` ou upgrade vers une version specifique).

Exemple de sortie :
```
Testing /path/to/project...

Tested 3 dependencies for known issues, found 12 issues.

Issues found:
  ✗ Prototype Pollution [Critical Severity][https://snyk.io/vuln/SNYK-JS-LODASH-567746]
    in lodash@3.0.0
    Remediation: Upgrade to lodash@4.17.21

  ✗ Cross-site Scripting (XSS) [Medium Severity][https://snyk.io/vuln/SNYK-JS-JQUERY-565129]
    in jquery@3.2.1
    Remediation: Upgrade to jquery@3.5.0

  ✗ Prototype Pollution [Critical Severity][https://snyk.io/vuln/SNYK-JS-MINIMIST-559764]
    in minimist@0.0.8
    Remediation: Upgrade to minimist@1.2.6
```

#### Comparaison entre OWASP Dependency-Check et Snyk

| Critere                    | OWASP Dependency-Check              | Snyk                                     |
|----------------------------|--------------------------------------|------------------------------------------|
| **Type**                   | Open source (gratuit)                | Freemium (gratuit avec limites)          |
| **Base de vulnerabilites** | NVD (NIST)                           | Base Snyk proprietaire + NVD             |
| **Mise a jour**            | Necessite la MAJ locale de la BDD NVD | Mise a jour continue cote serveur       |
| **Faux positifs**          | Relativement eleves                  | Moins eleves (curation humaine)          |
| **Langages supportes**     | Java, .NET, Python, Node.js, Ruby, etc. | Node.js, Python, Java, Go, Ruby, PHP, etc. |
| **Remediation**            | Liste les CVE seulement              | Propose des correctifs automatiques      |
| **Integration CI/CD**      | Via Docker ou CLI                    | CLI native + integrations Git            |
| **Dependances transitives**| Detection limitee                    | Detection complete avec arbre de dependances |
| **Vitesse**                | Lent (telechargement BDD NVD)        | Rapide (API cloud)                       |
| **Hors-ligne**             | Oui (apres telechargement BDD)       | Non (necessite une connexion internet)   |

**Conclusion** : Les deux outils sont complementaires. OWASP Dependency-Check est ideal pour un usage entierement gratuit et hors-ligne, tandis que Snyk offre une experience plus riche avec des recommandations de remediation et une base de vulnerabilites plus reactive. En production, il est recommande d'utiliser les deux pour maximiser la couverture de detection.

#### Integration dans le pipeline GitLab CI/CD

```yaml
oast-snyk:
  stage: build
  image: node:18-alpine
  before_script:
    - wget -O /usr/local/bin/snyk https://static.snyk.io/cli/latest/snyk-linux
    - chmod +x /usr/local/bin/snyk
  script:
    - npm install
    - snyk auth $SNYK_TOKEN
    - snyk test --json > snyk-results.json
    - cat snyk-results.json
  artifacts:
    paths:
      - snyk-results.json
    when: always
    expire_in: 1 week
  allow_failure: true
```

**Points importants** :
- La variable `$SNYK_TOKEN` doit etre configuree dans les variables CI/CD du projet GitLab (Settings > CI/CD > Variables) et marquee comme "Masked" pour ne pas apparaitre dans les logs.
- Le job est configure avec `allow_failure: true` pour ne pas bloquer le pipeline si des vulnerabilites sont detectees.
- Le rapport JSON est sauvegarde comme artefact pour consultation ulterieure et peut etre integre a des dashboards de securite.

---

## Fichiers de l'atelier

| Fichier              | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `.gitlab-ci.yml`     | Pipeline CI/CD complet avec tous les exercices (1 a 7) + SCA    |
| `config.conf`        | Fichier de configuration avec secrets volontairement exposes     |
| `package.json`       | Fichier de dependances Node.js avec des versions vulnerables     |
| `README.md`          | Ce document : reponses completes et documentation de l'atelier   |

---

## Synthese

Cet atelier a permis d'explorer les concepts fondamentaux des pipelines CI/CD avec GitLab et l'analyse de la composition logicielle (SCA) :

1. **Pipeline CI/CD** : Structuration en stages, gestion des artefacts, tolerances aux echecs, deploiement manuel et regles conditionnelles.
2. **Detection de secrets** : Utilisation de TruffleHog pour identifier les informations sensibles commitees dans le code source.
3. **Analyse SCA** : Comparaison de deux outils majeurs (OWASP Dependency-Check et Snyk) pour la detection de vulnerabilites dans les dependances tierces.

La combinaison de ces pratiques dans un pipeline CI/CD automatise constitue une base solide pour la securite du cycle de developpement logiciel (DevSecOps).
