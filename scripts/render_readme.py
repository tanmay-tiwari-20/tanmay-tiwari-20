#!/usr/bin/env python3
"""Compose the profile README from the current generated-card manifest."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"hero.svg", "repositories.svg", "languages.svg", "project-network.svg", "footer.svg"}
SOCIAL_SMALL = {"social-linkedin", "social-instagram", "social-github", "social-email"}
SOCIAL_GROUP = {"connect.svg", "social-portfolio.svg", *(name + ".svg" for name in SOCIAL_SMALL)}
ALT = {
    "hero": "Tanmay Tiwari — full-stack developer from India. Building web apps and real-time experiences.",
    "repositories": "Public repository growth, stars, and forks received. The timeline measures repository creation, not commits.",
    "languages": "Primary programming languages, measured as the share of eligible repositories with each GitHub primary language.",
    "footprint": "Source-language presence: the percentage of audited repositories containing each language. A repository may contain multiple languages.",
    "project-network": "Selected project technology map connecting Unoverse, Spools, Baithak, and Resumify to their documented tools.",
    "heatmap": "My real GitHub contribution calendar for the latest 365-day reporting window.",
    "activity": "Monthly GitHub contributions, active days, streaks, and busiest day, calculated from the displayed activity window.",
    "footer": "Let's build something together. Contact workwithtakneekitanmay@gmail.com.",
    "connect": "Connect with Tanmay through his portfolio, LinkedIn, Instagram, GitHub, or email.",
}


def social_links(profile: dict) -> dict[str, tuple[str, str]]:
    """Destinations belong on README anchors, because SVGs are image content."""
    return {
        "social-portfolio": (profile["portfolio"], "Visit Tanmay Tiwari's portfolio — projects and creative web experiences."),
        "social-linkedin": ("https://www.linkedin.com/in/tanmay-tiwari20/", "Connect with Tanmay Tiwari on LinkedIn."),
        "social-instagram": ("https://www.instagram.com/takneekitanmay/", "Follow takneekitanmay on Instagram."),
        "social-github": ("https://github.com/" + profile["username"], "Explore Tanmay Tiwari's GitHub profile and repositories."),
        "social-email": ("mailto:" + profile["email"], "Email Tanmay at " + profile["email"] + "."),
    }


def validate_manifest(manifest: dict, cards_root: Path) -> set[str]:
    if set(manifest.get("themes", [])) != {"light", "dark"}:
        raise ValueError("The README requires both light and dark themes")
    names = manifest.get("cards")
    if not isinstance(names, list) or not names:
        raise ValueError("The card manifest must contain a list of filenames")
    if any(not isinstance(name, str) or not re.fullmatch(r"[a-z0-9-]+\.svg", name) for name in names):
        raise ValueError("Manifest cards must be logical SVG filenames without directories")
    if len(names) != len(set(names)):
        raise ValueError("The card manifest must contain a unique list of filenames")
    names = set(names)
    if REQUIRED - names:
        raise ValueError(f"Required analytics cards are missing: {sorted(REQUIRED - names)}")
    if SOCIAL_GROUP & names and not SOCIAL_GROUP.issubset(names):
        raise ValueError(f"The social graphic group is incomplete: {sorted(SOCIAL_GROUP - names)}")
    for name in names:
        if name.endswith("-mobile.svg") and name.replace("-mobile.svg", ".svg") not in names:
            raise ValueError(f"Mobile card has no desktop counterpart: {name}")
        for theme in ("light", "dark"):
            if not (cards_root / theme / name).is_file():
                raise ValueError(f"Missing generated card: {theme}/{name}")
    return names


def picture(name: str, names: set[str], alt: str, link: str | None = None,
            *, width: str = "100%", paragraph: bool = True) -> str:
    filename = name + ".svg"
    if filename not in names:
        raise ValueError(f"Requested card is absent from the manifest: {filename}")
    if width not in {"100%", "49%"}:
        raise ValueError("Figure width must be full-width or a half-row social link")
    mobile = name + "-mobile.svg"
    parts = ["<picture>"]
    if mobile in names:
        parts.extend([
            f'  <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="./cards/dark/{mobile}" />',
            f'  <source media="(max-width: 600px)" srcset="./cards/light/{mobile}" />',
        ])
    parts.extend([
        f'  <source media="(prefers-color-scheme: dark)" srcset="./cards/dark/{filename}" />',
        f'  <img src="./cards/light/{filename}" width="{width}" alt="{escape(alt, quote=True)}" />',
        "</picture>",
    ])
    figure = "\n".join(parts)
    if link:
        figure = f'<a href="{escape(link, quote=True)}">\n{figure}\n</a>'
    return "<p>\n" + figure + "\n</p>" if paragraph else figure


def render_readme(profile: dict, names: set[str]) -> str:
    if profile.get("username") != "tanmay-tiwari-20":
        raise ValueError("Profile does not belong to tanmay-tiwari-20")
    portfolio = profile["portfolio"]
    email = "mailto:" + profile["email"]
    parts = ["<!-- Generated by scripts/render_readme.py from data/card-manifest.json. -->",
             '<div align="center">', picture("hero", names, ALT["hero"], portfolio)]
    if SOCIAL_GROUP & names:
        if not SOCIAL_GROUP.issubset(names):
            raise ValueError("The social graphic group is incomplete")
        links = social_links(profile)
        parts.append(picture("connect", names, ALT["connect"]))
        url, alt = links["social-portfolio"]
        parts.append(picture("social-portfolio", names, alt, url))
        for row in (("social-linkedin", "social-instagram"), ("social-github", "social-email")):
            figures = []
            for name in row:
                url, alt = links[name]
                figures.append(picture(name, names, alt, url, width="49%", paragraph=False))
            parts.append("<p>\n" + "\n".join(figures) + "\n</p>")
    for name in ("repositories", "languages", "footprint"):
        if name + ".svg" in names:
            parts.append(picture(name, names, ALT[name]))

    pages = sorted((name[:-4] for name in names if re.fullmatch(r"technologies-\d{2,}\.svg", name)),
                   key=lambda name: int(name.rsplit("-", 1)[1]))
    if pages:
        numbers = [int(name.rsplit("-", 1)[1]) for name in pages]
        if numbers != list(range(1, len(numbers) + 1)):
            raise ValueError("Technology graph pages must be consecutive, starting at 01")
        def technology_figure(name):
            return picture(name, names, "Technology usage by audited repository: declared direct dependencies and verified CDN use. "
                           f"Percentages overlap. Page {int(name.rsplit('-', 1)[1])} of {len(pages)}.")
        parts.append(technology_figure(pages[0]))
        if len(pages) > 1:
            parts.append("<details>\n<summary>View all technology percentages</summary>")
            parts.extend(technology_figure(name) for name in pages[1:])
            parts.append("</details>")

    parts.append(picture("project-network", names, ALT["project-network"]))
    parts.append("<p>" + " · ".join(f'<a href="{escape(project["url"], quote=True)}">{escape(project["name"])}</a>'
                                     for project in profile["projects"]) + "</p>")
    for name in ("heatmap", "activity"):
        if name + ".svg" in names:
            parts.append(picture(name, names, ALT[name]))
    parts.extend([picture("footer", names, ALT["footer"], email), "</div>"])

    project_text = "\n".join(
        f'- [{p["name"]}]({p["url"]}): {" ".join(p["description"])} Built with {p["stack"].replace(" / ", ", ")}.'
        for p in profile["projects"])
    parts.append(f'''<details>
<summary>About me, projects, and links in plain text</summary>

I'm **Tanmay Tiwari**, a full-stack developer from India. I build web applications, interactive 3D experiences, and products that bring people together. I'm currently working on personal projects and open to full-stack collaborations. Ask me about hackathons.

### Projects

{project_text}

### Toolkit

- **Frontend:** React, Next.js, TypeScript, JavaScript, Tailwind CSS.
- **Backend:** Node.js, Express, MongoDB, Redis, Socket.IO.
- **Creative web:** Three.js, React Three Fiber, GSAP, Framer Motion.
- **Tools:** Git, GitHub, Vercel, Vite, Figma.

### Find me

[Portfolio]({portfolio}) · [GitHub](https://github.com/{profile["username"]}) · [LinkedIn](https://www.linkedin.com/in/tanmay-tiwari20/) · [Instagram](https://www.instagram.com/takneekitanmay/) · [X](https://x.com/TakneekiTanmay) · [Email]({email})

The charts describe public repositories and their observed technologies. [Full technology inventory and percentages](./docs/TECHNOLOGIES.md) · [Measurement definitions and profile maintenance](./docs/PROFILE.md).

Design inspired by [Avi Vashishta's animated SVG README cards](https://www.avivashishta.com/blog/github-profile-readme-animated-svg-cards).

</details>''')
    return "\n\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/card-manifest.json")
    parser.add_argument("--profile", type=Path, default=ROOT / "data/profile.json")
    parser.add_argument("--cards-root", type=Path, default=ROOT / "cards")
    parser.add_argument("--output", type=Path, default=ROOT / "README.md")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    names = validate_manifest(manifest, args.cards_root)
    output = render_readme(profile, names)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=args.output.parent, delete=False) as file:
        file.write(output)
        temporary = Path(file.name)
    temporary.replace(args.output)
    print(f"Rendered README with {output.count('<picture>')} responsive figures from {len(names)} logical assets.")


if __name__ == "__main__":
    main()
