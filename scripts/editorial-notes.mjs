// Reject production instructions in reader-facing article content.
export function assertNoEditorialNotes(text, path, { html = false } = {}) {
  const body = html
    ? text.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '').replace(/<[^>]+>/g, ' ')
    : text.replace(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/, '');
  const forbidden = /(?:公開|編集)[／・]?担当|(?:公開|編集者|公開運営|公開・運営)Work|内部リンク(?:候補|設置|案|先)|リンク設置候補|制作(?:管理)?台帳|企画台帳|公開(?:前|直前|側)|公開用パス|完成稿v\d|初稿v\d|画像ブリーフ|SEOメタ|企画予約|未公開のため|BH-\d{4}/;
  const match = body.match(forbidden);
  if (match) throw Error(`Editorial note in ${path}: ${match[0]}`);
}
