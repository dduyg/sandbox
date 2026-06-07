"""
ARCV Ingestion Script
Watches a folder, uploads images to Cloudflare R2,
labels them with Claude Vision, saves metadata to Supabase.

Usage:
    python ingest.py                      # process ./images_to_upload folder
    python ingest.py /path/to/my/folder  # process a custom folder
"""

import os
import sys
import json
import base64
import mimetypes
from pathlib import Path

import boto3
import anthropic
from supabase import create_client
from PIL import Image


# ═══════════════════════════════════════════════════════════════
#  STEP 1 — PASTE YOUR CREDENTIALS HERE
# ═══════════════════════════════════════════════════════════════

SUPABASE_URL      = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_KEY      = "YOUR_SUPABASE_ANON_KEY"

R2_ACCOUNT_ID     = "YOUR_CLOUDFLARE_ACCOUNT_ID"
R2_ACCESS_KEY_ID  = "YOUR_R2_ACCESS_KEY_ID"
R2_SECRET_KEY     = "YOUR_R2_SECRET_ACCESS_KEY"
R2_BUCKET_NAME    = "YOUR_BUCKET_NAME"
R2_PUBLIC_URL     = "https://pub-XXXX.r2.dev"   # your R2 public domain (no trailing slash)

# Your Anthropic API key — set as env var OR paste here
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")

# ═══════════════════════════════════════════════════════════════


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}


def build_clients():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    r2 = boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
    )

    claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    return supabase, r2, claude


def upload_to_r2(r2_client, file_path: Path) -> tuple[str, str]:
    """
    Upload image to R2. Returns (full_url, thumb_url).
    Thumb is the same URL — R2 Image Resizing can be added later.
    """
    key = f"images/{file_path.name}"
    content_type = mimetypes.guess_type(str(file_path))[0] or "image/jpeg"

    print(f"    Uploading to R2 as '{key}'...")
    r2_client.upload_file(
        str(file_path),
        R2_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type},
    )

    url = f"{R2_PUBLIC_URL}/{key}"
    return url, url  # thumb_url = url for now


def get_image_metadata(file_path: Path) -> dict:
    """Extract width, height, file size."""
    with Image.open(file_path) as img:
        w, h = img.size
    size_bytes = file_path.stat().st_size
    size_mb = round(size_bytes / 1_000_000, 1)
    return {
        "dims": f"{w}×{h}",
        "size": f"{size_mb} MB",
    }


def label_with_claude(claude_client, file_path: Path) -> dict:
    """
    Send image to Claude Vision.
    Returns {"caption": "...", "tags": ["tag1", "tag2", ...]}
    """
    with open(file_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    media_type = mimetypes.guess_type(str(file_path))[0] or "image/jpeg"

    print("    Sending to Claude Vision for labeling...")
    response = claude_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image carefully and respond ONLY with valid JSON "
                            "in exactly this format, with no markdown, no explanation:\n"
                            '{"caption": "one clear descriptive sentence about the image", '
                            '"tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]}\n\n'
                            "Tags must be specific, searchable single words or short phrases "
                            "that describe objects, colors, themes, style, and subject matter."
                        ),
                    },
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip any accidental markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def already_ingested(supabase_client, filename: str) -> bool:
    """Return True if this filename is already in the database."""
    result = (
        supabase_client.table("images")
        .select("id")
        .eq("filename", filename)
        .execute()
    )
    return len(result.data) > 0


def process_folder(folder_path: str):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder}")
        sys.exit(1)

    files = [f for f in folder.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not files:
        print(f"No supported images found in {folder}")
        print(f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        return

    print(f"\n{'═'*55}")
    print(f"  ARCV Ingestion Pipeline")
    print(f"  Folder : {folder.resolve()}")
    print(f"  Images : {len(files)} found")
    print(f"{'═'*55}\n")

    supabase, r2, claude = build_clients()

    success = 0
    skipped = 0
    failed  = 0

    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {file_path.name}")

        if already_ingested(supabase, file_path.name):
            print("    ⏭  Already in database, skipping\n")
            skipped += 1
            continue

        try:
            # 1. Upload to Cloudflare R2
            url, thumb_url = upload_to_r2(r2, file_path)

            # 2. Get image dimensions + size
            meta = get_image_metadata(file_path)

            # 3. Label with Claude Vision
            labels = label_with_claude(claude, file_path)

            # 4. Save record to Supabase
            print("    Saving to Supabase...")
            supabase.table("images").insert({
                "filename":  file_path.name,
                "url":       url,
                "thumb_url": thumb_url,
                "caption":   labels["caption"],
                "tags":      labels["tags"],
                "dims":      meta["dims"],
                "size":      meta["size"],
            }).execute()

            print(f"    ✅ Done — {labels['caption'][:70]}")
            print(f"    Tags: {', '.join(labels['tags'])}\n")
            success += 1

        except json.JSONDecodeError as e:
            print(f"    ❌ Claude returned invalid JSON: {e}\n")
            failed += 1
        except Exception as e:
            print(f"    ❌ Error: {e}\n")
            failed += 1

    print(f"{'═'*55}")
    print(f"  Done! ✅ {success} ingested · ⏭ {skipped} skipped · ❌ {failed} failed")
    print(f"{'═'*55}\n")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "./images_to_upload"
    process_folder(folder)
