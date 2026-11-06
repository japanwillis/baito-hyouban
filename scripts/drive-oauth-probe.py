"""OAuth check and reversible Drive API upload/download test. No token logging."""
import hashlib
import io
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

FOLDER_ID = "1iaRf8yRxkpHnx4LSOgMDzo3U4LwmPYnV"

def main():
    keys = ("GOOGLE_DRIVE_CLIENT_ID", "GOOGLE_DRIVE_CLIENT_SECRET", "GOOGLE_DRIVE_REFRESH_TOKEN")
    missing = [key for key in keys if not os.environ.get(key)]
    if missing:
        raise RuntimeError("Missing GitHub secret names: " + ", ".join(missing))
    creds = Credentials(
        token=None, refresh_token=os.environ[keys[2]],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ[keys[0]], client_secret=os.environ[keys[1]],
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    creds.refresh(Request())
    print("OAuth refresh: SUCCESS")
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    # Existing folder may not be accessible to drive.file; root upload is supported.
    try:
        service.files().get(fileId=FOLDER_ID, fields="id,name").execute()
        print("Existing folder direct access: SUCCESS")
    except Exception:
        print("Existing folder direct access: unavailable with drive.file")
    data = b"baito-hyouban drive api upload verification v1\n"
    file_id = None
    try:
        media = MediaIoBaseUpload(io.BytesIO(data), mimetype="text/plain", resumable=False)
        created = service.files().create(
            body={"name":"baito-drive-api-connection-test.txt","mimeType":"text/plain"},
            media_body=media, fields="id").execute()
        file_id = created["id"]
        meta = service.files().get(fileId=file_id, fields="id,name,size,mimeType").execute()
        if meta.get("name") != "baito-drive-api-connection-test.txt" or int(meta.get("size",-1)) != len(data):
            raise RuntimeError("Test upload metadata mismatch")
        out = io.BytesIO()
        reader = MediaIoBaseDownload(out, service.files().get_media(fileId=file_id))
        done = False
        while not done:
            _, done = reader.next_chunk()
        if hashlib.sha256(out.getvalue()).digest() != hashlib.sha256(data).digest():
            raise RuntimeError("Test read-back digest mismatch")
        print("Drive API create/read-back: SUCCESS")
    finally:
        if file_id:
            service.files().delete(fileId=file_id).execute()
            print("Temporary test file removed: SUCCESS")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Drive OAuth API test failed:",type(e).__name__,file=sys.stderr)
        sys.exit(1)
