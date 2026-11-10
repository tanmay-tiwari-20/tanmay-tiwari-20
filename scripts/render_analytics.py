"""Animated SVG graphs drawn only from the checked-in GitHub audit."""
from html import escape
import math

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


def footprint(a, tech, static=False, mobile=False):
    entries = tech.get('language_presence', [])
    if not entries:
        return None
    w, h = (480, 731) if mobile else (960, 474)
    cx, cy, r = (240, 276, 119) if mobile else (235, 274, 124)
    n = len(entries)
    body = a.label(30, 33, 'LANGUAGE FOOTPRINT / FILE EVIDENCE')
    body += a.text(28, 80, 'Across the whole stack.', 26 if mobile else 34, weight=600,
                   extra='letter-spacing="-.8"')
    body += a.text(30, 108, f'Language presence across {tech["repository_count"]} public projects.', 12, 'muted')
    if not mobile:
        body += a.rect(443, 131, 488, 288, 'panel', 18, 'line')
        body += orbit_mark(a, 896, 55, 'violet')
    for level in (.25, .5, .75, 1):
        points = [(cx+math.cos(-math.pi/2+i*2*math.pi/n)*r*level,
                   cy+math.sin(-math.pi/2+i*2*math.pi/n)*r*level) for i in range(n)]
        body += a.path('M'+'L'.join(f'{x:.1f} {y:.1f}' for x, y in points)+'Z', 'line', 1,
                       extra='stroke-dasharray="3 5"' if level < 1 else '')
    vertices = []
    for i, entry in enumerate(entries):
        angle = -math.pi/2+i*2*math.pi/n
        x, y = cx+math.cos(angle)*r, cy+math.sin(angle)*r
        body += a.path(f'M{cx} {cy}L{x:.1f} {y:.1f}', 'line', 1)
        share = entry['count']/tech['repository_count']
        vertices.append((cx+math.cos(angle)*r*share, cy+math.sin(angle)*r*share))
        label_x, label_y = cx+math.cos(angle)*(r+23), cy+math.sin(angle)*(r+23)+4
        anchor = 'middle' if abs(math.cos(angle)) < .1 else 'start' if math.cos(angle) > 0 else 'end'
        body += a.text(round(label_x, 1), round(label_y, 1), entry['name'], 10, 'muted', 600,
                       f'text-anchor="{anchor}"')
    shape = 'M'+'L'.join(f'{x:.1f} {y:.1f}' for x, y in vertices)+'Z'
    body += a.path(shape, 'url(#spectrum)', 2.5, 'url(#area)', extra='class="draw"')
    for i, (x, y) in enumerate(vertices):
        body += a.circle(round(x, 1), round(y, 1), 5, ACCENTS[i % len(ACCENTS)],
                         f'stroke="{a.color("bg")}" stroke-width="2"')
    for i, entry in enumerate(entries):
        color = ACCENTS[i % len(ACCENTS)]
        if mobile:
            x, y, bar_width = 29+(i % 2)*230, 466+(i//2)*70, 204
            body += a.rect(x-8, y-22, 220, 62, 'panel', 13, 'line')
        else:
            x, y, bar_width = 463, 162+i*43, 448
        body += a.text(x, y, entry['name'], 15, 'ink', 600)
        body += a.text(x+bar_width, y, percent(entry['percent']), 15 if mobile else 16, color, 600, 'text-anchor="end"')
        body += a.text(x, y+17, f'{entry["count"]} of {tech["repository_count"]} projects', 10 if mobile else 9, 'muted')
        body += a.rect(x, y+26, bar_width, 5, 'soft', 2.5)
        body += a.rect(x, y+26, bar_width*entry['count']/tech['repository_count'], 5,
                       f'url(#accent-{color})', 2.5, extra='class="meter"')
    body += a.text(30, h-33, 'Repositories containing source files.', 11, 'muted')
    body += a.text(30, h-14, 'A project can contain several languages; percentages overlap.', 9, 'muted')
    return a.finish('Languages present in source files',
                    'Percentage of audited repositories containing source files in each language. A repository may contain several languages; percentages overlap.',
                    w, h, body, static)


def technology_pages(a, tech, static=False, mobile=False):
    entries, page_size = tech['technologies'], 20
    total_pages = math.ceil(len(entries)/page_size)
    cards = {}
    for page in range(total_pages):
        items = entries[page*page_size:(page+1)*page_size]
        rows = len(items) if mobile else math.ceil(len(items)/2)
        w, h = (480 if mobile else 960), 162+rows*66
        body = a.label(30, 33, f'TECHNOLOGY ATLAS / {page+1:02} OF {total_pages:02}')
        body += a.text(28, 78, 'The tools I build with.', 26 if mobile else 34, weight=600,
                       extra='letter-spacing="-.8"')
        body += a.text(30, 107, f'% of {tech["repository_count"]} public projects using each technology', 11, 'muted')
        if not mobile:
            body += orbit_mark(a, 896, 58, ACCENTS[page % len(ACCENTS)])
        for i, item in enumerate(items):
            column, row = (0, i) if mobile else (i//rows, i % rows)
            x, y, bar_width = 30+column*465, 153+row*66, 414
            color = ACCENTS[(page*page_size+i) % len(ACCENTS)]
            size = (16 if mobile else 13) if len(item['name']) <= 30 else (12 if mobile else 10)
            body += a.rect(x-11, y-25, 438, 59, 'panel', 13, 'line')
            body += a.text(x, y-4, item['name'], size, 'ink', 600)
            body += a.text(x+bar_width, y-4, f'{item["count"]}/{tech["repository_count"]} · {percent(item["percent"])}',
                           12 if mobile else 11, color, 600, 'text-anchor="end"')
            body += a.text(x, y+13, item.get('category', 'Declared technology'), 9, 'muted')
            body += a.rect(x, y+23, bar_width, 5, 'soft', 2.5)
            length = bar_width*item['count']/tech['repository_count']
            body += a.rect(x, y+23, length, 5, f'url(#accent-{color})', 2.5,
                           extra=f'class="meter" style="animation-delay:{row*.055}s"')
            if length > 0:
                body += a.circle(round(x+length, 2), y+25.5, 2.5, color, 'class="breathe"')
        body += a.text(30, h-15, 'Declared direct dependencies + verified CDN usage; percentages overlap.', 9, 'muted')
        filename = f'technologies-{page+1:02}'+('-mobile' if mobile else '')+'.svg'
        desc = 'Every percentage is repositories declaring that technology divided by the audited repository count. '
        desc += '; '.join(f'{item["name"]}: {item["count"]} repos, {percent(item["percent"])}' for item in items)
        cards[filename] = a.finish('Technology coverage '+str(page+1), desc, w, h, body, static)
    return cards


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
            chart = footprint(a, technology, static, mobile)
            if chart:
                cards['footprint'+suffix+'.svg'] = chart
            cards.update(technology_pages(a, technology, static, mobile))
    return cards
