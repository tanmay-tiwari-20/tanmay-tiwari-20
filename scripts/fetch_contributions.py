#!/usr/bin/env python3
"""Fetch the public GitHub calendar and write validated, exact activity data.

Uses only Python's standard library. A changed GitHub response or incomplete
calendar fails before replacing the last good JSON file.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
INDIA = timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")
USERNAME = "tanmay-tiwari-20"


class CalendarParser(HTMLParser):
    """Collect day cells and the count-bearing accessible tooltips."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cells: list[dict[str, str]] = []
        self.tooltips: dict[str, str] = {}
        self._tooltip_for: str | None = None
        self._tooltip_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value for key, value in attrs if value is not None}
        if "data-date" in attr and "data-level" in attr:
            self.cells.append(attr)
        if tag == "tool-tip" and attr.get("for"):
            self._tooltip_for = attr["for"]
            self._tooltip_parts = []

    def handle_data(self, data: str) -> None:
        if self._tooltip_for is not None:
            self._tooltip_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip" and self._tooltip_for is not None:
            text = " ".join("".join(self._tooltip_parts).split())
            previous = self.tooltips.get(self._tooltip_for)
            if previous is not None and previous != text:
                raise ValueError("Conflicting calendar tooltips")
            self.tooltips[self._tooltip_for] = text
            self._tooltip_for = None
            self._tooltip_parts = []


def parse_count(text: str) -> int:
    match = re.match(r"^\s*(No|\d[\d,]*)\s+contributions?\b", text, re.IGNORECASE)
    if match is None:
        raise ValueError(f"Unrecognized contribution count: {text[:100]!r}")
    value = match.group(1)
    if value.lower() == "no":
        return 0
    if not re.fullmatch(r"\d+|\d{1,3}(?:,\d{3})+", value):
        raise ValueError("Invalid count separator")
    return int(value.replace(",", ""))


def parse_calendar(html: str, as_of: date) -> list[dict[str, str | int]]:
    parser = CalendarParser()
    parser.feed(html)
    parser.close()
    start = as_of - timedelta(days=364)
    by_date: dict[date, dict[str, str | int]] = {}
    for cell in parser.cells:
        day = date.fromisoformat(cell["data-date"])
        if day < start or day > as_of:
            continue
        level = int(cell["data-level"])
        if level not in range(5):
            raise ValueError(f"Unexpected contribution level on {day}: {level}")
        candidates = []
        if "data-count" in cell:
            if not re.fullmatch(r"\d+", cell["data-count"]):
                raise ValueError(f"Invalid data-count on {day}")
            candidates.append(int(cell["data-count"]))
        tooltip = parser.tooltips.get(cell.get("id", ""))
        if tooltip:
            candidates.append(parse_count(tooltip))
        for key in ("aria-label", "data-tooltip-text"):
            if cell.get(key):
                candidates.append(parse_count(cell[key]))
        if not candidates:
            raise ValueError(f"Missing exact contribution count on {day}")
        if len(set(candidates)) != 1:
            raise ValueError(f"Conflicting contribution counts on {day}")
        count = candidates[0]
        if (count == 0) != (level == 0):
            raise ValueError(f"Contribution count and level disagree on {day}")
        if day in by_date:
            raise ValueError(f"Duplicate calendar date: {day}")
        by_date[day] = {"date": day.isoformat(), "count": count, "level": level}
    expected = {start + timedelta(days=index) for index in range(365)}
    if set(by_date) != expected:
        missing = sorted(expected - set(by_date))
        raise ValueError(f"Incomplete calendar: expected 365 days, received {len(by_date)}; "
                         f"first missing date: {missing[0] if missing else 'unknown'}")
    return [by_date[day] for day in sorted(by_date)]


def summarize(username: str, as_of: date, days: list[dict]) -> dict:
    """All statistics refer to this 365-day window, including partial months."""
    months: dict[str, int] = defaultdict(int)
    longest = running = active = total = 0
    for day in days:
        count = day["count"]
        total += count
        months[day["date"][:7]] += count
        if count:
            active += 1
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    current = 0
    streak_days = days[:-1] if days and days[-1]["count"] == 0 else days
    for day in reversed(streak_days):
        if not day["count"]:
            break
        current += 1
    best = max(days, key=lambda day: day["count"])
    return {
        "username": username,
        "as_of": as_of.isoformat(),
        "days": days,
        "total": total,
        "active_days": active,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": [{"month": month, "count": count} for month, count in sorted(months.items())],
    }


def fetch_html(username: str, as_of: date) -> str:
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", username):
        raise ValueError("Invalid GitHub username")
    query = urlencode({"from": (as_of - timedelta(days=364)).isoformat(), "to": as_of.isoformat()})
    url = f"https://github.com/users/{username}/contributions?{query}"
    request = Request(url, headers={
        "User-Agent": f"{username}-profile-art/1.0",
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    })
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                actual_url = urlsplit(response.geturl())
                if actual_url.scheme != "https" or actual_url.hostname != "github.com" or actual_url.path != f"/users/{username}/contributions":
                    raise ValueError("GitHub redirected away from the requested public calendar")
                if "text/html" not in response.headers.get("Content-Type", ""):
                    raise ValueError("GitHub returned an unexpected content type")
                html = response.read(5_000_001)
                if len(html) > 5_000_000:
                    raise ValueError("GitHub calendar response is unexpectedly large")
                return html.decode("utf-8")
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError("Could not fetch GitHub contribution calendar")


def write_json_atomic(destination: Path, payload: dict) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=destination.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--username", default=USERNAME)
    args.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(INDIA).date())
    args.add_argument("--output", type=Path, default=ROOT / "data" / "contributions.json")
    args.add_argument("--html-file", type=Path, help="Parse a saved GitHub response without network access")
    options = args.parse_args()
    html = options.html_file.read_text(encoding="utf-8") if options.html_file else fetch_html(options.username, options.as_of)
    days = parse_calendar(html, options.as_of)
    payload = summarize(options.username, options.as_of, days)
    write_json_atomic(options.output, payload)
    print(f"Saved {len(days)} verified days; {payload['total']:,} contributions through {options.as_of}.")


if __name__ == "__main__":
    main()
