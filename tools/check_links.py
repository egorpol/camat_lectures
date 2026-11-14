"""Check the local links and #anchors of built pages (mkdocs --strict skips anchors).

Usage: python tools/check_links.py SITE_DIR PAGE.html [PAGE.html ...]
"""
import sys, re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
site = Path(sys.argv[1]).resolve()
class P(HTMLParser):
    def __init__(s): super().__init__(); s.links=[]; s.ids=set()
    def handle_starttag(s, tag, attrs):
        a = dict(attrs)
        if 'id' in a: s.ids.add(a['id'])
        for k in ('href','src'):
            if a.get(k): s.links.append(a[k])
def parse(f):
    p = P(); p.feed(f.read_text(encoding='utf-8')); return p
cache = {}
def ids(f):
    if f not in cache: cache[f] = parse(f).ids
    return cache[f]
bad = total = 0
for page in sys.argv[2:]:
    f = site / page; pp = parse(f)
    for link in pp.links:
        u = urlsplit(link)
        if u.scheme or u.netloc or link.startswith(('mailto:', 'javascript:', 'data:')): continue
        total += 1
        target = (f.parent / unquote(u.path)).resolve() if u.path else f
        if target.is_dir(): target = target / 'index.html'
        if not target.is_file():
            bad += 1; print('MISSING', page, link); continue
        if u.fragment and target.suffix == '.html' and u.fragment not in ids(target):
            bad += 1; print('NO ANCHOR', page, link)
print(f'{total} local links checked, {bad} bad')
