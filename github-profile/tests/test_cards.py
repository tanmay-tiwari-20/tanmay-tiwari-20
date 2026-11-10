"""Renderer checks use synthetic activity only, in memory or temporary files."""

import base64
import copy
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    SPEC = importlib.util.spec_from_file_location("render_cards", ROOT / "scripts" / "render_cards.py")
    renderer = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(renderer)
finally:
    sys.path.pop(0)

SVG = {"svg": "http://www.w3.org/2000/svg"}
USERNAME = "tanmay-tiwari-20"


def activity_fixture(as_of=date(2026, 11, 10), counts=None):
    counts = counts if counts is not None else {0: 2, 1: 3, 180: 12, 363: 1, 364: 2}
    days = []
    for index in range(365):
        count = counts.get(index, 0)
        days.append({
            "date": (as_of - timedelta(days=364 - index)).isoformat(),
            "count": count,
            "level": min(count, 4),
        })
    return renderer.summarize(USERNAME, as_of, days)


def calendar_cells(svg):
    return ET.fromstring(svg).findall(".//svg:rect[svg:title]", SVG)


class CardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))

    def load_fixture(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "contributions.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            return renderer.load_activity(source, USERNAME)

    def test_valid_data_renders_every_date_and_exact_count(self):
        payload = activity_fixture()
        validated = self.load_fixture(payload)
        cards = renderer.build_cards(self.profile, validated)
        cells = calendar_cells(cards["heatmap.svg"])
        self.assertEqual(len(cells), 365)
        labels = [cell.find("svg:title", SVG).text for cell in cells]
        self.assertEqual(labels, [f'{day["date"]}: {day["count"]} contributions' for day in payload["days"]])
        self.assertIn("20 contributions", cards["heatmap.svg"])

    def test_missing_data_has_truthful_pending_state_without_counted_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            data = renderer.load_activity(Path(directory) / "does-not-exist.json", USERNAME)
        self.assertIsNone(data)
        cards = renderer.build_cards(self.profile, data)
        self.assertIn("FIRST SYNC PENDING", cards["heatmap.svg"])
        self.assertIn("LIVE STATS PENDING", cards["activity.svg"])
        self.assertEqual(calendar_cells(cards["heatmap.svg"]), [])
        self.assertNotRegex(cards["heatmap.svg"], r"\d[\d,]* contributions")

    def test_cached_summary_mismatch_and_wrong_account_are_rejected(self):
        changes = (
            ("total", 1000), ("active_days", 200), ("current_streak", 50),
            ("longest_streak", 100), ("best_day", {"date": "2026-01-01", "count": 99}),
            ("months", [{"month": "2026-11", "count": 1000}]),
            ("username", "another-person"),
        )
        for key, value in changes:
            with self.subTest(key=key):
                payload = activity_fixture()
                payload[key] = value
                with self.assertRaises(ValueError):
                    self.load_fixture(payload)

    def test_missing_reordered_and_duplicate_days_are_rejected(self):
        original = activity_fixture()
        variants = [original["days"][:-1], list(reversed(original["days"])), original["days"][:-1] + [original["days"][0]]]
        for days in variants:
            with self.subTest(first=days[0]["date"], length=len(days)):
                payload = copy.deepcopy(original)
                payload["days"] = days
                with self.assertRaisesRegex(ValueError, "365 chronological days"):
                    self.load_fixture(payload)

    def test_non_integer_negative_or_inconsistent_activity_is_rejected(self):
        for count, level in ((True, 1), (1.0, 1), (-1, 1), (2, True), (2, 5), (0, 2), (2, 0)):
            with self.subTest(count=count, level=level):
                payload = activity_fixture()
                payload["days"][0].update(count=count, level=level)
                with self.assertRaises(ValueError):
                    self.load_fixture(payload)

    def test_zero_activity_is_real_zero_not_pending_or_division_by_zero(self):
        payload = self.load_fixture(activity_fixture(counts={}))
        cards = renderer.build_cards(self.profile, payload)
        self.assertEqual(len(calendar_cells(cards["heatmap.svg"])), 365)
        self.assertIn("0 contributions", cards["heatmap.svg"])
        self.assertNotIn("PENDING", cards["heatmap.svg"])
        self.assertNotIn("PENDING", cards["activity.svg"])
        self.assertNotRegex(cards["activity.svg"], r"\b(?:nan|inf)\b")
        ET.fromstring(cards["activity.svg"])

    def test_leap_and_year_boundary_windows_have_no_missing_or_clipped_cells(self):
        for as_of in (date(2024, 3, 1), date(2024, 12, 31), date(2025, 1, 1)):
            with self.subTest(as_of=as_of):
                data = self.load_fixture(activity_fixture(as_of))
                cards = renderer.build_cards(self.profile, data)
                cells = calendar_cells(cards["heatmap.svg"])
                self.assertEqual(len(cells), 365)
                self.assertIn("2024-02-29", "".join(day["date"] for day in data["days"]))
                for cell in cells:
                    self.assertGreaterEqual(float(cell.attrib["x"]), 0)
                    self.assertLessEqual(float(cell.attrib["x"]) + float(cell.attrib["width"]), 960)
                    self.assertLessEqual(float(cell.attrib["y"]) + float(cell.attrib["height"]), 260)
                ET.fromstring(cards["activity.svg"])

    def test_all_cards_are_valid_accessible_self_contained_svg(self):
        for data in (None, activity_fixture()):
            for static in (False, True):
                for name, source in renderer.build_cards(self.profile, data, static).items():
                    with self.subTest(card=name, static=static, pending=data is None):
                        document = ET.fromstring(source)
                        self.assertEqual(document.tag, "{http://www.w3.org/2000/svg}svg")
                        self.assertEqual(document.attrib["role"], "img")
                        self.assertTrue(document.find("svg:title", SVG).text)
                        self.assertTrue(document.find("svg:desc", SVG).text)
                        ids = {element.attrib["id"] for element in document.iter() if "id" in element.attrib}
                        for element in document.iter():
                            local_name = element.tag.split("}")[-1].lower()
                            self.assertNotIn(local_name, ("script", "foreignobject", "iframe", "object"))
                            self.assertFalse(any(attr.split("}")[-1].lower().startswith("on") for attr in element.attrib))
                            for attr, value in element.attrib.items():
                                if attr.split("}")[-1].lower() == "href":
                                    self.assertEqual(local_name, "image")
                                    self.assertRegex(value, r"^data:image/png;base64,[A-Za-z0-9+/]+=*$")
                                    encoded = value.split(",", 1)[1]
                                    image = base64.b64decode(encoded, validate=True)
                                    self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
                                    self.assertEqual(image[12:16], b"IHDR")
                                    width, height = struct.unpack(">II", image[16:24])
                                    self.assertGreater(width, 0)
                                    self.assertGreater(height, 0)
                                for match in re.finditer(r"url\(([^)]+)\)", value, re.IGNORECASE):
                                    target = match.group(1).strip(" \t\r\n\"'")
                                    self.assertTrue(target.startswith("#"), target[:80])
                                    self.assertIn(target[1:], ids)
                        css = "".join(style.text or "" for style in document.findall("svg:style", SVG))
                        self.assertNotRegex(css, r"(?i)@import")
                        for match in re.finditer(r"url\(([^)]+)\)", css):
                            url = match.group(1).strip(" \t\r\n\"'")
                            self.assertTrue(url.startswith("data:font/woff;base64,"), url[:80])
                            font = base64.b64decode(url.split(",", 1)[1], validate=True)
                            self.assertEqual(font[:4], b"wOFF")
                            self.assertGreaterEqual(len(font), 44)
                            self.assertEqual(struct.unpack(">I", font[8:12])[0], len(font))

    def test_poppins_fonts_and_supplied_photo_are_embedded(self):
        cards = renderer.build_cards(self.profile, None)
        for name, source in cards.items():
            with self.subTest(card=name):
                document = ET.fromstring(source)
                css = "".join(style.text or "" for style in document.findall("svg:style", SVG))
                self.assertIn("font-family:Poppins", css)
                font_rules = re.findall(r"@font-face\s*\{([^}]+)\}", css)
                self.assertEqual(len(font_rules), 2)
                self.assertTrue(any("font-weight:400" in rule for rule in font_rules))
                self.assertTrue(any("font-weight:600" in rule for rule in font_rules))
                images = document.findall(".//svg:image", SVG)
                self.assertEqual(len(images), 1 if name == "hero.svg" else 0)

    def test_static_output_has_no_executable_animation(self):
        animated = renderer.build_cards(self.profile, activity_fixture(), static=False)
        static = renderer.build_cards(self.profile, activity_fixture(), static=True)
        self.assertIn("@keyframes", animated["hero.svg"])
        for name, source in static.items():
            with self.subTest(card=name):
                document = ET.fromstring(source)
                css = "".join(style.text or "" for style in document.findall("svg:style", SVG))
                self.assertNotIn("@keyframes", css)
                self.assertNotRegex(css, r"\banimation(?:-name)?\s*:")
                for tag in ("animate", "animateTransform", "animateMotion", "set"):
                    self.assertIsNone(document.find(".//svg:" + tag, SVG))

    def test_reduced_motion_keeps_structural_svg_positions(self):
        source = renderer.build_cards(self.profile, None)["hero.svg"]
        document = ET.fromstring(source)
        arrow_groups = [group for group in document.findall(".//svg:g[@transform]", SVG)
                        if group.find("svg:path[@class='arrow']", SVG) is not None]
        self.assertTrue(arrow_groups)
        for group in arrow_groups:
            self.assertRegex(group.attrib["transform"], r"^translate\(")
        css = "".join(style.text or "" for style in document.findall("svg:style", SVG))
        self.assertIn("prefers-reduced-motion", css)
        self.assertNotRegex(css, r"\*\s*\{[^}]*\btransform\s*:\s*none")

    def test_profile_copy_cannot_insert_svg_elements(self):
        profile = copy.deepcopy(self.profile)
        profile["first_name"] = '<script>alert("test")</script>'
        profile["tagline"] = 'A & B < C > D "quoted"'
        document = ET.fromstring(renderer.build_cards(profile, None)["hero.svg"])
        self.assertIsNone(document.find(".//svg:script", SVG))
        contents = "".join(document.itertext())
        self.assertIn(profile["first_name"], contents)
        self.assertIn(profile["tagline"], contents)


if __name__ == "__main__":
    unittest.main()
