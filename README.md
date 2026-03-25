# TerraPulse

> [English](#english) · [Français](#français)

---

## English

Real-time eco dashboard: climate news, green stock markets, air quality, weather, and market signal analysis - all powered by free APIs with no credit card required.

> **Note - Active MVP, work in progress**
> This project is an active MVP, still under construction. It was built through vibe coding, combined with years of hands-on Django experience. The code is functional and well-structured, but some features are still in progress.

### Features

- **Weather and air quality** - Open-Meteo API, auto-detected by IP geolocation
- **Green stock ticker** - BYD, First Solar, Vestas, Rivian, NextEra Energy, Beyond Meat via Yahoo Finance
- **Climate news feed** - Le Monde / BBC Science & Environment (RSS), or NewsAPI.org with a free key
- **Signal analysis** - RSI and moving average indicators on green stocks
- **Bilingual** - Automatic French/English detection based on user's country

### Stack

- **Backend**: Django 6, Python 3
- **Frontend**: Vanilla CSS + Vanilla JS (no framework)
- **Infrastructure**: Docker, Docker Compose, Gunicorn, WhiteNoise
- **APIs**: Open-Meteo, ip-api.com, Yahoo Finance (`yfinance`), RSS feeds, NewsAPI.org (optional)

### Setup

Prerequisites: Docker and Docker Compose installed on your machine.

```bash
git clone git@github.com:Hera-r/TerraPulse.git
cd TerraPulse
```

Create a `.env` file at the project root:
```env
DEBUG=False
SECRET_KEY=CHANGE_THIS_TO_A_LONG_RANDOM_STRING
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,127.0.0.1,localhost
APP_URL=https://yourdomain.com
NEWS_API_KEY=
```

Then run the project using the provided Makefile:
```bash
make
```
This single command will build the Docker image, start the container, and run the database migrations automatically.

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

**Useful commands:**
- `make logs`: View real-time container logs
- `make down`: Stop the application
- `make clean`: Remove containers and volumes

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | **Yes** | Django secret key |
| `DEBUG` | No | `True` for dev, `False` for prod (default: `False`) |
| `ALLOWED_HOSTS` | **Yes** | Comma-separated list, e.g. `127.0.0.1,localhost` |
| `NEWS_API_KEY` | No | Free key from [newsapi.org](https://newsapi.org/register), falls back to RSS if absent |
| `APP_URL` | No | Base URL of the app |


Generate a `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Français

Tableau de bord éco en temps réel : actualités climatiques, marchés boursiers verts, qualité de l'air, météo et analyse de signaux de marché - propulsé par des APIs gratuites, sans carte bancaire.

> **Note — MVP en cours de développement**
> Ce projet est un MVP actif, toujours en construction. Il a été développé en vibe coding, combiné à plusieurs années d'expérience concrète avec Django. Le code est fonctionnel et structuré, mais certaines fonctionnalités sont encore à venir.

### Fonctionnalités

- **Météo et qualité de l'air** - Open-Meteo, détection automatique par géolocalisation IP
- **Cours verts en direct** - BYD, First Solar, Vestas, Rivian, NextEra, Beyond Meat via Yahoo Finance
- **Actualités climatiques** - Le Monde / BBC Science & Environment (RSS) ou NewsAPI.org (clé optionnelle)
- **Analyse de signaux** - Indicateurs RSI et moyennes mobiles sur les actions vertes
- **Bilingue** - Français ou anglais détecté automatiquement selon le pays de l'utilisateur

### Stack

- **Backend** : Django 6, Python 3
- **Frontend** : CSS Vanilla + JS Vanilla (aucun framework)
- **Infrastructure** : Docker, Docker Compose, Gunicorn, WhiteNoise
- **APIs** : Open-Meteo, ip-api.com, Yahoo Finance (`yfinance`), RSS, NewsAPI.org (optionnel)

### Installation

Prérequis : Docker et Docker Compose installés sur votre machine.

```bash
git clone git@github.com:Hera-r/TerraPulse.git
cd TerraPulse
```

Créer un fichier `.env` à la racine du projet :
```env
DEBUG=False
SECRET_KEY=CHANGE_THIS_TO_A_LONG_RANDOM_STRING
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,127.0.0.1,localhost
APP_URL=https://yourdomain.com
NEWS_API_KEY=
```

Puis lancer le projet via le Makefile :
```bash
make
```
Cette commande unique compile l'image Docker, démarre le conteneur et exécute les migrations de base de données automatiquement.

Ouvrir [http://127.0.0.1:8000](http://127.0.0.1:8000)

**Commandes utiles :**
- `make logs` : Voir les logs en temps réel
- `make down` : Arrêter l'application
- `make clean` : Supprimer les conteneurs et les volumes

### Variables d'environnement

| Variable | Requis | Description |
|---|---|---|
| `SECRET_KEY` | **Oui** | Clé secrète Django |
| `DEBUG` | Non | `True` en dev, `False` en prod (défaut : `False`) |
| `ALLOWED_HOSTS` | **Oui** | Liste séparée par virgules, ex. `127.0.0.1,localhost` |
| `NEWS_API_KEY` | Non | Clé gratuite sur [newsapi.org](https://newsapi.org/register), RSS si absente |
| `APP_URL` | Non | URL de base de l'application |


Générer une `SECRET_KEY` :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Licence

MIT
