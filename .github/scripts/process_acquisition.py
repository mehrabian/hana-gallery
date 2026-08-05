#!/usr/bin/env python3
"""Turn a 'new-acquisition' GitHub issue into an art.json entry + web JPEG."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ART_JSON = ROOT / "art.json"
ART_DIR = ROOT / "art"
ORIG_DIR = ART_DIR / "originals"

MAX_EDGE = 1600
QUALITY = 85
TARGET_MAX_BYTES = 500_000

IMAGE_URL_RE = re.compile(
    r"https://(?:github\.com/user-attachments/assets/[a-zA-Z0-9-]+|"
    r"user-images\.githubusercontent\.com/[^\s)\"]+|"
    r"private-user-images\.githubusercontent\.com/[^\s)\"]+)"
)

SECTION_RE = re.compile(
    r"###\s+(?P<head>[^\n]+)\n+(?P<body>.*?)(?=\n###\s+|\Z)",
    re.DOTALL,
)


class AcquisitionError(Exception):
    pass


def field_map(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in SECTION_RE.finditer(body or ""):
        key = m.group("head").strip().lower()
        val = m.group("body").strip()
        if val.lower() in {"_no response_", "none"}:
            val = ""
        out[key] = val
    return out


def require_fields(fields: dict[str, str]) -> tuple[str, str, str, str, str]:
    title = fields.get("title", "").strip()
    medium = fields.get("medium", "").strip()
    date = fields.get("date", "").strip()
    category = fields.get("category", "").strip()
    note = fields.get("note", "").strip()
    missing = [n for n, v in [("Title", title), ("Medium", medium), ("Date", date), ("Category", category)] if not v]
    if missing:
        raise AcquisitionError("Missing required field(s): " + ", ".join(missing))
    return title, medium, date, category, note


def find_image_url(body: str) -> str:
    text = body or ""
    urls = IMAGE_URL_RE.findall(text)
    if not urls:
        loose = re.findall(
            r"(?:src=[\"']|!\[[^\]]*\]\()(https://[^\"'\s)]+)",
            text,
        )
        urls = [
            u.rstrip(").,;")
            for u in loose
            if "githubusercontent.com" in u or "user-attachments/assets" in u
        ]
    urls = [u.rstrip(").,;") for u in urls]
    if not urls:
        raise AcquisitionError(
            "No image attachment found. Attach exactly one photo to the issue and try again."
        )
    if len(urls) > 1:
        print(f"Multiple images found; using the first of {len(urls)}.", file=sys.stderr)
    return urls[0]


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if not s:
        raise AcquisitionError("Title slug is empty after cleaning; use letters or numbers in the title.")
    return s[:60]


class _StripAuthOnRedirect(urllib.request.HTTPRedirectHandler):
    """GitHub attachment URLs 302 to a signed host; forwarding Auth causes HTTP 400."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req is None:
            return None
        old_host = urlparse(req.full_url).netloc
        new_host = urlparse(newurl).netloc
        if old_host != new_host and new_req.has_header("Authorization"):
            new_req.remove_header("Authorization")
        return new_req


def download(url: str, token: str) -> bytes:
    url = url.rstrip(").,;")
    # curl strips Authorization on cross-host redirects — reliable for user-attachments.
    try:
        proc = subprocess.run(
            [
                "curl",
                "-fsSL",
                "--max-time",
                "120",
                "-H",
                f"Authorization: Bearer {token}",
                "-H",
                "Accept: */*",
                "-H",
                "User-Agent: hana-gallery-acquisition-bot",
                "-o",
                "-",
                url,
            ],
            check=False,
            capture_output=True,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
        curl_err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        print(f"curl download failed ({proc.returncode}): {curl_err}", file=sys.stderr)
    except FileNotFoundError:
        print("curl not available; falling back to urllib", file=sys.stderr)

    opener = urllib.request.build_opener(_StripAuthOnRedirect())
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "*/*",
            "User-Agent": "hana-gallery-acquisition-bot",
        },
    )
    try:
        with opener.open(req, timeout=120) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read()[:300] if e.fp else b""
        raise AcquisitionError(
            f"Failed to download image ({e.code}): {url} — {body!r}"
        ) from e
    if not data:
        raise AcquisitionError("Downloaded image is empty.")
    return data


def save_web_jpeg(raw: bytes, dest: Path) -> None:
    with Image.open(BytesIO(raw)) as im:
        rgb = im.convert("RGB")
        w, h = rgb.size
        scale = min(1.0, MAX_EDGE / max(w, h))
        if scale < 1.0:
            rgb = rgb.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        q = QUALITY
        while q >= 60:
            rgb.save(dest, "JPEG", quality=q, optimize=True)
            if dest.stat().st_size <= TARGET_MAX_BYTES:
                break
            q -= 5
    print(f"Wrote web image {dest} ({dest.stat().st_size} bytes)")


def prepend_entry(entry: dict) -> None:
    if not ART_JSON.is_file():
        raise AcquisitionError(f"Missing {ART_JSON}")
    data = json.loads(ART_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise AcquisitionError("art.json must be a JSON array")
    data.insert(0, entry)
    ART_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Prepended entry to {ART_JSON}")


def write_result(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    body = os.environ.get("ISSUE_BODY", "")
    created_at = os.environ.get("ISSUE_CREATED_AT", "")  # ISO8601
    token = os.environ.get("GITHUB_TOKEN", "")
    result_path = Path(os.environ.get("RESULT_PATH", "acquisition-result.json"))

    if not token:
        raise AcquisitionError("GITHUB_TOKEN is not set")

    try:
        fields = field_map(body)
        title, medium, date, category, note = require_fields(fields)
        image_url = find_image_url(body)
        day = (created_at[:10] if created_at else "undated")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise AcquisitionError(f"Invalid ISSUE_CREATED_AT date prefix: {created_at!r}")
        slug = slugify(title)
        basename = f"{day}-{slug}"
        web_rel = f"art/{basename}.jpg"
        web_path = ROOT / web_rel
        orig_path = ORIG_DIR / f"{basename}.bin"

        if web_path.exists():
            raise AcquisitionError(f"File already exists: {web_rel}. Rename the title or close and reopen.")

        ART_DIR.mkdir(parents=True, exist_ok=True)
        ORIG_DIR.mkdir(parents=True, exist_ok=True)

        raw = download(image_url, token)
        # detect extension for original archive name
        ext = ".jpg"
        try:
            with Image.open(BytesIO(raw)) as probe:
                fmt = (probe.format or "JPEG").lower()
            ext = { "jpeg": ".jpg", "png": ".png", "webp": ".webp", "gif": ".gif" }.get(fmt, ".bin")
        except Exception as e:
            raise AcquisitionError(f"Attachment is not a readable image: {e}") from e

        orig_path = ORIG_DIR / f"{basename}{ext}"
        orig_path.write_bytes(raw)
        save_web_jpeg(raw, web_path)

        entry = {
            "type": "image",
            "src": web_rel,
            "title": title,
            "medium": medium,
            "date": date,
            "category": category,
        }
        if note:
            entry["note"] = note
        prepend_entry(entry)

        write_result(
            result_path,
            {
                "ok": True,
                "title": title,
                "src": web_rel,
                "message": f"Published **{title}** as `{web_rel}`. Live shortly at the gallery site.",
            },
        )
        return 0
    except AcquisitionError as e:
        write_result(result_path, {"ok": False, "message": str(e)})
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
