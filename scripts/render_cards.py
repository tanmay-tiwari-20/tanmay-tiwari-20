#!/usr/bin/env python3
"""Animated, responsive GitHub artwork. Embedded assets; no dependencies.

Missing activity data shows a decorative build loop, never invented stats.
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
from render_analytics import build_analytics

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    'light': dict(bg='#fffaf7',panel='#fff1e9',soft='#f5e6df',ink='#211411',muted='#6a5751',line='#e4d4cb',blue='#3269d5',violet='#8844c4',red='#dc342f',mint='#008267',yellow='#ac6300',cyan='#007b91',glow='#ffd2c4',palette=['#f1e4de','#ffb7a3','#fa8469','#e55743','#b82f2b']),
    'dark': dict(bg='#000000',panel='#100b0d',soft='#211216',ink='#fff8f3',muted='#c1a9a0',line='#352026',blue='#6bb5ff',violet='#c799ff',red='#ff6558',mint='#44edba',yellow='#ffc45c',cyan='#49dded',glow='#39130f',palette=['#211216','#60201c','#a82f28','#ec4c3f','#ff9a7d']),
}


def font_css():
    rules=[]
    for weight,name in ((400,'Poppins-Regular.woff'),(600,'Poppins-SemiBold.woff')):
        data=base64.b64encode((ROOT/'assets/fonts'/name).read_bytes()).decode('ascii')
        rules.append(f"@font-face{{font-family:Poppins;font-weight:{weight};src:url(data:font/woff;base64,{data}) format('woff')}}")
    return '\n'.join(rules)


FONT_CSS=font_css()
PHOTO=base64.b64encode((ROOT/'assets/portrait.png').read_bytes()).decode('ascii')
MOTION='''
@keyframes float {0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes breathe {0%,100%{opacity:.65}50%{opacity:1}}
@keyframes orbit {to{transform:rotate(360deg)}}
@keyframes dash {to{stroke-dashoffset:-64}}
@keyframes nudge {0%,65%,100%{transform:translate(0,0)}80%{transform:translate(4px,-4px)}}
@keyframes ping {0%,100%{opacity:.25;transform:scale(.95)}50%{opacity:.75;transform:scale(1.04)}}
@keyframes cell-in {0%{opacity:.3;transform:scale(.65)}100%{opacity:1;transform:scale(1)}}
@keyframes dot {0%,60%,100%{opacity:.25}30%{opacity:1}}
@keyframes line-in {0%{stroke-dashoffset:1000}100%{stroke-dashoffset:0}}
@keyframes meter-grow {from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes ring-ink {from{stroke-dasharray:0 1000}}
@keyframes drift {0%,100%{transform:translate(0,0)}50%{transform:translate(5px,-5px)}}
@keyframes sweep {to{stroke-dashoffset:-240}}
.float{animation:float 6s ease-in-out infinite}.float-slow{animation:float 8s ease-in-out -2s infinite}
.breathe{animation:breathe 4s ease-in-out infinite}.orbit{transform-box:fill-box;transform-origin:center;animation:orbit 35s linear infinite}
.flow{animation:dash 4s linear infinite}.arrow{animation:nudge 6s ease-in-out infinite}
.ping{transform-box:fill-box;transform-origin:center;animation:ping 5s ease-in-out infinite}
.cell{transform-box:fill-box;transform-origin:center;animation:cell-in .6s ease-out backwards}
.typing{animation:dot 1.8s ease-in-out infinite}.draw{stroke-dasharray:1000;animation:line-in 2.4s ease-out backwards}
.meter{transform-box:fill-box;transform-origin:left center;animation:meter-grow 1.5s cubic-bezier(.2,.8,.2,1) backwards}
.segment{animation:ring-ink 1.8s ease-out backwards}
.drift{animation:drift 7s ease-in-out infinite}.sweep{animation:sweep 14s linear infinite}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
'''


class Art:
    def __init__(self,theme='light'):
        self.theme=theme
        self.t=THEMES[theme]

    def color(self,value):return self.t.get(value,value)

    def text(self,x,y,value,size=16,color='ink',weight=400,extra=''):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{self.color(color)}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'

    def label(self,x,y,value,color='muted',extra=''):
        return self.text(x,y,value,10,color,600,f'letter-spacing="1.7" {extra}')

    def rect(self,x,y,w,h,fill='panel',rx=14,stroke=None,extra=''):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{self.color(fill)}"'+(f' stroke="{self.color(stroke)}"' if stroke else '')+f' {extra}/>'

    def path(self,d,color='line',width=1.5,fill='none',extra=''):
        return f'<path d="{d}" fill="{self.color(fill)}" stroke="{self.color(color)}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'

    def circle(self,x,y,r,fill='blue',extra=''):
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{self.color(fill)}" {extra}/>'

    def group(self,body,x=0,y=0,cls='',extra=''):
        # Positional transforms stay on outer groups, independent of CSS motion.
        return f'<g transform="translate({x} {y})"><g class="{cls}" {extra}>{body}</g></g>'

    def arrow(self,x,y,color='blue',size=17):
        return self.group(self.path(f'M0 {size}L{size} 0M0 0H{size}V{size}',color,2,extra='class="arrow"'),x,y)

    def pill(self,x,y,value,color='blue',width=None,fill='soft'):
        width=width or len(value)*6.6+26
        return self.rect(x,y,width,29,fill,14)+self.text(x+13,y+19,value,10,color,600)

    def icon(self,kind,x,y,color='blue',scale=1):
        shapes={
            'code':'M9 5L1 13L9 21M25 5L33 13L25 21M21 1L14 26',
            'design':'M3 4H27V28H3ZM3 12H27M11 12V28M21 0V8',
            'refine':'M3 14A12 12 0 0 1 25 7M25 1V8H18M28 16A12 12 0 0 1 6 23M6 29V22H13',
            'ship':'M12 21L9 12Q17 1 30 1Q30 14 20 23ZM12 21L7 26M8 20L1 22L5 11L10 10M20 23L19 29L29 23L29 16M5 28L1 32',
            'chat':'M2 3H30V23H13L5 29V23H2ZM8 10H24M8 16H18',
            'database':'M3 6C3 0 29 0 29 6C29 12 3 12 3 6M3 6V25C3 31 29 31 29 25V6M3 15C3 21 29 21 29 15',
        }
        return f'<g transform="translate({x} {y}) scale({scale})">'+self.path(shapes[kind],color,1.8)+'</g>'

    def finish(self,title,desc,w,h,body,static=False):
        defs=f'''<linearGradient id="wash" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{self.t['glow']}"/><stop offset="1" stop-color="{self.t['bg']}"/></linearGradient>
<linearGradient id="spectrum" x1="0" y1="0" x2="1" y2=".5"><stop stop-color="{self.t['red']}"/><stop offset=".52" stop-color="{self.t['violet']}"/><stop offset="1" stop-color="{self.t['blue']}"/></linearGradient>
<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{self.t['red']}" stop-opacity=".32"/><stop offset="1" stop-color="{self.t['red']}" stop-opacity=".015"/></linearGradient>
<linearGradient id="portrait" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b82f2b"/><stop offset=".65" stop-color="#ef463e"/><stop offset="1" stop-color="#ff977b"/></linearGradient>
<radialGradient id="halo"><stop stop-color="{self.t['red']}" stop-opacity=".2"/><stop offset="1" stop-color="{self.t['red']}" stop-opacity="0"/></radialGradient>
<clipPath id="bounds"><rect width="{w}" height="{h}" rx="24"/></clipPath>'''
        for color in ('blue','violet','red','mint','yellow','cyan'):
            defs+=f'<linearGradient id="accent-{color}" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{self.t[color]}" stop-opacity=".6"/><stop offset="1" stop-color="{self.t[color]}"/></linearGradient>'
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" data-theme="{self.theme}">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><defs>{defs}</defs>
<style>{FONT_CSS}
text{{font-family:Poppins,Arial,sans-serif}}{'' if static else MOTION}</style>
<g clip-path="url(#bounds)">{self.rect(0,0,w,h,'bg',24)}{body}</g>
{self.rect(.5,.5,w-1,h-1,'none',24,'line')}
</svg>\n'''


def portrait_scene(a,x,y,w,h):
    body=a.rect(39,29,w-58,h-48,'soft',16)+a.rect(23,13,w-58,h-48,'url(#portrait)',16)
    for offset in range(52,int(w-26),48):body+=a.path(f'M{offset} 14V{h-35}','#ffffff',.65,extra='opacity=".14"')
    for offset in range(61,int(h-30),48):body+=a.path(f'M24 {offset}H{w-36}','#ffffff',.65,extra='opacity=".14"')
    body+=a.circle(w/2,h/2-5,min(w,h)*.38,'none','stroke="#ffd2c4" stroke-width="1.4" opacity=".6"')
    body+=a.circle(w/2,h/2-5,min(w,h)*.43,'none','stroke="#ffd2c4" stroke-width="1.4" stroke-dasharray="4 18" opacity=".7" class="orbit"')
    body+=f'<image x="0" y="5" width="{w}" height="{h-9}" preserveAspectRatio="xMidYMax meet" href="data:image/png;base64,{PHOTO}"/>'
    # Small orbit details stay beyond the silhouette, keeping the subject intact.
    body+=a.group(a.path('M-9 0H9M0 -9V9','yellow',2),w-13,30,'float')
    body+=a.group(a.circle(0,0,7,'mint')+a.circle(0,0,13,'none',f'stroke="{a.t["mint"]}" opacity=".4"'),10,h-40,'float-slow')
    return a.group(body,x,y)


def hero(profile,static=False,theme='light',mobile=False):
    a=Art(theme)
    if mobile:
        body=a.label(28,35,'@'+profile['username'].upper(),'red')+a.circle(445,31,4,'mint','class="breathe"')
        body+=a.path('M28 54H452','line',1)
        body+=a.text(25,124,profile['first_name'],63,weight=600,extra='letter-spacing="-3"')
        body+=a.text(22,205,profile['last_name'],86,'red',600,extra='letter-spacing="-4"')
        body+=a.text(29,247,profile['role'],21,weight=600)+a.text(29,278,'Ideas into experiences.',16,'muted')
        body+=portrait_scene(a,54,298,374,362)
        body+=a.path('M29 680H451','line',1)+a.label(29,713,'CREATIVE CODE / HUMAN CONNECTIONS')+a.arrow(428,695,'red')
        return a.finish(profile['name'],profile['tagline']+' Supplied portrait. Open to collaboration.',480,734,body,static)
    body=a.circle(785,205,247,'url(#halo)')+a.label(36,40,'@'+profile['username'].upper(),'red')
    body+=a.circle(731,36,4,'mint','class="breathe"')+a.text(744,41,'Open to collaboration',12,'muted')+a.path('M36 62H924','line',1)
    body+=a.text(31,176,profile['first_name'],93,weight=600,extra='letter-spacing="-4"')
    body+=a.text(26,283,profile['last_name'],118,'red',600,extra='letter-spacing="-6"')
    body+=a.text(37,332,profile['role'],23,weight=600)+a.text(37,365,profile['tagline'],15,'muted')
    body+=a.pill(37,392,'REAL-TIME APPS','red',138)+a.pill(185,392,'CREATIVE CODE','violet',140)
    body+=a.path('M440 344C513 347 505 206 565 220M552 208L566 220L551 227','red',1.8,extra='stroke-dasharray="6 5" class="flow"')
    body+=portrait_scene(a,558,86,377,372)
    body+=a.path('M36 481H924','line',1)+a.label(37,518,'DESIGN / BUILD / SHIP')
    body+=a.text(675,520,'BASED IN INDIA',10,'muted',600,extra='letter-spacing="1.8"')+a.arrow(900,502,'red')
    body+=a.path('M36 536H330','red',2,extra='stroke-dasharray="42 20 7 20" class="flow" opacity=".65"')
    return a.finish(profile['name']+' / Full Stack Developer',profile['tagline']+' Based in India, open to collaboration. Portrait and coral editorial styling inspired by his portfolio.',960,558,body,static)


def build_loop(static=False,theme='light'):
    a=Art(theme)
    body=a.circle(923,145,177,'url(#wash)','opacity=".5"')+a.label(32,33,'THE BUILD LOOP')
    body+=a.text(30,78,'Curiosity. Code. Repeat.',32,weight=600)+a.text(33,105,'From a first idea to something people can use.',14,'muted')
    body+=a.path('M131 169H829','line',2)+a.path('M131 169H829','blue',2,extra='stroke-dasharray="9 23" class="flow"')
    for i,(name,icon,color) in enumerate((('Explore','design','blue'),('Build','code','violet'),('Refine','refine','red'),('Ship','ship','mint'))):
        x=130+i*233
        body+=a.circle(x,169,32,'panel',f'stroke="{a.color(color)}" stroke-opacity=".28"')
        body+=a.circle(x,169,39,'none',f'stroke="{a.color(color)}" stroke-opacity=".18" class="ping" style="animation-delay:{i*.8}s"')
        body+=a.icon(icon,x-15,155,color,.95)+a.text(x,228,name,14,'ink',600,'text-anchor="middle"')
    return a.finish('The build loop','Decorative illustration of exploring, building, refining and shipping. This is a workflow illustration, not an activity chart or measured statistics.',960,258,body,static)


def heatmap(data,static=False,theme='light',mobile=False):
    if data is None:return build_loop(static,theme)
    a=Art(theme)
    if mobile:
        body=a.label(28,32,'ACTIVITY / LAST 365 DAYS','red')+a.text(26,78,f'{data["total"]:,} contributions',29,weight=600)
        body+=a.rect(23,102,434,119,'panel',14,'line')+a.rect(23,242,434,119,'panel',14,'line')
        first=date.fromisoformat(data['days'][0]['date']);start=first-timedelta(days=(first.weekday()+1)%7);prev=None
        for day in data['days']:
            d=date.fromisoformat(day['date']);col,row=divmod((d-start).days,7);block,local=divmod(col,27);x,y=34+local*15.2,125+block*140+row*13.4
            if d.month!=prev and (d.day<=7 or prev is None):
                body+=a.text(x,115+block*140,calendar.month_abbr[d.month],8,'muted');prev=d.month
            body+=f'<rect x="{x:.1f}" y="{y:.1f}" width="11" height="10" rx="2.8" fill="{a.t["palette"][day["level"]]}" class="cell" style="animation-delay:{col*.012+row*.016:.3f}s"><title>{day["date"]}: {day["count"]} contributions</title></rect>'
        body+=a.text(28,387,f'{data["active_days"]} active days · through {data["as_of"]}',11,'muted')
        return a.finish('GitHub activity',f'{data["total"]} contributions over 365 days ending {data["as_of"]}. Calendar continues left to right across the two blocks.',480,409,body,static)
    body=a.label(32,33,'ACTIVITY / LAST 365 DAYS')+a.text(30,78,'Consistency, in motion.',32,weight=600)
    body+=a.text(923,76,f'{data["total"]:,} contributions',19,'blue',600,'text-anchor="end"')+a.rect(26,104,908,145,'panel',18,'line')
    first=date.fromisoformat(data['days'][0]['date']);start=first-timedelta(days=(first.weekday()+1)%7);prev=None
    for day in data['days']:
        d=date.fromisoformat(day['date']);col,row=divmod((d-start).days,7);x,y=47+col*16.4,137+row*14.1
        if d.month!=prev and (d.day<=7 or prev is None):
            body+=a.text(x,126,calendar.month_abbr[d.month],9,'muted');prev=d.month
        body+=f'<rect x="{x}" y="{y}" width="11.5" height="10" rx="3" fill="{a.t["palette"][day["level"]]}" class="cell" style="animation-delay:{col*.012+row*.016:.3f}s"><title>{day["date"]}: {day["count"]} contributions</title></rect>'
    body+=a.text(32,279,f'{data["active_days"]} active days  ·  {data["current_streak"]}-day streak',12,'muted')+a.label(923,279,'THROUGH '+data['as_of'],extra='text-anchor="end"')
    return a.finish('GitHub activity',f'{data["total"]} contributions over 365 days ending {data["as_of"]}. Daily counts are exact public GitHub data.',960,304,body,static)


def activity(data,static=False,theme='light',mobile=False):
    if data is None:return build_loop(static,theme)
    a=Art(theme);w,h=(480,454) if mobile else (960,391)
    body=a.label(30,32,'THE YEAR IN MOTION','red')+a.text(28,77,'Small steps. Real progress.',24 if mobile else 32,weight=600)
    months=data['months'];maximum=max(m['count'] for m in months) or 1
    left,right,top,bottom=(34,446,131,247) if mobile else (44,916,115,247)
    for i in range(3):body+=a.path(f'M{left} {top+i*(bottom-top)/2}H{right}','line',1,extra='stroke-dasharray="3 8"')
    points=[(left+i*(right-left)/max(1,len(months)-1),bottom-m['count']/maximum*(bottom-top)) for i,m in enumerate(months)]
    d='M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in points)
    body+=a.path(d+f'L{right} {bottom}H{left}Z','none',0,'url(#area)')+a.path(d,'url(#spectrum)',3,extra='class="draw"')
    for i,(x,y) in enumerate(points):
        m=date.fromisoformat(months[i]['month']+'-01')
        body+=a.circle(round(x,2),round(y,2),3.5,'red')+a.text(round(x,2),271,m.strftime('%b'),8 if mobile else 10,'muted',extra='text-anchor="middle"')
        body+=a.text(round(x,2),round(y-12,2),months[i]['count'],9,'muted',extra='text-anchor="middle"')
    body+=a.text(30 if mobile else 44,298,'Rolling year · first and last months are partial',9,'muted')
    for i,(value,caption,color) in enumerate(((data['current_streak'],'DAY STREAK','blue'),(data['active_days'],'ACTIVE DAYS','violet'),(data['longest_streak'],'LONGEST STREAK','mint'),(data['best_day']['count'],'BEST DAY (COUNT)','red'))):
        x,y=(30+(i%2)*225,344+(i//2)*72) if mobile else (44+i*225,343)
        body+=a.text(x,y,str(value),30,color,600)+a.text(x+63 if mobile else x,y+1 if mobile else y+25,caption,9,'muted',600)
    return a.finish('Monthly activity',f'Monthly contribution totals. Longest streak {data["longest_streak"]}; best day {data["best_day"]["date"]}: {data["best_day"]["count"]} contributions.',w,h,body,static)


def tile(kind,static=False,theme='light'):
    a=Art(theme)
    color,icon,title,copy,cta={
        'build':('blue','code','Build.','Projects that work.','EXPLORE THE CODE'),
        'create':('violet','design','Create.','Interfaces with character.','VISIT MY PORTFOLIO'),
        'connect':('mint','chat','Connect.','Great things start together.','LET’S COLLABORATE'),
    }[kind]
    body=a.circle(281,18,92,'url(#wash)')+a.circle(272,25,52,'none',f'stroke="{a.color(color)}" stroke-opacity=".16" class="ping"')
    body+=a.rect(24,23,49,47,'soft',15)+a.icon(icon,33,32,color,.9)+a.arrow(266,29,color)
    body+=a.text(22,121,title,34,color,600,extra='letter-spacing="-1"')+a.text(25,153,copy,12,'muted')+a.path('M25 178H287','line',1)+a.label(25,205,cta,color)
    return a.finish(title,copy+' '+cta.capitalize()+'.',312,230,body,static)


def project_visual(a,kind):
    body=a.rect(0,0,326,181,'soft',20)+a.circle(300,13,80,'url(#wash)')
    if kind=='cards':
        body+=f'<ellipse cx="160" cy="145" rx="124" ry="23" fill="none" stroke="{a.t["blue"]}" stroke-opacity=".23" stroke-dasharray="3 8" class="flow"/>'
        for i,(x,y,angle,color,value) in enumerate(((91,31,-15,'violet','7'),(133,20,0,'blue','8'),(178,31,15,'red','+2'))):
            card=a.rect(0,0,66,105,color,11)+f'<ellipse cx="33" cy="54" rx="24" ry="36" fill="none" stroke="white" stroke-width="2" opacity=".6"/>'+a.text(33,65,value,29,'#ffffff',600,'text-anchor="middle"')+a.text(9,20,value,9,'#ffffff',600)
            body+=a.group(f'<g transform="rotate({angle} 33 52)">{card}</g>',x,y,'float',f'style="animation-delay:-{i*1.5}s"')
        body+=a.circle(50,51,4,'yellow','class="breathe"')+a.circle(272,123,3,'mint','class="breathe"')
    elif kind=='circles':
        body+=a.path('M63 53L260 126M63 126L260 53','line',1.5,extra='stroke-dasharray="5 8" class="flow"')
        for i,(x,y,w,c) in enumerate(((30,26,175,'violet'),(107,86,185,'blue'))):
            chat=a.rect(0,0,w,62,'panel',15,'line')+a.circle(23,22,11,c)+a.rect(43,16,w-60,6,'line',3)+a.rect(43,29,w-87,5,'line',3)
            for j in range(3):chat+=a.circle(46+j*10,46,2.6,c,f'class="typing" style="animation-delay:{j*.25}s"')
            body+=a.group(chat,x,y,'float' if i==0 else 'float-slow')
    elif kind=='video':
        for i,(x,y,c) in enumerate(((45,20,'blue'),(164,20,'violet'),(45,82,'mint'),(164,82,'red'))):
            body+=a.rect(x,y,107,56,'panel',10,'line')+a.circle(x+53,y+19,9,c,'opacity=".8"')+a.path(f'M{x+33} {y+46}Q{x+35} {y+29} {x+53} {y+31}Q{x+72} {y+29} {x+73} {y+46}',c,1,c,extra='opacity=".55"')
            body+=a.circle(x+94,y+11,2.7,'mint',f'class="breathe" style="animation-delay:{i*.6}s"')
        body+=a.rect(110,149,106,22,'panel',11,'line')+a.circle(135,160,4,'muted')+a.circle(161,160,4,'muted')+a.rect(181,154,21,12,'red',6)
    else:
        doc=a.rect(0,0,125,143,'panel',12,'line')+a.circle(22,24,9,'blue')+a.rect(41,18,61,6,'line',3)+a.rect(41,30,40,4,'line',2)
        for i in range(4):doc+=a.rect(16,56+i*18,91 if i%2==0 else 67,5,'line',2)
        doc+=a.rect(12,75,102,12,'blue',3,extra='opacity=".12" class="breathe"')+''
        body+=a.group(doc,82,18,'float-slow')
        for i,(x,y,txt,col) in enumerate(((181,58,'Review','violet'),(184,111,'Improve','mint'))):
            chip=a.rect(0,0,106,34,'panel',11,'line')+a.path('M11 17L16 22L24 12',col,2)+a.text(33,22,txt,11,'ink',600)
            body+=a.group(chip,x,y,'float',f'style="animation-delay:-{i*2}s"')
    return body


def project_card(project,index,static=False,theme='light',mobile=False):
    a=Art(theme);accent={'yellow':'mint','red':'red','blue':'blue'}[project['accent']]
    if mobile:
        body=a.group('<g transform="scale(1.36 .72)">'+project_visual(a,project['icon'])+'</g>',18,15)
        body+=a.label(24,174,project['category'])+a.arrow(433,159,accent)+a.text(22,215,project['name'],31,weight=600,extra='letter-spacing="-.8"')
        for i,value in enumerate(project['description']):body+=a.text(24,245+i*24,value,16,'muted')
        body+=a.path('M24 287H456','line',1)+a.text(24,312,project['stack'],11,accent,600)
        return a.finish(project['name'],' '.join(project['description'])+' '+project['stack'],480,330,body,static)
    body=a.label(31,35,project['category'])+a.arrow(569,23,accent,15)+a.text(29,89,project['name'],37,weight=600,extra='letter-spacing="-1"')
    for i,value in enumerate(project['description']):body+=a.text(32,125+i*26,value,17,'muted')
    body+=a.path('M32 178H587','line',1)+a.text(32,209,project['stack'],12,accent,600)+a.group(project_visual(a,project['icon']),611,30)
    return a.finish(project['name'],' '.join(project['description'])+' Stack: '+project['stack'],960,244,body,static)


def stack_card(profile,static=False,theme='light'):
    a=Art(theme)
    body=a.label(32,34,'THE TOOLKIT')+a.text(31,78,'Good tools. Better possibilities.',30,weight=600)
    for i,(group,icon,color) in enumerate(zip(profile['stack'],('design','database','code'),('blue','violet','mint'))):
        x=29+i*304
        body+=a.rect(x,104,294,128,'panel',18,'line')+a.icon(icon,x+18,124,color,.65)+a.label(x+51,141,group['label'],color)
        body+=a.text(x+18,179,group['lines'][0],16,weight=600)+a.text(x+18,207,group['lines'][1],13,'muted')
    return a.finish('The toolkit','; '.join(g['label']+': '+', '.join(g['lines']) for g in profile['stack']),960,258,body,static)


def social_icon(a,kind,x,y,color='red',scale=1):
    paths={
        'portfolio':'M3 16A13 13 0 1 0 29 16A13 13 0 1 0 3 16M3 16H29M16 3C7 11 7 21 16 29C25 21 25 11 16 3Z',
        'linkedin':'M5 12V28M5 5V5.1M13 28V12H19V15C25 7 30 13 30 19V28M19 28V20',
        'instagram':'M10 3H23Q30 3 30 10V23Q30 30 23 30H10Q3 30 3 23V10Q3 3 10 3ZM23 16.5A6.5 6.5 0 1 0 10 16.5A6.5 6.5 0 1 0 23 16.5M24 9H24.1',
        'github':'M11 30V24C5 25 5 21 2 20M23 30V24C23 21 22 20 21 20C29 19 31 15 29 9L28 3L21 6C18 5 14 5 11 6L4 3L3 9C1 15 3 19 11 20C10 21 10 23 11 24',
        'email':'M3 6H29V27H3ZM3 7L16 18L29 7M3 27L12 17M29 27L20 17',
    }
    return f'<g transform="translate({x} {y}) scale({scale})">'+a.path(paths[kind],color,2)+'</g>'


def connect(static=False,theme='light',mobile=False):
    a=Art(theme);w=480 if mobile else 960
    body=a.label(30,34,'FIND ME / AROUND THE INTERNET','red')
    body+=a.text(28,83,'Let’s connect.',34 if mobile else 40,weight=600,extra='letter-spacing="-1.5"')
    if not mobile:
        body+=a.path('M404 64C527 1 610 120 786 53','line',1.5)
        body+=a.path('M404 64C527 1 610 120 786 53','red',2,extra='stroke-dasharray="14 26" class="flow"')
        for i,(x,y,col) in enumerate(((481,44,'red'),(624,69,'violet'),(767,59,'blue'))):
            body+=a.circle(x,y,5,col,'class="breathe"')
        body+=a.arrow(900,54,'red',22)
    else:body+=a.arrow(425,61,'red',22)
    return a.finish('Find Tanmay online','Open my portfolio, LinkedIn, Instagram, GitHub or email using the individual links below.',w,111,body,static)


def social_card(kind,profile,static=False,theme='light',mobile=False):
    a=Art(theme)
    if kind=='portfolio':
        w,h=(480,176) if mobile else (960,156)
        body=a.rect(10,10,w-20,h-20,'panel',18)
        body+=a.rect(10,10,7,h-20,'red',3.5)
        if mobile:
            body+=social_icon(a,'portfolio',35,39,'red',1.2)+a.text(92,66,'Portfolio',33,'ink',600)
            body+=a.text(36,111,'takneekitanmay.tech',19,'red',600)+a.text(36,143,'Projects, experiments & a little more me.',12,'muted')
            body+=a.arrow(417,51,'red',25)
        else:
            body+=social_icon(a,'portfolio',42,53,'red',1.4)+a.label(111,44,'MY DIGITAL HOME','red')
            body+=a.text(109,94,'Portfolio',39,weight=600,extra='letter-spacing="-1"')+a.text(112,124,'Projects, experiments & a little more me.',13,'muted')
            body+=a.path('M530 33V124','line',1)+a.text(568,88,'takneekitanmay.tech',23,'red',600)
            body+=a.circle(891,77,28,'soft')+a.arrow(880,66,'red',21)
        return a.finish('Visit my portfolio','Visit '+profile['portfolio']+' for my projects and creative work.',w,h,body,static)
    title,subtitle,color={
        'linkedin':('LinkedIn','Ideas, work & connections','blue'),
        'instagram':('Instagram','Behind the work','red'),
        'github':('GitHub','Explore my repositories','violet'),
        'email':('Let’s talk','Work together on an idea','mint'),
    }[kind]
    body=a.circle(447,12,88,'url(#halo)')+a.rect(23,33,61,61,'soft',18)
    body+=social_icon(a,kind,37,46,color,1)+a.text(107,63,title,30,'ink',600,extra='letter-spacing="-.8"')
    body+=a.text(109,89,subtitle,13,'muted')+a.arrow(424,51,color,18)
    body+=a.path('M108 107H367',color,1.6,extra='stroke-dasharray="34 89" class="flow" opacity=".65"')
    return a.finish(title+' / Tanmay Tiwari',subtitle+'. Click this graphic to '+('send Tanmay an email.' if kind=='email' else 'open his '+title+' profile.'),470,129,body,static)


def build_social(profile,static=False,theme='light'):
    cards={'connect.svg':connect(static,theme),'connect-mobile.svg':connect(static,theme,True)}
    for kind in ('portfolio','linkedin','instagram','github','email'):
        cards['social-'+kind+'.svg']=social_card(kind,profile,static,theme)
    cards['social-portfolio-mobile.svg']=social_card('portfolio',profile,static,theme,True)
    return cards


def footer(profile,static=False,theme='light',mobile=False):
    a=Art(theme)
    if mobile:
        body=a.circle(437,160,163,'url(#halo)')+a.label(29,35,'HAVE AN IDEA? / LET’S BUILD IT','red')
        body+=a.text(27,91,'Good things start',30,weight=600)+a.text(27,131,'with a conversation.',29,'red',600)
        body+=a.text(30,174,profile['email'],13,'muted')+a.arrow(423,148,'red',22)
        return a.finish('Let’s build together','Contact Tanmay at '+profile['email'],480,203,body,static)
    body=a.circle(810,70,226,'url(#halo)')+a.label(33,35,'HAVE AN IDEA? / LET’S BUILD IT','red')
    body+=a.text(30,95,'Good things start with a conversation.',33,weight=600,extra='letter-spacing="-1"')+a.text(33,135,profile['email'],14,'muted')
    body+=a.circle(879,88,36,'red')+a.arrow(867,76,'#ffffff',24)
    return a.finish('Let’s build together','Contact Tanmay at '+profile['email'],960,171,body,static)


def load_activity(path,username):
    if not path.exists():return None
    payload=json.loads(path.read_text(encoding='utf-8'))
    if payload.get('username')!=username:raise ValueError('Contribution data belongs to another account')
    end=date.fromisoformat(payload['as_of']);days=payload['days']
    expected=[(end-timedelta(days=364-i)).isoformat() for i in range(365)]
    if [d['date'] for d in days]!=expected:raise ValueError('Contribution data must contain exactly 365 chronological days')
    for day in days:
        if type(day['count']) is not int or day['count']<0 or type(day['level']) is not int or day['level'] not in range(5):raise ValueError('Invalid count or intensity level')
        if (day['count']==0)!=(day['level']==0):raise ValueError('Contribution count and intensity disagree')
    derived=summarize(username,end,days)
    if payload!=derived:raise ValueError('Activity summary does not match its daily counts')
    return derived


def build_cards(profile,data,static=False,theme='light'):
    if theme not in THEMES:raise ValueError('Unknown theme')
    metrics=json.loads((ROOT/'data/repository-metrics.json').read_text(encoding='utf-8'))
    technology_path=ROOT/'data/technologies.json'
    technologies=json.loads(technology_path.read_text(encoding='utf-8')) if technology_path.exists() else None
    if metrics['username']!=profile['username'] or (technologies and technologies['username']!=profile['username']):raise ValueError('Repository metrics belong to another account')
    cards={'hero.svg':hero(profile,static,theme),'hero-mobile.svg':hero(profile,static,theme,True),'footer.svg':footer(profile,static,theme),'footer-mobile.svg':footer(profile,static,theme,True)}
    cards.update(build_social(profile,static,theme))
    cards.update(build_analytics(profile,metrics,technologies,Art,static,theme))
    if data is not None:
        cards['heatmap.svg']=heatmap(data,static,theme)
        cards['heatmap-mobile.svg']=heatmap(data,static,theme,True)
        cards['activity.svg']=activity(data,static,theme)
        cards['activity-mobile.svg']=activity(data,static,theme,True)
    for name,value in cards.items():
        ET.fromstring(value)
        if '<script' in value or '<foreignObject' in value or re.search(r'href="(?!data:image/png;base64,)',value):raise ValueError('Unexpected active or external content in '+name)
    return cards


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,default=ROOT/'data/profile.json')
    parser.add_argument('--data',type=Path,default=ROOT/'data/contributions.json')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--theme',choices=('light','dark','both'),default='both')
    parser.add_argument('--static',action='store_true',default=os.environ.get('STATIC')=='1')
    args=parser.parse_args();output=args.output or ROOT/('work/static-cards' if args.static else 'cards')
    profile=json.loads(args.profile.read_text(encoding='utf-8'));data=load_activity(args.data,profile['username'])
    themes=THEMES if args.theme=='both' else (args.theme,)
    generated={theme:build_cards(profile,data,args.static,theme) for theme in themes}
    for theme,cards in generated.items():
        destination=output/theme;destination.mkdir(parents=True,exist_ok=True)
        for name,value in cards.items():
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',newline='\n',dir=destination,delete=False) as f:
                f.write(value);temp=Path(f.name)
            temp.replace(destination/name)
    if not args.static and args.output is None and args.theme=='both':
        manifest={'themes':['light','dark'],'cards':sorted(generated['light'])}
        (ROOT/'data/card-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'Rendered {sum(map(len,generated.values()))} graphics: {", ".join(generated)}. Repository analytics included; contribution calendar {"included" if data else "unavailable and omitted"}.')


if __name__=='__main__':main()
