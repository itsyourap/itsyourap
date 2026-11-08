"""Recent public activity, rendered as a Markdown table.

Uses /users/{login}/events/public on purpose: even with a token that can see
private events, only public activity is ever written to the README.
"""

from __future__ import annotations

from datetime import datetime

from .http import gh_rest

MAX_LINES = 8


def _repo(name: str) -> str:
    return f"[{name}](https://github.com/{name})"


def _describe(ev: dict) -> tuple[str, str] | None:
    t, p, repo = ev["type"], ev.get("payload") or {}, ev["repo"]["name"]
    if t == "PushEvent":
        branch = p.get("ref", "").removeprefix("refs/heads/")
        return "⬆️", f"Pushed to `{branch}` in {_repo(repo)}"
    if t == "PullRequestEvent":
        pr = p.get("pull_request", {})
        num, url = pr.get("number") or p.get("number"), pr.get("html_url") or f"https://github.com/{repo}/pull/{p.get('number')}"
        action = p.get("action")
        if action == "closed" and pr.get("merged"):
            return "🎉", f"Merged PR [#{num}]({url}) in {_repo(repo)}"
        if action in ("opened", "reopened", "closed"):
            icon = {"opened": "🔀", "reopened": "🔀", "closed": "❌"}[action]
            return icon, f"{action.capitalize()} PR [#{num}]({url}) in {_repo(repo)}"
        return None
    if t == "IssuesEvent" and p.get("action") in ("opened", "closed", "reopened"):
        issue = p["issue"]
        icon = "✔️" if p["action"] == "closed" else "❗"
        return icon, f"{p['action'].capitalize()} issue [#{issue['number']}]({issue['html_url']}) in {_repo(repo)}"
    if t == "PullRequestReviewEvent":
        pr = p.get("pull_request", {})
        return "👀", f"Reviewed PR [#{pr.get('number')}]({pr.get('html_url')}) in {_repo(repo)}"
    if t == "ReleaseEvent" and p.get("action") == "published":
        rel = p["release"]
        return "🚀", f"Released [{rel.get('tag_name')}]({rel.get('html_url')}) in {_repo(repo)}"
    if t == "CreateEvent" and p.get("ref_type") == "repository":
        return "📦", f"Created repository {_repo(repo)}"
    if t == "PublicEvent":
        return "🌍", f"Open-sourced {_repo(repo)}"
    return None


def collect(login: str, ignored: set[str]) -> str:
    # The events API keeps ~90 days / 300 events, served in pages of 100.
    events: list[dict] = []
    for page in (1, 2, 3):
        batch = gh_rest(f"users/{login}/events/public?per_page=100&page={page}")
        events.extend(batch)
        if len(batch) < 100:
            break
    events.sort(key=lambda e: e["created_at"], reverse=True)
    rows: list[tuple[str, str, str]] = []
    pushed: set[str] = set()
    for ev in events:
        name = (ev.get("repo") or {}).get("name")
        if not name or name in ignored:
            continue
        if ev["type"] == "PushEvent":
            # one line per repo, otherwise a busy day of pushes drowns everything else
            if name in pushed:
                continue
            pushed.add(name)
        described = _describe(ev)
        if not described:
            continue
        icon, text = described
        when = datetime.fromisoformat(ev["created_at"].replace("Z", "+00:00"))
        rows.append((f"`{when:%b %d}`", icon, text))
        if len(rows) >= MAX_LINES:
            break

    if not rows:
        return "_No recent public activity — probably shipping something private._ 🤫"
    lines = ["| When | | What |", "| :-- | :-: | :-- |"]
    lines += [f"| {w} | {i} | {t} |" for w, i, t in rows]
    return "\n".join(lines)
