# v37 SEO pass (26 Nov 2026), from OpenSEO keyword data:
#  - county pages for searches with no page: East Sussex, West Sussex, Devon (5+ vineyards only)
#  - a national "vineyard tours & tastings" guide (estates whose own listing mentions tours or tastings)
#  - links to the new pages from the Sussex, South West, regions and home pages
#  - sitemap entries and lastmod
#  - .html -> clean-URL 301 redirects for every page
# Uses only facts already on the site (cards and Winery data harvested from the estate pages).
import os, re, json, glob, html, sys
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
BASE = 'https://thatchandtrail.com'
TODAY = '2026-11-26'
MONTH = 'November 2026'
MINN = 5

def rd(p): return open(os.path.join(SITE, p), encoding='utf-8').read()
def wr(p, s):
    os.makedirs(os.path.dirname(os.path.join(SITE, p)), exist_ok=True)
    open(os.path.join(SITE, p), 'w', encoding='utf-8').write(s)
def plain(s): return html.unescape(re.sub(r'<[^>]+>', '', s))

reg = rd('regions/index.html')
EST = json.loads(re.search(r'<script type="application/json" id="hub-map-data">(.*?)</script>', reg, re.S).group(1))
BYS = {e['s']: e for e in EST}

CARD = {}
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    s = open(p, encoding='utf-8').read()
    for m in re.finditer(r'<a class="card"[^>]*href="/v/([a-z0-9-]+)">.*?</a>', s, re.S):
        slug, c = m.group(1), m.group(0)
        if slug not in CARD or ('Verified' in c and 'Verified' not in CARD[slug]): CARD[slug] = c

COUNTY = {}
for p in glob.glob(SITE + '/v/*.html'):
    slug = os.path.basename(p)[:-5]
    s = open(p, encoding='utf-8').read()
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: j = json.loads(b)
        except Exception: continue
        for it in (j if isinstance(j, list) else j.get('@graph', [j])):
            if isinstance(it, dict) and it.get('@type') == 'Winery':
                COUNTY[slug] = (it.get('address') or {}).get('addressRegion')

k = rd('kent/index.html')
SHELL_HEAD = k[:k.find('<main')]; SHELL_FOOT = k[k.find('</main>'):]

def shell(title, desc, canon, ld, body):
    h = SHELL_HEAD
    t = html.escape(title, quote=False)
    h = re.sub(r'<title>.*?</title>', f'<title>{t}</title>', h, 1, re.S)
    for prop in ('description', 'og:description', 'twitter:description'):
        h = re.sub(rf'<meta content="[^"]*" (name|property)="{prop}"/>', lambda m: f'<meta content="{html.escape(desc, quote=True)}" {m.group(1)}="{prop}"/>', h, 1)
    for prop in ('og:title', 'twitter:title'):
        h = re.sub(rf'<meta content="[^"]*" (name|property)="{prop}"/>', lambda m: f'<meta content="{html.escape(title, quote=True)}" {m.group(1)}="{prop}"/>', h, 1)
    h = re.sub(r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{canon}" property="og:url"/>', h, 1)
    h = re.sub(r'<link href="[^"]*" rel="canonical"/>', f'<link href="{canon}" rel="canonical"/>', h, 1)
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>', h, 1, re.S)
    return h + body + '\n' + SHELL_FOOT

def verified(slug): return 'Verified' in CARD.get(slug, '')
def food(slug): return 'data-food="Yes"' in CARD.get(slug, '')

def order(slugs):  # verified first, then name
    return sorted(slugs, key=lambda s: (not verified(s), BYS[s]['n'].lower()))

def ld_for(title, desc, canon, slugs, crumbs, faqs):
    return [{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'description': desc, 'url': canon, 'dateModified': TODAY,
             'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(slugs), 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': BYS[s]['n'], 'url': BASE + BYS[s]['h']} for i, s in enumerate(slugs)]}},
            {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE + u} for i, (n, u) in enumerate(crumbs)]},
            {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}]

def page_body(crumbs, eyebrow, h1, lede, label, slugs, faqs, extra):
    cr = ' <i>/</i> '.join(f'<a href="{u}">{html.escape(n)}</a>' for n, u in crumbs[:-1]) + f' <i>/</i> <span aria-current="page">{html.escape(crumbs[-1][0])}</span>'
    mapdata = [dict(BYS[s]) for s in slugs]
    cards = ''.join(CARD[s] for s in slugs)
    fq = ''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in faqs)
    return f'''<main id="main">
<div class="wrap">
<nav aria-label="Breadcrumb" class="crumb">{cr}</nav>
<div class="hubhead">
<p class="eyebrow">{eyebrow}</p>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
</div>
<div class="hub-map" id="hub-map" role="region" aria-label="Map of {html.escape(label)}"><p class="atlas-fallback">The map needs JavaScript. Every vineyard is listed below.</p></div>
<script type="application/json" id="hub-map-data">{json.dumps(mapdata, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")}</script>
<div class="stn"><h2><span class="mono">Estate-checked first</span> <i>then A to Z</i></h2>
<div class="grid">{cards}</div></div>
<section class="prose">
<h2>Common questions</h2>
<div class="faq">{fq}</div>
{extra}
<p>Opening times change through the year, especially in winter, so check each estate’s page before you set off. Updated {MONTH}.</p>
</section>
</div>
'''

new_urls = []

# ---------- county pages ----------
COUNTIES = [
    ('east-sussex', 'East Sussex', '/sussex/', 'Sussex', 'The High Weald, the Rother valley, the Downs above Lewes and the coast near Rye.'),
    ('west-sussex', 'West Sussex', '/sussex/', 'Sussex', 'The South Downs, the Arun valley around Pulborough and the coastal plain near Chichester.'),
    ('devon', 'Devon', '/southwest/', 'South West', 'River valleys, the South Hams and the edges of Dartmoor and the Exe estuary.'),
    ('cornwall', 'Cornwall', '/southwest/', 'South West', 'From the Camel valley to the far west.'),
]
ELIG = {c[0] for c in COUNTIES if len([x for x, y in COUNTY.items() if y == c[1] and x in CARD and x in BYS]) >= MINN}
built = []
for slug, name, parent, parent_name, blurb in COUNTIES:
    slugs = order([s for s, c in COUNTY.items() if c == name and s in CARD and s in BYS])
    if len(slugs) < MINN:
        print('skip', name, len(slugs)); continue
    n = len(slugs); ver = [s for s in slugs if verified(s)]; fd = [s for s in slugs if food(s)]
    title = f'{name} Vineyards to Visit: All {n}, Tours & Tastings'
    if len(title) > 60: title = f'{name} Vineyards to Visit: {n} Estates'
    desc = f'All {n} {name} vineyards that welcome visitors, {len(ver)} confirmed by the estate: tours, tastings, cellar doors, food and how to get there.'
    canon = f'{BASE}/{slug}/'
    towns = sorted({BYS[s]['t'] for s in slugs if BYS[s].get('t')})
    faqs = [
        (f'How many vineyards can you visit in {name}?', f'{n} vineyards in {name} welcome visitors, and {len(ver)} of them have confirmed their details with Thatch & Trail directly.'),
        (f'Which {name} vineyards serve food?', (f'{len(fd)} have food on site, including ' + ', '.join(BYS[s]['n'] for s in fd[:5]) + '.') if fd else f'None of the {name} vineyards we list have food on site, so plan lunch nearby.'),
        (f'Where are the vineyards in {name}?', f'{blurb} Towns with a vineyard nearby include ' + ', '.join(towns[:8]) + '.'),
    ]
    crumbs = [('Vineyards', '/'), (parent_name, parent), (name, f'/{slug}/')]
    lede = f'Every vineyard in {name} that welcomes visitors: {n} estates, {len(ver)} of them checked with the estate itself (look for the Verified tag). Each card links to opening days, tours, food, dogs and how to get there without a car.'
    sib = [c for c in COUNTIES if c[2] == parent and c[0] != slug and c[0] in ELIG]
    extra = '<p><b>Nearby:</b> ' + ' · '.join(f'<a href="/{c[0]}/">{c[1]} vineyards</a>' for c in sib) + f' · <a href="{parent}">all of {parent_name}</a> · <a href="/near/">vineyards near a town</a></p>'
    body = page_body(crumbs, f'{name} · {n} vineyards', f'{name} vineyards to visit', lede, f'{name} vineyards', slugs, faqs, extra)
    wr(f'{slug}/index.html', shell(title, desc, canon, ld_for(title, desc, canon, slugs, crumbs, faqs), body))
    built.append((slug, name, parent, n)); new_urls.append(canon)
    print('built', name, n, title, len(title))

# ---------- tours & tastings guide ----------
def hook(slug):
    m = re.search(r'<p class="chook">(.*?)</p>', CARD[slug], re.S)
    return plain(m.group(1)) if m else ''
tour_slugs = [s for s in BYS if s in CARD and re.search(r'\btours?\b|tasting', hook(s), re.I)]
tour_slugs = order(tour_slugs)
n = len(tour_slugs)
title = f'Vineyard Tours & Tastings in England & Wales: {n} Estates'
if len(title) > 60: title = f'Vineyard Tours & Tastings: {n} English Estates'
desc = f'{n} vineyards in England and Wales that run tours or tastings, with what each offers, when, food on site and how to get there. Checked {MONTH}.'
canon = f'{BASE}/guide/vineyard-tours'
by_county = {}
for s in tour_slugs: by_county.setdefault(COUNTY.get(s) or 'Elsewhere', []).append(s)
top = sorted(by_county.items(), key=lambda x: -len(x[1]))[:5]
faqs = [
    ('Where can you do a vineyard tour in England?', f'{n} estates in England and Wales mention tours or tastings on their listing. The most are in ' + ', '.join(f'{c} ({len(v)})' for c, v in top) + '.'),
    ('Do you need to book a vineyard tour?', 'Most estates ask you to book tours in advance, and many only run them on set days or in the main season. Each estate page says what that estate does.'),
    ('Can you visit a vineyard without a car?', 'Yes. Many are a walk or short taxi from a railway station; each card shows the nearest station, and the vineyards-by-train guide picks the easiest ones.'),
]
crumbs = [('Vineyards', '/'), ('Guides', '/regions/'), ('Vineyard tours', '/guide/vineyard-tours')]
lede = f'{n} vineyards across England and Wales whose own details mention tours or tastings, estate-checked ones first. Open any card for days, booking, food, dogs and the nearest station.'
extra = '<p><b>More guides:</b> <a href="/guide/vineyards-open-to-visit">Sussex vineyard tours</a> · <a href="/guide/vineyards-by-train">vineyards by train</a> · <a href="/guide/vineyards-with-restaurants">with restaurants</a> · <a href="/guide/vineyards-with-accommodation">with somewhere to stay</a></p>'
body = page_body(crumbs, f'Tours and tastings · {n} estates', 'Vineyard tours &amp; tastings', lede, 'vineyards with tours', tour_slugs, faqs, extra)
wr('guide/vineyard-tours.html', shell(title, desc, canon, ld_for(title, desc, canon, tour_slugs, crumbs, faqs), body))
new_urls.append(canon); print('tours guide', n, title, len(title))

# ---------- links from parent pages ----------
def add_line(p, marker, line):
    s = rd(p)
    if marker in s: return
    i = s.rfind('</main>'); s = s[:i] + f'<div class="wrap">{line}</div>\n' + s[i:]; wr(p, s)
for parent in ('/sussex/', '/southwest/'):
    kids = [b for b in built if b[2] == parent]
    if kids:
        add_line(parent.strip('/') + '/index.html', 'county-links', '<p class="nearby-towns county-links"><b>By county:</b> ' + ' · '.join(f'<a href="/{b[0]}/">{b[1]} vineyards ({b[3]})</a>' for b in kids) + '</p>')
all_links = ' · '.join(f'<a href="/{b[0]}/">{b[1]}</a>' for b in built) + ' · <a href="/guide/vineyard-tours">Vineyard tours &amp; tastings</a>'
for p in ('index.html', 'regions/index.html'):
    add_line(p, 'county-links', f'<p class="nearby-towns county-links"><b>More guides:</b> {all_links}</p>')

# ---------- sitemap ----------
sm = rd('sitemap.xml')
add = ''.join(f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>\n' for u in new_urls if f'<loc>{u}</loc>' not in sm)
sm = sm.replace('</urlset>', add + '</urlset>')
for u in ('/', '/regions/', '/sussex/', '/southwest/', '/kent/', '/surrey/', '/hampshire/', '/trail/horsham-arun-valley'):
    sm = re.sub(rf'(<loc>{re.escape(BASE + u)}</loc><lastmod>)[^<]+', rf'\g<1>{TODAY}', sm)
wr('sitemap.xml', sm)

# ---------- .html -> clean redirects ----------
lines = []
for p in sorted(glob.glob(SITE + '/**/*.html', recursive=True)):
    rel = '/' + os.path.relpath(p, SITE).replace(os.sep, '/')
    if os.path.basename(rel).startswith('google') or rel in ('/404.html',): continue
    clean = rel[:-len('index.html')] if rel.endswith('/index.html') else rel[:-5]
    if rel == '/index.html': clean = '/'
    lines.append(f'{rel}  {clean}  301!')
wr('_redirects', '\n'.join(lines) + '\n/*  /404.html  404\n')
print('redirects', len(lines), 'sitemap urls', sm.count('<url>'))

# ---------- alt text for illustrations and badges that had none ----------
fixed = 0
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    s = open(p, encoding='utf-8').read(); o = s
    def alt(m):
        tag = m.group(0); src = re.search(r'src="([^"]+)"', tag)
        if not src or re.search(r'\balt="[^"]+"', tag) or 'hero-' in src.group(1): return tag
        slug = os.path.basename(src.group(1)).rsplit('.', 1)[0]
        if slug not in BYS: return tag
        kind = 'Illustration of ' if '/plates/' in src.group(1) else ('Thatch & Trail verified badge for ' if '/badge/' in src.group(1) else '')
        text = html.escape(kind + BYS[slug]['n'], quote=True)
        return re.sub(r'\balt=""', f'alt="{text}"', tag) if 'alt=""' in tag else tag.replace('<img ', f'<img alt="{text}" ', 1)
    s = re.sub(r'<img\b[^>]*>', alt, s)
    if s != o: open(p, 'w', encoding='utf-8').write(s); fixed += 1
print('alt text added on', fixed, 'pages')
