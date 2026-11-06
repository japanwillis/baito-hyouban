"""Validate image payload and upload it to the project's Google Drive folder."""
import hashlib
import io
import json
from pathlib import Path

FOLDER_ID = "1iaRf8yRxkpHnx4LSOgMDzo3U4LwmPYnV"

def validate(article_id, expected_sha256):
    path = Path("ops/image-staging") / (article_id + "-eyecatch.webp")
    if not path.is_file() or path.is_symlink():
        raise ValueError("Image not staged")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("Image digest mismatch")
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("Not WebP")
    from PIL import Image
    with Image.open(io.BytesIO(data)) as im:
        if im.format != "WEBP" or im.size != (1200, 630):
            raise ValueError("Image must be 1200x630 WebP")
        im.verify()
    return path, data

def upload_and_verify(service, article_id, sha256):
    """Existing same-name file is reused only on exact byte match."""
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    path, data = validate(article_id, sha256)
    name = path.name
    query = "'" + FOLDER_ID + "' in parents and name = '" + name + "' and trashed = false"
    existing = service.files().list(q=query, fields="nextPageToken,files(id,name,mimeType,size,md5Checksum,parents)",pageSize=100).execute()
    if existing.get("nextPageToken") or len(existing["files"]) > 1:
        raise ValueError("Duplicate filename in Google Drive")
    if existing["files"]:
        file_id = existing["files"][0]["id"]
    else:
        body = {"name": name, "mimeType": "image/webp", "parents": [FOLDER_ID]}
        media = MediaFileUpload(str(path), mimetype="image/webp", resumable=True)
        file_id = service.files().create(body=body, media_body=media, fields="id").execute()["id"]
    meta = service.files().get(fileId=file_id,fields="id,name,mimeType,size,md5Checksum,parents").execute()
    if (meta["name"] != name or meta["mimeType"] != "image/webp" or
        FOLDER_ID not in meta.get("parents",[]) or
        int(meta["size"]) != len(data) or
        meta["md5Checksum"] != hashlib.md5(data).hexdigest()):
        raise ValueError("Google Drive metadata mismatch")
    dest = io.BytesIO()
    reader = MediaIoBaseDownload(dest, service.files().get_media(fileId=file_id))
    done = False
    while not done:
        _, done = reader.next_chunk()
    if hashlib.sha256(dest.getvalue()).hexdigest() != sha256:
        raise ValueError("Downloaded image digest mismatch")
    return {"article_id":article_id, "id":file_id, "url":"https://drive.google.com/file/d/"+file_id+"/view", "sha256":sha256, "verified":True}
