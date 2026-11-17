"""Prevent internal BH article IDs from being rendered in reader-facing headers.

The ID remains in Markdown frontmatter and the approval registry for integrity
checks; only the public-facing date line should be shown to readers.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = ("CompanyArticle.astro", "JobArticle.astro")


class PublicMetadataPrivacyTests(unittest.TestCase):
    def test_reader_header_omits_internal_article_id(self):
        for name in LAYOUTS:
            with self.subTest(layout=name):
                html = (ROOT / "src" / "layouts" / name).read_text(encoding="utf-8")
                self.assertIn("情報確認日：{frontmatter.checkedDate}", html)
                self.assertNotIn("記事ID：", html)
                self.assertNotIn("{frontmatter.articleId}", html)

    def test_date_label_and_hero_alt_remain_present(self):
        for name in LAYOUTS:
            with self.subTest(layout=name):
                html = (ROOT / "src" / "layouts" / name).read_text(encoding="utf-8")
                self.assertIn("情報確認日：{frontmatter.checkedDate}", html)
                self.assertIn("alt={frontmatter.imageAlt}", html)


if __name__ == "__main__":
    unittest.main()
