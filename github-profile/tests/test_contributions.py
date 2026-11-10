import importlib.util
from datetime import date, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch


SPEC = importlib.util.spec_from_file_location("fetch_contributions", Path(__file__).resolve().parents[1] / "scripts" / "fetch_contributions.py")
calendar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calendar)
AS_OF = date(2026, 11, 10)


def fixture(counts=None, *, missing=None, future=False):
    counts = counts or {}
    parts = []
    for index in range(365 + int(future)):
        if index == missing:
            continue
        day = AS_OF - timedelta(days=364-index)
        count = counts.get(index, 0)
        parts.append(f'<td id="d{index}" data-date="{day}" data-level="{min(count, 4)}"></td>')
        phrase = f'{count:,} contributions' if count else 'No contributions'
        parts.append(f'<tool-tip for="d{index}">\n {phrase} on <span>{day}</span>.\n</tool-tip>')
    return "".join(parts)


class ContributionTests(unittest.TestCase):
    def test_real_tooltip_shape_exact_counts_and_future_exclusion(self):
        days = calendar.parse_calendar(fixture({0: 1200, 364: 1, 365: 99}, future=True), AS_OF)
        self.assertEqual(len(days), 365)
        self.assertEqual(days[0], {"date": "2025-11-11", "count": 1200, "level": 4})
        self.assertEqual(days[-1]["count"], 1)

    def test_count_grammar(self):
        self.assertEqual(calendar.parse_count("1 contribution on November 10."), 1)
        self.assertEqual(calendar.parse_count("No contributions on November 10."), 0)
        for broken in ("Contribution calendar", "1,2 contributions", "-1 contributions"):
            with self.assertRaises(ValueError):
                calendar.parse_count(broken)

    def test_missing_count_is_not_guessed_from_level(self):
        html = fixture({0: 3}).replace('for="d0"', 'for="other"')
        with self.assertRaisesRegex(ValueError, "Missing exact"):
            calendar.parse_calendar(html, AS_OF)

    def test_partial_response_rejected(self):
        with self.assertRaisesRegex(ValueError, "Incomplete calendar"):
            calendar.parse_calendar(fixture(missing=100), AS_OF)
        with self.assertRaisesRegex(ValueError, "Incomplete calendar"):
            calendar.parse_calendar("<html>Please sign in</html>", AS_OF)

    def test_redirected_calendar_or_non_html_response_rejected(self):
        for url, content_type, message in (
            ("https://github.com/login", "text/html", "redirected"),
            ("https://github.com/users/someone/contributions", "application/json", "content type"),
        ):
            with self.subTest(url=url, content_type=content_type):
                response = MagicMock()
                response.__enter__.return_value = response
                response.geturl.return_value = url
                response.headers = {"Content-Type": content_type}
                with patch.object(calendar, "urlopen", return_value=response):
                    with self.assertRaisesRegex(ValueError, message):
                        calendar.fetch_html("someone", AS_OF)
                response.read.assert_not_called()

    def test_duplicate_or_conflicting_days_rejected(self):
        duplicate = '<td id="d0" data-date="2025-11-11" data-level="0"></td>'
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            calendar.parse_calendar(fixture() + duplicate, AS_OF)
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            calendar.parse_calendar(fixture().replace('id="d0"', 'id="d0" data-count="5"'), AS_OF)

    def test_months_totals_and_streaks(self):
        days = calendar.parse_calendar(fixture({0: 4, 1: 2, 2: 1, 361: 2, 362: 8, 363: 3}), AS_OF)
        summary = calendar.summarize("someone", AS_OF, days)
        self.assertEqual(summary["total"], 20)
        self.assertEqual(summary["active_days"], 6)
        self.assertEqual(summary["current_streak"], 3) # today is not over
        self.assertEqual(summary["longest_streak"], 3)
        self.assertEqual(summary["best_day"], {"date": "2026-11-08", "count": 8})
        self.assertEqual(len(summary["months"]), 13)
        self.assertEqual(sum(month["count"] for month in summary["months"]), 20)

    def test_today_active_and_broken_streak(self):
        for counts, expected in (({363: 1, 364: 1}, 2), ({362: 1}, 0), ({}, 0)):
            with self.subTest(counts=counts):
                days = calendar.parse_calendar(fixture(counts), AS_OF)
                self.assertEqual(calendar.summarize("someone", AS_OF, days)["current_streak"], expected)

    def test_atomic_writer_replaces_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "data" / "contributions.json"
            calendar.write_json_atomic(destination, {"total": 1})
            calendar.write_json_atomic(destination, {"total": 2})
            self.assertEqual(json.loads(destination.read_text()), {"total": 2})
            self.assertEqual(list(destination.parent.iterdir()), [destination])


if __name__ == "__main__":
    unittest.main()
