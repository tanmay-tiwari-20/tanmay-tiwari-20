# Maintaining the profile

This README uses self-contained animated SVG cards: cream backgrounds, Poppins typography, dark ink, and blue, coral, and yellow accents. The layout and motion are inspired by [Avi Vashishta's animated SVG cards](https://www.avivashishta.com/blog/github-profile-readme-animated-svg-cards); the copy, project selection, and portrait are personalized for Tanmay.

The cards are committed to this repository. The README loads them directly through relative image paths, without a third-party stats-image service. Animations live inside the SVGs and respect `prefers-reduced-motion`.

## Install

Merge the profile changes into `main` in `tanmay-tiwari-20/tanmay-tiwari-20`. GitHub displays that repository's root `README.md` on the profile.

The **Refresh profile cards** workflow runs when relevant renderer, configuration, asset, or workflow files are pushed to `main`. It also runs daily at approximately **06:47 Asia/Kolkata**; GitHub may delay scheduled runs. To refresh manually, open **Actions → Refresh profile cards → Run workflow** after the workflow is on `main`.

The workflow uses the repository's built-in `GITHUB_TOKEN` to commit refreshed cards. A personal access token is not required. The refresh job requests `contents: write`; repository or organization policy must permit that permission and commits to `main`.

## Initial activity and artwork

The initial activity cards explicitly show a pending state until the first successful refresh. No contribution totals or streaks are invented.

The hero uses the photo supplied by Tanmay, with a transparency mask prepared locally around the subject. The cutout preserves the source photo's color pixels and is stored as `assets/portrait.png`; the original full-resolution photo is not included. Portrait preparation is separate from the daily activity refresh.

The cards use actual **Poppins Regular (400)** and **Poppins SemiBold (600)**, packaged as WOFF files and embedded in each SVG so they do not depend on locally installed fonts or external font requests. The font files and their [SIL Open Font License](../assets/fonts/OFL.txt) are stored in `assets/fonts/`.

The first successful refresh replaces the pending activity cards with real data. Until a refresh succeeds, the rest of the profile remains usable. A failed or incomplete response does not replace the last good contribution JSON.

## Edit and render

Use **Python 3.12**. The fetcher and renderer use the Python standard library, so no package installation is needed.

From the repository root:

```sh
# Edit biography, selected projects, and toolkit in data/profile.json.
python scripts/render_cards.py

# Fetch current activity, then redraw the cards.
python scripts/fetch_contributions.py
python scripts/render_cards.py
```

Commit changes to `data/profile.json` together with regenerated `cards/*.svg`. If you change project names, links, or descriptions, update the matching links and plain-text summaries in `README.md` as well.

The renderer has a static mode for inspecting the completed animation frame:

```sh
python scripts/render_cards.py --static
```

Static cards are written to `work/static-cards`, leaving the animated `cards/` output intact. `STATIC=1` enables the same mode. Use `--output PATH` to select a different output directory. Preview files under `work/` do not belong in the published README.

The committed WOFF files are ready to use and require no build step during refresh. To regenerate them from licensed local Poppins TTF files:

```sh
python scripts/prepare_fonts.py path/to/Poppins-Regular.ttf path/to/Poppins-SemiBold.ttf
```

This standard-library utility packages the complete fonts without modifying glyphs. It checks all table and font checksums and verifies that decoding each WOFF reproduces the original TTF byte for byte. Keep `assets/fonts/OFL.txt` with redistributed font files.

## What the activity means

- **Window:** 365 calendar days through the date in Asia/Kolkata, excluding future dates. This is a rolling window, not a calendar year.
- **Monthly bars:** totals grouped by calendar month within that window. The first and last months may be partial, so the chart may contain 13 month buckets.
- **Active days:** days with at least one contribution.
- **Current streak:** consecutive active days ending today; if today has no contributions yet, the sequence can end yesterday.
- **Longest streak:** longest uninterrupted active sequence inside the displayed 365-day window.
- **Busiest day:** a day with the highest contribution count in the window.

Counts come from the public calendar at `https://github.com/users/tanmay-tiwari-20/contributions`. They reflect what GitHub exposes publicly and can change when GitHub updates its records. The fetcher requires exact daily counts and a complete date range; it fails rather than guessing counts from color intensity.

`data/contributions.json` is generated data. Refresh it with the fetcher rather than manually changing numbers.

## Checks and recovery

Run the repository's checks with:

```sh
python -m unittest discover -s tests -p 'test_*.py'
```

If refresh fails, inspect the failed step in the Actions run. A calendar parsing error may mean GitHub changed its HTML; a push error may mean branch rules or token permissions prevent the workflow from committing. Keep the existing cards while fixing the problem, then run the workflow again. GitHub may disable scheduled workflows in public repositories after prolonged inactivity; enable the workflow again in Actions if necessary.

The README uses regular `<a>` and `<img>` elements so each tile and project card is a real link. Image alt text and the expandable plain-text section preserve the profile's essential information when images or animation are unavailable.
