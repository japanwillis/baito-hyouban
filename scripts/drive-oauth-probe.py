"""Read-only OAuth connectivity test. Do not output secret credentials."""
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    keys = ["GOOGLE_DRIVE_CLIENT_ID", "GOOGLE_DRIVE_CLIENT_SECRET", "GOOGLE_DRIVE_REFRESH_TOKEN"]
    missing = [key for key in keys if not os.environ.get(key)]
    if missing:
        raise RuntimeError("Missing GitHub secrets: " + ", ".join(missing))
    credentials = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_DRIVE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_DRIVE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    credentials.refresh(Request())
    print("OAuth refresh: SUCCESS")
    service = build("drive", "v3", credentials=credentials, cache_discovery=False)
    folder = "1iaRf8yRxkpHnx4LSOgMDzo3U4LwmPYnV"
    try:
        meta = service.files().get(fileId=folder,fields="id,name,mimeType").execute()
        if meta.get("mimeType") != "application/vnd.google-apps.folder":
            raise RuntimeError("Target is not a folder")
        print("Target folder access: SUCCESS")
    except Exception:
        print("Target folder access: FAILED; check drive.file authorization",file=sys.stderr)
        raise RuntimeError("Target folder inaccessible with current OAuth scope") from None

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("OAuth probe failed:",type(e).__name__,str(e) if isinstance(e,RuntimeError) else "",file=sys.stderr)
        sys.exit(1)
