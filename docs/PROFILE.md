# Maintaining the profile

This profile combines the supplied portrait with animated graphs and diagrams generated from public repository data. Poppins is embedded in every SVG. The warm coral accent (`#ef463e`) and light paper background (`#fffaf7`) draw from [Tanmay's portfolio](https://takneekitanmay.tech); dark mode keeps a true black background with vivid chart colors. The animated SVG approach is inspired by [Avi Vashishta's README](https://www.avivashishta.com/blog/github-profile-readme-animated-svg-cards), with Tanmay's own data, projects, and artwork.

## What the percentages measure

The primary-language graph measures repositories. Source-language and dependency percentages are retained in the detailed evidence document. The skill tiles show real named tools without estimating expertise.

| Graph | Measurement | Denominator |
| --- | --- | --- |
| Primary languages | Repositories assigned each primary language by GitHub | Eligible repositories with a nonempty GitHub primary-language value |
| Source-language presence (evidence document) | Repositories containing source files in each detected language | Repositories included in the source audit |
| Technologies (evidence document) | Repositories with a declared direct dependency or verified CDN use of each technology | Repositories included in the technology audit |

Primary-language shares describe one primary language per repository. Source-language and technology percentages overlap because one repository can contain several languages and use several technologies; these percentages are not expected to add up to 100%.

The technology evidence includes declared direct production, development, optional, and peer dependencies. The audit also checks script and stylesheet CDN references in root or one-level HTML files where no package or Python manifest exists. It examines current default branches. Skill categories remain visible in the main profile, while the complete dependency inventory and repository evidence are retained in `docs/TECHNOLOGIES.md`.

The **12 November 2026** repository snapshot contains **47 public repositories**, of which **46 are eligible** after excluding the profile repository. Those eligible repositories have **5 stars** and **3 forks received** in the snapshot. The scope excludes forks owned by the account. Repository growth is a cumulative count by repository creation date, not a contribution or commit timeline.

The inputs record their date, scope, source evidence, and completeness:

- `data/repository-metrics.json`: repository metadata, primary languages, stars, forks, and creation timeline.
- `data/technologies.json`: source-language and technology observations, repository counts, and percentage basis, when the technology audit is available.
- `data/contributions.json`: exact daily activity from the verified initial cache or a subsequent successful contribution-calendar fetch.
- `data/skills-catalog.json`: named technologies, authentic local logos, category order, supporting package families, and explicit exclusions.
- `data/skill-source-evidence.json`: source-confirmed tools not present in dependency manifests, with pinned blobs and excerpts.

Skill tiles contain technology names and their actual logos. They have no coverage bars or proficiency scores. Source languages, declared tools, and directly verified runtime/service use supply the evidence. Helpers are documented under their parent tools in `docs/TECHNOLOGIES.md`; the local `backend` workspace package is excluded. Concepts such as “APIs” and “responsive design” are not added as skills. Figma is absent because the inspected code does not establish its use.

The current complete repository audit is dated **12 November 2026**. It covers all 46 public, owned, non-fork project repositories and includes SHA-pinned manifest/CDN evidence. Additional source checks verify pandas, NumPy, Streamlit, Puter.js, Docker, Docker Compose, Redis, Node.js, and npm. This describes observable public repository code, not private/deleted projects or a complete Git history.

The selected-project diagram connects Unoverse, Spools, Baithak, and Resumify to their documented stacks. Its connections are project descriptions, not an extra percentage metric.

## README and themes

`data/card-manifest.json` is the authoritative list of assets produced by the latest renderer run. Its `cards` array contains logical SVG filenames, and its `themes` array contains `light` and `dark`. The README generator reads this manifest rather than scanning potentially obsolete files in the output folders.

The generated layout is: hero, graphic social links, repository growth, primary languages, categorized skill tiles, selected-project diagram and links, verified contribution graphs when available, and a contact footer. The skill tiles replace the old Language Footprint and Technology Atlas graphs. Every category remains visible in the README.

The social section has a full-width connection heading and portfolio link, followed by LinkedIn/Instagram and GitHub/email in two rows. Each smaller image uses 49% width and has its own outer README `<a>` wrapping its light/dark `<picture>`. The full-width portfolio image is also independently linked. Destinations come from the verified profile URLs; they do not rely on clickable content inside an SVG embedded as an image. The expandable plain-text section retains all contact links, including X.

Every figure uses a native `<picture>` with light and dark image files under `cards/light/` and `cards/dark/`. Responsive figures add ordered sources for dark mobile, light mobile, dark desktop, and a light desktop `<img>` fallback. Mobile sources apply at a maximum viewport width of 600px. The fallback image carries the width and descriptive alternative text.

The two themes use separate SVG palettes. The local preview uses the same image order, social rows, and clickable anchors as the generated README, and switches the actual SVG sources when changing theme or width. Its controls use the same warm coral, paper, and black palette. Animations live inside the SVGs and stop under `prefers-reduced-motion`, leaving the full chart or diagram visible.

The number of generated assets varies with the technology page count and available data. The contribution heatmap and monthly chart are included only when verified contribution data exists. Without a valid snapshot, the README omits those figures entirely. A local snapshot and the scheduled refresh are separate: use the reporting date in the data and the latest Actions result to check freshness.

## Update data and render

Use **Python 3.12**. The data and rendering scripts use the Python standard library.

From the repository root:

```sh
# Refresh public repository and technology evidence.
python scripts/fetch_repository_metrics.py

# Optionally fetch exact contribution-calendar data.
python scripts/fetch_contributions.py

# Generate the current SVGs and manifest, then compose the README.
python scripts/render_cards.py
python scripts/render_readme.py
python scripts/render_technology_inventory.py
```

The repository fetcher can use the `GITHUB_TOKEN` environment variable to avoid the low anonymous API rate limit. Keep tokens in environment variables or GitHub Actions secrets; never add them to profile data or SVGs.

Edit biography, selected projects, and toolkit in `data/profile.json`. Regenerate both the cards and README after changes. Commit the updated data, `README.md`, and current files under both theme directories. Remove obsolete generated SVG files that are no longer listed in the manifest.

After a new technology appears in the audit, add it to `data/skills-catalog.json` with an authentic logo in `assets/technology-logos/` and a provenance entry. The renderer rejects unaccounted dependencies and missing logos, preventing silent omissions or made-up marks. Add source-only skills to `data/skill-source-evidence.json` with actual file evidence before including them in the catalog. Logos are inlined as vector paths or embedded official PNG bytes and never request remote assets when viewed on GitHub.

`render_readme.py` accepts `--manifest`, `--profile`, `--cards-root`, and `--output` for validation or alternate output locations. It keeps every skill category visible. The renderer retires obsolete generated assets from the previous manifest when both themes are regenerated.

The card renderer accepts `--theme light`, `--theme dark`, or `--theme both` (the default). For a complete publishable README, generate both themes. Static previews are available with:

```sh
python scripts/render_cards.py --static
```

Static files are written beneath `work/static-cards/light/` and `work/static-cards/dark/`, leaving animated cards intact. `STATIC=1` enables the same mode. `--output PATH` changes the output root while retaining theme subfolders. Preview files under `work/` do not belong in the published repository.

## Portrait and fonts

The hero uses the photo supplied by Tanmay, with a transparency mask prepared locally around the subject. The cutout preserves the original RGB pixels and is stored as `assets/portrait.png`. The original full-resolution photo is not included. Portrait preparation is separate from data refreshes.

Actual **Poppins Regular (400)** and **Poppins SemiBold (600)** are stored as WOFF files in `assets/fonts/` and embedded in the SVGs. They do not require locally installed fonts or external font requests. Keep the [SIL Open Font License](../assets/fonts/OFL.txt) with redistributed font files.

The committed WOFF files are ready to use. To regenerate them from licensed local TTF files:

```sh
python scripts/prepare_fonts.py path/to/Poppins-Regular.ttf path/to/Poppins-SemiBold.ttf
```

This utility packages the complete fonts without modifying glyphs. It checks table and whole-font checksums and verifies byte-exact round-trip decoding.

## Contribution data and initial snapshot

The initial package includes the public [portfolio contribution cache](https://github.com/tanmay-tiwari-20/Portfolio-2.0/blob/eaebef78a258167ff29c5611f72aaed24e291a6b/data/github-contributions.json), pinned to commit `eaebef78a258167ff29c5611f72aaed24e291a6b` and blob `13b8b12ad01b6e69390f3b2c54c94d81ad7ebce9`. Its generation timestamp is **10 November 2026, 10:28:47 UTC**. The portfolio's checked-in fetch script obtains exact day counts and levels from GitHub's contribution-calendar API.

All 367 source dates, count/level pairs, and the total were validated. The two earliest dates had zero contributions and were removed to match this README's 365-day window, **11 November 2025–10 November 2026**. The normalized snapshot contains **392 contributions**, **147 active days**, a **13-day current streak**, and a **62-day longest streak**. It supplies the initial heatmap and monthly graphs.

This is the user's publicly committed, API-derived snapshot, not a fresh direct calendar query from this work session. The daily direct-calendar fetch remains configured but has not yet been verified by a successful run here.

When present, contribution data covers 365 calendar days through the reporting date in Asia/Kolkata, excluding future dates. Monthly totals use calendar months within that window, so the first and last buckets may be partial and there may be 13 buckets.

Active days contain at least one contribution. The current streak ends today, or yesterday if today has no contributions yet. The longest streak and busiest day are calculated inside the displayed window.

The fetcher reads the public calendar at `https://github.com/users/tanmay-tiwari-20/contributions`. It requires exact daily counts and a complete date range. A failed or incomplete response does not replace the last valid JSON, and the renderer does not invent missing activity values.

## Publish and maintain

After reviewing the design, merge the changes into `main` in `tanmay-tiwari-20/tanmay-tiwari-20`. GitHub displays that repository's root `README.md` on the profile.

This checkout currently has no refresh workflow. Run the data fetcher and renderers above when updating the profile. A future GitHub Actions workflow can run the same commands using the built-in `GITHUB_TOKEN` and commit the regenerated data, documentation, and cards.

The renderers validate complete evidence accounting, authentic local logo availability, SVG content, and README asset references. Check the generated profile with:

```sh
python scripts/render_cards.py
python scripts/render_readme.py
python scripts/render_technology_inventory.py
```

Inspect failed fetch or render output before changing stored data. API or calendar changes may require updating a parser. Preserve the last verified assets while fixing the issue.
