import yfinance as yf
from django.core.cache import cache

SIGNALS_CACHE_KEY = 'trading_signals'
CACHE_TTL = 600


def _compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def generate_signal(ticker, name):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period='30d', interval='1d')

        if len(hist) < 10:
            return None

        close = hist['Close']
        current_price = round(float(close.iloc[-1]), 2)
        prev_price = round(float(close.iloc[-2]), 2)
        change_pct = round((current_price - prev_price) / prev_price * 100, 2)

        rsi = _compute_rsi(close).iloc[-1]
        ma5 = float(close.tail(5).mean())
        ma20 = float(close.tail(20).mean())
        vol = hist['Volume']
        vol_ratio = float(vol.iloc[-1]) / float(vol.tail(5).mean()) if vol.tail(5).mean() > 0 else 1.0
        score = 50

        if rsi < 30:
            score += 30
        elif rsi < 45:
            score += 15
        elif rsi > 70:
            score -= 30
        elif rsi > 55:
            score -= 10

        if ma5 > ma20:
            score += 15
        else:
            score -= 15

        if vol_ratio > 1.5 and change_pct > 0:
            score += 10
        elif vol_ratio > 1.5 and change_pct < 0:
            score -= 10

        score = max(10, min(90, score))
        confidence = int(score)

        if score >= 60:
            signal = 'BUY'
            signal_label = 'ACHAT FORT' if score >= 75 else 'ACHAT'
            signal_color = '#22c55e'
            reasoning = (
                f"RSI à {rsi:.0f} — {'survendu, rebond probable' if rsi < 40 else 'momentum positif'}. "
                f"MM5 {'>' if ma5 > ma20 else '<'} MM20 indique une {'tendance haussière' if ma5 > ma20 else 'faiblesse'}. "
                f"Volume {'en hausse' if vol_ratio > 1.0 else 'stable'} ({vol_ratio:.1f}x la moyenne)."
            )
        elif score <= 40:
            signal = 'SELL'
            signal_label = 'VENTE FORTE' if score <= 25 else 'VENTE'
            signal_color = '#ef4444'
            reasoning = (
                f"RSI à {rsi:.0f} — {'surachat détecté' if rsi > 65 else 'momentum négatif'}. "
                f"Tendance baissière confirmée par les moyennes mobiles. "
                f"Pression vendeuse {'élevée' if vol_ratio > 1.0 else 'modérée'}."
            )
        else:
            signal = 'HOLD'
            signal_label = 'ATTENTE'
            signal_color = '#f59e0b'
            reasoning = (
                f"RSI neutre à {rsi:.0f}. Signal mixte entre MM5 et MM20. "
                f"Attendre une confirmation de direction avant de prendre position."
            )

        return {
            'ticker': ticker,
            'name': name,
            'signal': signal,
            'signal_label': signal_label,
            'signal_color': signal_color,
            'confidence': confidence,
            'reasoning': reasoning,
            'price': current_price,
            'change': change_pct,
            'positive': change_pct >= 0,
            'rsi': round(float(rsi), 1),
        }
    except Exception:
        return None


def get_signals():
    cached = cache.get(SIGNALS_CACHE_KEY)
    if cached:
        return cached

    from api.services.stocks import GREEN_TICKERS

    signals = []
    for stock in GREEN_TICKERS:
        sig = generate_signal(stock['ticker'], stock['name'])
        if sig:
            signals.append(sig)

    if signals:
        cache.set(SIGNALS_CACHE_KEY, signals, CACHE_TTL)
    return signals
