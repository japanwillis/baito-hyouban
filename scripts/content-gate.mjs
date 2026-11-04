import { readdirSync, readFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, relative } from 'node:path';

const root = resolve(process.argv[2] || '.');
const sha = path => createHash('sha256').update(readFileSync(resolve(root, path))).digest('hex');
const approvals = JSON.parse(readFileSync(resolve(root, 'ops/publication-approvals.json')));
function walk(dir) {
  return readdirSync(resolve(root, dir), { withFileTypes: true }).flatMap(e => {
    const p = `${dir}/${e.name}`;
    if (e.isSymbolicLink()) throw Error(`Symlink refused: ${p}`);
    return e.isDirectory() ? walk(p) : [p];
  });
}
const articles = walk('src/pages').filter(p => /\.(md|mdx)$/i.test(p));
const seen = new Set();
for (const path of articles) {
  const a = approvals.articles.find(a => a.sourcePath === path);
  if (!a || seen.has(a.articleId)) throw Error(`No unique approval record: ${path}`);
  seen.add(a.articleId);
  if (!['approved', 'conditionally-approved'].includes(a.editorialStatus) || !a.conditionsResolved || !a.imageVerified || !a.linksVerifiedOn)
    throw Error(`Approval incomplete: ${path}`);
  for (const key of ['manuscriptUrl', 'reviewUrl', 'imageUrl']) {
    if (!/^https:\/\/(docs\.google\.com|drive\.google\.com)\//.test(a[key] || '')) throw Error(`Missing evidence ${key}: ${path}`);
  }
  const text = readFileSync(resolve(root, path), 'utf8');
  // These frontmatter fields are plain scalar lines under this project's authoring convention.
  const field = key => text.match(new RegExp(`^${key}: *([^\\r\\n]+)$`, 'm'))?.[1].trim().replace(/^['"]|['"]$/g, '');
  if (field('articleId') !== a.articleId || field('editorialStatus') !== a.editorialStatus || field('heroImage') !== a.imagePath)
    throw Error(`Frontmatter differs from approval: ${path}`);
  if (sha(path) !== a.sourceSha256 || sha(`public${a.imagePath}`) !== a.imageSha256)
    throw Error(`Approved source/image has changed: ${path}`);
  if (!a.imagePath.startsWith('/images/') || a.imagePath.includes('..') || !/^\/[a-z0-9/-]+\/$/.test(a.publicPath))
    throw Error(`Unsafe path: ${path}`);
  const derived = '/' + relative('src/pages', path).replace(/\.(md|mdx)$/i, '') + '/';
  if (derived !== a.publicPath) throw Error(`Route differs from approval: ${path}`);
}
if (seen.size !== approvals.articles.length) throw Error('Approval records and routes differ');
// No unpublished article image can slip into the public build by itself.
for (const path of walk('public/images')) {
  if (/BH-\d{4}/.test(path) && !approvals.articles.some(a => `public${a.imagePath}` === path)) throw Error(`Unapproved article image: ${path}`);
}
if (process.argv.includes('--dist')) {
  const dist = walk('dist');
  for (const a of approvals.articles) if (!existsSync(resolve(root, `dist${a.publicPath}index.html`))) throw Error(`Missing output ${a.articleId}`);
  const fixed = ['index.html','404.html','about/index.html','advertising/index.html','contact/index.html','editorial-policy/index.html','privacy/index.html','guide/index.html','company/index.html','job/index.html'];
  for (const p of dist.filter(p => p.endsWith('.html'))) if (!fixed.includes(p.slice(5)) && !approvals.articles.some(a => `dist${a.publicPath}index.html` === p)) throw Error(`Unapproved output route ${p}`);
  const images = dist.filter(p => /\/BH-\d{4}/.test(p));
  for (const p of images) if (!approvals.articles.some(a => `dist${a.imagePath}` === p)) throw Error(`Unapproved output image ${p}`);
}
console.log(`Publication gate passed: ${seen.size} approved article(s)`);
