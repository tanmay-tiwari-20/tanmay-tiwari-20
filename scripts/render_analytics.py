"""Animated SVG graphs drawn only from the checked-in GitHub audit."""
from html import escape
import math
from render_skills import skill_pages

ACCENTS = ('red', 'blue', 'violet', 'mint', 'yellow', 'cyan')


def percent(value):
    return f'{value:.2f}%'


def orbit_mark(a, x, y, color='red'):
    """A header flourish spatially separate from measured chart marks."""
    body = a.path('M-20 10C-24 -13 14 -25 23 -5C32 14 -8 26 -18 7', color, 1.3,
                  extra=a.flow(4,5)+' opacity=".45"')
    body += a.circle(19, -10, 3, color, 'class="breathe"')
    body += a.path('M-22 6L-18 13L-13 6', color, 1.4, extra='opacity=".65"')
    return a.group(body, x, y)


def languages(a, data, static=False, mobile=False):
    entries = data['languages']
    w, h = (480, 680) if mobile else (960, 466)
    cx, cy, r = (240, 270, 112) if mobile else (228, 261, 112)
    circumference = 2 * math.pi * r
    body = a.label(30, 34, 'LANGUAGE MIX / PRIMARY LANGUAGE')
    body += a.text(28, 81, 'The code behind the work.', 24 if mobile else 34, weight=600,
                   extra='letter-spacing="-.8"')
    body += a.text(30, 109, 'One primary language per repository.', 12, 'muted')
    if not mobile:
        body += orbit_mark(a, 897, 62)
        body += a.rect(421, 132, 510, 278, 'panel', 18, 'line')
    body += a.circle(cx, cy, r+34, 'none', f'stroke="{a.t["line"]}" stroke-dasharray="1 10" class="orbit"')
    body += a.circle(cx, cy, r, 'none', f'stroke="{a.t["soft"]}" stroke-width="34"')
    offset = 0
    denominator = data['language_repositories']
    for i, item in enumerate(entries):
        length = circumference*item['repository_count']/denominator if denominator else 0
        color = ACCENTS[i % len(ACCENTS)]
        title = escape(f'{item["name"]}: {item["repository_count"]} repositories, {percent(item["percent"])}')
        # Exact count-based angular offsets; the narrow separators are visual gaps.
        body += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#accent-{color})" stroke-width="34" stroke-dasharray="{max(0, length-3):.4f} {circumference:.4f}" stroke-dashoffset="{-offset:.4f}" transform="rotate(-90 {cx} {cy})" class="segment" style="animation-delay:{i*.09}s"><title>{title}</title></circle>'
        offset += length
    body += a.circle(cx, cy, 79, 'panel', f'stroke="{a.t["line"]}"')
    body += a.text(cx, cy+4, str(denominator), 59, 'ink', 600, 'text-anchor="middle" letter-spacing="-2"')
    body += a.text(cx, cy+31, 'WITH A LANGUAGE', 9, 'muted', 600, 'text-anchor="middle" letter-spacing="1.7"')
    for i, item in enumerate(entries):
        color = ACCENTS[i % len(ACCENTS)]
        if mobile:
            x, y = 28+(i % 2)*230, 440+(i//2)*70
            body += a.rect(x-8, y-21, 216, 61, 'panel', 13, 'line')
            body += a.circle(x+5, y-4, 4, color)+a.text(x+17, y, item['name'], 15, 'ink', 600)
            body += a.text(x+17, y+23, f'{item["repository_count"]} repos', 12, 'muted')
            body += a.text(x+194, y+23, percent(item['percent']), 15, color, 600, 'text-anchor="end"')
        else:
            x, y = 442, 159+i*43
            body += a.rect(x, y-9, 4, 26, color, 2)+a.text(x+18, y+2, item['name'], 17, 'ink', 600)
            body += a.text(x+18, y+19, f'{item["repository_count"]} repositories', 10, 'muted')
            body += a.text(910, y+10, percent(item['percent']), 20, color, 600, 'text-anchor="end" letter-spacing="-.5"')
            if i < len(entries)-1:
                body += a.path(f'M{x+18} {y+28}H910', 'line', 1)
    body += a.text(30, h-34, 'Share of repositories, not source-code bytes.', 11, 'muted')
    body += a.text(30, h-15, 'Public non-fork projects · profile repository excluded', 9, 'muted')
    desc = 'Percentages use repositories with each primary language, not code bytes. '
    desc += '; '.join(f'{item["name"]}: {percent(item["percent"])}' for item in entries)
    return a.finish('Primary language distribution', desc, w, h, body, static)


def repositories(a, data, static=False, mobile=False):
    w, h = (480, 552) if mobile else (960, 474)
    body = a.label(30, 33, 'GITHUB / TANMAY-TIWARI-20')
    body += a.text(28, 79, 'A growing body of work.', 24 if mobile else 34, weight=600,
                   extra='letter-spacing="-.8"')
    if not mobile:
        body += orbit_mark(a, 897, 54)
    for i, (value, caption, color) in enumerate((
        (data['repository_count'], 'PUBLIC PROJECTS', 'red'),
        (data['stars'], 'STARS RECEIVED', 'violet'),
        (data['forks'], 'FORKS RECEIVED', 'mint'),
    )):
        x, width = (24+i*146, 136) if mobile else (30+i*303, 294)
        body += a.rect(x, 106, width, 98, 'panel', 17, 'line')
        body += a.rect(x+15, 120, 21, 3, color, 1.5)
        body += a.text(x+15, 166, str(value), 42 if mobile else 47, color, 600, 'letter-spacing="-1.5"')
        body += a.text(x+15, 189, caption, 8 if mobile else 10, 'muted', 600, 'letter-spacing=".9"')
    timeline = data['creation_timeline']
    maximum = data['repository_count'] or 1
    left, right, top, bottom = 50, w-39, 253, h-90
    for tick in sorted(set((0, math.ceil(maximum/2), maximum))):
        y = bottom-tick/maximum*(bottom-top)
        body += a.path(f'M{left} {y:.2f}H{right}', 'line', 1, extra='stroke-dasharray="2 7"')
        body += a.text(left-12, round(y+3, 2), str(tick), 9, 'muted', extra='text-anchor="end"')
    points = [(left+i*(right-left)/max(1, len(timeline)-1),
               bottom-row['cumulative_repositories']/maximum*(bottom-top)) for i, row in enumerate(timeline)]
    if points:
        d = 'M'+'L'.join(f'{x:.2f} {y:.2f}' for x, y in points)
        body += a.path(d+f'L{points[-1][0]:.2f} {bottom}H{left}Z', 'none', 0, 'url(#area)')
        # The halo follows the same measured line; it is not a separate series.
        body += a.path(d, 'red', 10, extra='opacity=".08"')
        body += a.path(d, 'url(#spectrum)', 3.7, extra='class="draw"')
        for i, (x, y) in enumerate(points):
            if i == 0 or i == len(points)-1 or timeline[i]['month'].endswith('-01'):
                body += a.circle(round(x, 2), round(y, 2), 4, 'panel', f'stroke="{a.color("red")}" stroke-width="2"')
                anchor = 'start' if i == 0 else 'end' if i == len(points)-1 else 'middle'
                body += a.text(round(x, 2), bottom+24, timeline[i]['month'], 9, 'muted', extra=f'text-anchor="{anchor}"')
        last_x, last_y = points[-1]
        body += a.circle(round(last_x, 2), round(last_y, 2), 9, 'none',
                         f'stroke="{a.color("red")}" stroke-opacity=".5" class="ping"')
        body += a.text(round(last_x, 2), round(last_y-15, 2), str(timeline[-1]['cumulative_repositories']),
                       13, 'red', 600, 'text-anchor="end"')
    body += a.text(30, h-37, 'Cumulative repositories by creation month.', 11, 'muted')
    body += a.text(30, h-17, 'Repository creation, not commits · '+data['as_of'], 9, 'muted')
    return a.finish('Public GitHub footprint',
                    f'{data["repository_count"]} repositories, {data["stars"]} stars, {data["forks"]} forks received. Timeline is cumulative repository creation, not commits.',
                    w, h, body, static)


def project_network(a, profile, static=False, mobile=False):
    projects = profile['projects']
    if mobile:
        w, h = 480, 160+len(projects)*169
        body = a.label(26, 34, 'SELECTED PROJECTS / STACK MAP')
        body += a.text(25, 80, 'Ideas meet their tools.', 27, weight=600, extra='letter-spacing="-.8"')
        for i, project in enumerate(projects):
            y, color = 119+i*169, ACCENTS[i % len(ACCENTS)]
            body += a.rect(22, y, 436, 153, 'panel', 19, 'line')
            body += a.rect(126, y+17, 228, 41, 'soft', 13)
            body += a.text(240, y+44, project['name'], 20, color, 600, 'text-anchor="middle"')
            tools = project['stack'].split(' / ')
            gap, chip_width = 13, (396-13*(len(tools)-1))/len(tools)
            for j, label in enumerate(tools):
                x = 42+j*(chip_width+gap)
                center = x+chip_width/2
                body += a.path(f'M240 {y+58}C240 {y+79} {center:.2f} {y+77} {center:.2f} {y+98}',
                               color, 1.5, extra=a.flow(4,7)+f' data-project="{escape(project["name"], quote=True)}" data-technology="{escape(label, quote=True)}"')
                body += a.rect(x, y+98, chip_width, 36, 'bg', 11, 'line')
                body += a.text(round(center, 2), y+121, label, 14, 'ink', 600, 'text-anchor="middle"')
        body += a.text(26, h-17, 'Documented project stacks · each line is a real relationship', 9, 'muted')
        return a.finish('Selected project technology map',
                        'Mobile diagram of the documented technology stack for '+', '.join(p['name'] for p in projects)+'.',
                        w, h, body, static)

    w, h = 960, 580
    body = a.label(30, 34, 'SELECTED PROJECTS / STACK MAP')
    body += a.text(28, 81, 'Different ideas. Shared tools.', 34, weight=600, extra='letter-spacing="-1"')
    body += orbit_mark(a, 896, 58)
    body += a.label(32, 120, 'PROJECTS')+a.label(384, 120, 'DOCUMENTED TECHNOLOGIES')
    tool_names = list(dict.fromkeys(tool for project in projects for tool in project['stack'].split(' / ')))
    nodes = {tool: (382+(i % 3)*183, 153+(i//3)*144) for i, tool in enumerate(tool_names)}
    memberships = {tool: [] for tool in tool_names}
    # Edges are behind both node layers, never an extra measured data series.
    for i, project in enumerate(projects):
        y, color = 149+i*99, ACCENTS[i % len(ACCENTS)]
        for tool in project['stack'].split(' / '):
            x, node_y = nodes[tool]
            # Bow longer edges above the preceding columns, rather than passing
            # through other technology nodes and suggesting nonexistent links.
            control_y = node_y+28 if x == 382 else node_y-70
            d = f'M232 {y+28}C{285+(x-382)*.2:.2f} {y+28} {x-68} {control_y} {x} {node_y+28}'
            body += a.path(d, color, 1.7, extra=a.flow(4,8)+f' opacity=".48" data-project="{escape(project["name"], quote=True)}" data-technology="{escape(tool, quote=True)}"')
            memberships[tool].append(color)
    for i, project in enumerate(projects):
        y, color = 149+i*99, ACCENTS[i % len(ACCENTS)]
        body += a.rect(30, y, 202, 56, 'panel', 16, 'line')
        body += a.rect(30, y+15, 3, 26, color, 1.5)+a.text(49, y+35, project['name'], 19, color, 600)
    for tool, (x, y) in nodes.items():
        color = memberships[tool][0]
        fill = 'url(#spectrum)' if len(memberships[tool]) > 1 else f'url(#accent-{color})'
        body += a.rect(x, y, 165, 56, 'panel', 16, 'line')
        body += a.rect(x+17, y+12, 23, 3, fill, 1.5)+a.text(x+17, y+37, tool, 14, 'ink', 600)
    body += a.text(31, 539, 'Shared nodes connect the same tool across different projects.', 11, 'muted')
    body += a.text(31, 558, 'Only relationships documented in the selected project stacks are shown.', 9, 'muted')
    return a.finish('Selected project technology map',
                    'A diagram of the documented technology stack for '+', '.join(p['name'] for p in projects)+'.',
                    w, h, body, static)


def build_analytics(profile, metrics, technology, Art, static=False, theme='light'):
    a, cards = Art(theme), {}
    for mobile in (False, True):
        suffix = '-mobile' if mobile else ''
        cards['languages'+suffix+'.svg'] = languages(a, metrics, static, mobile)
        cards['repositories'+suffix+'.svg'] = repositories(a, metrics, static, mobile)
        cards['project-network'+suffix+'.svg'] = project_network(a, profile, static, mobile)
        if technology:
            cards.update(skill_pages(a, technology, static, mobile))
    return cards
