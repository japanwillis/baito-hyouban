import hashlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_controller", BASE / "scripts/release-controller.py")
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)

class Response(io.BytesIO):
    status = 200

class FixedOpener:
    def __init__(self, html):
        self.html = html
    def open(self, request, timeout=30):
        assert request.full_url == "https://baito-hyouban.com/guide/first-part-time-job/"
        return Response(self.html)

class ProtectedHtmlPreservationTests(unittest.TestCase):
    def test_live_bytes_replace_generated_only_in_release_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "guide/first-part-time-job/index.html"
            target.parent.mkdir(parents=True)
            target.write_text("<html><body>Generated with new css</body></html>")
            live = b"<html><body>" + b"Previously published verified article " * 24 + b"</body></html>"
            with patch.object(controller.urllib.request, "build_opener", return_value=FixedOpener(live)):
                digest = controller.preserve_bh0001_live_html(root)
            self.assertEqual(target.read_bytes(), live)
            self.assertEqual(digest, hashlib.sha256(live).hexdigest())

    def test_invalid_live_page_does_not_overwrite_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "guide/first-part-time-job/index.html"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"candidate")
            with patch.object(controller.urllib.request, "build_opener", return_value=FixedOpener(b"error")):
                with self.assertRaisesRegex(ValueError, "Unexpected protected"):
                    controller.preserve_bh0001_live_html(root)
            self.assertEqual(target.read_bytes(), b"candidate")

if __name__ == "__main__":
    unittest.main()
