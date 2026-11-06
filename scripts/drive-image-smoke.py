"""Exercise WebP API upload/download using a disposable copy of an approved asset."""
import hashlib
import os
import shutil
from pathlib import Path
from importlib.machinery import SourceFileLoader
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    module=SourceFileLoader("drive_validation","scripts/drive-image-validation.py").load_module()
    source=Path("public/images/BH-0001-eyecatch.webp")
    staged=Path("ops/image-staging/BH-0999-eyecatch.webp")
    staged.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,staged)
    digest=hashlib.sha256(staged.read_bytes()).hexdigest()
    credentials=Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_DRIVE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_DRIVE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive.file"])
    credentials.refresh(Request())
    service=build("drive","v3",credentials=credentials,cache_discovery=False)
    file_id=None
    try:
        result=module.upload_and_verify(service,"BH-0999",digest)
        file_id=result["id"]
        print("WebP create/download/hash verification: SUCCESS")
        print("Drive test file ID:", file_id)
    finally:
        # Keep temporary image only for the cross-connector folder-move test.
        # The orchestrator will delete it after verifying move.
        staged.unlink(missing_ok=True)

if __name__=="__main__":
    main()
