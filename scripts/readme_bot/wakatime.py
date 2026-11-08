"""WakaTime stats in two requests (summaries + all-time total).

WakaTime API keys became plugin-only (write-only) on 2026-11-01. Reads need a
personal OAuth token from https://wakatime.com/oauth, stored in the
WAKATIME_TOKEN secret, sent as a Bearer token.
"""

from __future__ import annotations

import os
import urllib.parse
from collections import defaultdict
from datetime import date

from .http import HTTPError, request_json

API = os.environ.get("WAKATIME_API_URL", "https://wakatime.com/api/v1").rstrip("/")


def _get(path: str, **params: str) -> tuple[int, dict]:
    token = os.environ.get("WAKATIME_TOKEN") or os.environ.get("WAKATIME_API_KEY")
    if not token:
        raise SystemExit("WAKATIME_TOKEN is not set")
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    try:
        return request_json(f"{API}/{path}{qs}", headers={"Authorization": f"Bearer {token}"})
    except HTTPError as exc:
        if exc.status in (401, 403):
            raise SystemExit(
                f"WakaTime rejected the token (HTTP {exc.status}): {exc.body[:200]}\n"
                "Create a personal OAuth token at https://wakatime.com/oauth (scopes: read_summaries, read_stats) "
                "and save it as the WAKATIME_TOKEN repository secret. Plain API keys are plugin-only since 2026-11-01."
            ) from None
        raise


def hm(seconds: float) -> str:
    seconds = int(seconds)
    h, m = divmod(seconds // 60, 60)
    if h:
        return f"{h}h {m}m"
    return f"{m}m" if m else f"{seconds}s"


def _rank(totals: dict[str, float], grand: float) -> list[dict]:
    items = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    return [
        {"name": name, "seconds": secs, "text": hm(secs), "percent": secs * 100 / grand if grand else 0}
        for name, secs in items
        if secs >= 60
    ]


def collect() -> dict:
    # Completed days only, so the numbers don't wobble during the day.
    _, summaries = _get("users/current/summaries", range="Last 7 Days from Yesterday")
    days_raw = summaries["data"]

    langs: dict[str, float] = defaultdict(float)
    editors: dict[str, float] = defaultdict(float)
    systems: dict[str, float] = defaultdict(float)
    ai = 0.0
    days = []
    for day in days_raw:
        for key, bucket in (("languages", langs), ("editors", editors), ("operating_systems", systems)):
            for item in day.get(key, []):
                bucket[item["name"]] += item["total_seconds"]
        for cat in day.get("categories", []):
            if cat["name"].lower() == "ai coding":
                ai += cat["total_seconds"]
        d = date.fromisoformat(day["range"]["date"])
        secs = day["grand_total"]["total_seconds"]
        days.append({"date": d, "seconds": secs, "short": hm(secs) if secs >= 60 else "0", "label": f"{d:%a}"})

    grand = sum(d["seconds"] for d in days)
    best = max(days, key=lambda d: d["seconds"], default=None)

    all_time = None
    try:
        status, body = _get("users/current/all_time_since_today")
        all_time = (body or {}).get("data", {}).get("text") or None
    except Exception as exc:  # all-time is a nice-to-have; never fail the card for it
        print(f"  warn: all-time total unavailable: {exc}")

    first, last = (days[0]["date"], days[-1]["date"]) if days else (None, None)
    return {
        "week_total": hm(grand),
        "daily_avg": hm(grand / max(len(days), 1)),
        "all_time": all_time.replace(" hrs", "h").replace(" mins", "m") if all_time else None,
        "ai_week": hm(ai) if ai >= 60 else None,
        "best_day": f"{best['date']:%a, %b} {best['date'].day} · {hm(best['seconds'])}" if best and best["seconds"] else None,
        "days": days,
        "languages": _rank(langs, grand),
        "editors": _rank(editors, grand),
        "os": _rank(systems, grand),
        "range": f"{first:%b} {first.day} – {last:%b} {last.day}" if first else "last 7 days",
    }
