#!/usr/bin/env python3
"""Render self-contained animated SVG cards. Python 3.12, no dependencies.

Missing activity data produces an explicitly labelled pending state. Invalid
activity data fails without replacing any cards. Use STATIC=1 for still previews.
"""
from __future__ import annotations

import argparse
import base64
import calendar
from datetime import date, timedelta
from html import escape
import json
import os
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

from fetch_contributions import summarize

ROOT = Path(__file__).resolve().parents[1]
PAPER = "#f7f5ee"
INK = "#252820"
MUTED = "#686b63"
LINE = "#dedfd4"
BLUE = "#3157ec"
RED = "#e94f3b"
YELLOW = "#f2c747"
PALETTE = ["#e8e9e1", "#ced9ff", "#91aaff", "#5a7aef", BLUE]
COLORS = {"blue": BLUE, "red": RED, "yellow": YELLOW}


def font_css():
    rules = []
    for weight, filename in ((400,"Poppins-Regular.woff"),(600,"Poppins-SemiBold.woff")):
        encoded = base64.b64encode((ROOT/"assets/fonts"/filename).read_bytes()).decode("ascii")
        rules.append(f"@font-face{{font-family:Poppins;font-weight:{weight};font-style:normal;src:url(data:font/woff;base64,{encoded}) format('woff')}}")
    return "\n".join(rules)


FONT_CSS = font_css()


def text(x, y, value, size=16, fill=INK, cls="sans", extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" {extra}>{escape(str(value))}</text>'


def line(x1, y1, x2, y2, color=LINE):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{color}"/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}"/>'


def rect(x, y, w, h, fill, rx=0, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'


def label(x, y, value, fill=MUTED, extra=""):
    return text(x, y, value, 11, fill, "mono", f'letter-spacing="1.6" {extra}')


def arrow(x, y, color=INK, size=20):
    return f'<g transform="translate({x} {y})"><path class="arrow" d="M0 {size}L{size} 0M0 0H{size}V{size}" fill="none" stroke="{color}" stroke-width="2"/></g>'


def reveal(content, delay=0, cls="reveal"):
    return f'<g class="{cls}" style="animation-delay:{delay:.3f}s">{content}</g>'


def svg(title, description, w, h, body, static=False, background=PAPER, defs=""):
    motion = "" if static else """
      @keyframes arrive {from {opacity:0;transform:translateY(12px)} to {opacity:1;transform:translateY(0)}}
      @keyframes print {from {opacity:0} to {opacity:1}}
      @keyframes grow {from {transform:scaleY(0)} to {transform:scaleY(1)}}
      @keyframes swing {from {opacity:0;transform:translateY(22px) rotate(3deg)} to {opacity:1;transform:translateY(0) rotate(0deg)}}
      @keyframes nudge {0%,70%,100% {transform:translate(0,0)} 80% {transform:translate(3px,-3px)}}
      @keyframes pulse {0%,100% {opacity:1} 50% {opacity:.35}}
      @keyframes shine {0%,55% {transform:translateX(-520px)} 80%,100% {transform:translateX(520px)}}
      .reveal {animation:arrive .65s cubic-bezier(.16,1,.3,1) both}
      .print {animation:print .2s ease both}
      .bar {transform-box:fill-box;transform-origin:center bottom;animation:grow .75s cubic-bezier(.16,1,.3,1) both}
      .tile {transform-box:fill-box;transform-origin:center;animation:swing .8s cubic-bezier(.16,1,.3,1) both}
      .arrow {animation:nudge 6s ease-in-out 3s infinite}
      .dot {animation:pulse 3s ease-in-out infinite}
      .shine {animation:shine 9s ease-in-out 1.5s infinite}
      @media (prefers-reduced-motion:reduce) {
        * {animation:none!important;opacity:1!important}
        .shine {display:none}
      }
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>{defs}</defs><style>
{FONT_CSS}
.serif {{font-family:Poppins,Arial,sans-serif;font-weight:600;letter-spacing:-1px}}
.sans {{font-family:Poppins,Arial,sans-serif;font-weight:400}}
.mono {{font-family:Poppins,Arial,sans-serif;font-weight:400}}
{motion}
</style>
{rect(0,0,w,h,background,16)}
{body}
</svg>\n'''


def hero(profile, static):
    body = label(40, 35, "TANMAY / BUILDING ON THE WEB")
    body += '<circle class="dot" cx="741" cy="31" r="4" fill="'+BLUE+'"/>'
    body += text(754, 35, "Open to collaboration", 12)
    body += line(40, 54, 920, 54)
    body += reveal(text(37, 154, profile["first_name"], 85, cls="serif"), .05)
    body += reveal(text(35, 248, profile["last_name"], 104, BLUE, "serif"), .16)
    name_clip = '<clipPath id="name-clip">'+text(35,248,profile["last_name"],104,BLUE,"serif")+'</clipPath>'
    name_clip += '<linearGradient id="sheen"><stop stop-color="#adc0ff" stop-opacity="0"/><stop offset=".5" stop-color="#adc0ff" stop-opacity=".65"/><stop offset="1" stop-color="#adc0ff" stop-opacity="0"/></linearGradient>'
    if not static:
        body += '<g clip-path="url(#name-clip)">'+rect(0,154,180,110,'url(#sheen)',0,'class="shine"')+'</g>'
    body += reveal(text(42, 294, profile["role"], 20), .35)
    body += reveal(text(42, 328, profile["tagline"], 15, MUTED), .48)
    body += reveal(label(42, 366, "WEB APPS / REAL-TIME / CREATIVE CODE", BLUE), .6)
    body += '<circle cx="761" cy="234" r="148" fill="#e5eaff"/>'
    body += '<circle cx="890" cy="100" r="14" fill="'+YELLOW+'"/>'
    body += '<path d="M604 146Q656 41 802 79" fill="none" stroke="'+BLUE+'" stroke-width="1.2" opacity=".35"/>'
    photo = base64.b64encode((ROOT/"assets/portrait.png").read_bytes()).decode("ascii")
    body += reveal(f'<image x="579" y="60" width="364" height="334" preserveAspectRatio="xMidYMax meet" href="data:image/png;base64,{photo}"/>', .28)
    body += line(40, 399, 920, 399)
    body += label(42, 426, "BASED IN "+profile["location"].upper())
    body += text(600, 426, "takneekitanmay.tech", 12, MUTED, "mono")
    body += arrow(900, 413, BLUE, 12)
    return svg(profile["name"]+" — "+profile["role"], profile["tagline"]+" Based in India, open to full-stack collaboration. Tanmay holding a microphone, from his supplied photo.", 960, 440, body, static, defs=name_clip)


def heatmap(data, static):
    body = label(40, 34, "01 / THE DAILY PRACTICE")
    body += text(38, 78, "A little, every day.", 35, cls="serif")
    if not data:
        body += label(920, 34, "FIRST SYNC PENDING", BLUE, 'text-anchor="end"')
        for col in range(53):
            for row in range(7):
                body += rect(48+col*16.4, 111+row*14.5, 11.5, 10, "none", 2, f'stroke="{LINE}"')
        body += rect(228, 135, 502, 54, PAPER, 8)
        body += text(480, 158, "Your real contribution calendar belongs here.", 16, MUTED, extra='text-anchor="middle"')
        body += text(480, 179, "Waiting for the first successful activity refresh.", 12, MUTED, extra='text-anchor="middle"')
        body += label(40, 237, "REAL ACTIVITY / NO ESTIMATED COUNTS")
    else:
        as_of = date.fromisoformat(data["as_of"])
        first = date.fromisoformat(data["days"][0]["date"])
        grid_start = first - timedelta(days=(first.weekday()+1)%7)
        body += text(920, 75, f'{data["total"]:,} contributions', 17, BLUE, extra='text-anchor="end"')
        last_month = None
        for day in data["days"]:
            d = date.fromisoformat(day["date"])
            col, row = divmod((d-grid_start).days, 7)
            x, y = 48+col*16.4, 111+row*14.5
            if d.month != last_month and (d.day <= 7 or last_month is None):
                body += text(x, 102, calendar.month_abbr[d.month], 9, MUTED, "mono")
                last_month = d.month
            cell = f'<rect x="{x}" y="{y}" width="11.5" height="10" rx="2" fill="{PALETTE[day["level"]]}"><title>{d.isoformat()}: {day["count"]} contributions</title></rect>'
            body += reveal(cell, .15+col*.012+row*.012, "print")
        body += label(40, 236, f"365 DAYS / THROUGH {as_of.strftime('%d %b %Y').upper()}")
        body += text(780, 236, "Less", 10, MUTED, "mono")
        for i, color in enumerate(PALETTE):
            body += rect(815+i*16, 226, 11, 11, color, 2)
        body += text(920, 236, "More", 10, MUTED, "mono", 'text-anchor="end"')
    return svg("Tanmay's contribution calendar", "Real public GitHub contribution counts for a rolling 365-day window." if data else "Activity data is pending. The outlined calendar contains no contribution values.", 960, 260, body, static)


def activity(data, static):
    body = label(40, 33, "02 / THE BIGGER PICTURE")
    body += text(38, 76, "Built over time.", 35, cls="serif")
    body += text(918, 32, "Rolling year · edge months are partial", 11, MUTED, extra='text-anchor="end"')
    body += line(630, 95, 630, 258)
    body += line(43, 234, 594, 234)
    if data:
        months = data["months"]
        maximum = max(m["count"] for m in months) or 1
        step = 546 / len(months)
        for i, month in enumerate(months):
            x = 47 + i*step
            height = 110*month["count"]/maximum
            color = BLUE if month["count"] == maximum else "#d3d5c9"
            body += reveal(rect(round(x, 2), round(234-height, 2), round(step-13, 2), round(height, 2), color, 3), .2+i*.035, "bar")
            m = date.fromisoformat(month["month"]+"-01")
            body += text(round(x+(step-13)/2,2), 253, m.strftime("%b")[0:3], 9, MUTED, "mono", 'text-anchor="middle"')
            if i == 0 or m.month == 1:
                body += text(round(x+(step-13)/2,2), 269, str(m.year), 8, MUTED, "mono", 'text-anchor="middle"')
            if month["count"] == maximum and month["count"] > 0:
                body += reveal(text(round(x+(step-13)/2,2), round(224-height,2), str(month["count"]), 10, BLUE, "mono", 'text-anchor="middle"'), .75)
        stats = [(f'{data["current_streak"]}', "DAY STREAK"), (f'{data["active_days"]}', "ACTIVE DAYS"), (f'{data["longest_streak"]}', "LONGEST STREAK"), (f'{data["best_day"]["count"]}', "BEST DAY (COUNT)")]
        desc = f'{data["current_streak"]}-day current streak; {data["active_days"]} active days; {data["longest_streak"]}-day longest streak; best day {data["best_day"]["date"]}: {data["best_day"]["count"]} contributions. Partial first and last calendar months.'
    else:
        body += text(42, 145, "Good things take consistency.", 21, MUTED, "serif")
        body += text(43, 176, "Monthly totals will appear after the first refresh.", 14, MUTED)
        body += label(43, 256, "LIVE STATS PENDING", BLUE)
        stats = [("—", "DAY STREAK"), ("—", "ACTIVE DAYS"), ("—", "LONGEST STREAK"), ("—", "BEST DAY (COUNT)")]
        desc = "Monthly contributions, streaks and active-day statistics awaiting the first successful refresh. No sample statistics are shown."
    for i, (value, title) in enumerate(stats):
        x, y = 660+(i%2)*148, 138+(i//2)*94
        body += reveal(text(x, y, value, 40, BLUE if i==0 else INK, "serif"), .45+i*.08)
        body += text(x, y+23, title, 9, MUTED, "mono", 'letter-spacing=".7"')
    return svg("Activity over time", desc, 960, 290, body, static)


def tile(kind, static):
    spec = {
        "build": (BLUE, "#ffffff", "01 / BUILD", "Made to work.", ["Full-stack applications,", "from idea to interaction."], "EXPLORE MY PROJECTS"),
        "create": (RED, "#ffffff", "02 / CREATE", "Made to feel.", ["Creative interfaces and", "a little curiosity in code."], "VISIT MY PORTFOLIO"),
        "connect": (YELLOW, INK, "03 / CONNECT", "Made together.", ["Hackathons, conversations", "and the next good idea."], "LET'S COLLABORATE")
    }
    bg, fg, eyebrow, headline, copy, cta = spec[kind]
    body = label(25, 32, eyebrow, fg)+arrow(268, 21, fg, 17)
    body += text(23, 89, headline, 32, fg, "serif")
    body += text(25, 124, copy[0], 14, fg)+text(25, 145, copy[1], 14, fg)
    body += line(25, 171, 287, 171, fg)
    body += label(25, 198, cta, fg)
    body = reveal(body, .18, "tile")
    return svg(headline, " ".join(copy)+" "+cta.capitalize()+".", 312, 220, body, static, bg)


def project_card(project, index, static):
    accent = COLORS[project["accent"]]
    body = label(27, 31, project["category"])
    body += rect(0, 0, 6, 245, accent)
    body += arrow(426, 24, accent, 18)
    body += text(25, 86, project["name"], 39, cls="serif")
    for i, value in enumerate(project["description"]):
        body += text(27, 124+i*24, value, 16, MUTED)
    body += line(27, 182, 445, 182)
    body += text(27, 212, project["stack"], 11, INK, "mono")
    body += text(443, 235, f"0{index+1}", 10, MUTED, "mono", 'text-anchor="end"')
    return svg(project["name"], " ".join(project["description"])+" Stack: "+project["stack"]+".", 472, 245, reveal(body, .16+index*.06), static)


def stack_card(profile, static):
    body = label(40, 33, "03 / MY TOOLBOX")
    body += text(38, 77, "The tools behind the work.", 34, cls="serif")
    for i, group in enumerate(profile["stack"]):
        x = 42+i*300
        body += label(x, 113, group["label"], [BLUE,RED,MUTED][i])
        body += text(x, 143, group["lines"][0], 17)
        body += text(x, 169, group["lines"][1], 15, MUTED)
    return svg("Tech stack", "; ".join(g["label"]+": "+", ".join(g["lines"]) for g in profile["stack"]), 960, 200, reveal(body, .15), static)


def footer(profile, static):
    body = text(38, 58, "Have an idea? Let's build it.", 34, cls="serif")
    body += text(922, 57, profile["email"], 13, MUTED, extra='text-anchor="end"')
    body += label(40, 83, "ALWAYS CURIOUS. ALWAYS BUILDING.", BLUE)
    return svg("Let's build together", "Contact Tanmay at "+profile["email"], 960, 100, body, static)


def load_activity(path, username):
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("username") != username:
        raise ValueError("Contribution data belongs to another account")
    end = date.fromisoformat(payload["as_of"])
    days = payload["days"]
    expected = [(end-timedelta(days=364-i)).isoformat() for i in range(365)]
    if [d["date"] for d in days] != expected:
        raise ValueError("Contribution data must contain exactly 365 chronological days")
    for day in days:
        if type(day["count"]) is not int or day["count"] < 0 or type(day["level"]) is not int or day["level"] not in range(5):
            raise ValueError("Invalid count or intensity level")
        if (day["count"] == 0) != (day["level"] == 0):
            raise ValueError("Contribution count and intensity disagree")
    derived = summarize(username, end, days)
    if payload != derived:
        raise ValueError("Activity summary does not match its daily counts")
    return derived


def build_cards(profile, data, static=False):
    cards = {"hero.svg": hero(profile, static), "heatmap.svg": heatmap(data, static), "activity.svg": activity(data, static), "stack.svg": stack_card(profile, static), "footer.svg": footer(profile, static)}
    cards.update({kind+".svg":tile(kind, static) for kind in ("build", "create", "connect")})
    for index, project in enumerate(profile["projects"]):
        if not re.fullmatch(r"[a-z0-9-]+", project["slug"]):
            raise ValueError("Invalid project slug")
        cards["project-"+project["slug"]+".svg"] = project_card(project, index, static)
    for name, value in cards.items():
        ET.fromstring(value)
        if "<script" in value or "<foreignObject" in value or re.search(r'href="(?!data:image/png;base64,)', value):
            raise ValueError(f"Unexpected active or external content in {name}")
    return cards


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=ROOT/"data/profile.json")
    parser.add_argument("--data", type=Path, default=ROOT/"data/contributions.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--static", action="store_true", default=os.environ.get("STATIC")=="1")
    args = parser.parse_args()
    output = args.output or ROOT/("work/static-cards" if args.static else "cards")
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    data = load_activity(args.data, profile["username"])
    cards = build_cards(profile, data, args.static)
    output.mkdir(parents=True, exist_ok=True)
    for name, value in cards.items():
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=output, delete=False) as f:
            f.write(value)
            temp = Path(f.name)
        temp.replace(output/name)
    print(f'Rendered {len(cards)} {"static" if args.static else "animated"} cards into {output}. Activity: {"verified data" if data else "pending first sync"}.')


if __name__ == "__main__":
    main()
