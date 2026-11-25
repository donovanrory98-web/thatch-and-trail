# Thatch & Trail v33 generator (estate machinery, adapted from v32)
import re, json, html, glob, os, importlib.util, random, datetime, shutil
from PIL import Image

SP = '/tmp/claude-0/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/scratchpad'
SITE = SP + '/v33/thatch-site'
DATA = SP + '/v33data'
TR = '/root/.claude/projects/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/tool-results'
TODAY = '2026-11-22'
BASE = 'https://thatchandtrail.com'

def rd(p): return open(os.path.join(SITE, p), encoding='utf-8').read()
def wr(p, s):
    fp = os.path.join(SITE, p); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w', encoding='utf-8').write(s)
def plain(s): return html.unescape(re.sub(r'<[^>]+>', '', s))
def poss(n): return n + ('’' if plain(n).endswith('s') else '’s')
def join_names(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
def ld(obj): return json.dumps(obj, ensure_ascii=False)

# ---------- data ----------
E, FLAGS, PHOTOS = [], [], {}
for f in sorted(glob.glob(DATA + '/b*.py')):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    E += m.E; FLAGS += getattr(m, 'FLAGS', []); PHOTOS.update(getattr(m, 'PHOTOS', {}))
slugs = [e['slug'] for e in E]
assert len(slugs) == len(set(slugs)), 'duplicate slug'
import zipfile
_z = set(zipfile.ZipFile('/mnt/user-data/outputs/thatch-and-trail-v32.zip').namelist())
for e in E: assert f'thatch-site/v/{e["slug"]}.html' not in _z, e['slug']

REG = {
 'north':     dict(dir='north', name='Yorkshire', eb='Yorkshire'),
 'east':      dict(dir='east', name='East of England', eb='East of England'),
 'southwest': dict(dir='southwest', name='The South West', eb='South West'),
 'west':      dict(dir='west', name='Cotswolds &amp; the West', eb='Cotswolds &amp; the West'),
 'wales':     dict(dir='wales', name='Wales', eb='Wales'),
 'thames':    dict(dir='thames', name='Berkshire &amp; Buckinghamshire', eb='Thames Valley'),
 'midlands':  dict(dir='midlands', name='The Midlands', eb='Midlands', new=True),
 'islands':   dict(dir='channel-islands', name='Channel Islands', eb='Channel Islands', new=True),
}
# Sussex trails for new Sussex estates
TRAIL = {'rowfant-vineyard': 'eg'}
TRAILS = {
 'wealden': dict(file='trail/wealden-wine-trail.html', name='The Wealden Wine Trail', t='Wealden Trail', tl='Wealden Trail', c='#2F6E6A'),
 'hh':      dict(file='trail/haywards-heath-ditchling.html', name='Haywards Heath &amp; Ditchling', t='Haywards Heath', tl='Haywards Heath &amp; Ditchling', c='#A8853A'),
 'eg':      dict(file='trail/east-grinstead-high-weald.html', name='East Grinstead, Tunbridge Wells &amp; the High Weald', t='East Grinstead', tl='East Grinstead &amp; High Weald', c='#4C5A63'),
 'chi':     dict(file='trail/chichester-petworth.html', name='Chichester &amp; Petworth', t='Chichester', tl='Chichester &amp; Petworth', c='#7A3B4E'),
}
GEO = {'rowfant-vineyard': (51.1220, -0.1250)}
RAIL = {'rowfant-vineyard': 'Three Bridges or East Grinstead, taxi'}
COUNTY_SEC = {'Vale of Glamorgan': 'wales'}
REG['kent'] = dict(dir='kent', name='Kent', eb='Kent')
REG['hampshire'] = dict(dir='hampshire', name='Hampshire', eb='Hampshire')
REG['surrey'] = dict(dir='surrey', name='Surrey', eb='Surrey')   # Wales hub groups the Vale under "Wales"

# ---------- photos ----------
# slug: (tool-result file, crop box as fractions (x0,y0,x1,y1) or None for centre 3:2, alt, caption)
PH = {}
NAME = {e['slug']: e['name'] for e in E}
photo_dims = {}
def make_photos():
    for slug, (src, box, alt, cap) in PH.items():
        im = Image.open(os.path.join(TR, src)).convert('RGB')
        W, H = im.size
        if box:
            im = im.crop((int(box[0]*W), int(box[1]*H), int(box[2]*W), int(box[3]*H)))
        W, H = im.size
        # centre-crop to exactly 3:2
        if W / H > 1.5:
            nw = int(H * 1.5); x0 = (W - nw) // 2; im = im.crop((x0, 0, x0 + nw, H))
        else:
            nh = int(W / 1.5); y0 = (H - nh) // 2; im = im.crop((0, y0, W, y0 + nh))
        w = min(1600, im.size[0]); h = round(w / 1.5)
        im = im.resize((w, h), Image.LANCZOS)
        im.save(f'{SITE}/img/{slug}-1.jpg', quality=82, optimize=True, progressive=True)
        im.save(f'{SITE}/img/{slug}-1.webp', quality=80)
        photo_dims[slug] = (w, h)
        if TRAIL.get(slug):   # homepage thumbs 720x540 (4:3)
            th = im.copy(); tw, thh = th.size; nw = int(thh * 4 / 3); x0 = (tw - nw)//2
            th = th.crop((x0, 0, x0 + nw, thh)).resize((720, 540), Image.LANCZOS)
            th.save(f'{SITE}/img/thumbs/{slug}.webp', quality=80); th.save(f'{SITE}/img/thumbs/{slug}.jpg', quality=82)

def phero(e):
    s = e['slug']
    if s not in PH: return ''
    w, h = photo_dims[s]; alt, cap = PH[s][2], PH[s][3]
    return (f'<div class="phero"><picture><source srcset="../img/{s}-1.webp" type="image/webp"><img src="../img/{s}-1.jpg" alt="{html.escape(alt)}" '
            f'loading="lazy" width="{w}" height="{h}"></picture><div class="phcap">{cap} · Photograph courtesy of {e["name"]}</div></div>')

# ---------- templates ----------
TPL_EST = rd('v/llaethliw.html')
VNOTE = re.search(r'<p class="verified-note">.*?</p>', TPL_EST, re.S).group(0)
def fill_page(tpl, title, desc, canon, ldobj, main, ogimg=None):
    s = tpl
    s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{title}</title>', s, 1, re.S)
    s = re.sub(r'<meta content="[^"]*" name="description"/>', lambda m: f'<meta content="{desc}" name="description"/>', s, 1)
    s = re.sub(r'<link href="[^"]*" rel="canonical"/>', lambda m: f'<link href="{canon}" rel="canonical"/>', s, 1)
    s = re.sub(r'<meta content="[^"]*" property="og:title"/>', lambda m: f'<meta content="{title}" property="og:title"/>', s, 1)
    s = re.sub(r'<meta content="[^"]*" property="og:description"/>', lambda m: f'<meta content="{desc}" property="og:description"/>', s, 1)
    s = re.sub(r'<meta content="[^"]*" property="og:url"/>', lambda m: f'<meta content="{canon}" property="og:url"/>', s, 1)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: f'<script type="application/ld+json">{ld(ldobj)}</script>', s, 1, re.S)
    if ogimg:
        s = re.sub(r'<meta content="[^"]*" property="og:image"/>', lambda m: f'<meta content="{ogimg}" property="og:image"/>', s, 1)
        s = re.sub(r'<meta content="[^"]*" name="twitter:image"/>', lambda m: f'<meta content="{ogimg}" name="twitter:image"/>', s, 1)
    s = re.sub(r'<main id="main">.*?</main>', lambda m: main, s, 1, re.S)
    return s

LBL = {'C': 'Confirmed by the estate', 'W': 'What’s on', 'S': 'From their website'}
RAILKEYS = ('Nearest station', 'Nearest stations', 'By train', 'By bus', 'Without a car', 'On foot')
def rail(e):
    if e['slug'] in RAIL: return RAIL[e['slug']]
    for k, v in e['facts']:
        if k in RAILKEYS: return v
    return 'Check with the estate'
def where(e): return e['town'] or e['county']

# hub card html for a region hub (county-labelled)
def hub_card(e, label, trailattr=None, foodword='Food'):
    tags = '<span class="tag verified">Verified</span>'
    if e.get('food'): tags += f'<span class="tag on">{foodword}</span>'
    if e.get('stay'): tags += '<span class="tag on">Stay</span>'
    return (f'<a class="card" data-food="{"Yes" if e.get("food") else "No"}" data-stay="{"Yes" if e.get("stay") else "No"}" '
            f'data-trail="{trailattr or label}" data-visit="open" data-wed="?" href="../v/{e["slug"]}.html">\n'
            f'<div class="ctrail">{label}</div>\n<div class="cname">{e["name"]}</div>\n<div class="ctown">{where(e)}</div>\n'
            f'<div class="tags">{tags}</div>\n<div class="crail">&#8614; {rail(e)}</div>\n'
            f'<p class="chook">Estate-verified: {e["hook"]}</p>\n</a>')

def estate_page(e, parent_href, parent_name, crumb_root, crumb_root_name, eyebrow, first_fact, also_title, also_items, bc2_name, bc2_url):
    s = e['slug']; canon = f'{BASE}/v/{s}'
    boxes = ''.join(f'<div class="estate-answer"><span>{LBL[t]}</span><h3>{h}</h3><p>{p}</p></div>\n' for t, h, p in e['boxes'])
    getting = f'<div class="visit"><div class="lbl">Getting there</div><p>{e["getting"]}</p></div>\n' if e.get('getting') else ''
    faqs = ''.join(f'<div class="fq"><h3>{q}</h3><p>{a}</p></div>' for q, a in e['faqs'])
    facts = f'<div><dt>{first_fact[0]}</dt><dd>{first_fact[1]}</dd></div>' + ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in e['facts'])
    also = ''
    if also_items:
        also = f'<div class="sec"><h2>{also_title}</h2><ul class="near">' + ''.join(f'<li><a href="{h}">{n}</a> <span>{t}</span></li>' for h, n, t in also_items[:5]) + '</ul></div>'
    lmeta = f'{e["town"]} · {e["county"]}' if e['town'] else e['county']
    vnote = VNOTE.replace('November 2026', e['month']).replace('October 2026', e['month'])
    main = f'''<main id="main">
<div class="wrap">
<nav aria-label="Breadcrumb" class="crumb"><a href="{crumb_root}">{crumb_root_name}</a> <i>/</i> <a href="{parent_href}">{parent_name}</a> <i>/</i> <span aria-current="page">{e["name"]}</span></nav>
<article>
<div class="lhead">
<p class="eyebrow">{eyebrow}</p>
<h1>{e["name"]}</h1>
<p class="lmeta">{lmeta}</p>
{vnote}
<p class="lhook">{e["hook"]}</p>
</div>
{phero(e)}
<div class="cols">
<div>
<div class="sec">
<h2>The visit</h2>
<p class="verified-lead">{e["lead"]}</p>
{boxes}{getting}<a class="btn" href="{e["site"]}" rel="noopener">Visit {poss(e["name"])} website →</a>
</div>
<div class="sec">
<h2>Common questions</h2>
{faqs}
</div>
</div>
<div>
<div class="sec">
<h2>At a glance</h2>
<dl class="facts">{facts}</dl>
</div>
{also}
</div>
</div>
</article>
</div>
</main>'''
    addr = {'@type': 'PostalAddress', 'addressRegion': plain(e['county']), 'addressCountry': 'GB'}
    if e['town']: addr = {'@type': 'PostalAddress', 'addressLocality': plain(e['town']), 'addressRegion': plain(e['county']), 'addressCountry': 'GB'}
    winery = {'@context': 'https://schema.org', '@type': 'Winery', 'name': plain(e['name']), 'description': plain(e['hook']), 'address': addr,
              'publicAccess': True, 'subjectOf': {'@type': 'WebPage', 'url': canon}, 'sameAs': [e['site']]}
    if s in PH: winery['image'] = f'{BASE}/img/{s}-1.jpg'
    ldobj = [winery,
             {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                 {'@type': 'ListItem', 'position': 1, 'name': plain(crumb_root_name), 'item': BASE + '/'},
                 {'@type': 'ListItem', 'position': 2, 'name': bc2_name, 'item': bc2_url},
                 {'@type': 'ListItem', 'position': 3, 'name': plain(e['name']), 'item': canon}]},
             {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
                 {'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in e['faqs']]}]
    place = plain(e['county'])
    title = f'{e["name"]} — visiting, tours &amp; tastings in {e["county"]} | Thatch &amp; Trail'
    desc = html.escape(plain(e['hook']) + ' Estate-verified.', quote=True)
    og = f'{BASE}/img/{s}-1.jpg' if s in PH else None
    return fill_page(TPL_EST, title, desc, canon, ldobj, main, og)

# ---------- hubs ----------
CARD_RE = re.compile(r'<a class="card"[^>]*href="\.\./v/([a-z0-9-]+)\.html">.*?</a>', re.S)
def parse_hub(p):
    s = rd(p); secs = []
    for m in re.finditer(r'<div class="stn" id="([^"]+)">\n<h2><span class="mono">(.*?)</span> <i>(.*?)</i></h2>\n<div class="grid">(.*?)</div>\n</div>', s, re.S):
        sid, label, info, grid = m.groups()
        towns = info.split(' · ', 1)[1] if ' · ' in info else ''
        cards = [(cm.group(1), cm.group(0)) for cm in CARD_RE.finditer(grid)]
        secs.append(dict(id=sid, label=label, towns=[t for t in towns.split(', ') if t], cards=cards))
    return s, secs
def town_token(e):
    t = e['town']
    if not t: return plain(e['county']) if False else e['county']
    if 'near ' in t: return t.split('near ', 1)[1]
    return t.split(', ')[-1] if ', ' in t and 'Chesterton' in t else t.split(', ')[0]
def card_name(cardhtml): return re.search(r'<div class="cname">(.*?)</div>', cardhtml).group(1)

def build_hub(rkey, new_es):
    R = REG[rkey]; p = f'{R["dir"]}/index.html'
    if R.get('new'):
        tpl = rd('north/index.html'); secs = []
    else:
        tpl, secs = parse_hub(p)
    for e in new_es:
        sid = COUNTY_SEC.get(e['county'], re.sub(r'[^a-z]+', '-', e['county'].lower()).strip('-'))
        sec = next((x for x in secs if x['id'] == sid), None)
        if not sec:
            sec = dict(id=sid, label=e['county'], towns=[], cards=[]); secs.append(sec)
        sec['cards'].append((e['slug'], hub_card(e, sec['label'])))
        tk = town_token(e)
        if tk and tk not in sec['towns'] and tk != sec['label']: sec['towns'].append(tk)
    if R.get('new'): secs.sort(key=lambda x: x['label'])
    for sec in secs:
        sec['cards'].sort(key=lambda c: plain(card_name(c[1])).lower().removeprefix('the '))
        sec['towns'].sort()
    n = sum(len(x['cards']) for x in secs)
    body = ''
    for sec in secs:
        k = len(sec['cards'])
        info = f'{k} vineyard{"s" if k != 1 else ""}' + (f' · {", ".join(sec["towns"])}' if sec['towns'] else '')
        body += (f'<div class="stn" id="{sec["id"]}">\n<h2><span class="mono">{sec["label"]}</span> <i>{info}</i></h2>\n'
                 f'<div class="grid">{"".join(c[1] for c in sec["cards"])}</div>\n</div>\n')
    allcards = sorted([c for x in secs for c in x['cards']], key=lambda c: plain(card_name(c[1])).lower())
    canon = f'{BASE}/{R["dir"]}/'
    hubname = plain(R['name'])
    counties = [x['label'] for x in secs]
    if rkey == 'midlands':
        h1 = 'Midlands vineyards you can visit'; title = 'Midlands vineyards to visit: tours, tastings and cellar doors | Thatch &amp; Trail'
        lede_lead = f'{join_names(counties)}.'
        nameshort = 'Midlands'
    elif rkey == 'islands':
        h1 = 'Channel Islands vineyards you can visit'; title = 'Channel Islands vineyards to visit: tours and tastings | Thatch &amp; Trail'
        lede_lead = 'Guernsey, to begin with.'
        nameshort = 'Channel Islands'
    else:
        h1 = re.search(r'<h1>(.*?)</h1>', tpl).group(1); title = re.search(r'<title>(.*?)</title>', tpl).group(1)
        old = re.search(r'<p class="lede">(.*?) \d+ estates so far', tpl).group(1)
        lede_lead = old
        if rkey == 'east': lede_lead = 'Essex, Suffolk, Norfolk, Hertfordshire, Cambridgeshire and Bedfordshire, from the Crouch to the Broads, Cambridge and Old Warden.'
        nameshort = re.search(r'<meta content="\d+ (.*?) vineyards open to visitors', tpl).group(1)
    if n == 1:
        lede = f'{lede_lead} 1 estate so far, and it has confirmed its details with us by email: opening days, tours, food, dogs and how to get there. Hours change with the seasons, so check with the estate before you travel.'
    else:
        lede = f'{lede_lead} {n} estates so far, and every one has confirmed its details with us by email: opening days, tours, food, dogs and how to get there. Hours change with the seasons, so check with the estate before you travel.'
    desc = f'{n} {nameshort} vineyard{"s" if n != 1 else ""} open to visitors, every one checked with the estate: opening days, tours, food, dogs and the nearest station.'
    main = f'''<main id="main">
<div class="wrap">
<nav aria-label="Breadcrumb" class="crumb"><a href="../index.html">Vineyards</a> <i>/</i> <a href="../regions/index.html">Regions</a> <i>/</i> <span aria-current="page">{R["name"]}</span></nav>
<div class="hubhead">
<p class="eyebrow">New · {R["name"]}</p>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
</div>
{body}<section class="prose">
<p class="pfoot"><a href="../regions/index.html">← All regions</a> · <a href="../index.html">The Sussex vineyards</a></p>
</section>
</div>
</main>'''
    ldobj = [{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': plain(h1).replace(' you can visit', ' to visit'), 'description': plain(desc), 'url': canon,
              'mainEntity': {'@type': 'ItemList', 'numberOfItems': n, 'itemListElement': [
                  {'@type': 'ListItem', 'position': i + 1, 'name': plain(card_name(c[1])), 'url': f'{BASE}/v/{c[0]}'} for i, c in enumerate(allcards)]}},
             {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                 {'@type': 'ListItem', 'position': 1, 'name': 'Vineyards', 'item': BASE + '/'},
                 {'@type': 'ListItem', 'position': 2, 'name': 'Regions', 'item': BASE + '/regions/'},
                 {'@type': 'ListItem', 'position': 3, 'name': hubname, 'item': canon}]}]
    page = fill_page(tpl, title, desc, canon, ldobj, main)
    wr(p, page)
    return dict(n=n, counties=counties, cards=allcards, secs=secs)

# ---------- plates (illustrations for homepage cards) ----------
def plate(slug, c):
    r = random.Random(slug)
    def ridge(y, amp, n=11):
        pts = [(-20 + i * 440 / (n - 1), y + r.uniform(-amp, amp)) for i in range(n)]
        d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f} '
        for i in range(1, n):
            x0, y0 = pts[i - 1]; x1, y1 = pts[i]
            d += f'C{x0 + (x1 - x0) / 3:.1f},{y0:.1f} {x1 - (x1 - x0) / 3:.1f},{y1:.1f} {x1:.1f},{y1:.1f} '
        return d.strip(), pts
    skies = [('#e7ede8', '#cad6d0'), ('#f1ece0', '#dfd6c2'), ('#eef0ea', '#d5ddd4'), ('#f3ebe2', '#e1d3c4')]
    s0, s1 = r.choice(skies)
    far, _ = ridge(118 + r.uniform(-8, 8), 14)
    mid, midpts = ridge(160 + r.uniform(-6, 6), 9)
    near, nearpts = ridge(196 + r.uniform(-5, 5), 8)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{s0}"/><stop offset="1" stop-color="{s1}"/></linearGradient><clipPath id="n"><path d="{near} L420.0,320 L-20.0,320 Z"/></clipPath></defs>',
           '<rect width="400" height="300" fill="url(#s)"/>',
           f'<circle cx="{r.randint(60, 340)}" cy="{r.randint(60, 95)}" r="{r.randint(14, 22)}" fill="#B99647" opacity=".32"/>',
           f'<path d="{far} L420.0,320 L-20.0,320 Z" fill="#9bb3a8"/>',
           f'<path d="{mid} L420.0,320 L-20.0,320 Z" fill="#7b957b"/>']
    for _ in range(r.randint(3, 5)):
        i = r.randint(1, 9); x, y = midpts[i]
        for k in range(r.randint(2, 4)):
            out.append(f'<circle cx="{x + k * 7:.1f}" cy="{y - 4 + r.uniform(-1.5, 1.5):.1f}" r="{r.uniform(5.4, 8):.1f}" fill="#2C4630" opacity=".78"/>')
    bx, by = midpts[r.randint(3, 7)]
    out.append(f'<g fill="#4C5A63"><rect x="{bx:.1f}" y="{by - 9:.1f}" width="26" height="11"/><path d="M{bx:.1f} {by - 9:.1f}l13 -9 13 9z"/></g>')
    out.append(f'<path d="{near} L420.0,320 L-20.0,320 Z" fill="{c}"/>')
    vx, vy = r.uniform(120, 280), min(p[1] for p in nearpts) - r.uniform(40, 60)
    lines = ''.join(f'<line x1="{vx:.1f}" y1="{vy:.1f}" x2="{-276 + 34 * i:.1f}" y2="320"/>' for i in range(29))
    out.append(f'<g clip-path="url(#n)" stroke="#e9e2cf" stroke-width="2.2" opacity=".35">{lines}</g>')
    out.append(f'<path d="{near}" fill="none" stroke="#2C4630" stroke-width="1.2" opacity=".55"/></svg>')
    return ''.join(out)

if __name__ == '__main__':
    import sys
    make_photos()
    print('photos', len(photo_dims))
