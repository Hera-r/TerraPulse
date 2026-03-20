/**
 * TerraPulse Dashboard — Vanilla JS
 * Language-aware, geo-driven, no emoji overload.
 */

/* =============================================
   STATE
   ============================================= */
let lang = 'en';
let allArticles = [];
let allSignals  = [];
let currentTicker = 'TSLA';
let refreshTimer  = null;

/* =============================================
   LANGUAGE HELPERS
   ============================================= */
function applyLang(l) {
  lang = l;
  document.documentElement.lang = l;

  // Update all data-fr / data-en labelled elements
  document.querySelectorAll('[data-fr][data-en]').forEach(el => {
    el.textContent = l === 'fr' ? el.dataset.fr : el.dataset.en;
  });

  // Search placeholder
  const si = document.getElementById('search-input');
  if (si) {
    si.placeholder = l === 'fr'
      ? 'Rechercher actualités climat, marchés verts…'
      : 'Search climate news, green markets…';
  }
}

function t(fr, en) { return lang === 'fr' ? fr : en; }

/* =============================================
   GEO — detect location and language via IP
   ============================================= */
async function loadGeo() {
  try {
    const res = await fetch('/api/geo/');
    const geo = await res.json();
    lang = geo.lang || 'en';
    applyLang(lang);

    // Update location display
    const locEl = document.getElementById('header-location');
    if (locEl) locEl.textContent = `${geo.city}, ${geo.country}`;

    return geo;
  } catch {
    return { lang: 'en', city: '—', country: '—' };
  }
}

/* =============================================
   WEATHER
   ============================================= */
async function loadWeather() {
  try {
    const res = await fetch('/api/weather/');
    const { weather: w, air_quality: a } = await res.json();

    // Header pill
    document.getElementById('weather-label').textContent = `${w.city} ${w.temp}°C`;

    // Weather widget
    const wtitle = document.getElementById('weather-widget-title');
    if (wtitle) wtitle.textContent = t('Météo', 'Weather') + ' — ' + w.city;

    const tempEl  = document.getElementById('weather-temp');
    const descEl  = document.getElementById('weather-desc');
    const humEl   = document.getElementById('weather-hum');
    const windEl  = document.getElementById('weather-wind');

    if (tempEl) tempEl.textContent = `${w.temp}°`;
    if (descEl) descEl.textContent = w.condition;
    if (humEl)  humEl.textContent  = `${w.humidity}%`;
    if (windEl) windEl.textContent = `${w.windspeed} km/h`;

    // AQI
    if (a) {
      const aqiBadge = document.getElementById('aqi-badge');
      const aqiBar   = document.getElementById('aqi-bar');
      const pm25El   = document.getElementById('pm25-val');
      const pm10El   = document.getElementById('pm10-val');

      const aqiLabels = {
        fr: ['Bon', 'Passable', 'Moyen', 'Mauvais', 'Très mauvais'],
        en: ['Good', 'Fair', 'Moderate', 'Poor', 'Very poor'],
      };
      const aqiIdx = a.aqi <= 20 ? 0 : a.aqi <= 40 ? 1 : a.aqi <= 60 ? 2 : a.aqi <= 80 ? 3 : 4;
      const aqiLabel = aqiLabels[lang][aqiIdx];

      if (aqiBadge) { aqiBadge.textContent = `${aqiLabel} · ${a.aqi}`; aqiBadge.style.color = a.aqi_color; }
      if (aqiBar)   { aqiBar.style.width = `${a.aqi_pct}%`; aqiBar.style.background = a.aqi_color; }
      if (pm25El)   pm25El.textContent = `${a.pm2_5} μg/m³`;
      if (pm10El)   pm10El.textContent = `${a.pm10} μg/m³`;

      // Climate widget AQI row
      const wAqi    = document.getElementById('widget-aqi');
      const wAqiBar = document.getElementById('widget-aqi-bar');
      if (wAqi)    { wAqi.textContent = `${a.aqi} (${aqiLabel})`; wAqi.style.color = a.aqi_color; }
      if (wAqiBar) { wAqiBar.style.width = `${a.aqi_pct}%`; wAqiBar.style.background = a.aqi_color; }
    }
  } catch (e) {
    console.warn('[TerraPulse] weather error', e);
  }
}

/* =============================================
   STOCKS + TICKER
   ============================================= */
async function loadStocks() {
  try {
    const res = await fetch('/api/stocks/');
    const { stocks } = await res.json();
    buildTicker(stocks);
    buildSidebarStocks(stocks);
  } catch (e) {
    console.warn('[TerraPulse] stocks error', e);
  }
}

function buildTicker(stocks) {
  const track = document.getElementById('ticker-track');
  if (!track || !stocks.length) return;

  const items = stocks.map(s => {
    const sign = s.positive ? '+' : '';
    const cls  = s.positive ? 'ticker__item--up' : 'ticker__item--down';
    return `<span class="ticker__item ${cls}">${s.name} <strong>${s.price}</strong> (${sign}${s.change}%)</span>
            <span class="ticker__sep">·</span>`;
  });

  // Duplicate for seamless loop
  track.innerHTML = items.join('') + items.join('');
  track.classList.add('running');
}

function buildSidebarStocks(stocks) {
  const el = document.getElementById('sidebar-stocks');
  if (!el || !stocks.length) return;

  el.innerHTML = stocks.map(s => {
    const sign = s.positive ? '+' : '';
    const cls  = s.positive ? 'up' : 'down';
    return `
      <div class="stock-row">
        <span class="stock-row__name">${s.ticker}</span>
        <div class="stock-row__right">
          <span class="stock-row__price">$${s.price}</span>
          <span class="stock-row__change ${cls}">${sign}${s.change}%</span>
        </div>
      </div>`;
  }).join('');
}

/* =============================================
   MINI CHART (Canvas)
   ============================================= */
async function loadChart(ticker) {
  try {
    const res = await fetch(`/api/stock-history/?ticker=${ticker}`);
    const { history } = await res.json();
    drawChart(history);
  } catch {}
}

function drawChart(data) {
  const canvas = document.getElementById('mini-chart');
  if (!canvas || !data || !data.length) return;

  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  const prices = data.map(d => d.price);
  const min = Math.min(...prices), max = Math.max(...prices);
  const range = max - min || 1;
  const pad = { t: 4, b: 4, l: 2, r: 2 };
  const cW = W - pad.l - pad.r, cH = H - pad.t - pad.b;

  const x = i => pad.l + (i / (prices.length - 1)) * cW;
  const y = v => pad.t + (1 - (v - min) / range) * cH;

  const isUp = prices[prices.length - 1] >= prices[0];
  const color = isUp ? '#22c55e' : '#ef4444';

  // Area fill
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, isUp ? 'rgba(34,197,94,0.25)' : 'rgba(239,68,68,0.25)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');

  ctx.beginPath();
  ctx.moveTo(x(0), y(prices[0]));
  prices.forEach((p, i) => { if (i > 0) ctx.lineTo(x(i), y(p)); });
  ctx.lineTo(x(prices.length - 1), H);
  ctx.lineTo(x(0), H);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Line
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.lineJoin = 'round';
  ctx.moveTo(x(0), y(prices[0]));
  prices.forEach((p, i) => { if (i > 0) ctx.lineTo(x(i), y(p)); });
  ctx.stroke();
}

/* =============================================
   SIGNALS (trading bot)
   ============================================= */
async function loadSignals() {
  try {
    const res = await fetch('/api/signals/');
    const { signals } = await res.json();
    allSignals = signals || [];
    updateBotDisplay(allSignals.find(s => s.ticker === currentTicker) || allSignals[0]);
  } catch (e) {
    console.warn('[TerraPulse] signals error', e);
  }
}

function updateBotDisplay(sig) {
  if (!sig) return;

  document.getElementById('bot-name').textContent = `${sig.ticker}`;

  const priceEl  = document.getElementById('bot-price');
  const changeEl = document.getElementById('bot-change');
  const tagEl    = document.getElementById('signal-tag');
  const confEl   = document.getElementById('signal-confidence');
  const reasonEl = document.getElementById('bot-reasoning');

  if (priceEl)  priceEl.textContent = `$${sig.price}`;
  if (changeEl) {
    const sign = sig.positive ? '+' : '';
    changeEl.textContent = `${sign}${sig.change}%`;
    changeEl.className = 'bot-change ' + (sig.positive ? 'up' : 'down');
  }

  if (tagEl) {
    const labels = {
      BUY:  { fr: 'ACHAT',  en: 'BUY'  },
      SELL: { fr: 'VENTE',  en: 'SELL' },
      HOLD: { fr: 'ATTENTE', en: 'HOLD' },
    };
    tagEl.textContent = (labels[sig.signal] || {})[lang] || sig.signal;
    tagEl.className = 'signal-tag';
    if (sig.signal === 'SELL') tagEl.classList.add('signal-tag--sell');
    if (sig.signal === 'HOLD') tagEl.classList.add('signal-tag--hold');
  }

  if (confEl) {
    confEl.textContent = t(`Confiance : ${sig.confidence}%`, `Confidence: ${sig.confidence}%`);
  }
  if (reasonEl) reasonEl.textContent = sig.reasoning || '';
}

/* =============================================
   NEWS
   ============================================= */
async function loadNews() {
  try {
    const res = await fetch(`/api/news/?lang=${lang}`);
    const { articles } = await res.json();
    allArticles = articles || [];

    if (allArticles.length) {
      renderFeatured(allArticles[0]);
      renderGrid(allArticles.slice(1));
      buildFilters(allArticles);
    }
  } catch (e) {
    console.warn('[TerraPulse] news error', e);
  }
}

function renderFeatured(a) {
  if (!a) return;
  const container = document.getElementById('featured');
  const img = a.image || PLACEHOLDER;
  container.innerHTML = `
    <a href="${esc(a.url || '#')}" target="_blank" rel="noopener" class="featured-card">
      <img class="featured-card__img" src="${esc(img)}" alt="${esc(a.title)}"
           onerror="this.src='${PLACEHOLDER}'">
      <div class="featured-card__overlay"></div>
      <div class="featured-card__body">
        <span class="featured-card__tag">${esc(a.category)}</span>
        <h2 class="featured-card__title">${esc(a.title)}</h2>
        <div class="featured-card__meta">
          <span>${esc(a.source)}</span><span>·</span><span>${esc(a.time)}</span>
        </div>
      </div>
    </a>`;
}

function renderGrid(articles) {
  const grid = document.getElementById('grid');
  if (!grid) return;
  if (!articles.length) { grid.innerHTML = `<p style="color:var(--gray-400)">${t('Aucun article','No articles found')}</p>`; return; }

  grid.innerHTML = articles.map(a => {
    const img = a.image || PLACEHOLDER;
    return `
      <a href="${esc(a.url||'#')}" target="_blank" rel="noopener" class="article-card">
        <div class="article-card__img-wrap">
          <img class="article-card__img" src="${esc(img)}" alt="${esc(a.title)}"
               onerror="this.src='${PLACEHOLDER}'">
        </div>
        <div class="article-card__body">
          <span class="article-card__tag">${esc(a.category)}</span>
          <h3 class="article-card__title">${esc(a.title)}</h3>
          <div class="article-card__meta">
            <span class="article-card__source">${esc(a.source)}</span>
            <span>${esc(a.time)}</span>
          </div>
        </div>
      </a>`;
  }).join('');
}

function buildFilters(articles) {
  const bar = document.getElementById('filter-bar');
  if (!bar) return;
  bar.removeAttribute('hidden');

  const cats = ['all', ...new Set(articles.map(a => a.category))];
  bar.innerHTML = cats.map((c, i) => {
    const lbl = c === 'all' ? t('Tous', 'All') : c;
    return `<button class="filter-btn${i===0?' active':''}" data-cat="${c}">${esc(lbl)}</button>`;
  }).join('');

  bar.addEventListener('click', e => {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    bar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterArticles(btn.dataset.cat);
  });
}

function filterArticles(cat) {
  const filtered = cat === 'all' ? allArticles.slice(1) : allArticles.filter(a => a.category === cat);
  renderGrid(filtered);
}

/* =============================================
   SIDEBAR NAV
   ============================================= */
function setupNav() {
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      const cat = link.dataset.category;
      if (cat === 'all') {
        renderFeatured(allArticles[0]);
        renderGrid(allArticles.slice(1));
      } else {
        const f = allArticles.filter(a => a.category === cat);
        if (f.length) renderFeatured(f[0]);
        renderGrid(f.slice(1));
      }
    });
  });
}

/* =============================================
   STOCK SELECTOR
   ============================================= */
function setupStockSelect() {
  const sel = document.getElementById('stock-select');
  if (!sel) return;
  sel.addEventListener('change', async () => {
    currentTicker = sel.value;
    const sig = allSignals.find(s => s.ticker === currentTicker);
    if (sig) updateBotDisplay(sig);
    await loadChart(currentTicker);
  });
}

/* =============================================
   SEARCH
   ============================================= */
function setupSearch() {
  const input = document.getElementById('search-input');
  if (!input) return;
  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      const q = input.value.trim().toLowerCase();
      if (!q) { renderFeatured(allArticles[0]); renderGrid(allArticles.slice(1)); return; }
      const f = allArticles.filter(a =>
        a.title.toLowerCase().includes(q) ||
        (a.category||'').toLowerCase().includes(q) ||
        (a.source||'').toLowerCase().includes(q)
      );
      if (f.length) renderFeatured(f[0]);
      renderGrid(f.slice(1));
    }, 280);
  });
}

/* =============================================
   MOBILE MENU
   ============================================= */
function setupMenu() {
  const btn = document.getElementById('menu-btn');
  const sidebar = document.getElementById('sidebar');
  if (!btn || !sidebar) return;
  btn.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (!sidebar.contains(e.target) && !btn.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

/* =============================================
   POLLING
   ============================================= */
function startPolling() {
  clearInterval(refreshTimer);
  refreshTimer = setInterval(async () => {
    await loadStocks();
    await loadSignals();
    await loadChart(currentTicker);
  }, 60000);
}

/* =============================================
   UTILS
   ============================================= */
const PLACEHOLDER = 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600&h=400&fit=crop&auto=format';

function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

/* =============================================
   INIT
   ============================================= */
async function init() {
  setupMenu();
  setupNav();
  setupStockSelect();
  setupSearch();

  // First detect geo (sets lang)
  await loadGeo();
  applyLang(lang);

  // Then load content in parallel
  await Promise.all([loadWeather(), loadNews()]);
  await Promise.all([loadStocks(), loadSignals()]);
  await loadChart(currentTicker);

  startPolling();
}

document.addEventListener('DOMContentLoaded', init);
