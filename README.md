# CampusGive

> Plateforme de dons et d'échanges d'objets entre étudiants d'un même campus,
> sans transaction financière.

CampusGive permet aux étudiants de déposer une annonce en quelques secondes
pour transmettre un objet dont ils n'ont plus l'usage à un autre étudiant qui
en a besoin. L'objectif : réduire les achats inutiles, éviter le gaspillage,
et le tout dans un site **éco-conçu** (sobriété visuelle, technique et
fonctionnelle).

## Site déployé

**[greenit-project-1.onrender.com](https://greenit-project-1.onrender.com/)**

## Rapport et documentation

Le rapport PDF complet est disponible dans [`/docs/rapport.pdf`](docs/rapport.pdf).

Il contient : conception détaillée, diagrammes UML, captures Lighthouse / EcoIndex
avant et après optimisations, tableau comparatif d'empreinte carbone, scénarios
de tests fonctionnels, et discussion critique.

## Équipe

| Membre | Rôle principal |
|---|---|
| **Sam Dossu** | Design & fonctionnalités |
| **Hamza El Fferdi** | Panneau admin & base de données |
| **Eytan Guernigou** | Templates HTML/CSS |
| **Angel Hakomani** | Gestion des annonces & diagrammes PlantUML |
| **Frédéric Jalaguier** | Configuration GitHub & rédaction du rapport |

## Stack technique et justification Green IT

| Composant | Choix retenu | Justification Green IT |
|---|---|---|
| **Front-end** | HTML5 + CSS3 + Jinja2 (rendu côté serveur) | Aucun framework JS (pas de React, Vue…). Le navigateur ne reçoit que le HTML déjà rendu. Économie : **~150 Ko de JS évités** par rapport à un SPA équivalent. |
| **CSS** | Une seule feuille, **~10 Ko**, polices système | Aucun CDN externe (Google Fonts, Bootstrap). Une seule requête HTTP pour le style. Polices natives du système, 0 octet à télécharger. |
| **Back-end** | Python 3.11 + Flask 3.0 | Micro-framework léger, démarrage rapide, faible empreinte mémoire (~30 Mo). Pas de magie cachée comparé à Django. |
| **ORM** | Flask-SQLAlchemy | Requêtes paramétrées (anti-injection SQL) sans coût significatif. Permet le `SELECT` ciblé, la pagination native, les index. |
| **BDD (dev)** | SQLite | Pas de serveur séparé en dev, pas de processus supplémentaire en mémoire. Idéal pour itérer rapidement. |
| **BDD (prod)** | PostgreSQL | Performant, mature, inclus gratuitement chez Render. Migration depuis SQLite triviale grâce à SQLAlchemy. |
| **Sécurité** | bcrypt (cost 12), sessions Flask signées | Standard OWASP. Pas de bibliothèque exotique. |
| **Hébergement** | Render.com (plan gratuit) | Hébergeur référencé par The Green Web Foundation. Mise en veille automatique, 0 W consommé hors trafic. |
| **JavaScript** | **0 bibliothèque externe** | Le seul JS du site est `confirm()` natif dans `onsubmit` pour les suppressions. |
| **Images** | **Aucune image** dans le MVP | Les annonces sont 100 % textuelles. Économie massive de bande passante. |

**Résultat visé** : page d'accueil < 50 Ko, score EcoIndex A/B, Lighthouse Performance > 90.

## Installation locale

### Prérequis

- Python **3.10+**

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/Fido-Midou/GreenIT_Project.git
cd GreenIT_Project

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et générer une vraie SECRET_KEY :
python -c "import secrets; print(secrets.token_hex(32))"

# 4. (Optionnel) Initialiser la base avec des données de démo
python seed.py

# 5. Lancer le serveur de développement
python app.py
```

Le site est accessible sur **http://localhost:5000**.

### Comptes de démonstration (créés par `seed.py`)

| Email | Mot de passe | Rôle |
|---|---|---|
| `admin@campusgive.fr` | `AdminCampus2026!` | Admin |
| `alice.dupont@efrei.net` | `alice12345` | Utilisateur |
| `bilal.martin@efrei.net` | `bilal12345` | Utilisateur |

## Structure du dépôt

```
campusgive/
├── app.py                      # Point d'entrée Flask
├── config.py                   # Configuration par environnement
├── seed.py                     # Script de peuplement initial
├── requirements.txt            # Dépendances Python (4 paquets)
├── build.sh, render.yaml       # Script bash et yaml pour le déploiment sur Render
├── .env.example                # Modèle de variables d'environnement
├── .gitignore                  # Exclusions Git (.env, venv, *.db, …)
├── README.md                   # Ce fichier
│
├── backend/                    # Logique serveur
│   ├── __init__.py             #   Factory create_app + blueprints
│   ├── models.py               #   Modèles SQLAlchemy : Utilisateur, Annonce
│   ├── auth.py                 #   Routes inscription / connexion / déconnexion
│   ├── annonces.py             #   CRUD complet de l'entité Annonce + profil
│   ├── admin.py                #   Panneau d'administration
│   └── decorators.py           #   @login_required, @admin_required
│
├── frontend/                   # Présentation
│   ├── static/css/style.css    #   Feuille CSS unique (~10 Ko)
│   └── templates/              #   Templates Jinja2
│       ├── base.html           #     Layout commun (header, nav, footer)
│       ├── index.html          #     Page d'accueil + engagements écolo
│       ├── login.html          #     Connexion
│       ├── register.html       #     Inscription
│       ├── annonces.html       #     Liste paginée et filtrable
│       ├── annonce_form.html   #     Formulaire création/édition
│       ├── annonce_detail.html #     Fiche détaillée d'une annonce
│       ├── profile.html        #     Espace personnel
│       ├── profile_edit.html   #     Édition du profil
│       ├── _pagination.html    #     Composant pagination réutilisable
│       ├── 404.html, 403.html, 500.html
│       └── admin/
│           ├── dashboard.html
│           ├── users.html, user_edit.html
│           └── annonces.html
│
├── database/
│   └── schema.sql              # Schéma SQL de référence (création manuelle)
│
└── docs/                       # Livrables de conception et rapport
    ├── rapport.pdf             # Rapport final (max 25 p.)
    ├── diagramme_use_case.png
    ├── diagramme_classes.png
    ├── diagramme_sequence.png
    ├── wireframes.pdf
    ├── ecoindex_avant.png      # Captures avant/après optimisations
    ├── ecoindex_apres.png
    ├── lighthouse_*.png
    └── ...
```

## Stratégie de branches

- `main` — branche stable, protégée des push directs (PR uniquement)
- `dev` — intégration continue
- `feature/auth` — inscription, connexion, déconnexion
- `feature/annonces` — CRUD des annonces
- `feature/admin` — panneau d'administration
- `feature/front` — templates HTML / CSS

## Déploiement (Render.com)

1. Créer un compte sur [render.com](https://render.com).
2. **New -> Web Service** : connecter le dépôt GitHub.
3. Configuration :
   - **Build command** : `bash build.sh`
   - **Start command** : `gunicorn app:app`
   - **Environment** : `Python 3`
4. Variables d'environnement à définir dans Render :
   - `SECRET_KEY` — générer avec `secrets.token_hex(32)`
   - `FLASK_ENV` — `production`
5. Render redéploie automatiquement à chaque push sur `main`.

## Checklist Green IT (auto-évaluation)

- [x] Aucun framework JavaScript embarqué
- [x] Une seule feuille CSS, polices système uniquement
- [x] Aucune image, aucun média lourd
- [x] `loading="lazy"` prévu si des images sont ajoutées en V2
- [x] Pagination obligatoire (LIMIT 20)
- [x] Index BDD sur les colonnes filtrées
- [x] `SELECT` ciblé via SQLAlchemy (pas de `SELECT *`)
- [x] Mots de passe hashés avec bcrypt (cost 12)
- [x] Requêtes paramétrées (anti-injection SQL)
- [x] Cookies de session `HttpOnly` + `SameSite=Lax`
- [x] HTML5 sémantique (`<main>`, `<nav>`, `<article>`, `<footer>`)
- [x] Attributs `alt` sur toutes les images (s'il y en a)
- [x] Mode sombre auto via `prefers-color-scheme`
- [x] `.env` exclu du dépôt
- [x] Architecture sobre : 4 dépendances Python en production
