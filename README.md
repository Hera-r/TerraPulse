# TerraPulse

Eco dashboard built with Django and vanilla CSS/JS. Displays real-time climate news, green stock markets, air quality, weather, and RSI-based trading signals — all powered by free APIs with no credit card required.

## Features

- **Weather & Air Quality** — Open-Meteo API, auto-detected by IP geolocation
- **Green Stock Ticker** — Tesla, First Solar, Vestas, Rivian, NextEra Energy, Beyond Meat via Yahoo Finance
- **Climate News Feed** — Le Monde / BBC Science & Environment (RSS), or NewsAPI.org with a free key
- **Trading Bot** — BUY/SELL/HOLD signals calculated from RSI + Moving Averages
- **Bilingual** — automatic French/English detection based on user's country (no configuration needed)

## Stack

- **Backend** : Django 6, Python 3
- **Frontend** : Vanilla CSS + Vanilla JS (no framework, no Tailwind)
- **APIs** : Open-Meteo · ip-api.com · Yahoo Finance (`yfinance`) · RSS feeds · NewsAPI.org (optional)

## Setup

```bash
# 1. Clone
git clone git@github.com:Hera-r/TerraPulse.git
cd TerraPulse

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and ALLOWED_HOSTS

# 4. Apply migrations
python manage.py migrate

# 5. Run
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | **Yes** | Django secret key — generate a random one |
| `DEBUG` | No | `True` for dev, `False` for prod (default: `False`) |
| `ALLOWED_HOSTS` | **Yes** | Comma-separated list, e.g. `127.0.0.1,localhost` |
| `NEWS_API_KEY` | No | Free key from [newsapi.org](https://newsapi.org/register) — falls back to RSS if absent |
| `GEMINI_API_KEY` | No | Reserved for future use |
| `APP_URL` | No | Base URL of the app |

> **Never commit your `.env` file.** It is listed in `.gitignore`.

## Generating a SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## License

MIT
