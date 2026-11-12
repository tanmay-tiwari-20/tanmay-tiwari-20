#!/usr/bin/env python3
"""Render the complete observed technology inventory from the audited data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from render_skills import load_showcase

ROOT = Path(__file__).resolve().parents[1]


def cell(value):
    return str(value).replace('|', r'\|').replace('\n', ' ').replace('\r', ' ')


def render_inventory(data):
    denominator = data['repository_count']
    if data['failures'] or data['scanned_repositories'] != denominator:
        raise ValueError('Cannot publish an incomplete technology inventory')
    for row in data['technologies'] + data['language_presence']:
        if row['count'] != len(set(row['repositories'])) or row['percent'] != round(row['count']*100/denominator, 2):
            raise ValueError('Technology percentage does not match repository evidence')
    lines = [
        '# Skills showcase and technology evidence', '',
        f"Snapshot: **{data['as_of']}** · **{denominator} public, non-fork repositories**, excluding the profile repository.", '',
        f"The audit found **{len(data['technologies'])} technology families** containing **{data['package_identifier_count']} distinct package/CDN identifiers**. It inspected {data['manifest_count']} manifests across {data['manifest_repositories']} repositories, plus root and one-level HTML files in {data['cdn_scanned_repositories']} repositories without manifests.", '',
        '**Coverage = repositories with a declared technology ÷ all eligible repositories.** A technology counts once per repository, even when several manifests or aliases declare it. The denominator includes repositories without manifests. Technologies and languages overlap, so their percentages do not sum to 100.', '',
        'These percentages describe current public default branches. They are not proficiency scores, time spent, code-byte percentages, deployed runtime usage, or a complete history of everything used. Private and deleted repositories, transitive dependencies, undeclared imports, and tools used outside these repositories are outside the measurement.', '',
        'Runtime, development, optional, and peer dependency declarations are included. Clear families are grouped (for example, React and React DOM); every original identifier remains in the table. Type declarations are grouped separately and do not imply that a repository is written in TypeScript. CDN identifiers prefixed with `cdn:` represent an explicitly linked service or library rather than an npm package.', '',
        'The language table uses file-extension presence in first-party source, configuration, and test files. Generated/vendor directories and minified JavaScript/CSS files are excluded; data formats, assets, and languages embedded inside HTML are not inferred. The separate profile primary-language chart uses GitHub’s one primary-language label per repository.', '',
    ]
    groups = load_showcase(data)
    count = sum(len(group['skills']) for group in groups)
    lines += ['## Skills on the profile', '',
              f'The profile showcases **{count} real, named technologies** with authentic local logos. Tiles are grouped by role. Supporting adapters, middleware, and small utility packages appear under the related tool here rather than becoming invented skills. Every audited dependency family is accounted for; the local `backend` workspace package is excluded. Source-language tiles require source files, not just type packages.', '',
              'The showcase also includes source-confirmed pandas, NumPy, Streamlit, Puter.js, Docker, Docker Compose, Redis, Node.js, and npm. These additions are recorded with file paths, immutable blob references, and source excerpts in [the source evidence](../data/skill-source-evidence.json). Logo provenance and licenses are in [the logo inventory](../assets/technology-logos/README.md).', '',
              '| Skill | Group | Supporting libraries | Repositories with evidence |',
              '| --- | --- | --- | --- |']
    for group in groups:
        for skill in group['skills']:
            support = ', '.join('`'+cell(value)+'`' for value in skill.get('supporting_technologies', [])) or '—'
            repos = ', '.join(f'[{cell(name)}](https://github.com/{data["username"]}/{name})' for name in skill['repositories'])
            lines.append(f'| {cell(skill["name"])} | {cell(group["title"])} | {support} | {repos} |')
    lines += ['', '## Source-language presence', '',
              '| Language | Repositories | Coverage | Observed extensions |',
              '| --- | ---: | ---: | --- |']
    for row in data['language_presence']:
        extensions = ', '.join('`'+cell(value)+'`' for value in row['extensions_present'])
        lines.append(f"| {cell(row['name'])} | {row['count']} / {denominator} | {row['percent']:.2f}% | {extensions} |")
    lines += ['', '## Complete technology inventory', '',
              '| Technology | Category | Repositories | Coverage | Declared package/CDN identifiers |',
              '| --- | --- | ---: | ---: | --- |']
    for row in data['technologies']:
        packages = ', '.join('`'+cell(value)+'`' for value in row['package_names'])
        lines.append(f"| {cell(row['name'])} | {cell(row['category'])} | {row['count']} / {denominator} | {row['percent']:.2f}% | {packages} |")
    lines += ['', '<details>', '<summary>Repositories behind each technology</summary>', '',
              '| Technology | Repositories with evidence |', '| --- | --- |']
    for row in data['technologies']:
        repositories = ', '.join('`'+cell(value)+'`' for value in row['repositories'])
        lines.append(f"| {cell(row['name'])} | {repositories} |")
    lines += ['', '</details>', '',
              'The [machine-readable audit](../data/technologies.json) includes counts, repository membership, measurement definitions, and GitHub source URLs. The [repository metadata snapshot](../data/repository-metrics.json) records the eligible set. Refresh the audit and regenerate the cards and this inventory after adding projects or technologies.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'data/technologies.json')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/TECHNOLOGIES.md')
    args = parser.parse_args()
    text = render_inventory(json.loads(args.data.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=args.output.parent, delete=False) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(args.output)
    print(f'Rendered the complete technology inventory into {args.output}.')


if __name__ == '__main__':
    main()
