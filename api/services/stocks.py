import yfinance as yf
from django.core.cache import cache

STOCKS_CACHE_KEY = 'green_stocks'
HISTORY_CACHE_KEY = 'stock_history_{ticker}'
CACHE_TTL = 300

GREEN_TICKERS = [
    {'ticker': 'TSLA',   'name': 'Tesla',         'sector': 'EV'},
    {'ticker': 'FSLR',   'name': 'First Solar',   'sector': 'Solar'},
    {'ticker': 'VWS.CO', 'name': 'Vestas',        'sector': 'Wind'},
    {'ticker': 'RIVN',   'name': 'Rivian',        'sector': 'EV'},
    {'ticker': 'BYND',   'name': 'Beyond Meat',   'sector': 'Food'},
    {'ticker': 'NEE',    'name': 'NextEra Energy', 'sector': 'Renewable'},
]

VALID_TICKERS = {s['ticker'] for s in GREEN_TICKERS}


def get_green_stocks():
    cached = cache.get(STOCKS_CACHE_KEY)
    if cached:
        return cached

    results = []
    for stock in GREEN_TICKERS:
        try:
            t = yf.Ticker(stock['ticker'])
            hist = t.history(period='5d', interval='1d')

            if len(hist) >= 2:
                prev = float(hist['Close'].iloc[-2])
                curr = float(hist['Close'].iloc[-1])
                change = round((curr - prev) / prev * 100, 2)
                price = round(curr, 2)
            elif len(hist) == 1:
                price = round(float(hist['Close'].iloc[-1]), 2)
                change = 0.0
            else:
                continue

            results.append({
                'ticker': stock['ticker'],
                'name': stock['name'],
                'sector': stock['sector'],
                'price': price,
                'change': change,
                'positive': change >= 0,
            })
        except Exception:
            continue

    if results:
        cache.set(STOCKS_CACHE_KEY, results, CACHE_TTL)
    return results


def get_stock_history(ticker='TSLA', period='1d', interval='5m'):
    if ticker not in VALID_TICKERS:
        return []

    cache_key = HISTORY_CACHE_KEY.format(ticker=ticker)
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval=interval)
        if hist.empty:
            hist = t.history(period='5d', interval='1d')

        data = [
            {
                'time': idx.strftime('%H:%M') if hasattr(idx, 'strftime') else str(idx),
                'price': round(float(row['Close']), 2),
            }
            for idx, row in hist.iterrows()
        ]
        cache.set(cache_key, data, CACHE_TTL)
        return data
    except Exception:
        return []
