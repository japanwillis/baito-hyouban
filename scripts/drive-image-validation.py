"""Validate staged WebP images before Google Drive upload."""
import hashlib
import json
from pathlib import Path

def load_staged_image(article_id, expected_sha256):
    path = Path("ops/image-staging") / (article_id + "-eyecatch.webp")
    if not path.is_file() or path.is_symlink():
        raise ValueError("Image not staged")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("Image digest mismatch")
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("Not WebP")
    return data
