#!/usr/bin/env python3
"""Job Scout fetcher — deterministic, no LLM calls.

Fetches postings from ATS APIs for watchlist companies, applies hard filters
(title band, location, recency), dedupes against state, writes new postings to
state/pending_review.json for Claude Code to score.

Usage:
  python3 src/fetch.py            # weekly fetch
  python3 src/fetch.py --verify   # test every endpoint, report health
"""

import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import yaml  # pip install pyyaml
except ImportError:
    sys.exit("Missing dependency: run  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST = ROOT / "config" / "watchlist.yaml"
STATE = ROOT / "state" / "jobs.json"
PENDING = ROOT / "state" / "pending_review.json"

MAX_AGE_DAYS = 45
UA = {"User-Agent": "Mozilla/5.0 (job-scout personal agent)"}

# ---- Hard filters (deterministic; judgment gates live in CLAUDE.md) ----

TITLE_INCLUDE = re.compile(
    r"(senior\s+product\s+manager|sr\.?\s*product\s+manager|product\s+manager\s*(ii|iii|2|3)"
    r"|lead\s+product\s+manager|product\s+lead|founding\s+product|first\s+product)",
    re.I,
)
TITLE_EXCLUDE = re.compile(
    r"(director|vp|vice\s+president|head\s+of|principal|group\s+product|gpm"
    r"|associate\s+product|apm|intern|graduate|manager,?\s+marketing|program\s+manager"
    r"|project\s+manager|technical\s+program)",
    re.I,
)
# Bare "Product Manager" (no seniority marker) also passes — level gets judged at scoring
TITLE_BARE = re.compile(r"^product\s+manager\b", re.I)

INDIA_HINTS = re.compile(
    r"(bengaluru|bangalore|india|mumbai|delhi|gurgaon|gurugram|noida|hyderabad|pune|chennai)",
    re.I,
)
REMOTE_ONLY = re.compile(r"^\s*remote\s*$", re.I)


def canonical_hash(company: str, url: str) -> str:
    u = re.sub(r"[?#].*$", "", url.strip().lower()).rstrip("/")
    return hashlib.sha1(f"{company.lower()}|{u}".encode()).hexdigest()[:16]


def get_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def strip_html(text: str, limit: int = 4000) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.replace("Z", "+00:00"), fmt)
        except (ValueError, TypeError):
            continue
    try:  # epoch millis (lever)
        return datetime.fromtimestamp(int(s) / 1000, tz=timezone.utc)
    except (ValueError, TypeError, OSError):
        return None


# ---- ATS adapters: each yields dicts {title, location, url, posted, description} ----

def fetch_greenhouse(token):
    data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")
    for j in data.get("jobs", []):
        yield {
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "posted": j.get("updated_at") or j.get("first_published"),
            "description": strip_html(j.get("content", "")),
        }


def fetch_lever(token):
    data = get_json(f"https://api.lever.co/v0/postings/{token}?mode=json")
    for j in data:
        yield {
            "title": j.get("text", ""),
            "location": (j.get("categories") or {}).get("location", ""),
            "url": j.get("hostedUrl", ""),
            "posted": j.get("createdAt"),
            "description": strip_html(j.get("descriptionPlain") or j.get("description", "")),
        }


def fetch_ashby(token):
    data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true")
    for j in data.get("jobs", []):
        yield {
            "title": j.get("title", ""),
            "location": j.get("location", ""),
            "url": j.get("jobUrl") or j.get("applyUrl", ""),
            "posted": j.get("publishedAt"),
            "description": strip_html(j.get("descriptionPlain") or j.get("descriptionHtml", "")),
        }


ADAPTERS = {"greenhouse": fetch_greenhouse, "lever": fetch_lever, "ashby": fetch_ashby}


def title_passes(title):
    t = title.strip()
    if TITLE_EXCLUDE.search(t):
        return False
    return bool(TITLE_INCLUDE.search(t) or TITLE_BARE.match(t))


def location_passes(loc):
    loc = (loc or "").strip()
    if not loc:
        return True  # unknown location -> let scoring judge
    if INDIA_HINTS.search(loc):
        return True
    if "remote" in loc.lower() and "india" in loc.lower():
        return True
    return False  # non-India office or bare "Remote" (remote-only is gated out)


def recency_passes(posted_raw):
    d = parse_date(str(posted_raw)) if posted_raw else None
    if d is None:
        return True  # unknown date -> keep, scoring can judge staleness
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - d <= timedelta(days=MAX_AGE_DAYS)


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"meta": {}, "jobs": {}}


def main():
    verify = "--verify" in sys.argv
    watchlist = yaml.safe_load(WATCHLIST.read_text())["companies"]
    state = load_state()
    seen = set(state.get("jobs", {}).keys())
    pending, report = [], []

    for c in watchlist:
        name, ats = c["name"], c.get("ats", "custom")
        if c.get("rhythm_verdict") == "fail":
            report.append(f"[GATED] {name}: rhythm_verdict=fail, skipped")
            continue
        if ats not in ADAPTERS:
            report.append(f"[SKIP ] {name}: ats={ats} (covered by weekly web-sweep)")
            continue
        try:
            postings = list(ADAPTERS[ats](c["token"]))
            kept = 0
            for p in postings:
                if not (title_passes(p["title"]) and location_passes(p["location"])
                        and recency_passes(p["posted"])):
                    continue
                h = canonical_hash(name, p["url"])
                if h in seen:
                    continue
                seen.add(h)
                kept += 1
                pending.append({"hash": h, "company": name, "tier": c.get("tier"),
                                "rhythm_verdict": c.get("rhythm_verdict", "unknown"),
                                "watchlist_notes": c.get("notes", ""), **p})
            report.append(f"[OK   ] {name}: {len(postings)} postings, {kept} new after filters")
        except Exception as e:
            report.append(f"[ERROR] {name}: {type(e).__name__}: {e}")

    print("\n".join(report))
    if verify:
        print("\n--verify complete. Fix [ERROR] tokens in config/watchlist.yaml, "
              "set verified: true on [OK] entries.")
        return

    PENDING.parent.mkdir(parents=True, exist_ok=True)
    PENDING.write_text(json.dumps(pending, indent=2, ensure_ascii=False))
    print(f"\n{len(pending)} new posting(s) -> {PENDING.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
