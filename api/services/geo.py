import requests
from django.core.cache import cache

GEO_CACHE_KEY = 'geo_{ip}'
CACHE_TTL = 3600

FRANCOPHONE_COUNTRIES = {
    'FR', 'BE', 'CH', 'LU', 'MC', 'CA', 'SN', 'CI', 'ML', 'BF',
    'GN', 'NE', 'TG', 'BJ', 'CM', 'GA', 'CG', 'CD', 'CF', 'TD',
    'DJ', 'KM', 'MG', 'MU', 'SC', 'RW', 'BI', 'HT', 'VU', 'PF',
    'NC', 'RE', 'GP', 'MQ', 'GF', 'MF', 'PM', 'WF',
}

_DEFAULT_GEO = {
    'city': 'Montréal',
    'country': 'Canada',
    'country_code': 'CA',
    'lat': 45.5017,
    'lon': -73.5673,
    'timezone': 'America/Toronto',
    'lang': 'fr',
    'ip': '',
}


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def _is_local(ip):
    return ip in ('127.0.0.1', '::1', 'localhost') \
        or ip.startswith('192.168.') \
        or ip.startswith('10.') \
        or ip.startswith('172.16.')


def get_geo(request):
    ip = get_client_ip(request)
    cache_key = GEO_CACHE_KEY.format(ip=ip)
    cached = cache.get(cache_key)
    if cached:
        return cached

    result = _fetch_geo('' if _is_local(ip) else ip)
    cache.set(cache_key, result, CACHE_TTL)
    return result


def _fetch_geo(ip):
    try:
        r = requests.get(
            f'http://ip-api.com/json/{ip}',
            params={'fields': 'status,country,countryCode,city,lat,lon,timezone,query', 'lang': 'fr'},
            timeout=5,
        )
        data = r.json()
        if data.get('status') == 'success':
            code = data.get('countryCode', 'CA')
            return {
                'city': data.get('city', _DEFAULT_GEO['city']),
                'country': data.get('country', _DEFAULT_GEO['country']),
                'country_code': code,
                'lat': data.get('lat', _DEFAULT_GEO['lat']),
                'lon': data.get('lon', _DEFAULT_GEO['lon']),
                'timezone': data.get('timezone', _DEFAULT_GEO['timezone']),
                'lang': 'fr' if code in FRANCOPHONE_COUNTRIES else 'en',
                'ip': data.get('query', ip),
            }
    except Exception:
        pass
    return {**_DEFAULT_GEO, 'ip': ip}
