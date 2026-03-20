"""
Climate news via NewsAPI.org (free tier) with BBC/Guardian/Le Monde RSS fallback.
Language-aware: uses French sources for francophone users, English otherwise.
"""
import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.cache import cache
from datetime import datetime

CACHE_TTL = 900  # 15 minutes

CATEGORY_KEYWORDS = {
    'Green Finance': ['finance', 'green bond', 'forex', 'invest', 'bourse', 'ESG', 'fonds', 'marché'],
    'Energy': ['solar', 'wind', 'éolien', 'solaire', 'energy', 'énergie', 'renewable', 'nucléaire'],
    'Oceans': ['ocean', 'mer', 'sea', 'coral', 'reef', 'maritime'],
    'Innovation': ['startup', 'technolog', 'innovation', 'plastic', 'plastique', 'invention'],
    'Climate': ['climate', 'climat', 'COP', 'carbon', 'CO2', 'température', 'global warming'],
    'Lifestyle': ['sustainable', 'durable', 'vegan', 'organic', 'bio', 'recyclage'],
}

CATEGORY_LABELS = {
    'en': {
        'Green Finance': 'Green Finance',
        'Energy': 'Energy',
        'Oceans': 'Oceans',
        'Innovation': 'Innovation',
        'Climate': 'Climate',
        'Lifestyle': 'Lifestyle',
    },
    'fr': {
        'Green Finance': 'Finance Verte',
        'Energy': 'Énergies',
        'Oceans': 'Océans',
        'Innovation': 'Innovation',
        'Climate': 'Climat Mondial',
        'Lifestyle': 'Mode Durable',
    },
}

# RSS feeds per language
RSS_FEEDS = {
    'fr': [
        'https://www.lemonde.fr/planete/rss_full.xml',
        'https://reporterre.net/spip.php?page=backend',
        'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
    ],
    'en': [
        'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
        'https://www.theguardian.com/environment/climate-crisis/rss',
    ],
}

PLACEHOLDER_IMAGES = [
    'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600&h=400&fit=crop&auto=format',
    'https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=600&h=400&fit=crop&auto=format',
    'https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=600&h=400&fit=crop&auto=format',
    'https://images.unsplash.com/photo-1569163139599-0f4517e36f51?w=600&h=400&fit=crop&auto=format',
    'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=600&h=400&fit=crop&auto=format',
    'https://images.unsplash.com/photo-1508193638397-1c4234db14d8?w=600&h=400&fit=crop&auto=format',
]


def _guess_category(text, lang='en'):
    text_lower = (text or '').lower()
    for key, keywords in CATEGORY_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            return CATEGORY_LABELS[lang].get(key, key)
    return CATEGORY_LABELS[lang].get('Climate', 'Climate')


def _format_time(date_str, lang='en'):
    try:
        for fmt in ('%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S %z'):
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        else:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

        now = datetime.utcnow()
        try:
            diff = now - dt.replace(tzinfo=None)
        except Exception:
            diff = now - dt

        hours = int(diff.total_seconds() / 3600)
        if hours < 1:
            minutes = max(1, int(diff.total_seconds() / 60))
            return f'il y a {minutes} min' if lang == 'fr' else f'{minutes} min ago'
        elif hours < 24:
            return f'il y a {hours}h' if lang == 'fr' else f'{hours}h ago'
        else:
            days = diff.days
            return f'il y a {days}j' if lang == 'fr' else f'{days}d ago'
    except Exception:
        return 'Récemment' if lang == 'fr' else 'Recently'


def _get_rss(lang='en'):
    articles = []
    feeds = RSS_FEEDS.get(lang, RSS_FEEDS['en'])
    for feed_url in feeds:
        try:
            r = requests.get(feed_url, timeout=7, headers={'User-Agent': 'TerraPulse/2.0'})
            root = ET.fromstring(r.content)
            items = root.findall('.//item')
            for item in items:
                title = item.findtext('title', '').strip()
                pub = item.findtext('pubDate', '')
                link = item.findtext('link', '#')
                desc = item.findtext('description', '')
                if not title:
                    continue
                articles.append({
                    'title': title,
                    'category': _guess_category(title + ' ' + desc, lang),
                    'image': PLACEHOLDER_IMAGES[len(articles) % len(PLACEHOLDER_IMAGES)],
                    'url': link,
                    'source': feed_url.split('/')[2].replace('www.', '').split('.')[0].title(),
                    'time': _format_time(pub, lang),
                })
                if len(articles) >= 10:
                    break
        except Exception:
            continue
        if len(articles) >= 10:
            break
    return articles[:10]


def get_climate_news(lang='en', page_size=10):
    cache_key = f'climate_news_{lang}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    key = getattr(settings, 'NEWS_API_KEY', '')

    if key:
        try:
            queries = {
                'fr': '(changement climatique OR énergie renouvelable OR finance verte OR biodiversité)',
                'en': '(climate change OR renewable energy OR "green finance" OR biodiversity)',
            }
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': queries.get(lang, queries['en']),
                'sortBy': 'publishedAt',
                'pageSize': page_size,
                'apiKey': key,
                'language': lang,
            }
            r = requests.get(url, params=params, timeout=8)
            r.raise_for_status()
            raw = r.json().get('articles', [])
            articles = []
            for i, a in enumerate(raw):
                if not a.get('title') or a['title'] == '[Removed]':
                    continue
                articles.append({
                    'title': a['title'],
                    'category': _guess_category(
                        (a.get('title') or '') + ' ' + (a.get('description') or ''), lang
                    ),
                    'image': a.get('urlToImage') or PLACEHOLDER_IMAGES[i % len(PLACEHOLDER_IMAGES)],
                    'url': a.get('url', '#'),
                    'source': (a.get('source') or {}).get('name', 'NewsAPI'),
                    'time': _format_time(a.get('publishedAt', ''), lang),
                })
            if articles:
                cache.set(cache_key, articles, CACHE_TTL)
                return articles
        except Exception:
            pass

    articles = _get_rss(lang)
    if articles:
        cache.set(cache_key, articles, CACHE_TTL)
    return articles
