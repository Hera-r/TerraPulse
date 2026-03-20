import requests
from django.core.cache import cache

CACHE_TTL = 600

WMO_CODES = {
    0:  'Clear sky',
    1:  'Mainly clear',
    2:  'Partly cloudy',
    3:  'Overcast',
    45: 'Foggy',
    48: 'Freezing fog',
    51: 'Light drizzle',
    53: 'Moderate drizzle',
    55: 'Dense drizzle',
    61: 'Light rain',
    63: 'Moderate rain',
    65: 'Heavy rain',
    71: 'Light snow',
    73: 'Moderate snow',
    75: 'Heavy snow',
    80: 'Light showers',
    81: 'Moderate showers',
    82: 'Violent showers',
    95: 'Thunderstorm',
    99: 'Thunderstorm with hail',
}

WMO_CODES_FR = {
    0:  'Ciel dégagé',
    1:  'Principalement dégagé',
    2:  'Partiellement nuageux',
    3:  'Couvert',
    45: 'Brouillard',
    48: 'Brouillard givrant',
    51: 'Bruine légère',
    53: 'Bruine modérée',
    55: 'Bruine dense',
    61: 'Pluie légère',
    63: 'Pluie modérée',
    65: 'Pluie forte',
    71: 'Neige légère',
    73: 'Neige modérée',
    75: 'Neige forte',
    80: 'Averses légères',
    81: 'Averses modérées',
    82: 'Averses violentes',
    95: 'Orage',
    99: 'Orage avec grêle',
}


def get_weather(city, lat, lon, lang='en', timezone='auto'):
    cache_key = f'weather_{lat:.2f}_{lon:.2f}'
    cached = cache.get(cache_key)
    if cached:
        if cached.get('_lang') != lang:
            cached = None
        else:
            return cached

    try:
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,precipitation,weathercode,windspeed_10m,relative_humidity_2m',
            'timezone': timezone or 'auto',
        }
        r = requests.get(url, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()['current']

        code = data.get('weathercode', 0)
        codes = WMO_CODES_FR if lang == 'fr' else WMO_CODES
        condition = codes.get(code, 'Unknown')

        result = {
            'city': city,
            'temp': round(data['temperature_2m']),
            'humidity': data.get('relative_humidity_2m', 0),
            'windspeed': round(data.get('windspeed_10m', 0)),
            'precipitation': data.get('precipitation', 0),
            'condition': condition,
            '_lang': lang,
        }
        cache.set(cache_key, result, CACHE_TTL)
        return result
    except Exception:
        return {
            'city': city,
            'temp': '--',
            'humidity': '--',
            'windspeed': '--',
            'precipitation': 0,
            'condition': 'Unavailable' if lang == 'en' else 'Indisponible',
            '_lang': lang,
        }


def get_air_quality(lat, lon):
    cache_key = f'aqi_{lat:.2f}_{lon:.2f}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = 'https://air-quality-api.open-meteo.com/v1/air-quality'
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'pm10,pm2_5,european_aqi',
        }
        r = requests.get(url, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()['current']

        aqi = data.get('european_aqi', 0)
        if aqi <= 20:
            color = '#16a34a'
        elif aqi <= 40:
            color = '#65a30d'
        elif aqi <= 60:
            color = '#ca8a04'
        elif aqi <= 80:
            color = '#ea580c'
        else:
            color = '#dc2626'

        result = {
            'aqi': aqi,
            'aqi_pct': min(int(aqi), 100),
            'aqi_color': color,
            'pm10': round(data.get('pm10', 0), 1),
            'pm2_5': round(data.get('pm2_5', 0), 1),
        }
        cache.set(cache_key, result, CACHE_TTL)
        return result
    except Exception:
        return {'aqi': 0, 'aqi_pct': 0, 'aqi_color': '#94a3b8', 'pm10': 0, 'pm2_5': 0}
