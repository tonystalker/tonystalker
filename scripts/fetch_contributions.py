"""
fetch_contributions.py

GitHub serves your contribution calendar as a public HTML fragment at
https://github.com/users/<username>/contributions — the same markup
the profile page itself uses. No GraphQL API, no personal access
token. Parse the day cells with BeautifulSoup and write out raw days
plus derived stats (current streak, longest streak, best day, monthly
totals) to data/contributions.json.

Usage:
    python scripts/fetch_contributions.py <username>
Writes:
    data/contributions.json
"""
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (compatible; profile-readme-bot/1.0)"


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Newer GitHub markup: <td> cells with data-date / data-level,
    # older markup: <rect> cells with data-date / data-count.
    cells = soup.select("td.ContributionCalendar-day, td[data-date]")
    if cells:
        for td in cells:
            d = td.get("data-date")
            if not d:
                continue
            level = td.get("data-level")
            tooltip_id = td.get("id")
            count = 0
            if tooltip_id:
                tip = soup.find("tool-tip", attrs={"for": tooltip_id})
                if tip and tip.text:
                    first_tok = tip.text.strip().split(" ")[0]
                    count = 0 if first_tok in ("No",) else _safe_int(first_tok)
            days.append({"date": d, "level": _safe_int(level), "count": count})
    else:
        for rect in soup.select("rect[data-date]"):
            d = rect.get("data-date")
            level = rect.get("data-level")
            count = rect.get("data-count")
            days.append(
                {"date": d, "level": _safe_int(level), "count": _safe_int(count)}
            )

    days.sort(key=lambda x: x["date"])
    return days


def _safe_int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    current_streak = 0
    longest_streak = 0
    running = 0
    today = date.today()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # current streak: walk backwards from most recent day
    for d in reversed(days):
        d_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
        if d_date > today:
            continue
        if d["count"] > 0:
            current_streak += 1
        else:
            if d_date == today:
                continue  # today can still be zero and not break the streak
            break

    best_day = max(days, key=lambda x: x["count"], default=None)

    monthly = defaultdict(int)
    for d in days:
        month = d["date"][:7]
        monthly[month] += d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": dict(sorted(monthly.items())),
    }


def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/fetch_contributions.py <github-username>")
        sys.exit(1)
    username = sys.argv[1]

    html = fetch_html(username)
    days = parse_days(html)
    if not days:
        print("warning: no contribution cells parsed — GitHub markup may have changed")
    stats = compute_stats(days)

    out = {
        "username": username,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }

    Path("data").mkdir(exist_ok=True)
    Path("data/contributions.json").write_text(json.dumps(out, indent=2))
    print(
        f"wrote data/contributions.json "
        f"({len(days)} days, {stats['total_last_year']} contributions, "
        f"streak {stats['current_streak']})"
    )


if __name__ == "__main__":
    main()
