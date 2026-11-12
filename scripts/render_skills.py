"""Render authentic logo tiles from repository and source-file evidence."""
from __future__ import annotations

import base64
from html import escape
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def load_showcase(technology):
    catalog = json.loads((ROOT / 'data/skills-catalog.json').read_text(encoding='utf-8'))
    source = json.loads((ROOT / 'data/skill-source-evidence.json').read_text(encoding='utf-8'))
    observed = {item['name']: item for item in technology['technologies']}
    languages = {item['name']: item for item in technology.get('language_presence', [])}
    supplements = {item['name']: item for item in source['skills']}
    groups = {item['id']: {**item, 'skills': []} for item in catalog['groups']}
    accounted = set()
    for skill in catalog['skills']:
        if skill['group'] not in groups:
            raise ValueError('Unknown skill group: ' + skill['group'])
        names = skill.get('technology_names', []) + skill.get('supporting_technologies', [])
        if accounted.intersection(names):
            raise ValueError('A technology is assigned to multiple skill tiles')
        accounted.update(names)
        repositories, evidence_names = set(), []
        for name in skill.get('technology_names', []):
            if name in observed:
                repositories.update(observed[name]['repositories'])
                evidence_names.append(name)
        for name in skill.get('language_names', []):
            if name in languages:
                repositories.update(languages[name]['repositories'])
                evidence_names.append(name + ' source files')
        for name in skill.get('source_skills', []):
            if name in supplements:
                repositories.update(supplements[name]['repositories'])
                evidence_names.append(name + ' source usage')
        if repositories:
            logo = ROOT / 'assets/technology-logos' / skill['logo']
            if not logo.is_file() or logo.parent != ROOT / 'assets/technology-logos':
                raise ValueError('Missing local authentic logo: ' + skill['name'])
            if not skill.get('icon_source'):
                raise ValueError('Logo provenance is missing: ' + skill['name'])
            groups[skill['group']]['skills'].append({**skill,
                'repositories': sorted(repositories, key=str.casefold),
                'evidence_names': evidence_names,
                'supporting_repositories': {
                    name: observed[name]['repositories'] for name in skill.get('supporting_technologies', [])
                    if name in observed}})
    accounted.update(item['technology'] for item in catalog.get('exclusions', []))
    if set(observed) - accounted:
        raise ValueError('Add real technology names to the skill catalog: ' + ', '.join(sorted(set(observed) - accounted)))
    return [group for group in groups.values() if group['skills']]


def logo_markup(skill, x, y, size, theme):
    """Inline original logo artwork; viewing never needs image requests."""
    source = (ROOT / 'assets/technology-logos' / skill['logo']).read_text(encoding='utf-8')
    root = ET.fromstring(source)
    for element in root.iter():
        tag = element.tag.rsplit('}', 1)[-1]
        if tag in {'script', 'foreignObject', 'use', 'style'}:
            raise ValueError('Logo must contain self-contained vector artwork: ' + skill['name'])
        if tag == 'image':
            href = element.get('href', element.get('{http://www.w3.org/1999/xlink}href', ''))
            if not href.startswith('data:image/png;base64,'):
                raise ValueError('Bitmap logos must embed local PNG bytes')
            payload = base64.b64decode(href.split(',', 1)[1], validate=True)
            if not payload.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Bitmap logo is not a valid PNG')
            element.attrib.pop('{http://www.w3.org/1999/xlink}href', None)
            element.set('href', href)
        for attribute in element.attrib:
            if attribute.lower().startswith('on') or (attribute.rsplit('}', 1)[-1] == 'href' and tag != 'image'):
                raise ValueError('Unexpected active logo attribute')
    # Keep official gradients/clipping independent from other inlined logos.
    prefix = 'logo-' + re.sub(r'[^a-z0-9]', '-', skill['name'].lower()) + '-'
    identifiers = {element.get('id'): prefix+element.get('id') for element in root.iter() if element.get('id')}
    for element in root.iter():
        for attribute, value in list(element.attrib.items()):
            if attribute == 'id':
                element.set(attribute, identifiers[value])
            else:
                for original, unique in identifiers.items():
                    value = value.replace('url(#'+original+')', 'url(#'+unique+')')
                element.set(attribute, value)
    inner = ''.join(ET.tostring(child, encoding='unicode') for child in root if child.tag.rsplit('}', 1)[-1] != 'title')
    color = skill.get('color', '#777777')
    # Neutral black/white brand marks follow the theme for visibility.
    if color.lower() in {'#000000', '#ffffff', '#111111', '#181818'}:
        color = '#fff8f3' if theme == 'dark' else '#211411'
    viewbox = root.get('viewBox', '0 0 24 24')
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{escape(viewbox, quote=True)}" '
            f'fill="{color}" color="{color}" aria-hidden="true">{inner}</svg>')


def wrap_name(name, limit=19):
    if len(name) <= limit:
        return [name]
    words, lines, current = name.split(), [], ''
    for word in words:
        candidate = (current + ' ' + word).strip()
        if current and len(candidate) > limit:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def skill_pages(a, technology, static=False, mobile=False):
    groups = load_showcase(technology)
    total = sum(len(group['skills']) for group in groups)
    cards = {}
    for index, group in enumerate(groups):
        columns, width, padding, gap = (3, 480, 22, 12) if mobile else (6, 960, 30, 14)
        # Keep every category together; height follows the actual tile count.
        tile_width = (width - 2*padding - (columns-1)*gap) / columns
        tile_height = 112 if mobile else 118
        rows = math.ceil(len(group['skills']) / columns)
        first = index == 0
        top = (207 if mobile else 215) if first else (132 if mobile else 138)
        height = top + rows*(tile_height+gap) - gap + 32
        accent = group.get('accent', 'red')
        body = ''
        if first:
            body += a.label(padding, 34, 'SKILLS / BUILT THROUGH PROJECTS', 'red')
            body += a.text(padding-2, 80, 'Skills in action.', 32 if mobile else 38, weight=600,
                           extra='letter-spacing="-1.1"')
            body += a.text(padding, 108, 'A toolkit built one project at a time.', 12 if mobile else 14, 'muted')
            body += a.path(f'M{padding} 132H{width-padding}', 'line', 1)
            if not mobile:
                body += a.pill(width-217, 53, f'{total} TECHNOLOGIES', 'red', 187)
            body += a.label(padding, 163, group['title'].upper(), accent)
            body += a.text(padding, 187, group['subtitle'], 11 if mobile else 12, 'muted')
        else:
            body += a.label(padding, 32, f'SKILLS / {index+1:02}', accent)
            body += a.text(padding-2, 76, group['title'], 27 if mobile else 32, weight=600,
                           extra='letter-spacing="-.8"')
            body += a.text(padding, 104, group['subtitle'], 11 if mobile else 12, 'muted')
            if not mobile:
                body += a.text(width-padding, 75, f'{len(group["skills"]):02} TOOLS', 10, 'muted', 600,
                               'text-anchor="end" letter-spacing="1.5"')
        for position, skill in enumerate(group['skills']):
            x = padding + (position % columns)*(tile_width+gap)
            y = top + (position // columns)*(tile_height+gap)
            center = x + tile_width/2
            tooltip = skill['name'] + '. Observed in: ' + ', '.join(skill['repositories']) + '. Evidence: ' + ', '.join(skill['evidence_names'])
            body += f'<g data-skill="{escape(skill["name"], quote=True)}"><title>{escape(tooltip)}</title>'
            body += a.rect(round(x, 2), y, round(tile_width, 2), tile_height, 'panel', 16, 'line')
            body += a.rect(round(x+13, 2), y+12, 17, 2, accent, 1, extra='opacity=".5"')
            # Brand marks sit in generous neutral wells with no invented symbols.
            color = skill.get('color', '#777777').lstrip('#')
            def luminance(hex_color):
                rgb = [int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)]
                linear = [value/12.92 if value <= .04045 else ((value+.055)/1.055)**2.4 for value in rgb]
                return .2126*linear[0] + .7152*linear[1] + .0722*linear[2]
            neutral = color.lower() in {'000000','ffffff','111111','181818'}
            brand_luminance = luminance(color)
            background_luminance = luminance(a.t['bg'].lstrip('#'))
            contrast = (max(brand_luminance, background_luminance)+.05)/(min(brand_luminance, background_luminance)+.05)
            well = 'bg' if neutral or contrast >= 4 else '#211b24' if a.theme == 'light' else '#fffaf7'
            if skill.get('logo_background') in {'light', 'dark'}:
                well = '#fffaf7' if skill['logo_background'] == 'light' else '#211b24'
            body += a.rect(round(center-25, 2), y+15, 50, 50, well, 13)
            body += logo_markup(skill, round(center-17, 2), y+23, 34, a.theme)
            lines = wrap_name(skill['name'], 16 if mobile else 19)
            for line_index, line in enumerate(lines):
                size = 11 if len(line) > 16 and mobile else 12 if len(line) > 18 else 13 if mobile else 12.5
                body += a.text(round(center, 2), y+(86 if len(lines) == 1 else 83)+line_index*16,
                               line, size, 'ink', 600, 'text-anchor="middle"')
            body += '</g>'
        suffix = '-mobile' if mobile else ''
        filename = f'skills-{index+1:02}{suffix}.svg'
        description = group['title'] + ': ' + '; '.join(skill['name'] for skill in group['skills'])
        cards[filename] = a.finish(group['title'] + ' — skills showcase', description,
                                   width, height, body, static)
    return cards
