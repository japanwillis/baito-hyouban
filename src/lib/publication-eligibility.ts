import approvals from '../../ops/publication-approvals.json';

// Registered source/image records drive discovery, not editorial approval labels.
// The content gate independently enforces artifact identity and safe routes.
const registeredIds = new Set(approvals.articles.map(a => a.articleId));
export function isPublicArticle(frontmatter: { articleId?: string }) {
  return registeredIds.has(frontmatter.articleId || '');
}
