"""Source-change watcher: hashes each enabled scheme's first official page.

Reports baseline / unchanged / changed / unreachable plus a staleness flag.
It never edits schemes.json -- a changed page only flags a human review.
"""
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import httpx

import config
from engine import data

HASH_FILE = config.DATA_DIR / "source_hashes.json"
STALE_DAYS = 30
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

_SCRIPT_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.I | re.S)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def normalise(html: str) -> str:
    text = _SCRIPT_STYLE.sub(" ", html or "")
    text = _TAG.sub(" ", text)
    return _WS.sub(" ", text).strip().lower()


def fetch(url: str, timeout: float = 6) -> str:
    headers = {"User-Agent": USER_AGENT}
    try:
        r = httpx.get(url, headers=headers, timeout=timeout,
                      follow_redirects=True, verify=True)
    except httpx.ConnectError as exc:
        if "ssl" not in str(exc).lower() and "certificate" not in str(exc).lower():
            raise
        # Many .gov.in sites ship incomplete cert chains; retry once unverified.
        r = httpx.get(url, headers=headers, timeout=timeout,
                      follow_redirects=True, verify=False)
    r.raise_for_status()
    return r.text


def _load_hashes() -> dict:
    try:
        with open(HASH_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _is_stale(checked_on, today: date) -> bool:
    if not checked_on:
        return True
    try:
        d = date.fromisoformat(str(checked_on)[:10])
    except ValueError:
        return True
    return (today - d) > timedelta(days=STALE_DAYS)


def check_all(fetcher=fetch, today=None, schemes=None) -> list[dict]:
    today = today or date.today()
    if schemes is None:
        schemes = data.SCHEMES_FILE["schemes"]
    targets = []
    for s in schemes:
        if not s.get("enabled", True):
            continue
        srcs = s.get("official_sources") or []
        targets.append((s, srcs[0] if srcs else None))

    def _get(url):
        if not url:
            return None, ValueError("no official source")
        try:
            return fetcher(url), None
        except Exception as exc:  # noqa: BLE001 -- any failure = unreachable
            return None, exc

    urls = list(dict.fromkeys(u for _, u in targets))  # fetch each URL once
    with ThreadPoolExecutor(max_workers=6) as pool:
        by_url = dict(zip(urls, pool.map(_get, urls)))
    fetched = [by_url[u] for _, u in targets]

    hashes = _load_hashes()
    stored = dict(hashes)  # snapshot: schemes sharing a URL get the same status
    results = []
    for (s, url), (body, err) in zip(targets, fetched):
        now = datetime.now().isoformat(timespec="seconds")
        checked_on = (s.get("verification") or {}).get("checked_on")
        if err is not None:
            status = "unreachable"
        else:
            digest = hashlib.sha256(normalise(body).encode("utf-8")).hexdigest()
            prev = stored.get(url)
            if prev is None:
                status = "baseline"
            elif prev.get("hash") == digest:
                status = "unchanged"
            else:
                status = "changed"
            hashes[url] = {"hash": digest, "checked_at": now}
        results.append({
            "scheme_id": s.get("id"),
            "name_en": s.get("name_en"),
            "url": url,
            "status": status,
            "checked_at": now,
            "stale": _is_stale(checked_on, today),
            "checked_on": checked_on,
        })

    with open(HASH_FILE, "w", encoding="utf-8") as fh:
        json.dump(hashes, fh, indent=2, ensure_ascii=False)
    return results
