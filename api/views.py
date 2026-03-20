from django.http import JsonResponse
from django.views.decorators.http import require_GET

from api.services.geo import get_geo
from api.services.weather import get_weather, get_air_quality
from api.services.stocks import get_green_stocks, get_stock_history, VALID_TICKERS
from api.services.news import get_climate_news
from api.services.trading_bot import get_signals

VALID_LANGS = {'en', 'fr'}


@require_GET
def weather_view(request):
    geo = get_geo(request)
    weather = get_weather(
        city=geo['city'],
        lat=geo['lat'],
        lon=geo['lon'],
        lang=geo['lang'],
        timezone=geo.get('timezone', 'auto'),
    )
    air = get_air_quality(lat=geo['lat'], lon=geo['lon'])
    return JsonResponse({
        'weather': weather,
        'air_quality': air,
        'geo': {
            'city': geo['city'],
            'country': geo['country'],
            'country_code': geo['country_code'],
            'lang': geo['lang'],
        },
    })


@require_GET
def stocks_view(request):
    return JsonResponse({'stocks': get_green_stocks()})


@require_GET
def stock_history_view(request):
    raw = request.GET.get('ticker', 'TSLA').upper().strip()
    ticker = raw if raw in VALID_TICKERS else 'TSLA'
    return JsonResponse({'ticker': ticker, 'history': get_stock_history(ticker)})


@require_GET
def news_view(request):
    geo = get_geo(request)
    raw_lang = request.GET.get('lang', geo['lang']).lower().strip()
    lang = raw_lang if raw_lang in VALID_LANGS else geo['lang']
    return JsonResponse({'articles': get_climate_news(lang=lang), 'lang': lang})


@require_GET
def signals_view(request):
    geo = get_geo(request)
    return JsonResponse({'signals': get_signals(), 'lang': geo['lang']})


@require_GET
def geo_view(request):
    geo = get_geo(request)
    return JsonResponse({
        'city': geo['city'],
        'country': geo['country'],
        'country_code': geo['country_code'],
        'lang': geo['lang'],
    })
