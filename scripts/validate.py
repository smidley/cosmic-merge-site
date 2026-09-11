#!/usr/bin/env python3
"""Dependency-free structural, local-link and design-token contrast checks."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.ids=set(); self.links=[]; self.images=[]; self.metas={}; self.canonicals=[]; self.scripts=[]
    def handle_starttag(self, tag, attributes):
        attrs=dict(attributes); self.tags.append((tag,attrs))
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate id {attrs['id']}"
            self.ids.add(attrs['id'])
        if tag=='a': self.links.append(attrs.get('href',''))
        if tag=='img': self.images.append(attrs)
        if tag=='meta': self.metas[attrs.get('name',attrs.get('property',''))]=attrs.get('content','')
        if tag=='link':
            self.links.append(attrs.get('href',''))
            if attrs.get('rel')=='canonical': self.canonicals.append(attrs['href'])
        if tag=='script': self.scripts.append(attrs)

pages={}
for path in sorted(ROOT.glob('*.html')):
    page=Page(); page.feed(path.read_text()); pages[path.name]=page
    assert sum(tag=='h1' for tag,_ in page.tags)==1, f'{path.name}: needs one h1'
    assert any(tag=='main' for tag,_ in page.tags), f'{path.name}: missing main'
    assert any(tag=='html' and attrs.get('lang')=='en' for tag,attrs in page.tags)
    assert len(page.canonicals)==1 and page.canonicals[0].startswith('https://smidley.github.io/cosmic-merge-site/')
    for key in ['viewport','description','og:title','og:description','og:image','twitter:card']:
        assert page.metas.get(key), f'{path.name}: missing {key}'
    assert all(not attrs.get('src') for attrs in page.scripts), 'unexpected third-party script'
    for image in page.images:
        assert 'alt' in image and image.get('width') and image.get('height'), f'{path.name}: image semantics'
        source=ROOT/image['src']; assert source.is_file(), f'missing {source}'
        assert source.stat().st_size < 1_200_000, f'{source.name}: optimize image delivery'
    for raw in page.links:
        parsed=urlparse(raw)
        if parsed.scheme or parsed.netloc: continue
        target=unquote(parsed.path) or path.name
        target=target.removeprefix('./') or 'index.html'
        assert (ROOT/target).is_file(), f'{path.name}: missing local link {raw}'
        if parsed.fragment:
            destination=Page(); destination.feed((ROOT/target).read_text())
            assert parsed.fragment in destination.ids, f'{path.name}: missing fragment {raw}'
    print(f'{path.name}: landmarks, metadata, image semantics and local links pass')

css=(ROOT/'assets/site.css').read_text()
assert 'prefers-reduced-motion:reduce' in css and ':focus-visible' in css
colors=dict(re.findall(r'--([a-z]+):\s*(#[0-9a-fA-F]{6})',css))
def luminance(color):
    channels=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in channels]
    return sum(v*w for v,w in zip(linear,[0.2126,0.7152,0.0722]))
def contrast(a,b):
    a,b=sorted([luminance(a),luminance(b)])
    return (b+0.05)/(a+0.05)
for foreground in ('text','muted','accent'):
    ratios=[contrast(colors[foreground],background) for background in [colors['bg'],colors['panel'],'#23204b','#141c34']]
    assert min(ratios)>=4.5, f'{foreground}: insufficient contrast {min(ratios):.2f}'
    print(f'{foreground}: at least {min(ratios):.2f}:1 against page/panel colors')
assert contrast(colors['ink'],colors['button'])>=4.5
home=(ROOT/'index.html').read_text()
structured=re.search(r'<script type="application/ld\+json">(.*?)</script>',home,re.S)
assert structured and json.loads(structured.group(1))['@type']=='VideoGame'
print('Structured app data, reduced motion and keyboard focus styles pass')
