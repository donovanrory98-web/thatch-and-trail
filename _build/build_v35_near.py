# v35: "Vineyards near <town>" pages, a /near/ hub, links from homepage, regions and estate pages, sitemap.
import os, re, json, glob, math, html
SITE = '/tmp/claude-0/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/scratchpad/v35/thatch-site'
BASE = 'https://thatchandtrail.com'
TODAY = '2026-11-22'
MONTH = 'November 2026'

def rd(p): return open(os.path.join(SITE, p)).read()
def wr(p, s):
    os.makedirs(os.path.dirname(os.path.join(SITE, p)), exist_ok=True); open(os.path.join(SITE, p), 'w').write(s)

# master estate data (with region colours) from the regions page map
reg = rd('regions/index.html')
EST = json.loads(re.search(r'<script type="application/json" id="hub-map-data">(.*?)</script>', reg, re.S).group(1))
print('estates', len(EST))
BYS = {e['s']: e for e in EST}

# harvest one card per estate from every page that has them
CARD = {}
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    s = open(p).read()
    for m in re.finditer(r'<a class="card"[^>]*href="/v/([a-z0-9-]+)">.*?</a>', s, re.S):
        slug = m.group(1)
        c = m.group(0)
        if slug not in CARD or ('Verified' in c and 'Verified' not in CARD[slug]): CARD[slug] = c
missing = [e['s'] for e in EST if e['s'] not in CARD]
print('cards', len(CARD), 'missing', missing)

def miles(a, b, c, d):
    R = 3958.8; p1, p2 = math.radians(a), math.radians(c); dp = p2 - p1; dl = math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

# towns in priority order (search demand first); radius in miles
TOWNS = [('london', 'London', 51.5074, -0.1278, 40), ('brighton', 'Brighton', 50.8225, -0.1372, 20), ('canterbury', 'Canterbury', 51.2802, 1.0789, 20),
 ('guildford', 'Guildford', 51.2362, -0.5704, 20), ('winchester', 'Winchester', 51.0632, -1.3080, 20), ('oxford', 'Oxford', 51.7520, -1.2577, 25),
 ('cambridge', 'Cambridge', 52.2053, 0.1218, 25), ('bath', 'Bath', 51.3811, -2.3590, 25), ('bristol', 'Bristol', 51.4545, -2.5879, 25),
 ('exeter', 'Exeter', 50.7184, -3.5339, 25), ('norwich', 'Norwich', 52.6309, 1.2974, 25), ('tunbridge-wells', 'Tunbridge Wells', 51.1324, 0.2637, 20),
 ('chichester', 'Chichester', 50.8365, -0.7792, 20), ('horsham', 'Horsham', 51.0629, -0.3259, 20), ('maidstone', 'Maidstone', 51.2704, 0.5227, 20),
 ('eastbourne', 'Eastbourne', 50.7684, 0.2903, 20), ('hastings', 'Hastings', 50.8543, 0.5735, 20), ('rye', 'Rye', 50.9502, 0.7330, 15),
 ('ashford', 'Ashford', 51.1465, 0.8750, 20), ('cardiff', 'Cardiff', 51.4816, -3.1791, 25), ('cheltenham', 'Cheltenham', 51.8994, -2.0783, 25),
 ('hereford', 'Hereford', 52.0565, -2.7160, 25), ('reading', 'Reading', 51.4543, -0.9781, 25), ('southampton', 'Southampton', 50.9097, -1.4044, 20),
 ('ipswich', 'Ipswich', 52.0567, 1.1482, 25), ('dorchester', 'Dorchester', 50.7154, -2.4367, 25), ('truro', 'Truro', 50.2632, -5.0510, 25),
 ('plymouth', 'Plymouth', 50.3755, -4.1427, 25), ('birmingham', 'Birmingham', 52.4862, -1.8904, 30), ('york', 'York', 53.9600, -1.0873, 30),
 ('leeds', 'Leeds', 53.8008, -1.5491, 30), ('manchester', 'Manchester', 53.4808, -2.2426, 30), ('lewes', 'Lewes', 50.8739, 0.0088, 15),
 ('arundel', 'Arundel', 50.8551, -0.5530, 15), ('dorking', 'Dorking', 51.2325, -0.3305, 15), ('sevenoaks', 'Sevenoaks', 51.2724, 0.1909, 15),
 ('petersfield', 'Petersfield', 51.0040, -0.9356, 15), ('haywards-heath', 'Haywards Heath', 50.9990, -0.1063, 15), ('tenterden', 'Tenterden', 51.0693, 0.6866, 12)]

MINN = 5          # quality gate: a town page needs at least 5 vineyards
OVERLAP = 0.7     # skip a town whose list mostly repeats a town already chosen (avoids competing pages)
chosen = []
for slug, name, la, lo, rad in TOWNS:
    near = sorted(((miles(la, lo, e['lat'], e['lng']), e) for e in EST), key=lambda x: x[0])
    near = [(d, e) for d, e in near if d <= rad and e['s'] in CARD]
    if len(near) < MINN: continue
    S = {e['s'] for _, e in near}
    if any(len(S & c['set']) / len(S) >= OVERLAP for c in chosen): continue
    chosen.append({'slug': slug, 'name': name, 'lat': la, 'lng': lo, 'rad': rad, 'near': near, 'set': S})
print('town pages:', [(c['name'], len(c['near'])) for c in chosen])

# page shell from the Kent hub page
k = rd('kent/index.html')
head_end = k.find('<main'); main_end = k.find('</main>')
SHELL_HEAD = k[:head_end]; SHELL_FOOT = k[main_end:]

def shell(rel_depth, title, desc, canon, ld, body):
    h = SHELL_HEAD
    h = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', h, 1, re.S)
    for prop in ('description', 'og:description', 'twitter:description'):
        h = re.sub(rf'<meta content="[^"]*" (name|property)="{prop}"/>', lambda m: f'<meta content="{html.escape(desc, quote=True)}" {m.group(1)}="{prop}"/>', h, 1)
    for prop in ('og:title', 'twitter:title'):
        h = re.sub(rf'<meta content="[^"]*" (name|property)="{prop}"/>', lambda m: f'<meta content="{title}" {m.group(1)}="{prop}"/>', h, 1)
    h = re.sub(r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{canon}" property="og:url"/>', h, 1)
    h = re.sub(r'<link href="[^"]*" rel="canonical"/>', f'<link href="{canon}" rel="canonical"/>', h, 1)
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', h, 1, re.S)
    body = body.rstrip()
    if body.endswith('</main>'): body = body[:-len('</main>')]
    out = h + body + '\n' + SHELL_FOOT
    if rel_depth != 1:  # Kent page sits one level down; fix relative asset paths for other depths
        pre = '../' * rel_depth
        out = out.replace('href="../', f'href="{pre}').replace('src="../', f'src="{pre}')
    return out

def plain(s): return html.unescape(re.sub(r'<[^>]+>', '', s))

def card_with_distance(slug, d):
    c = CARD[slug]
    return re.sub(r'(<div class="ctown">)(.*?)(</div>)', lambda m: f'{m.group(1)}{m.group(2)} · {d:.0f} miles{m.group(3)}' if d >= 1 else f'{m.group(1)}{m.group(2)} · under a mile{m.group(3)}', c, 1)

for c in chosen:
    n = len(c['near']); ver = [e for _, e in c['near'] if e.get('v')]
    food = [e for _, e in c['near'] if 'data-food="Yes"' in CARD[e['s']]]
    d0, e0 = c['near'][0]
    title = f'Vineyards near {c["name"]}: {n} to visit'
    if len(title) > 60: title = f'Vineyards near {c["name"]}'
    desc = f'{n} vineyards within {c["rad"]} miles of {c["name"]}, {len(ver)} confirmed by the estate: tours, tastings, cellar doors, food and how far each one is.'
    canon = f'{BASE}/near/{c["slug"]}'
    mapdata = [dict(BYS[e['s']]) for _, e in c['near']]
    cards = ''.join(card_with_distance(e['s'], d) for d, e in c['near'])
    others = [o for o in chosen if o is not c]
    others.sort(key=lambda o: miles(c['lat'], c['lng'], o['lat'], o['lng']))
    other_links = ' · '.join(f'<a href="/near/{o["slug"]}">{o["name"]}</a>' for o in others[:8])
    closest3 = ', '.join(f'{e["n"]} ({d:.0f} miles)' for d, e in c['near'][:3])
    faqs = [
        (f'How many vineyards are there near {c["name"]}?', f'{n} vineyards that welcome visitors are within {c["rad"]} miles of {c["name"]}, and {len(ver)} of them have confirmed their details with Thatch & Trail directly.'),
        (f'What is the closest vineyard to {c["name"]}?', f'{e0["n"]} in {e0["t"]}, about {max(d0,1):.0f} miles away as the crow flies. The next closest are {", ".join(f"{e["n"]} ({d:.0f} miles)" for d, e in c["near"][1:3])}.'),
        (f'Which vineyards near {c["name"]} serve food?', (f'{len(food)} of them have food on site, including ' + ', '.join(e['n'] for e in food[:4]) + '. Opening days vary through the year, so check each page before you go.') if food else f'None of the vineyards within {c["rad"]} miles list food on site, so plan lunch nearby.'),
    ]
    ld = [{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': plain(title), 'description': desc, 'url': canon, 'dateModified': TODAY,
           'mainEntity': {'@type': 'ItemList', 'numberOfItems': n, 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': e['n'], 'url': BASE + e['h']} for i, (d, e) in enumerate(c['near'])]}},
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Vineyards', 'item': BASE + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Vineyards near you', 'item': BASE + '/near/'}, {'@type': 'ListItem', 'position': 3, 'name': f'Near {c["name"]}', 'item': canon}]},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}]
    fq = ''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in faqs)
    body = f'''<main id="main">
<div class="wrap">
<nav aria-label="Breadcrumb" class="crumb"><a href="/">Vineyards</a> <i>/</i> <a href="/near/">Near you</a> <i>/</i> <span aria-current="page">{c["name"]}</span></nav>
<div class="hubhead">
<p class="eyebrow">Within {c["rad"]} miles · nearest first</p>
<h1>Vineyards near {c["name"]}</h1>
<p class="lede">{n} vineyards you can visit within {c["rad"]} miles of {c["name"]}, nearest first. {len(ver)} have confirmed their details with us directly (look for the Verified tag); everything else comes from the estate’s own website. The closest are {html.escape(closest3)}.</p>
</div>
<div class="hub-map" id="hub-map" role="region" aria-label="Map of vineyards near {c["name"]}"><p class="atlas-fallback">The map needs JavaScript. Every vineyard is listed below.</p></div>
<script type="application/json" id="hub-map-data">{json.dumps(mapdata, ensure_ascii=False, separators=(",", ":"))}</script>
<div class="stn"><h2><span class="mono">Nearest first</span> <i>distances are straight-line miles from the centre of {c["name"]}</i></h2>
<div class="grid">{cards}</div></div>
<section class="prose">
<h2>Common questions</h2>
<div class="faq">{fq}</div>
<p>Distances are as the crow flies, so allow for country lanes. Opening times change through the year, especially in winter, so check the estate’s page before you set off. Updated {MONTH}.</p>
<p><b>Other towns:</b> {other_links} · <a href="/near/">all towns</a></p>
</section>
</div>
</main>
'''
    wr(f'near/{c["slug"]}.html', shell(1, title, desc, canon, ld, body))

# hub page
rows = ''.join(f'<li><a href="/near/{c["slug"]}">Vineyards near {c["name"]}</a> <i>{len(c["near"])} within {c["rad"]} miles</i></li>' for c in chosen)
hub_title = 'Vineyards near you: find one by town'
hub_desc = f'Find vineyards to visit near {", ".join(c["name"] for c in chosen[:6])} and {len(chosen) - 6} more towns, with distances and estate-confirmed details.'
hub_ld = [{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': hub_title, 'description': hub_desc, 'url': BASE + '/near/',
           'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': f'Vineyards near {c["name"]}', 'url': f'{BASE}/near/{c["slug"]}'} for i, c in enumerate(chosen)]}},
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Vineyards', 'item': BASE + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Vineyards near you', 'item': BASE + '/near/'}]}]
hub_body = f'''<main id="main"><div class="wrap">
<nav aria-label="Breadcrumb" class="crumb"><a href="/">Vineyards</a> <i>/</i> <span aria-current="page">Near you</span></nav>
<div class="hubhead"><p class="eyebrow">By town</p><h1>Vineyards near you</h1>
<p class="lede">Pick the town you’re starting from to see every vineyard within reach, nearest first, with distances and the details each estate has confirmed. Or use the <a href="/#vineyards">map on the home page</a>.</p></div>
<section class="prose"><ul class="nearlist">{rows}</ul></section>
</div></main>
'''
wr('near/index.html', shell(1, hub_title, hub_desc, BASE + '/near/', hub_ld, hub_body))

# small style for the hub list
css = rd('style.css')
if '.nearlist' not in css:
    css += '\n.nearlist{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px 24px}.nearlist li{padding:10px 0;border-bottom:1px solid rgba(0,0,0,.08)}.nearlist i{display:block;font-style:normal;opacity:.7;font-size:.9em}\n.nearby-towns{margin-top:1.4em}\n'
    wr('style.css', css)

# links: homepage + regions page get a "Vineyards near" line; each estate page gets its towns
chips = ' · '.join(f'<a href="/near/{c["slug"]}">{c["name"]}</a>' for c in chosen)
line = f'<p class="nearby-towns"><b>Vineyards near:</b> {chips} · <a href="/near/">all towns</a></p>'
for p in ('index.html', 'regions/index.html'):
    s = rd(p)
    if 'nearby-towns' not in s:
        i = s.find('</main>'); s = s[:i] + f'<div class="wrap">{line}</div>\n' + s[i:]; wr(p, s)
est_towns = {}
for c in chosen:
    for d, e in c['near']: est_towns.setdefault(e['s'], []).append((d, c))
added = 0
for slug, lst in est_towns.items():
    p = f'v/{slug}.html'
    if not os.path.exists(os.path.join(SITE, p)): continue
    s = rd(p)
    if 'nearby-towns' in s: continue
    lst.sort(key=lambda x: x[0])
    links = ' · '.join(f'<a href="/near/{c["slug"]}">Vineyards near {c["name"]}</a> ({d:.0f} miles)' for d, c in lst[:4])
    i = s.find('</main>'); s = s[:i] + f'<div class="wrap"><p class="nearby-towns"><b>Also near here:</b> {links}</p></div>\n' + s[i:]; wr(p, s); added += 1
print('estate pages linked', added)

# nav: add "Near you" to the menus
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    s = open(p).read(); o = s
    s = s.replace('<a href="/regions/">Regions</a>', '<a href="/regions/">Regions</a><a href="/near/">Near you</a>', 2) if '/near/">Near you</a>' not in s else s
    if s != o: open(p, 'w').write(s)

# sitemap
sm = rd('sitemap.xml')
new = [BASE + '/near/'] + [f'{BASE}/near/{c["slug"]}' for c in chosen]
add = ''.join(f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n' for u in new if u not in sm)
sm = re.sub(r'<lastmod>2026-11-18</lastmod>', f'<lastmod>{TODAY}</lastmod>', sm) if False else sm
sm = sm.replace('</urlset>', add + '</urlset>')
for slug in est_towns:  # pages that changed get a new lastmod
    sm = re.sub(rf'(<loc>{re.escape(BASE)}/v/{slug}</loc><lastmod>)[^<]+', rf'\g<1>{TODAY}', sm)
for u in ('/', '/regions/'):
    sm = re.sub(rf'(<loc>{re.escape(BASE + u)}</loc><lastmod>)[^<]+', rf'\g<1>{TODAY}', sm)
wr('sitemap.xml', sm)
print('sitemap urls', sm.count('<url>'))
