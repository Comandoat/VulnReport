

**VULNREPORT**

Assistant de génération de rapports de Pentest

& Base de Connaissance Offensive

**ATELIER 1 — PRÉSENTATION DU PROJET**

Plan de Développement · DAT · Analyse des Risques

| Projet | VulnReport – UE7 DevSecOps |
| :---- | :---- |
| **Classe** | B2 / GCS2 – Guardia Cybersecurity School |
| **Période** | 23 mars → 10 avril 2026 |
| **Équipe** | Noa B. · Diego D. · Raphaël L. · Antoine C. |

# **1\. PLAN DE DÉVELOPPEMENT DU PROJET**

## **1.1 Vision du Projet**

VulnReport est une application web sécurisée dont l'objectif est d'accélérer, de standardiser et de fiabiliser la rédaction de rapports de tests d'intrusion (pentest). Elle s'adresse aux pentesters qui souhaitent produire des rapports professionnels à partir d'une base de connaissance (KB) centralisée, tout en permettant la saisie de findings personnalisés.

La plateforme repose sur deux piliers fonctionnels complémentaires :

* Génération de rapports : création, édition et publication de rapports de pentest avec gestion des findings (depuis la KB ou en mode custom), scoring, preuves (PoC) et export.

* Base de Connaissance offensive (KB) : fiches pédagogiques sur les vulnérabilités (OWASP Top 10, CWE), recommandations types, liens vers des ressources pratiques.

L'application intègre un RBAC strict (Viewer / Pentester / Admin), un audit log, une démarche DevSecOps complète (CI/CD GitLab avec SAST et SCA) et une conteneurisation Docker garantissant une exécution reproductible.

## **1.2 Organisation et Responsabilités**

L'équipe est composée de quatre membres aux rôles complémentaires :

| Membre | Rôle | Responsabilités principales |
| :---- | :---- | :---- |
| **Noa B.** | Chef de Projet | Coordination équipe, gestion du board GitLab (issues, sprints), suivi des jalons, rédaction des livrables documentaires, point de contact pédagogique. |
| **Diego D.** | Responsable Frontend | Interfaces utilisateur (templates), intégration backend, UX des workflows Pentester / Admin / Viewer, validation côté client. |
| **Raphaël L.** | Responsable Backend | Logique serveur, authentification, sessions, RBAC, modules Rapports / KB / Audit log, conception et migrations de la base de données. |
| **Antoine C.** | Responsable Sécurité / DevOps | Pipeline CI/CD GitLab, Docker, intégration SAST/SCA, headers de sécurité HTTP, CSP, protection anti-XSS/SQLi, rapport de sécurité final. |

Note : chaque membre contribue au code au-delà de son domaine principal. La spécialisation définit la responsabilité de chaque périmètre, pas une frontière rigide.

## **1.3 Organisation du Travail**

**Méthode de travail**

Le projet suit une organisation agile légère en trois sprints, avec des points de synchronisation quotidiens ("daily express") de 10 minutes maximum sur Discord. Des réunions plus longues sont organisées lors des créneaux communs en présentiel.

**Conventions Git**

Chaque tâche suit la règle : une issue GitLab \= une branche \= une Merge Request (MR).

Les préfixes de branches retenus sont les suivants :

| Préfixe | Usage | Exemple |
| :---- | :---- | :---- |
| **feature/** | Nouvelle fonctionnalité métier | feature/4-creation-rapport |
| **fix/** | Correction d'un bug fonctionnel | fix/15-erreur-affichage-dashboard |
| **sec/** | Mesure Security by Design ou correction de vulnérabilité | sec/8-ajout-headers-http |
| **ops/ / ci/** | Infrastructure Docker, pipeline CI/CD | ops/2-creation-dockerfile |
| **docs/** | README, rapport de sécurité, fiches KB | docs/25-redaction-rapport-architecture |
| **refactor/** | Refactoring sans changement de comportement | refactor/11-nettoyage-auth |

## **1.4 Besoins en Ressources**

| Catégorie | Détail |
| :---- | :---- |
| **Environnement de dev** | Développement en local (Windows) \+ runners GitLab CI/CD (cloud GitLab.com) pour l'automatisation du pipeline. |
| **Contrôle de version** | GitLab.com — dépôt privé du groupe, CI/CD intégré, board Kanban (GitLab Issues). |
| **Conteneurisation** | Docker Desktop (Windows) — Dockerfile \+ docker-compose pour l'application et la base de données. |
| **Communication** | Discord — daily express asynchrone (10 min/jour) et points synchrones lors des créneaux communs. |
| **Outils de sécurité** | À préciser lors du DAT : Bandit/Semgrep (SAST), Safety/Trivy (SCA), outil DAST à définir (Sprint 3). |
| **Éditeur de code** | VS Code avec extensions Python, Docker, GitLab (selon préférence de chaque membre). |

## **1.5 Planning et Jalons de Livraison**

Le projet se déroule du 23 mars au 10 avril 2026 (18 jours calendaires) et est organisé en trois sprints d'une semaine, suivis d'une phase de finalisation.

| Sprint | Période | Objectifs et tâches |
| :---- | :---- | :---- |
| **Sprint 1Fondations** | 23/03 → 29/03 | Initialisation du dépôt GitLab (structure, branches, board). Création du Dockerfile de base et de la structure de la base de données. Implémentation de l'authentification sécurisée (cookies HttpOnly, Secure, SameSite, headers HTTP). RBAC strict (Viewer, Pentester, Admin). Fondations Security by Design. |
| **Sprint 2Cœur Fonctionnel** | 30/03 → 05/04 | Module Base de Connaissance (KB) — CRUD Admin. Module Rapports — création, ajout de findings (depuis KB ou custom), statuts. Audit log (traçabilité des actions sensibles). Validation rigoureuse des entrées (anti-SQLi, anti-XSS). Dashboard (compteurs). |
| **Sprint 3Pipeline & Finalisation** | 06/04 → 10/04 | Configuration du pipeline CI/CD GitLab. Intégration SAST, SCA, DAST — récupération des artefacts. Feature freeze le 08/04 : correction des vulnérabilités détectées. Rédaction README (variables d'env, comptes seed, commandes Docker) et Rapport de sécurité final. |

**Jalons de validation**

| Jalon | Date | Livrables attendus |
| ----- | :---- | :---- |
| **J1** | **Dimanche 29 mars** | Dépôt GitLab initialisé, Dockerfile fonctionnel, authentification \+ RBAC codés. |
| **J2** | **Dimanche 5 avril** | Modules Rapports, KB et Audit log fonctionnels. Protections SQLi/XSS actives. |
| **J3** | **Mercredi 8 avril** | Feature freeze. Pipeline CI/CD actif. Artefacts SAST/SCA/DAST générés. |
| **J4** | **Vendredi 10 avril** | README final, Rapport de sécurité complet, application dockerisée et testable. |

# **2\. DOCUMENT D'ARCHITECTURE LOGICIELLE (DAT)**

## **2.1 Schéma Général de l'Architecture**

VulnReport repose sur une architecture découplée en trois conteneurs Docker orchestrés par docker-compose : un conteneur frontend (React), un conteneur backend (Django \+ API REST) et un conteneur base de données (PostgreSQL). Cette séparation garantit l'isolement des composants, facilite le déploiement reproductible et s'inscrit dans une démarche DevSecOps.

| Composant | Technologie | Rôle |
| :---- | :---- | :---- |
| **Frontend** | React (SPA) | Interface utilisateur — workflows Pentester, Admin, Viewer. Appels REST vers le backend Django. |
| **Backend / API** | Django \+ DRF | Logique métier, API REST, authentification, sessions, RBAC, audit log, gestion des rapports et de la KB. |
| **Base de données** | PostgreSQL | Persistance des données : utilisateurs, rapports, findings, KB, audit log. |
| **Serveur web** | Nginx (optionnel) | Reverse proxy — sert les assets statiques React et redirige les appels /api/ vers Django. |
| **Conteneurisation** | Docker \+ docker-compose | Orchestration des trois conteneurs avec variables d'environnement, volumes et réseau isolé. |

**Justification des choix techniques :**

* Django : framework Python mature, batteries incluses (ORM, admin, système d'authentification natif, migrations). Idéal pour un projet avec RBAC et modèle relationnel complexe. La sécurité est intégrée par défaut (protection CSRF, échappement des templates, gestion des sessions).

* React : SPA moderne permettant une UX fluide pour les workflows Pentester/Admin. Le découplage frontend/backend via API REST facilite l'évolution indépendante des deux couches.

* PostgreSQL : SGBD robuste, conforme ACID, adapté à un modèle relationnel avec contraintes d'intégrité fortes (rapports, findings, rôles). Supérieur à SQLite pour une utilisation multi-utilisateurs.

* Architecture multi-conteneurs : isolement des responsabilités, secrets gérés par variables d'environnement, reproductibilité garantie entre environnements de développement et CI/CD.

## **2.2 Design de la Base de Données**

Le modèle relationnel de VulnReport s'articule autour de six entités principales. Les contraintes d'intégrité référentielle (clés étrangères, contraintes NOT NULL) sont gérées par l'ORM Django et appliquées au niveau PostgreSQL.

| Table | Champs clés | Description |
| :---- | :---- | :---- |
| **User** | id, username, email, password\_hash, role, is\_active, created\_at | Compte utilisateur. Rôle (Viewer / Pentester / Admin) géré par RBAC. Mot de passe haché via Argon2id (django-argon2). |
| **Report** | id, title, context, executive\_summary, status, created\_at, updated\_at, owner\_id (FK User) | Rapport de pentest. Statuts : Brouillon, En cours, Finalisé, Publié. Lié à son propriétaire (Pentester). |
| **Finding** | id, title, description, proof, impact, recommendation, references, severity, cvss\_score, report\_id (FK Report), kb\_entry\_id (FK KBEntry nullable) | Vulnérabilité associée à un rapport. Peut être créée depuis la KB (pré-remplissage) ou manuellement (custom). |
| **KBEntry** | id, name, description, recommendation, references, severity\_default, category, created\_at, updated\_at | Fiche de la Base de Connaissance. Gérée par l'Admin. Catégories : Injection, Auth, XSS, CSRF, etc. |
| **Resource** | id, title, url, description, category | Liens et ressources pédagogiques (PortSwigger, OWASP, labs). Pages statiques gérées par l'Admin. |
| **AuditLog** | id, actor\_id (FK User), action, object\_type, object\_id, timestamp, metadata (JSON) | Journal d'audit. Trace les actions sensibles : login, CRUD rapports/findings/KB, changements de rôles. |

## **2.3 Authentification, Sessions et Contrôle d'Accès**

**Authentification**

L'authentification repose sur le système natif de Django (django.contrib.auth). Les mots de passe sont hachés avec Argon2id via le package django-argon2 (pip install django\[argon2\] \+ PASSWORD\_HASHERS dans settings.py). Argon2id est l'algorithme recommandé par l'OWASP (Password Storage Cheat Sheet) et le NIST pour sa résistance aux attaques GPU/ASIC grâce à sa consommation mémoire configurable, supérieure à PBKDF2 sur ce point. Aucun mot de passe n'est stocké en clair.

**Gestion des sessions**

Les sessions sont gérées côté serveur (base de données Django) avec les attributs de cookie suivants :

| Attribut cookie | Valeur | Justification |
| :---- | ----- | :---- |
| **HttpOnly** | True | Empêche l'accès au cookie via JavaScript — protection contre le vol de session par XSS. |
| **Secure** | True | Transmission du cookie uniquement en HTTPS — protection contre l'interception réseau. |
| **SameSite** | Strict | Bloque l'envoi du cookie dans les requêtes cross-site — protection CSRF renforcée. |
| **SESSION\_COOKIE\_AGE** | 3600 s | Expiration de session après 1 heure d'inactivité. |

**Contrôle d'accès — RBAC**

Trois rôles sont définis, avec des permissions strictement délimitées :

| Rôle | Permissions |
| ----- | :---- |
| **Viewer** | Lecture seule : consulte la KB et les rapports au statut Publié. Aucune création ni modification. |
| **Pentester** | Crée, édite et supprime ses propres rapports. Ajoute des findings (KB ou custom). Consulte la KB. Ne voit pas les rapports d'autrui (sauf Publié). |
| **Admin** | Accès complet : gestion des utilisateurs (rôles, activation), CRUD KB, lecture/suppression de tous les rapports, accès au dashboard et à l'audit log. |

## **2.4 Architecture DevSecOps — Pipeline CI/CD**

Le pipeline GitLab CI/CD est déclenché à chaque push sur toutes les branches. Il est structuré en quatre étapes successives, garantissant qu'aucun code non analysé ne peut être mergé sur la branche principale.

| Étape | Type | Outil(s) | Artefact produit |
| :---- | :---- | :---- | :---- |
| **1 — Lint** | Qualité de code | flake8 / ruff | Rapport de conformité PEP8 |
| **2 — SAST** | Analyse statique | Bandit \+ Semgrep | Rapports JSON des vulnérabilités détectées |
| **3 — SCA** | Analyse des dépendances | Safety \+ Trivy | Liste CVE sur les dépendances Python et l'image Docker |
| **4 — Build** | Conteneurisation | Docker build | Image Docker validée |
| **5 — DAST** | Test dynamique (Sprint 3\) | OWASP ZAP | Rapport HTML des vulnérabilités en boîte noire |

Tous les artefacts (rapports SAST, SCA, DAST) sont conservés dans GitLab CI/CD et accessibles après chaque exécution du pipeline. Le DAST (OWASP ZAP) est intégré en Sprint 3 uniquement, une fois l'application déployée dans un environnement de test.

# **3\. ANALYSE DES RISQUES SÉCURITÉ**

L'analyse des risques de VulnReport identifie les actifs critiques, les menaces associées et les mesures de mitigation retenues. Elle s'appuie sur le référentiel OWASP Top 10 et le triptyque CIA (Confidentialité / Intégrité / Disponibilité). La criticité est calculée par le produit Probabilité × Impact, chacun noté de 1 à 3\.

## **3.1 Identification des Actifs**

| Actif | Type | Description |
| :---- | :---- | :---- |
| **Comptes utilisateurs** | Données personnelles | Identifiants, mots de passe hachés, rôles RBAC. Cible principale pour l'usurpation d'identité. |
| **Rapports de pentest** | Données métier sensibles | Contenu hautement confidentiel (vulnérabilités client, PoC, recommandations). Atteinte grave si divulgués. |
| **Base de Connaissance (KB)** | Données opérationnelles | Fiches vulnérabilités gérées par l'Admin. Intégrité critique pour la qualité des rapports. |
| **Audit log** | Données de traçabilité | Historique des actions sensibles. Toute altération compromet la non-répudiation. |
| **Code source** | Actif technique | Dépôt GitLab. Une exposition du code faciliterait l'identification de vulnérabilités. |
| **Base de données PostgreSQL** | Actif technique | Contient l'ensemble des données applicatives. Cible principale pour l'exfiltration. |
| **Pipeline CI/CD** | Actif technique | Intégration SAST/SCA/DAST. Une compromission pourrait introduire du code malveillant. |

## **3.2 Matrice des Risques**

Échelle : Probabilité (P) et Impact (I) notés de 1 (faible) à 3 (élevé). Criticité \= P × I. Niveaux : 1-2 \= Faible, 3-4 \= Moyen, 6-9 \= Élevé.

| Risque / Menace | Actif(s) ciblé(s) | CIA | P | I | P×I | Mesures de mitigation |
| :---- | :---- | :---: | :---: | :---: | :---: | :---- |
| Injection SQL (A03 OWASP) | BDD PostgreSQL | **C, I** | 3 | 3 | **9** | Requêtes paramétrées via l'ORM Django, validation stricte des entrées, principe du moindre privilège sur le compte DB. |
| Cross-Site Scripting — XSS (A03) | Rapports, KB, findings | **C, I** | 3 | 2 | **6** | Échappement automatique Django/React, Content-Security-Policy (CSP), validation et sanitisation des champs libres. |
| Broken Access Control (A01) | Rapports, comptes, KB | **C, I** | 2 | 3 | **6** | RBAC strict, vérification de l'ownership côté serveur à chaque requête, tests automatisés des droits. |
| Vol de session / Cookie hijacking | Comptes utilisateurs | **C** | 2 | 3 | **6** | Cookies HttpOnly \+ Secure \+ SameSite=Strict, HTTPS obligatoire, expiration de session (1h). |
| Exposition de données sensibles (A02) | BDD, rapports | **C** | 2 | 3 | **6** | Argon2id pour les mots de passe, chiffrement des secrets via variables d'env, pas de données sensibles dans les logs. |
| CSRF (A01 adjacent) | Actions authentifiées | **I** | 2 | 2 | **4** | Token CSRF Django actif sur tous les formulaires, SameSite=Strict sur les cookies. |
| Mauvaise configuration sécurité (A05) | Infrastructure Docker | **C,I,D** | 2 | 2 | **4** | Headers HTTP sécurité (X-Frame-Options, HSTS, X-Content-Type), review pipeline, secrets hors du code source. |
| Compromission supply chain (A06) | Dépendances Python | **I, D** | 1 | 3 | **3** | SCA automatisé (Safety \+ Trivy) dans le pipeline CI/CD, versions épinglées dans requirements.txt. |
| Déni de service (DoS) | Application, BDD | **D** | 1 | 2 | **2** | Rate limiting Django, timeouts de session, architecture Docker isolée. |
| Altération de l'audit log | Audit log | **I** | 1 | 3 | **3** | Écriture append-only, accès réservé à l'Admin, intégrité vérifiée via SAST. |

## **3.3 Analyse CIA — Synthèse par Axe**

| Axe CIA | Risques principaux | Mesures clés |
| :---- | :---- | :---- |
| **Confidentialité** | Vol de session, exposition de données (rapports, mots de passe), SQLi, XSS. | Cookies sécurisés, Argon2id, RBAC strict, HTTPS, CSP, chiffrement des secrets. |
| **Intégrité** | Altération des rapports ou de la KB, CSRF, XSS stocké, compromission du pipeline. | Tokens CSRF, validation des entrées, ORM Django (requêtes paramétrées), audit log, SAST/SCA en CI/CD. |
| **Disponibilité** | Déni de service, compromission de l'infrastructure Docker. | Rate limiting, timeouts de session, architecture conteneurisée isolée, pipeline de build automatisé. |

Risques résiduels : malgré les mesures mises en place, un risque résiduel demeure principalement sur les axes Broken Access Control (complexité des règles d'ownership) et Supply Chain (dépendances tierces non auditées en profondeur). Ces risques seront réévalués après les résultats SAST/SCA/DAST du Sprint 3\.