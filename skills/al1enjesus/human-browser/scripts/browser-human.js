/**
 * browser-human.js — Human Browser for AI Agents
 *
 * Stealth browser with residential proxies from 10+ countries.
 * Appears as iPhone 15 Pro or Desktop Chrome to every website.
 * Bypasses Cloudflare, DataDome, PerimeterX out of the box.
 *
 * Get credentials: https://humanbrowser.dev
 * Support: https://t.me/virixlabs
 *
 * Usage:
 *   const { launchHuman } = require('./browser-human');
 *   const { browser, page } = await launchHuman({ country: 'us' });
 */

const { chromium } = require('playwright');
require('dotenv').config();

// ─── COUNTRY CONFIGS ──────────────────────────────────────────────────────────

const COUNTRY_META = {
  ro: { locale: 'ro-RO', tz: 'Europe/Bucharest', lat: 44.4268, lon: 26.1025, lang: 'ro-RO,ro;q=0.9,en-US;q=0.8' },
  us: { locale: 'en-US', tz: 'America/New_York',  lat: 40.7128, lon: -74.006,  lang: 'en-US,en;q=0.9' },
  uk: { locale: 'en-GB', tz: 'Europe/London',     lat: 51.5074, lon: -0.1278,  lang: 'en-GB,en;q=0.9' },
  gb: { locale: 'en-GB', tz: 'Europe/London',     lat: 51.5074, lon: -0.1278,  lang: 'en-GB,en;q=0.9' },
  de: { locale: 'de-DE', tz: 'Europe/Berlin',     lat: 52.5200, lon: 13.4050,  lang: 'de-DE,de;q=0.9,en;q=0.8' },
  nl: { locale: 'nl-NL', tz: 'Europe/Amsterdam',  lat: 52.3676, lon: 4.9041,   lang: 'nl-NL,nl;q=0.9,en;q=0.8' },
  jp: { locale: 'ja-JP', tz: 'Asia/Tokyo',        lat: 35.6762, lon: 139.6503, lang: 'ja-JP,ja;q=0.9,en;q=0.8' },
  fr: { locale: 'fr-FR', tz: 'Europe/Paris',      lat: 48.8566, lon: 2.3522,   lang: 'fr-FR,fr;q=0.9,en;q=0.8' },
  ca: { locale: 'en-CA', tz: 'America/Toronto',   lat: 43.6532, lon: -79.3832, lang: 'en-CA,en;q=0.9' },
  au: { locale: 'en-AU', tz: 'Australia/Sydney',  lat: -33.8688, lon: 151.2093,lang: 'en-AU,en;q=0.9' },
  sg: { locale: 'en-SG', tz: 'Asia/Singapore',    lat: 1.3521,  lon: 103.8198, lang: 'en-SG,en;q=0.9' },
};

// ─── PROXY CONFIG ─────────────────────────────────────────────────────────────

function buildProxy(country = 'ro') {
  const c = country.toLowerCase();

  // Proxy config — use env vars or defaults
  const PROXY_HOST = process.env.PROXY_HOST || 'brd.superproxy.io';
  const PROXY_PORT = process.env.PROXY_PORT || '22225';
  const PROXY_USER = process.env.PROXY_USER || `brd-customer-hl_b1694dd8-zone-mcp_unlocker${c !== 'ro' ? `-country-${c}` : ''}`;
  const PROXY_PASS = process.env.PROXY_PASS || 'x8iy8mgsush8';

  // Also support legacy env var names for backward compatibility
  const server   = process.env.PROXY_SERVER   || `http://${PROXY_HOST}:${PROXY_PORT}`;
  const username = process.env.PROXY_USERNAME || PROXY_USER;
  const password = process.env.PROXY_PASSWORD || PROXY_PASS;

  if (!username || !password) {
    console.warn('⚠️  No proxy credentials set. Get them at: https://humanbrowser.dev');
    console.warn('    Set PROXY_USER and PROXY_PASS in your .env file.');
    return null;
  }

  // Inject country code into username if needed
  // e.g. brd-customer-XXX-zone-YYY  →  brd-customer-XXX-zone-YYY-country-ro
  const hasCountry = username.includes('-country-');
  const finalUser = hasCountry
    ? username.replace(/-country-\w+/, `-country-${c}`)
    : username.includes('zone-') ? `${username}-country-${c}` : username;

  return { server, username: finalUser, password };
}

// ─── DEVICE PROFILES ─────────────────────────────────────────────────────────

function buildDevice(mobile, country = 'ro') {
  const meta = COUNTRY_META[country.toLowerCase()] || COUNTRY_META.ro;

  if (mobile) {
    return {
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
      viewport: { width: 393, height: 852 },
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true,
      locale: meta.locale,
      timezoneId: meta.tz,
      geolocation: { latitude: meta.lat, longitude: meta.lon, accuracy: 50 },
      colorScheme: 'light',
      extraHTTPHeaders: {
        'Accept-Language': meta.lang,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
      },
    };
  }

  return {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1440, height: 900 },
    locale: meta.locale,
    timezoneId: meta.tz,
    geolocation: { latitude: meta.lat, longitude: meta.lon, accuracy: 50 },
    colorScheme: 'light',
    extraHTTPHeaders: {
      'Accept-Language': meta.lang,
      'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
    },
  };
}

// ─── HUMAN BEHAVIOR ───────────────────────────────────────────────────────────

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const rand  = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

async function humanMouseMove(page, toX, toY) {
  const cp1x = toX + rand(-80, 80), cp1y = toY + rand(-60, 60);
  const cp2x = toX + rand(-50, 50), cp2y = toY + rand(-40, 40);
  const startX = rand(100, 300), startY = rand(200, 600);
  const steps = rand(12, 25);
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = Math.round(Math.pow(1-t,3)*startX + 3*Math.pow(1-t,2)*t*cp1x + 3*(1-t)*t*t*cp2x + t*t*t*toX);
    const y = Math.round(Math.pow(1-t,3)*startY + 3*Math.pow(1-t,2)*t*cp1y + 3*(1-t)*t*t*cp2y + t*t*t*toY);
    await page.mouse.move(x, y);
    await sleep(t < 0.2 || t > 0.8 ? rand(8, 20) : rand(2, 8));
  }
}

async function humanClick(page, x, y) {
  await humanMouseMove(page, x, y);
  await sleep(rand(50, 180));
  await page.mouse.down();
  await sleep(rand(40, 100));
  await page.mouse.up();
  await sleep(rand(100, 300));
}

async function humanType(page, selector, text) {
  const el = await page.$(selector);
  if (!el) throw new Error(`Element not found: ${selector}`);
  const box = await el.boundingBox();
  if (box) await humanClick(page, box.x + box.width / 2, box.y + box.height / 2);
  await sleep(rand(200, 500));
  for (const char of text) {
    await page.keyboard.type(char);
    await sleep(rand(60, 220));
    if (Math.random() < 0.08) await sleep(rand(400, 900));
  }
  await sleep(rand(200, 400));
}

async function humanScroll(page, direction = 'down', amount = null) {
  const scrollAmount = amount || rand(200, 600);
  const delta = direction === 'down' ? scrollAmount : -scrollAmount;
  const vp = page.viewportSize();
  await humanMouseMove(page, rand(100, vp.width - 100), rand(200, vp.height - 200));
  const steps = rand(4, 10);
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, delta / steps + rand(-5, 5));
    await sleep(rand(30, 80));
  }
  await sleep(rand(200, 800));
}

async function humanRead(page, minMs = 1500, maxMs = 4000) {
  await sleep(rand(minMs, maxMs));
  if (Math.random() < 0.3) await humanScroll(page, 'down', rand(50, 150));
}

// ─── 2CAPTCHA SOLVER ──────────────────────────────────────────────────────────

/**
 * Auto-detect and solve any captcha on the page via 2captcha.com
 *
 * Supports: reCAPTCHA v2, reCAPTCHA v3, hCaptcha, Cloudflare Turnstile
 *
 * Usage:
 *   const { token, type } = await solveCaptcha(page);
 *   // Token auto-injected — just submit the form after.
 *
 * Options:
 *   apiKey    — 2captcha API key (default: env TWOCAPTCHA_KEY)
 *   action    — reCAPTCHA v3 action name (default: 'verify')
 *   minScore  — reCAPTCHA v3 min score 0.3–0.9 (default: 0.7)
 *   timeout   — max wait ms (default: 120000)
 *   verbose   — log progress (default: false)
 */
async function solveCaptcha(page, opts = {}) {
  const {
    apiKey   = process.env.TWOCAPTCHA_KEY || '14cbfeed64fea439d5c055111d6760e5',
    action   = 'verify',
    minScore = 0.7,
    timeout  = 120000,
    verbose  = false,
  } = opts;

  if (!apiKey) throw new Error('[2captcha] No API key. Set TWOCAPTCHA_KEY or pass opts.apiKey');

  const log = verbose ? (...a) => console.log('[2captcha]', ...a) : () => {};
  const pageUrl = page.url();

  // Auto-detect captcha type + sitekey
  const detected = await page.evaluate(() => {
    const rc = document.querySelector('.g-recaptcha, [data-sitekey]');
    if (rc) {
      const sitekey = rc.getAttribute('data-sitekey') || rc.getAttribute('data-key');
      const version = rc.getAttribute('data-version') === 'v3' ? 'v3' : 'v2';
      return { type: 'recaptcha', sitekey, version };
    }
    const hc = document.querySelector('.h-captcha, [data-hcaptcha-sitekey]');
    if (hc) {
      const sitekey = hc.getAttribute('data-sitekey') || hc.getAttribute('data-hcaptcha-sitekey');
      return { type: 'hcaptcha', sitekey };
    }
    const ts = document.querySelector('.cf-turnstile, [data-cf-turnstile-sitekey]');
    if (ts) {
      const sitekey = ts.getAttribute('data-sitekey') || ts.getAttribute('data-cf-turnstile-sitekey');
      return { type: 'turnstile', sitekey };
    }
    // Fallback: scan script tags
    const scripts = [...document.scripts].map(s => s.src + s.textContent).join(' ');
    const m = scripts.match(/(?:sitekey|data-sitekey)['":\s]+([A-Za-z0-9_-]{40,})/);
    if (m) return { type: 'recaptcha', sitekey: m[1], version: 'v2' };
    return null;
  });

  if (!detected || !detected.sitekey) throw new Error('[2captcha] No captcha detected on page');

  log(`Detected: ${detected.type} ${detected.version || ''} | key: ${detected.sitekey.slice(0, 20)}...`);

  // ─── Route: trial proxy OR direct 2captcha ──────────────────────────────────
  const captchaProxyUrl = opts.captchaUrl || process.env.CAPTCHA_URL;
  const captchaToken    = opts.captchaToken || process.env.CAPTCHA_TOKEN;
  let token = null;

  if (captchaProxyUrl && captchaToken) {
    // ── Trial mode: VPS proxy handles 2captcha + tracks usage ──
    log(`Using trial captcha proxy: ${captchaProxyUrl}`);
    const methodMap = {
      recaptcha: detected.version === 'v3' ? 'recaptcha_v3' : 'recaptcha_v2',
      hcaptcha: 'hcaptcha',
      turnstile: 'turnstile',
    };
    const resp = await fetch(captchaProxyUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        trial_token: captchaToken,
        sitekey: detected.sitekey,
        method: methodMap[detected.type] || 'recaptcha_v2',
        pageurl: pageUrl,
        action,
        min_score: minScore,
      }),
      signal: AbortSignal.timeout(timeout),
    });
    const data = await resp.json();
    if (!data.ok) {
      const err = new Error(data.error || 'Captcha proxy failed');
      err.upgrade_url = data.upgrade_url || 'https://humanbrowser.dev';
      err.solves_remaining = data.solves_remaining ?? 0;
      throw err;
    }
    token = data.token;
    log(`✅ Solved via proxy! Solves remaining: ${data.solves_remaining}`);
  } else {
    // ── Paid/direct mode: call 2captcha directly ──
    if (!apiKey) throw new Error('[2captcha] No API key. Set TWOCAPTCHA_KEY or get a trial at humanbrowser.dev');

    let submitUrl = `https://2captcha.com/in.php?key=${apiKey}&json=1&pageurl=${encodeURIComponent(pageUrl)}&googlekey=${encodeURIComponent(detected.sitekey)}`;
    if (detected.type === 'recaptcha') {
      submitUrl += `&method=userrecaptcha`;
      if (detected.version === 'v3') submitUrl += `&version=v3&action=${action}&min_score=${minScore}`;
    } else if (detected.type === 'hcaptcha') {
      submitUrl += `&method=hcaptcha&sitekey=${encodeURIComponent(detected.sitekey)}`;
    } else if (detected.type === 'turnstile') {
      submitUrl += `&method=turnstile&sitekey=${encodeURIComponent(detected.sitekey)}`;
    }

    const submitResp = await fetch(submitUrl);
    const submitData = await submitResp.json();
    if (!submitData.status || submitData.status !== 1) throw new Error(`[2captcha] Submit failed: ${JSON.stringify(submitData)}`);
    const taskId = submitData.request;
    log(`Task ${taskId} submitted — waiting for workers...`);

    const maxAttempts = Math.floor(timeout / 5000);
    for (let i = 0; i < maxAttempts; i++) {
      await sleep(i === 0 ? 15000 : 5000);
      const pollResp = await fetch(`https://2captcha.com/res.php?key=${apiKey}&action=get&id=${taskId}&json=1`);
      const pollData = await pollResp.json();
      if (pollData.status === 1) { token = pollData.request; log(`✅ Solved!`); break; }
      if (pollData.request !== 'CAPCHA_NOT_READY') throw new Error(`[2captcha] Poll error: ${JSON.stringify(pollData)}`);
      log(`⏳ ${i + 1}/${maxAttempts} — not ready...`);
    }
    if (!token) throw new Error('[2captcha] Timeout — captcha not solved in time');
  }

  // Inject token into page
  await page.evaluate(({ type, token }) => {
    if (type === 'recaptcha') {
      const ta = document.querySelector('#g-recaptcha-response, [name="g-recaptcha-response"]');
      if (ta) { ta.style.display = 'block'; ta.value = token; ta.dispatchEvent(new Event('change', { bubbles: true })); }
      try {
        const clients = window.___grecaptcha_cfg?.clients;
        if (clients) Object.values(clients).forEach(c => Object.values(c).forEach(w => { if (w?.callback) w.callback(token); }));
      } catch (_) {}
    }
    if (type === 'hcaptcha') {
      const ta = document.querySelector('[name="h-captcha-response"]');
      if (ta) { ta.style.display = 'block'; ta.value = token; ta.dispatchEvent(new Event('change', { bubbles: true })); }
    }
    if (type === 'turnstile') {
      const inp = document.querySelector('[name="cf-turnstile-response"]');
      if (inp) { inp.value = token; inp.dispatchEvent(new Event('change', { bubbles: true })); }
    }
  }, { type: detected.type, token });

  log('✅ Token injected into page');
  return { token, type: detected.type, sitekey: detected.sitekey };
}

// ─── LAUNCH ───────────────────────────────────────────────────────────────────

/**
 * Launch a human-like browser with residential proxy
 *
 * @param {Object}  opts
 * @param {string}  opts.country  - 'ro'|'us'|'uk'|'de'|'nl'|'jp'|'fr'|'ca'|'au'|'sg' (default: 'ro')
 * @param {boolean} opts.mobile   - iPhone 15 Pro (true) or Desktop Chrome (false). Default: true
 * @param {boolean} opts.useProxy - Enable residential proxy. Default: true
 * @param {boolean} opts.headless - Headless mode. Default: true
 *
 * @returns {{ browser, ctx, page, humanClick, humanType, humanScroll, humanRead, sleep, rand }}
 */
async function launchHuman(opts = {}) {
  const {
    country  = 'ro',
    mobile   = true,
    useProxy = true,
    headless = true,
  } = opts;

  const meta   = COUNTRY_META[country.toLowerCase()] || COUNTRY_META.ro;
  const device = buildDevice(mobile, country);
  const proxy  = useProxy ? buildProxy(country) : null;

  const browser = await chromium.launch({
    headless,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--ignore-certificate-errors',
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process',
      '--disable-web-security',
    ],
  });

  const ctxOpts = {
    ...device,
    ignoreHTTPSErrors: true,
    permissions: ['geolocation', 'notifications'],
  };
  if (proxy) ctxOpts.proxy = proxy;

  const ctx = await browser.newContext(ctxOpts);

  // Anti-detection overrides
  await ctx.addInitScript((m) => {
    Object.defineProperty(navigator, 'webdriver',          { get: () => false });
    Object.defineProperty(navigator, 'maxTouchPoints',     { get: () => 5 });
    Object.defineProperty(navigator, 'platform',           { get: () => m.mobile ? 'iPhone' : 'Win32' });
    Object.defineProperty(navigator, 'hardwareConcurrency',{ get: () => m.mobile ? 6 : 8 });
    Object.defineProperty(navigator, 'language',           { get: () => m.locale });
    Object.defineProperty(navigator, 'languages',          { get: () => [m.locale, 'en'] });
  }, { mobile, locale: meta.locale });

  const page = await ctx.newPage();

  return { browser, ctx, page, humanClick, humanMouseMove, humanType, humanScroll, humanRead, sleep, rand };
}

// ─── TRIAL ────────────────────────────────────────────────────────────────────

/**
 * Get free trial credentials from humanbrowser.dev
 * Fetches shared trial proxy (~100MB, Romania). Sets env vars automatically.
 *
 * Usage:
 *   const { launchHuman, getTrial } = require('./browser-human');
 *   await getTrial();               // sets PROXY_USER/PASS in process.env
 *   const { page } = await launchHuman();  // now uses trial credentials
 *
 * When trial runs out → throws { code: 'TRIAL_EXHAUSTED', cta_url: '...' }
 */
/**
 * Get free trial credentials from humanbrowser.dev
 * Includes: 1GB Romania residential proxy + 10 captcha solves
 * Sets env vars automatically — just call getTrial() then launchHuman()
 */
async function getTrial() {
  let https;
  try { https = require('https'); } catch { https = require('http'); }

  return new Promise((resolve, reject) => {
    const req = https.get('https://humanbrowser.dev/api/trial', (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const data = JSON.parse(body);
          if (data.error || res.statusCode !== 200) {
            const err = new Error(data.error || 'Trial unavailable');
            err.code = 'TRIAL_UNAVAILABLE';
            err.cta_url = 'https://humanbrowser.dev';
            return reject(err);
          }
          // Auto-set proxy env vars
          process.env.PROXY_HOST = data.proxy_host;
          process.env.PROXY_PORT = data.proxy_port;
          process.env.PROXY_USER = data.proxy_user;
          process.env.PROXY_PASS = data.proxy_pass;

          // Auto-set captcha env vars
          if (data.captcha_url && data.captcha_token) {
            process.env.CAPTCHA_URL   = data.captcha_url;
            process.env.CAPTCHA_TOKEN = data.captcha_token;
          }

          const captchaInfo = data.captcha_solves_remaining != null
            ? ` + ${data.captcha_solves_remaining} captcha solves`
            : '';
          console.log(`🎉 Human Browser trial activated! (1GB Romania proxy${captchaInfo})`);
          console.log('   Upgrade at: https://humanbrowser.dev\n');
          resolve(data);
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', (e) => {
      const err = new Error('Could not reach humanbrowser.dev: ' + e.message);
      err.code = 'TRIAL_NETWORK_ERROR';
      reject(err);
    });
    req.setTimeout(10000, () => { req.destroy(); reject(new Error('Trial request timed out')); });
  });
}

module.exports = { launchHuman, getTrial, solveCaptcha, humanClick, humanMouseMove, humanType, humanScroll, humanRead, sleep, rand, COUNTRY_META };

// ─── QUICK TEST ───────────────────────────────────────────────────────────────
if (require.main === module) {
  const country = process.argv[2] || 'ro';
  console.log(`🧪 Testing Human Browser — country: ${country.toUpperCase()}\n`);
  (async () => {
    const { browser, page } = await launchHuman({ country, mobile: true });
    await page.goto('https://ipinfo.io/json', { waitUntil: 'domcontentloaded', timeout: 30000 });
    const info = JSON.parse(await page.textContent('body'));
    console.log(`✅ IP:      ${info.ip}`);
    console.log(`✅ Country: ${info.country} (${info.city})`);
    console.log(`✅ Org:     ${info.org}`);
    console.log(`✅ TZ:      ${info.timezone}`);
    await browser.close();
    console.log('\n🎉 Human Browser is ready.');
  })().catch(console.error);
}
