// Read-only responsive QA for the newest approved article; local preview by default.
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE_PATH).href);
const canonicalOrigin = 'https://baito-hyouban.com';
const origin = process.env.QA_ORIGIN || 'http://127.0.0.1:4321';
if (!['http://127.0.0.1:4321', canonicalOrigin].includes(origin)) throw Error('Unapproved QA origin');
const approvals = JSON.parse(await readFile('ops/publication-approvals.json', 'utf8'));
const articlePath = approvals.articles.at(-1).publicPath;
const out = 'responsive-qa-evidence';
await mkdir(out, { recursive: true });
const browser = await chromium.launch();
const results = [];
try {
  for (const width of [320, 390, 768, 1366]) {
    const context = await browser.newContext({ viewport: { width, height: 844 },
      isMobile: width < 800, hasTouch: width < 800, deviceScaleFactor: 1, locale: 'ja-JP' });
    await context.route('**/*', route => {
      const url = new URL(route.request().url());
      return url.origin === origin ? route.continue() : route.abort();
    });
    const page = await context.newPage();
    for (const [label, path] of [['home', '/'], ['guide', '/guide/'], ['article', articlePath]]) {
      const response = await page.goto(origin + path, { waitUntil: 'networkidle', timeout: 45000 });
      await page.evaluate(async () => { await document.fonts.ready; });
      await page.locator('footer').scrollIntoViewIfNeeded();
      await page.waitForFunction(() => [...document.images].every(img => img.complete && img.naturalWidth > 0));
      await page.evaluate(() => window.scrollTo(0, 0));
      const metrics = await page.evaluate(() => ({
        width: innerWidth, clientWidth: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth, h1: document.querySelectorAll('h1').length,
        canonical: document.querySelector('link[rel=canonical]')?.href,
        description: document.querySelector('meta[name=description]')?.content,
        images: [...document.images].map(img => ({ loaded: img.complete && img.naturalWidth > 0,
          width: img.naturalWidth, height: img.naturalHeight })),
        heroColumns: document.querySelector('.hero') ? getComputedStyle(document.querySelector('.hero')).gridTemplateColumns : null,
        articleColumns: document.querySelector('.feature-article') ? getComputedStyle(document.querySelector('.feature-article')).gridTemplateColumns : null,
      }));
      const screenshot = `${label}-${width}.png`;
      await page.screenshot({ path: `${out}/${screenshot}`, fullPage: true });
      const errors = [];
      if (response.status() !== 200) errors.push(`HTTP ${response.status()}`);
      if (metrics.width !== width) errors.push('Viewport differs from requested width');
      if (metrics.scrollWidth > metrics.clientWidth + 1) errors.push('Horizontal overflow');
      if (metrics.h1 !== 1 || metrics.canonical !== canonicalOrigin + path || !metrics.description) errors.push('Page metadata/heading mismatch');
      if (!metrics.images.every(x => x.loaded && x.width > 0)) errors.push('Image did not load');
      results.push({ label, path, width, screenshot, metrics, errors });
    }
    await page.goto(origin + '/', { waitUntil: 'networkidle' });
    await page.locator(`a.feature-article[href="${articlePath}"]`).click();
    await page.waitForURL(origin + articlePath);
    results.push({ label: 'home-to-article-navigation', width, errors: [] });
    await context.close();
  }
} finally {
  await browser.close();
  await writeFile(`${out}/results.json`, JSON.stringify({ checkedAt: new Date().toISOString(),
    environment: 'GitHub Actions Chromium; viewport/touch emulation, not physical iPhone/Safari',
    origin, productionModified: false, results }, null, 2));
}
const failed = results.filter(x => x.errors.length);
console.log(JSON.stringify({ checks: results.length, failed: failed.length, results }, null, 2));
if (failed.length || results.length !== 16) process.exitCode = 1;
