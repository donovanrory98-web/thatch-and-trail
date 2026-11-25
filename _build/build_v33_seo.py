# v34 step 3 (runs after build_v33_post.py): titles, descriptions, clean internal links.
import os, re, glob, html, json
SP = '/tmp/claude-0/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/scratchpad'
SITE = SP + '/v33/thatch-site'
BRAND = ' | Thatch &amp; Trail'
def L(s): return len(html.unescape(s))
stats = {'titles': 0, 'desc': 0, 'links': 0}

def new_title(rel, t, s):
    MANUAL = {
     'guide/christmas-at-the-vineyard.html': 'Christmas at the vineyard 2026: markets &amp; tastings',
     'guide/vineyard-wedding-venues.html': 'Vineyard weddings in Sussex: 12 estates',
     'guide/vineyards-by-train.html': 'Vineyards by train from London: Sussex &amp; Kent',
     'guide/vineyards-in-winter.html': 'Vineyards open in winter: Sussex &amp; Kent, 2026',
     'guide/vineyards-with-restaurants.html': 'Sussex vineyards with restaurants: 16 places to eat',
     'trail/horsham-arun-valley.html': 'Horsham &amp; Arun Valley vineyards: 8 to visit',
     'trail/index.html': f'Sussex wine trails: 7 routes, {TRAILN} vineyards',
     'trail/rother-wine-triangle.html': 'Rother Wine Triangle: 7 vineyards near Rye',
     'trail/wealden-wine-trail.html': 'Wealden Wine Trail: 12 vineyards to visit',
     'sussex/index.html': 'Sussex Vineyards: Visitor Guide to 46 Estates',
    }
    if rel in MANUAL: return MANUAL[rel]
    if rel == 'index.html': return 'Vineyards to Visit in England &amp; Wales' + BRAND
    if rel == 'verified.html': return 'What estate-verified means' + BRAND
    if rel.startswith('v/'):
        name = re.search(r'<h1>(.*?)</h1>', s).group(1)
        lm = re.search(r'<p class="lmeta">(.*?)</p>', s).group(1)
        county = lm.split(' · ')[-1]
        for c in (f'{name}: tours &amp; tastings in {county}', f'{name}: tours &amp; tastings', f'{name} visitor guide'):
            if L(c) <= 60: return c
        return name
    m = re.match(r'(.*?) vineyards to visit: tours, tastings(?: and cellar doors)?' + re.escape(BRAND) + '$', t)
    if m:
        for c in (f'{m.group(1)} vineyards to visit: tours &amp; tastings{BRAND}', f'{m.group(1)} vineyards to visit{BRAND}', f'{m.group(1)} vineyards to visit'):
            if L(c) <= 60: return c
    if L(t) > 60 and t.endswith(BRAND) and rel != 'sussex/index.html': return t[:-len(BRAND)]
    return t

def trim_desc(d):
    if L(d) <= 158: return d
    d2 = d.removesuffix(' Estate-verified.')
    if L(d2) <= 158: return d2
    sents = re.split(r'(?<=\.) ', d2); out = ''
    for x in sents:
        if L((out + ' ' + x).strip()) <= 158: out = (out + ' ' + x).strip()
        else: break
    if out: return out
    cut = d2[:150]; k = max(cut.rfind(', '), cut.rfind(' and '))
    return (cut[:k] + '.') if k > 90 else d

TRAILN = 0
for tp in glob.glob(SITE + '/trail/*.html'):
    if tp.endswith('index.html'): continue
    tt = open(tp).read(); TRAILN += len(re.findall(r'<a class="card"', tt[tt.find('<div class="grid">'):tt.find('<section class="prose trail-facts"')]))
ti = open(SITE + '/trail/index.html').read()
ti = ti.replace('7 routes, 37 vineyards', f'7 routes, {TRAILN} vineyards').replace('37 vineyards, with stations, food and stay', f'{TRAILN} vineyards, with stations, food and stay')
open(SITE + '/trail/index.html', 'w').write(ti)
for p in sorted(glob.glob(SITE + '/**/*.html', recursive=True)):
    rel = os.path.relpath(p, SITE)
    if rel.startswith('google') or rel.startswith('badge/'): continue
    s = open(p).read(); o = s
    m = re.search(r'<title>(.*?)</title>', s, re.S)
    if m:
        t = m.group(1); nt = new_title(rel, t, s)
        if nt != t:
            s = s.replace(f'<title>{t}</title>', f'<title>{nt}</title>', 1)
            for prop in ('og:title', 'twitter:title'):
                s = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda x: f'<meta content="{nt}" {x.group(1)}="{prop}"/>', s, count=1)
            stats['titles'] += 1
    m = re.search(r'<meta content="([^"]*)" name="description"/>', s)
    if m:
        d = m.group(1); nd = trim_desc(d)
        if nd != d:
            for prop in ('description', 'og:description', 'twitter:description'):
                s = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda x: f'<meta content="{nd}" {x.group(1)}="{prop}"/>', s, count=1)
            stats['desc'] += 1
    # internal links -> root-relative clean URLs (what the canonicals already say)
    base = os.path.dirname(rel)
    def clean(u):
        path, hashpart = (u.split('#', 1) + [''])[:2]
        if not path.endswith('.html'): return None
        full = os.path.normpath(os.path.join(base, path)) if not path.startswith('/') else path.lstrip('/')
        if full.startswith('..') or full.startswith('badge/'): return None
        if full == 'index.html': c = '/'
        elif full.endswith('/index.html'): c = '/' + full[:-len('index.html')]
        else: c = '/' + full[:-5]
        return c + ('#' + hashpart if hashpart else '')
    def fix(mm):
        u = mm.group(2)
        if re.match(r'(https?:|mailto:|tel:|data:|#|javascript:)', u): return mm.group(0)
        c = clean(u)
        if c is None: return mm.group(0)
        stats['links'] += 1
        return f'{mm.group(1)}="{c}"'
    s = re.sub(r'(\s(?:href|action))="([^"]+)"', fix, s)
    # map data links
    s = re.sub(r'"h":"(?:\.\./)?(v/[a-z0-9-]+)\.html"', lambda mm: f'"h":"/{mm.group(1)}"', s)
    s = re.sub(r'"h": "(?:\.\./)?(v/[a-z0-9-]+)\.html"', lambda mm: f'"h": "/{mm.group(1)}"', s)
    if s != o: open(p, 'w').write(s)
print(stats)
