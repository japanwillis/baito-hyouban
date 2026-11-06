"""Run the Drive image uploader from a trusted CI environment."""
import json
import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    from importlib.machinery import SourceFileLoader
    mod = SourceFileLoader("image_validation","scripts/drive-image-validation.py").load_module()
    request = json.loads(Path("ops/drive-image-upload-request.json").read_text())
    if set(request) != {"schema_version", "request_id", "article_id", "sha256"} or request.get("schema_version") != 1:
        raise ValueError("Invalid upload request fields")
    import re
    if not isinstance(request.get("request_id"),str) or not re.fullmatch(r"[A-Za-z0-9_-]{8,80}",request["request_id"]):
        raise ValueError("Invalid request ID")
    article_id, digest = request["article_id"], request["sha256"]
    credentials = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_DRIVE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_DRIVE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    credentials.refresh(Request())
    service = build("drive","v3",credentials=credentials,cache_discovery=False)
    evidence = mod.upload_and_verify(service,article_id,digest)
    Path("drive-upload-evidence").mkdir(exist_ok=True)
    Path("drive-upload-evidence/result.json").write_text(json.dumps(evidence,indent=2))
    print("Pending Drive folder move:", evidence["needs_move_to_folder"])
    print("Verified Google Drive upload:", evidence["article_id"], evidence["url"])

if __name__=="__main__":
    try:
        main()
    except ValueError as error:
        print("Drive upload validation failed:", str(error), file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print("Drive upload failed:",type(error).__name__,file=sys.stderr)
        sys.exit(1)
