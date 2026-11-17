"""Regression coverage for production notes leaking into approved articles."""
import subprocess
import unittest
from pathlib import Path

class EditorialNotesTests(unittest.TestCase):
    def test_source_and_rendered_notes_are_rejected(self):
        script = r'''
import { assertNoEditorialNotes as check } from './scripts/editorial-notes.mjs';
const bad = [
  '【本文中に置く関連内部リンク候補（IDのみ）】',
  '公開担当がURLを確認してください。',
  '公開・運営Workへの申し送り',
  '詳細はBH-0003へつなぎます。',
  '公開前に再確認すること。',
  '制作管理台帳のURLのみ使用',
];
for (const note of bad) {
  for (const html of [false, true]) {
    let rejected = false;
    try { check(html ? `<p>${note}</p>` : `---\narticleId: "BH-0003"\n---\n${note}`, 'fixture', {html}); }
    catch { rejected = true; }
    if (!rejected) throw Error(`Accepted editorial note: ${note}`);
  }
}
check('---\narticleId: "BH-0003"\n---\n勤務の申し送りは店長に確認しましょう。応募前に条件を確認してください。', 'valid');
check('<p>最新の募集条件は応募先に確認してください。</p>', 'valid.html', {html: true});
'''
        subprocess.run(['node', '--input-type=module', '-e', script], cwd=Path(__file__).resolve().parents[1], check=True)
