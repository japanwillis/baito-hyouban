# Google Drive API image delivery (verified integration)

## Verified on 2026-11-06

- The three OAuth credentials are configured in GitHub Actions Secrets. Do not print or store their values in files.
- GitHub Actions successfully refreshed the OAuth access token.
- With `drive.file`, the OAuth app **cannot directly access** the existing project's image folder.
- A disposable WebP from the repository was uploaded via Google Drive API, downloaded, SHA256-verified, and cleaned up.
- A separate disposable API-uploaded WebP was successfully moved into the existing image folder by the connected Google Drive integration and then deleted. This confirms both halves of the two-step workflow.
- CI run: https://github.com/japanwillis/baito-hyouban/actions/runs/42146061139
- Cross-connector move test run: https://github.com/japanwillis/baito-hyouban/actions/runs/42146342767
- Destination folder: https://drive.google.com/drive/folders/1iaRf8yRxkpHnx4LSOgMDzo3U4LwmPYnV

## Actual delivery flow

1. Image Work generates and validates the actual `BH-####-eyecatch.webp` file. Keep the original bytes and SHA256.
2. Stage the **actual binary** in the private GitHub repository under `ops/image-staging/BH-####-eyecatch.webp`. For GitHub connector writes, the `create_blob` API accepts base64 binary; then add that blob via a tree/commit/ref update, or use a supported cloud-computer file upload. A local `/mnt/data` path by itself is NOT a valid GitHub file upload and is NOT a connector file URI.
3. Create `ops/drive-image-upload-request.json` in the same release or a later commit. Example:
```json
{"schema_version":1,"request_id":"bh0013image01","article_id":"BH-0013","sha256":"<actual 64-character SHA256 of WebP>"}
```
4. Pushing either staged media or the request triggers `.github/workflows/drive-image-upload.yml`. The OAuth probe and WebP smoke test run, and if the request exists, the `scripts/drive-image-runner.py` script uploads the staged image to the OAuth app's Drive root. It never alters Xserver.
5. Require the GitHub Actions upload step to succeed and read its `drive-upload-evidence/result.json` receipt. Check `verified: true`, article ID, SHA256, Drive file ID and URL. This means API upload+readback succeeded **but the folder move is still pending**.
6. Using the existing connected Google Drive tool, call `get_file_metadata` for the Drive file ID to get its current parent ID. Use `update_file(fileId, addParents=<image folder ID>, removeParents=<current parent ID>)` to move the file into the target folder. It should keep the same ID. No new OAuth permission is required.
7. Re-read metadata to verify the name, MIME, byte size and folder ID, and if possible fetch the file to verify SHA256 again. Only now update article management sheet E/H with the completed image and URL.
8. Existing filename with different bytes, unauthorized parent move, duplicate processing, or incomplete API run => mark as pending, do not overwrite and do not publish.

## Security and limitations

- Never commit tokens, client secrets or OAuth JSON; only names of secrets appear in workflows.
- Keep `drive.file` scope rather than granting full Drive permissions.
- Each request must carry a verifiable file digest, and a real binary file must be staged. **This binary handoff is not yet automated for Image Work**, and can still require a supported Work upload action. Do not claim full end-to-end unattended image delivery until it has been proven with an actual newly generated image.
- The GitHub tool `create_file` accepts UTF-8 text only; it cannot upload WebP raw bytes. For binaries use `create_blob` (base64) or a supported cloud-computer file upload.
- Images are not publicly deployed until editorial and image approval are complete. No changes to publication workflow permissions.
