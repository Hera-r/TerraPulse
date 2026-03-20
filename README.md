# TerraPulse

> 🇫🇷 [Français](#français) · 🇬🇧 [English](#english)

---

## Français

Tableau de bord éco en temps réel : actualités climatiques, marchés boursiers verts, qualité de l'air, météo et signaux de trading RSI — propulsé par des APIs gratuites, sans carte bancaire.

> **Note — MVP en cours de développement**
> Ce projet est un MVP actif, toujours en construction. Il a été développé en mode *vibe coding* — c'est-à-dire en itérant rapidement et intuitivement — tout en s'appuyant sur plusieurs années d'expérience concrète avec Django. Le code est fonctionnel et structuré, mais certaines fonctionnalités sont encore à venir.

### Fonctionnalités

- **Météo & Qualité de l'air** — Open-Meteo, détection automatique par géolocalisation IP
- **Cours verts en direct** — Tesla, First Solar, Vestas, Rivian, NextEra, Beyond Meat via Yahoo Finance
- **Actualités climatiques** — Le Monde / BBC Science & Environment (RSS) ou NewsAPI.org (clé optionnelle)
- **Bot de trading** — Signaux BUY/SELL/HOLD calculés via RSI + Moyennes Mobiles
- **Bilingue** — Français ou anglais détecté automatiquement selon le pays de l'utilisateur

### Stack

- **Backend** : Django 6, Python 3
- **Frontend** : CSS Vanilla + JS Vanilla (aucun framework)
- **APIs** : Open-Meteo · ip-api.com · Yahoo Finance (`yfinance`) · RSS · NewsAPI.org (optionnel)

### Installation

```bash
git clone git@github.com:Hera-r/TerraPulse.git
cd TerraPulse
pip install -r requirements.txt
cp .env.example .env   # Remplir les variables
python manage.py migrate
python manage.py runserver
```

Ouvrir [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Variables d'environnement

| Variable | Requis | Description |
|---|---|---|
| `SECRET_KEY` | **Oui** | Clé secrète Django — générer une valeur aléatoire |
| `DEBUG` | Non | `True` en dev, `False` en prod (défaut : `False`) |
| `ALLOWED_HOSTS` | **Oui** | Liste séparée par virgules, ex. `127.0.0.1,localhost` |
| `NEWS_API_KEY` | Non | Clé gratuite sur [newsapi.org](https://newsapi.org/register) — RSS si absente |
| `APP_URL` | Non | URL de base de l'application |

> **Ne jamais commiter le fichier `.env`.** Il est listé dans `.gitignore`.

Générer une `SECRET_KEY` :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## English

Real-time eco dashboard: climate news, green stock markets, air quality, weather, and RSI-based trading signals - all powered by free APIs with no credit card required.

> **Note — Active MVP, work in progress**
> This project is an active MVP, still under construction. It was built through *vibe coding* — iterating quickly and intuitively — combined with years of hands-on Django experience. The code is functional and well-structured, but some features are still in progress.

### Features

- **Weather & Air Quality** - Open-Meteo API, auto-detected by IP geolocation
- **Green Stock Ticker** - Tesla, First Solar, Vestas, Rivian, NextEra Energy, Beyond Meat via Yahoo Finance
- **Climate News Feed** - Le Monde / BBC Science & Environment (RSS), or NewsAPI.org with a free key
- **Trading Bot** - BUY/SELL/HOLD signals calculated from RSI + Moving Averages
- **Bilingual** - Automatic French/English detection based on user's country

### Stack

- **Backend**: Django 6, Python 3
- **Frontend**: Vanilla CSS + Vanilla JS (no framework)
- **APIs**: Open-Meteo · ip-api.com · Yahoo Finance (`yfinance`) · RSS feeds · NewsAPI.org (optional)

### Setup

```bash
git clone git@github.com:Hera-r/TerraPulse.git
cd TerraPulse
pip install -r requirements.txt
cp .env.example .env   # Fill in your values
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | **Yes** | Django secret key - generate a random one |
| `DEBUG` | No | `True` for dev, `False` for prod (default: `False`) |
| `ALLOWED_HOSTS` | **Yes** | Comma-separated list, e.g. `127.0.0.1,localhost` |
| `NEWS_API_KEY` | No | Free key from [newsapi.org](https://newsapi.org/register) - falls back to RSS if absent |
| `APP_URL` | No | Base URL of the app |

> **Never commit your `.env` file.** It is listed in `.gitignore`.

Generate a `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### License

MIT
