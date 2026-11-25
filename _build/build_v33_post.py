# v33 step 2: photo, badges, UK homepage + map, Sussex page, region maps, site-wide fixes, sitemap.
import sys, os, re, json, html, glob, csv, subprocess, shutil
SP = '/tmp/claude-0/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/scratchpad'
sys.path.insert(0, SP)
from build_v33 import SITE, BASE, TODAY, rd, wr, plain, ld, join_names, E, fill_page
from PIL import Image
REP = json.load(open(SP + '/v33_report.json'))
N_SUS, VER, PAGES, KENT = REP['N_SUS'], REP['VER'], REP['PAGES'], REP['KENT']
ASSETS = SP + '/v33assets'
TR = '/root/.claude/projects/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/tool-results'
LOG = []

# ---------- 1. Limeburn Hill photo ----------
im = Image.open(TR + '/mcp-Gmail-blob-1795008545470-txfpix.jpg').convert('RGB')
W, H = im.size; im = im.crop((0, int(.07 * H), W, int(.07 * H) + int(W / 1.5)))
im = im.resize((1600, round(1600 / 1.5)), Image.LANCZOS)
im.save(f'{SITE}/img/limeburn-hill-vineyard-1.jpg', quality=82, optimize=True, progressive=True)
im.save(f'{SITE}/img/limeburn-hill-vineyard-1.webp', quality=80)
s = rd('v/limeburn-hill-vineyard.html')
ph = ('<div class="phero"><picture><source srcset="../img/limeburn-hill-vineyard-1.webp" type="image/webp"><img src="../img/limeburn-hill-vineyard-1.jpg" '
      'alt="Rows of vines at Limeburn Hill at dawn, looking out over mist in the Chew Valley" loading="lazy" width="1600" height="1067"></picture>'
      '<div class="phcap">Dawn over the Chew Valley · Photograph courtesy of Limeburn Hill Vineyard</div></div>')
assert 'class="phero"' not in s
k = s.find('<div class="cols">'); assert k > 0
s = s[:k] + ph + '\n' + s[k:]
assert ph in s
s = re.sub(r'<meta content="[^"]*" property="og:image"/>', f'<meta content="{BASE}/img/limeburn-hill-vineyard-1.jpg" property="og:image"/>', s, 1)
s = re.sub(r'<meta content="[^"]*" name="twitter:image"/>', f'<meta content="{BASE}/img/limeburn-hill-vineyard-1.jpg" name="twitter:image"/>', s, 1)
s = s.replace('"@type": "Winery", ', f'"@type": "Winery", "image": "{BASE}/img/limeburn-hill-vineyard-1.jpg", ', 1)
wr('v/limeburn-hill-vineyard.html', s)
LOG.append('limeburn photo added')

# ---------- 2. badge share images for the new estates ----------
seal = re.search(r'<svg class="vn-seal".*?</svg>', rd('v/llaethliw.html'), re.S).group(0).replace('class="vn-seal" ', '')
font = lambda f: f'file://{SITE}/fonts/{f}'
os.makedirs(SP + '/share', exist_ok=True); jobs = []
for e in E:
    nm_ = e['name']; size = 74 if len(plain(nm_)) <= 22 else (62 if len(plain(nm_)) <= 28 else 52)
    page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:F;src:url({font("fraunces.woff2")})}}@font-face{{font-family:FI;src:url({font("fraunces-italic.woff2")})}}
@font-face{{font-family:K;src:url({font("karla.woff2")})}}@font-face{{font-family:M;src:url({font("space-mono.woff2")})}}
html,body{{margin:0;width:1080px;height:1080px;background:#f6efdf}}
.c{{position:absolute;inset:36px;border:2px solid #c9a86a;border-radius:6px;display:flex;flex-direction:column;align-items:center;overflow:hidden;
background:repeating-linear-gradient(105deg,transparent 0 46px,rgba(176,160,120,.16) 46px 48px) bottom/100% 300px no-repeat,#f6efdf}}
.c:after{{content:"";position:absolute;left:0;right:0;bottom:300px;height:200px;background:linear-gradient(#f6efdf,rgba(246,239,223,0))}}
.seal{{margin-top:228px;width:250px;height:250px;filter:drop-shadow(0 18px 30px rgba(90,70,30,.18))}}
.l{{margin-top:44px;font:400 26px M;letter-spacing:.32em;color:#a0522d;text-transform:uppercase}}
.n{{margin-top:18px;font:400 {size}px/1.08 F;color:#23211c;text-align:center;padding:0 60px;letter-spacing:-.01em}}
.o{{margin-top:14px;font:italic 400 44px FI;color:#4a542c}}
.d{{margin-top:22px;font:400 24px K;color:#5c584c;letter-spacing:.01em}}
.u{{position:absolute;bottom:36px;font:400 23px M;color:#4a542c;letter-spacing:.06em;z-index:2}}
.seal,.l,.n,.o,.d{{position:relative;z-index:2}}
</style></head><body><div class="c"><div class="seal">{seal.replace('<svg ', '<svg width="250" height="250" ')}</div>
<div class="l">Estate-verified</div><div class="n">{nm_}</div><div class="o">on Thatch &amp; Trail</div>
<div class="d">Details confirmed with the estate · {e["month"]}</div><div class="u">thatchandtrail.com/v/{e["slug"]}</div></div></body></html>'''
    hp = f'{SP}/share/{e["slug"]}.html'; open(hp, 'w').write(page); jobs.append((hp, f'{SITE}/badge/share/{e["slug"]}.jpg'))
json.dump(jobs, open(SP + '/share/jobs.json', 'w'))
open(SP + '/share/render.js', 'w').write(f'''const {{chromium}}=require('playwright');const jobs=require('{SP}/share/jobs.json');
(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1080}},deviceScaleFactor:1}});
for(const [h,o] of jobs){{await p.goto('file://'+h);await p.evaluate(()=>document.fonts.ready);await p.screenshot({{path:o,type:'jpeg',quality:90}});}}
await b.close();}})();''')
r = subprocess.run(['node', SP + '/share/render.js'], capture_output=True, text=True); LOG.append(f'badges rendered rc={r.returncode} {r.stderr[-200:]}')

# ---------- 3. every estate, with region, flags and map position ----------
RG = [  # key, name, page, colour
 ('sussex', 'Sussex', 'sussex/index.html', '#3B5A3F'), ('kent', 'Kent', 'kent/index.html', '#9A6233'),
 ('surrey', 'Surrey', 'surrey/index.html', '#6E5C9A'), ('hampshire', 'Hampshire', 'hampshire/index.html', '#2F6E6A'),
 ('thames', 'Berkshire &amp; Buckinghamshire', 'thames/index.html', '#A8853A'), ('east', 'East of England', 'east/index.html', '#7A3B4E'),
 ('southwest', 'The South West', 'southwest/index.html', '#3E6F8E'), ('west', 'Cotswolds &amp; the West', 'west/index.html', '#86702F'),
 ('wales', 'Wales', 'wales/index.html', '#B0473A'), ('midlands', 'The Midlands', 'midlands/index.html', '#5E7A33'),
 ('north', 'Yorkshire', 'north/index.html', '#4C5A63'), ('islands', 'Channel Islands', 'channel-islands/index.html', '#24777A')]
RGK = {k: (n, p, c) for k, n, p, c in RG}
DIR2R = {p.split('/')[0]: k for k, n, p, c in RG if k != 'sussex'}
MAN = {
 'aldwick-estate': (51.355, -2.715), 'albury-vineyard': (51.222, -0.487), 'astley-vineyard': (52.302, -2.327), 'bailey-hills': (51.880, 0.150),
 'bantham-vineyard': (50.279, -3.873), 'barnsole-vineyard': (51.270, 1.255), 'biddenden-vineyards': (51.098, 0.652), 'brabourne-vineyard': (51.132, 0.985),
 'brecks-vineyard': (52.462, 0.540), 'bride-valley': (50.716, -2.630), 'burn-valley-vineyard': (52.915, 0.745), 'carlton-towers': (53.710, -1.020),
 'chase-end-vineyard': (51.998, -2.392), 'chet-valley-vineyard': (52.565, 1.395), 'crouch-ridge-estate': (51.655, 0.762), 'davenport-vineyards': (51.140, 0.428),
 'dedham-vale-vineyard': (51.950, 0.910), 'domaine-evremond': (51.245, 0.965), 'dunesforde': (54.056, -1.335), 'exton-park': (50.985, -1.118),
 'greyfriars-vineyard': (51.222, -0.672), 'gusbourne-estate': (51.031, 0.790), 'ham-street-wines': (51.066, 0.856), 'hambledon-vineyard': (50.932, -1.077),
 'hanwell-wine-estate': (52.835, -1.005), 'heron-farm': (50.795, -3.235), 'knotfield-vines': (53.851, -1.680), 'little-waddon-vineyard': (50.668, -2.560),
 'marlbank-vineyard': (52.060, -2.290), 'mereworth-wines': (51.258, 0.385), 'new-hall-wine-estate': (51.690, 0.660), 'northbrook-vineyard': (50.955, -1.212),
 'poulton-hill-estate': (51.700, -1.858), 'raimes': (51.090, -1.163), 'reservoir-view-vineyard': (49.452, -2.595), 'st-hilary-vineyard': (51.457, -3.405),
 'candover-brook': (51.160, -1.170), 'the-dell-vineyard': (51.765, -2.851), 'valley-farm-vineyards': (52.355, 1.470), 'veenow': (52.765, -2.548),
 'walsingham-estate-vineyard': (52.893, 0.874), 'warehorne-vineyard': (51.048, 0.833), 'wellhayes-vineyard': (50.995, -3.405), 'westwell-wine-estates': (51.208, 0.797),
 'white-castle-vineyard': (51.850, -2.930), 'white-heron-estate': (52.203, -2.975), 'wolds-wine-estate': (52.880, -1.075), 'woodchurch-wine-estate': (51.077, 0.773),
 'stanlake-park': (51.478, -0.865), 'harrow-and-hope': (51.578, -0.790), 'marlow-valley-vineyard': (51.565, -0.770), 'langham-wine-estate': (50.785, -2.335),
 'glyndwr-vineyard': (51.462, -3.447), 'nine-oaks-vineyard': (51.168, 0.815), 'leventhorpe-vineyard': (53.752, -1.450), 'alder-vineyard': (50.660, -4.205),
 'warden-abbey-vineyard': (52.079, -0.355), 'bosue-vineyard': (50.290, -4.830), 'kenton-park-estate': (50.637, -3.480),
 'the-b58-winery': (50.792, -1.493), 'breezy-ridge-vineyard': (50.980, -2.205), 'godstone-vineyards': (51.256, -0.065),
 'winding-wood-vineyard': (51.420, -1.290), 'all-angels-vineyard': (51.385, -1.350), 'helme-edge-vineyard': (53.595, -1.850),
}
import reverse_geocoder
gaz = {}
for r_ in csv.DictReader(open(os.path.join(os.path.dirname(reverse_geocoder.__file__), 'rg_cities1000.csv'))):
    if r_['cc'] == 'GB': gaz.setdefault(r_['name'].lower(), []).append(r_)
home = rd('index.html')   # still the Sussex homepage at this point
home = home.replace('imagesrcset="img/hero-1-900.webp 900w, img/hero-1-1600.webp 1600w, img/hero-1.webp 2000w"', 'imagesrcset="img/hero-autumn-900.webp 900w, img/hero-autumn-1600.webp 1600w, img/hero-autumn.webp 2000w"')
assert 'imagesrcset="img/hero-autumn-900.webp' in home
atlas = {x['s']: x for x in json.loads(re.search(r'id="atlas-data">(.*?)</script>', home, re.S).group(1))}
D = json.loads(re.search(r'var D=(\{.*?\});', rd('verified.html')).group(1))
flags = {}
for p in glob.glob(SITE + '/*/index.html') + glob.glob(SITE + '/trail/*.html') + [SITE + '/index.html']:
    t = open(p).read()
    for m in re.finditer(r'<(?:a class="card"|article class="vcard")[^>]*?data-food="(\w+)"[^>]*?data-stay="(\w+)"[^>]*?(?:href="\.\./v/([a-z0-9-]+)\.html"|data-slug="([a-z0-9-]+)")', t):
        flags[m.group(3) or m.group(4)] = (m.group(1) == 'Yes', m.group(2) == 'Yes')
for m in re.finditer(r'<article class="vcard" id="v-([a-z0-9-]+)" data-slug="[^"]+" data-trail="[^"]*" data-visit="[^"]*" data-food="(\w+)" data-stay="(\w+)"', home):
    flags[m.group(1)] = (m.group(2) == 'Yes', m.group(3) == 'Yes')
ALL = []; unresolved = []
for p in sorted(glob.glob(SITE + '/v/*.html')):
    slug = os.path.basename(p)[:-5]; t = open(p).read()
    name = re.sub(r'<[^>]+>', '', re.search(r'<h1>(.*?)</h1>', t).group(1))
    lm = re.search(r'<p class="lmeta">(.*?)</p>', t).group(1)
    town, _, county = lm.partition(' · ')
    if not county: county, town = town, ''
    crumb = re.search(r'<nav aria-label="Breadcrumb" class="crumb">(.*?)</nav>', t, re.S).group(1)
    parent = re.findall(r'<a href="\.\./([^"]+)">', crumb)[-1]
    reg = 'sussex' if (parent.startswith('trail/') or parent == 'index.html') else DIR2R[parent.split('/')[0]]
    if slug in atlas: la, lo = atlas[slug]['lat'], atlas[slug]['lng']
    elif slug in MAN: la, lo = MAN[slug]
    else:
        la = lo = None
        cands = [x.strip() for x in re.split(r',| / |\(|\)', html.unescape(town).replace('near ', ',')) if x.strip()]
        for c in cands:
            for r_ in gaz.get(c.lower(), []):
                if html.unescape(county).split()[-1].lower() in (r_['admin2'] + ' ' + r_['admin1']).lower():
                    la, lo = float(r_['lat']), float(r_['lon']); break
            if la: break
        if la is None: unresolved.append(slug); continue
    f, st = flags.get(slug, (False, False))
    ALL.append(dict(s=slug, n=html.unescape(name), t=html.unescape(town or county), county=html.unescape(county), r=reg, h=f'v/{slug}.html',
                    lat=round(la, 4), lng=round(lo, 4), v=slug in D, f=f, st=st, nh=name))
assert not unresolved, unresolved
# nudge pins that sit on exactly the same spot
seen = {}
for d in ALL:
    k = (d['lat'], d['lng'])
    if k in seen: seen[k] += 1; d['lat'] = round(d['lat'] + 0.012 * seen[k], 4); d['lng'] = round(d['lng'] + 0.018 * seen[k], 4)
    else: seen[k] = 0
assert len(ALL) == PAGES, (len(ALL), PAGES)
N = len(ALL); NV = sum(d['v'] for d in ALL)
assert NV == VER, (NV, VER)
cnt = {k: sum(1 for d in ALL if d['r'] == k) for k, *_ in RG}
LOG.append(f'directory {N} estates, {NV} verified; per region {cnt}')
json.dump(ALL, open(SP + '/v33_directory.json', 'w'), ensure_ascii=False, indent=0)

# ---------- 4. the Sussex homepage moves to /sussex/ ----------
def prefix_urls(t, pre='../'):
    def fix(u):
        if re.match(r'(https?:|#|/|mailto:|tel:|data:|javascript:)', u) or u == '': return u
        return pre + u
    t = re.sub(r'(\s(?:href|src))="([^"]*)"', lambda m: f'{m.group(1)}="{fix(m.group(2))}"', t)
    t = re.sub(r'(\s(?:srcset|imagesrcset))="([^"]*)"', lambda m: m.group(1) + '="' + ', '.join(' '.join([fix(x.strip().split(' ')[0])] + x.strip().split(' ')[1:]) for x in m.group(2).split(',')) + '"', t)
    return t
sus = prefix_urls(home)
tag = '<script type="application/json" id="atlas-data">'
ai = sus.find(tag) + len(tag); aj = sus.find('</script>', ai)
adata = json.loads(sus[ai:aj])
for x in adata: x['h'] = '../' + x['h']; x['img'] = '../' + x['img']
sus = sus[:ai] + json.dumps(adata, ensure_ascii=False) + sus[aj:]
sus = re.sub(r'<link href="[^"]*" rel="canonical"/>', f'<link href="{BASE}/sussex/" rel="canonical"/>', sus, 1)
sus = re.sub(r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{BASE}/sussex/" property="og:url"/>', sus, 1)
m = re.search(r'<script type="application/ld\+json">(.*?)</script>', sus, re.S)
blocks = json.loads(m.group(1))
nb = []
for b in blocks:
    if b.get('@type') == 'Organization': continue
    if isinstance(b.get('@type'), list) and 'WebSite' in b['@type']:
        b['@type'] = 'CollectionPage'; b['url'] = f'{BASE}/sussex/'; b.pop('potentialAction', None)
    nb.append(b)
nb.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': 1, 'name': 'Vineyards', 'item': BASE + '/'},
    {'@type': 'ListItem', 'position': 2, 'name': 'Sussex', 'item': BASE + '/sussex/'}]})
sus = sus[:m.start(1)] + json.dumps(nb, ensure_ascii=False, separators=(',', ':')) + sus[m.end(1):]
sus = sus.replace('<span class="au-pill">Autumn 2026</span> The independent guide to Sussex &amp; Kent wine country', '<span class="au-pill">Winter 2026</span> Part of the guide to vineyards across England &amp; Wales')
sus = sus.replace('updated October 2026', 'updated November 2026')
sus = sus.replace('>What’s on this autumn</a>', '>What’s on this winter</a>').replace('What’s on at the vineyards this autumn', 'What’s on at the vineyards this winter')
sus = re.sub(r'<p aria-hidden="true" class="hero-signoff">.*?</p>', '<p aria-hidden="true" class="hero-signoff">Cellar doors.<br/>Sunday roasts.<br/><em>Christmas.</em></p>', sus, 1, re.S)
sus = re.sub(r'plus 14 new in Kent', f'plus {KENT} in Kent', sus)
OTHERS = N - N_SUS - KENT
sus = re.sub(r'\d+ new estates so far, from Guernsey to Yorkshire, plus \d+ more in Kent\.', f'{OTHERS} new estates so far, from Guernsey to Yorkshire, plus {KENT - 14} more in Kent.', sus)
for k, n_, pg, c in RG:
    if k == 'sussex': continue
    sus = re.sub(rf'(<a href="\.\./{re.escape(pg)}"><b>[^<]*</b><span>)\d+( vineyards?</span></a>)', lambda x: x.group(1) + str(cnt[k]) + (' vineyards</span></a>' if cnt[k] != 1 else ' vineyard</span></a>'), sus, 1)
os.makedirs(SITE + '/sussex', exist_ok=True)
wr('sussex/index.html', sus)
LOG.append('sussex page written')

# ---------- 5. the new UK homepage ----------
uk = home
head_end = uk.find('</head>')
title = f'Vineyards to Visit in England &amp; Wales: {N} Estates | Thatch &amp; Trail'
desc = f'{N} vineyards to visit across England, Wales and the Channel Islands, {NV} checked with the estate: tours, tastings, cellar doors, food, stays and the nearest station.'
hd = uk[:head_end]
hd = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', hd, 1, re.S)
for prop in ('og:title', 'twitter:title'):
    hd = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda x: f'<meta content="{title}" {x.group(1)}="{prop}"/>', hd)
for prop in ('description', 'og:description', 'twitter:description'):
    hd = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda x: f'<meta content="{desc}" {x.group(1)}="{prop}"/>', hd)
hd = re.sub(r'<meta content="[^"]*" property="og:image:alt"/>', '<meta content="Rows of vines in the English countryside" property="og:image:alt"/>', hd)
faq = [
 ('Do I need to book before visiting a vineyard?', 'Often, yes. Many tours and tastings are pre-booked only, and some estates open their cellar door on set days. Each guide says what the estate told us, so check it before you travel.'),
 ('Can I visit a vineyard without a car?', 'Many estates are a short taxi from a station, and a few are a walk. Every guide gives the nearest station and how the estate suggests you finish the journey.'),
 ('What does estate-verified mean?', f'The estate itself has confirmed its details to us by email: opening days, tours, food, dogs and how to get there. {NV} of the {N} estates in the guide have done so.'),
 ('Which parts of the UK does the guide cover?', 'Sussex, where it began, plus Kent, Surrey, Hampshire, the Thames Valley, the East of England, the South West, the Cotswolds and the West, Wales, the Midlands, Yorkshire and the Channel Islands, with more estates added every week.'),
]
ldobj = [
 {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Thatch & Trail', 'url': BASE + '/', 'logo': BASE + '/icon-512.png',
  'description': 'An independent, estate-checked guide to vineyards and wine days out across England and Wales.', 'email': 'thatchandtrail@gmail.com'},
 {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Thatch & Trail', 'url': BASE + '/', 'inLanguage': 'en-GB'},
 {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Vineyards to visit in England and Wales', 'url': BASE + '/', 'description': plain(desc),
  'mainEntity': {'@type': 'ItemList', 'name': 'Vineyards open to visitors', 'numberOfItems': N,
                 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': d['n'], 'url': f'{BASE}/v/{d["s"]}'} for i, d in enumerate(sorted(ALL, key=lambda d: d['n'].lower()))]}},
 {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
hd = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _m: '<script type="application/ld+json">' + json.dumps(ldobj, ensure_ascii=False, separators=(',', ':')) + '</script>', hd, 1, re.S)
body_start = uk.find('<main id="main">'); main_end = uk.find('</main>') + len('</main>')
old_main = uk[body_start:main_end]
def sec(start, end=None):
    i = old_main.find(start); assert i >= 0, start
    j = old_main.find('</section>', i) + len('</section>') if end is None else old_main.find(end, i)
    return old_main[i:j]
hero = sec('<section aria-labelledby="home-title" class="warm-hero">')
hero = hero.replace('<span class="au-pill">Autumn 2026</span> The independent guide to Sussex &amp; Kent wine country',
                    '<span class="au-pill">Winter 2026</span> The independent guide to vineyards in England &amp; Wales')
hero = re.sub(r'<h1 id="home-title">.*?</h1>', '<h1 id="home-title">Discover the <em>vineyards</em> of England &amp; Wales</h1>', hero, 1, re.S)
hero = re.sub(r'<p class="hero-lede">.*?</p>', f'<p class="hero-lede">Cellar doors, tours and long lunches from Cornwall to Yorkshire, and across to Wales and Guernsey. {N} vineyards so far, {NV} of them checked with the estate itself, with the details that make a day out easy.</p>', hero, 1, re.S)
hero = re.sub(r'<div class="hero-actions">.*?</div>', '<div class="hero-actions">\n<a class="btn btn-light" href="#vineyards">Find a vineyard on the map</a>\n<a class="btn btn-ghost" href="guide/christmas-at-the-vineyard.html">Christmas at the vineyard</a>\n</div>', hero, 1, re.S)
hero = re.sub(r'<p class="hero-note">.*?</p>', '<p class="hero-note">England, Wales &amp; the Channel Islands · estate-checked · updated November 2026</p>', hero, 1)
hero = re.sub(r'<p aria-hidden="true" class="hero-signoff">.*?</p>', '<p aria-hidden="true" class="hero-signoff">Cellar doors.<br/>Winter walks.<br/><em>English fizz.</em></p>', hero, 1, re.S)
assert 'England &amp; Wales</h1>' in hero and 'Find a vineyard on the map' in hero
promises = sec('<section aria-label="What Thatch and Trail helps you find" class="warm-promises">')
promises = promises.replace('Boutique vineyards', 'Every region').replace('Every visitor-friendly estate in East and West Sussex.', 'From Cornwall to Yorkshire, plus Wales and Guernsey, with more added every week.')
promises = promises.replace('Beautiful countryside', 'Checked with the estate').replace('Wine days set among the South Downs and High Weald.', f'{NV} estates have confirmed their own details with us by email.')
assert 'Every region' in promises and 'Checked with the estate' in promises
# map + directory
keys = '<button type="button" class="uk-key" data-r="" aria-pressed="true">All regions</button>' + ''.join(
    f'<button type="button" class="uk-key" data-r="{k}" aria-pressed="false" style="--tc:{c}"><i aria-hidden="true"></i>{n_}</button>' for k, n_, pg, c in RG)
groups = ''
for k, n_, pg, c in RG:
    ds = sorted([d for d in ALL if d['r'] == k], key=lambda d: d['n'].lower().removeprefix('the '))
    rows = ''.join(f'<li class="ud-row" data-s="{d["s"]}"><a href="{d["h"]}">{d["nh"]}</a><span>{html.escape(d["t"])}</span>{"<b>&#10003; Verified</b>" if d["v"] else ""}</li>' for d in ds)
    groups += f'<section class="ud-group" data-r="{k}" style="--tc:{c}"><h3><a href="{pg}">{n_}</a> <i>{len(ds)}</i></h3><ul>{rows}</ul></section>'
mapdata = [{'s': d['s'], 'n': d['n'], 't': d['t'], 'r': d['r'], 'h': d['h'], 'lat': d['lat'], 'lng': d['lng'], 'v': d['v'], 'f': d['f'], 'st': d['st']} for d in ALL]
regmeta = {k: {'n': plain(n_), 'c': c, 'h': pg} for k, n_, pg, c in RG}
directory = f'''<section aria-labelledby="directory-title" class="directory uk-directory" id="vineyards">
<div class="wrap">
<div class="section-head directory-head"><div><p class="eyebrow">Every vineyard in the guide</p><h2 id="directory-title">Find a vineyard near you</h2><p>All {N} estates on one map. Pick a region, or show only the estates that have confirmed their details, serve food or have rooms. Tap a pin for its guide, or browse the list below.</p></div></div>
<div class="uk-controls"><div class="uk-keys" role="group" aria-label="Show one region">{keys}</div>
<div class="uk-chips" role="group" aria-label="Filter the vineyards"><button type="button" class="chip" data-f="v" aria-pressed="false">Estate-verified</button><button type="button" class="chip" data-f="food" aria-pressed="false">Food on site</button><button type="button" class="chip" data-f="stay" aria-pressed="false">Stay the night</button></div></div>
<div class="uk-map" id="uk-map" role="region" aria-label="Map of vineyards in England, Wales and the Channel Islands"><p class="atlas-fallback">The map needs JavaScript. Every vineyard is listed below.</p></div>
<p class="uk-note"><span class="ak-pin ak-pin--v" aria-hidden="true"></span>Estate-verified <span class="ak-pin ak-pin--o" aria-hidden="true"></span>Details being confirmed <span>Pins are placed by town or village, not exact address.</span></p>
<p class="count uk-count"><b id="uk-n">{N}</b> vineyards shown</p>
<div class="ud-groups" id="uk-list">{groups}</div>
<p class="ud-empty" hidden id="uk-empty">No vineyards match those filters. Try fewer.</p>
<script type="application/json" id="uk-data">{json.dumps(mapdata, ensure_ascii=False, separators=(',', ':'))}</script>
<script type="application/json" id="uk-regions">{json.dumps(regmeta, ensure_ascii=False, separators=(',', ':'))}</script>
</div>
</section>'''
rgrid = ''.join(f'<a href="{pg}"><b>{n_}</b><span>{cnt[k]} vineyard{"s" if cnt[k] != 1 else ""}</span></a>' for k, n_, pg, c in RG)
regions_strip = f'''<section aria-labelledby="regions-title" class="rs-strip">
<div class="wrap">
<div class="rs-copy"><p class="eyebrow">Explore by region</p>
<h2 id="regions-title">Twelve regions, one guide</h2>
<p>Thatch &amp; Trail began in Sussex, with seven wine trails and a day planner. Every region now has its own page and map, and we check the details of every estate with the estate itself.</p>
<a href="regions/index.html">See every region →</a></div>
<div class="rs-grid">{rgrid}</div>
</div>
</section>'''
season = '''<section aria-labelledby="season-uk-title" class="uk-season">
<div class="wrap">
<div><p class="eyebrow">This winter</p><h2 id="season-uk-title">Christmas markets, winter walks and fizz to take home</h2>
<p>Plenty of cellar doors stay open through the winter, and some hold Christmas markets and festive tastings. Every date in our guides comes from the estate itself.</p></div>
<div class="uk-season-links"><a href="guide/christmas-at-the-vineyard.html"><b>Christmas at the vineyard</b><span>Markets, tastings and gifts across England &amp; Wales</span></a>
<a href="guide/vineyards-in-winter.html"><b>Vineyards open in winter</b><span>Cellar doors and dates in Sussex &amp; Kent</span></a>
<a href="sussex/index.html"><b>The Sussex guide</b><span>Seven wine trails and a day planner</span></a></div>
</div>
</section>'''
discover = sec('<section aria-labelledby="guide-title" class="v4-discover">')
discover = discover.replace('<p class="eyebrow">Choose the day you want</p>', '<p class="eyebrow">Sussex &amp; Kent guides</p>')
verified_sec = sec('<section aria-labelledby="verified-title" class="v4-verified">')
faq_html = '''<section aria-labelledby="faq-title" class="v4-faq">
<div class="wrap v4-faq-grid">
<div><p class="eyebrow">Before you set off</p><h2 id="faq-title">A few useful answers</h2><p>Vineyards vary enormously, from big estates with restaurants to a cellar door open a few afternoons a week. These are the questions people ask most.</p></div>
<div class="v4-faq-list">
''' + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>\n' for q, a in faq) + '''</div>
</div>
</section>'''
new_main = '<main id="main">\n' + '\n'.join([hero, promises, directory, regions_strip, season, discover, verified_sec, faq_html]) + '\n</main>'
uk = hd + uk[head_end:body_start] + new_main + uk[main_end:]
uk = uk.replace('<script src="atlas.js" defer></script>', '<script src="maps.js" defer></script>')
assert 'maps.js' in uk and 'atlas.js' not in uk
wr('index.html', uk)
shutil.copy(ASSETS + '/maps.js', SITE + '/maps.js')
LOG.append('uk homepage written')

# ---------- 6. a map on every region page, and on the regions page ----------
def hub_map(dpath, ds, label):
    t = rd(dpath)
    pts = [{'s': d['s'], 'n': d['n'], 't': d['t'], 'h': '../' + d['h'], 'lat': d['lat'], 'lng': d['lng'], 'v': d['v'], 'c': RGK[d['r']][2], 'r': d['r']} for d in ds]
    blk = (f'<div class="hub-map" id="hub-map" role="region" aria-label="Map of {label} vineyards"><p class="atlas-fallback">The map needs JavaScript. Every vineyard is listed below.</p></div>\n'
           f'<script type="application/json" id="hub-map-data">{json.dumps(pts, ensure_ascii=False, separators=(",", ":"))}</script>\n')
    i = t.find('<div class="hubhead">'); j = t.find('</div>\n', i) + len('</div>\n')
    assert i > 0 and 'hub-map' not in t
    t = t[:j] + blk + t[j:]
    t = t.replace('</body>', '<script src="../maps.js" defer></script>\n</body>', 1)
    wr(dpath, t)
for k, n_, pg, c in RG:
    if k == 'sussex': continue
    hub_map(pg, [d for d in ALL if d['r'] == k], plain(n_))
hub_map('regions/index.html', ALL, 'England and Wales')

# regions page counts
t = rd('regions/index.html')
t = re.sub(r'(only once the estate itself has confirmed the details\. )\d+( so far)', lambda x: x.group(1) + str(OTHERS) + x.group(2), t)
t = t.replace('<a class="card" href="../index.html"><div class="ctrail">The original guide</div>', '<a class="card" href="../sussex/index.html"><div class="ctrail">The original guide</div>')
t = re.sub(r'(<a class="card" href="\.\./sussex/index\.html">.*?<span class="tag on">)\d+( vineyards</span>)', lambda x: x.group(1) + str(cnt['sussex']) + x.group(2), t, 1, re.S)
for k, n_, pg, c in RG:
    if k == 'sussex': continue
    t = re.sub(rf'(<a class="card" href="\.\./{re.escape(pg)}">.*?<span class="tag (?:on|verified)">)\d+( (?:verified|vineyards)</span>)', lambda x: x.group(1) + str(cnt[k]) + x.group(2), t, 1, re.S)
wr('regions/index.html', t)

# ---------- 7. site-wide: nav + phone menu, footer, Sussex links, icons, 404 ----------
NAV = [('Vineyards', 'index.html'), ('Regions', 'regions/index.html'), ('Sussex', 'sussex/index.html'), ('By train', 'guide/vineyards-by-train.html'),
       ('Food', 'guide/vineyards-with-restaurants.html'), ('Stay', 'guide/vineyards-with-accommodation.html'), ('About', 'about.html')]
ICONS = ('<link href="/favicon.ico" rel="icon" sizes="32x32"/>\n<link href="/favicon.svg" rel="icon" type="image/svg+xml"/>\n'
         '<link href="/apple-touch-icon.png" rel="apple-touch-icon"/>\n<link href="/site.webmanifest" rel="manifest"/>\n<meta content="#4a542c" name="theme-color"/>')
FNOTE = 'The independent guide to vineyards across England and Wales: cellar doors, tours, wine trails and slow countryside days, checked with the estates.'
stats = {'nav': 0, 'menu': 0, 'footer': 0, 'icons': 0, 'crumb': 0}
for p in sorted(glob.glob(SITE + '/**/*.html', recursive=True)):
    rel = os.path.relpath(p, SITE)
    if rel.startswith('google'): continue
    t = open(p).read(); o = t
    pre = '/' if rel == '404.html' else '../' * rel.count('/')
    nav = ''.join(f'<a href="{pre}{h}">{n_}</a>' for n_, h in NAV) + f'<a class="nav-cta" href="{pre}index.html#vineyards">Find a vineyard</a>'
    menu = ('<details class="mnav"><summary>Menu</summary><div class="mnav-panel">' + ''.join(f'<a href="{pre}{h}">{n_}</a>' for n_, h in NAV) +
            f'<a href="{pre}guide/christmas-at-the-vineyard.html">Christmas</a><a href="{pre}verified.html">Estate-verified</a>'
            f'<a class="mnav-cta" href="{pre}index.html#vineyards">Find a vineyard</a></div></details>')
    t, n1 = re.subn(r'<nav aria-label="Primary">.*?</nav>', lambda _m: f'<nav aria-label="Primary">{nav}</nav>{menu}', t, 1, re.S)
    stats['nav'] += n1; stats['menu'] += n1
    # footer
    t = re.sub(r'<p class="fnote">.*?</p>', f'<p class="fnote">{FNOTE}</p>', t, 1, re.S)
    t, n2 = re.subn(r'<li><a href="[^"]*">All \d+ vineyards</a></li>', f'<li><a href="{pre}index.html#vineyards">All {N} vineyards</a></li><li><a href="{pre}sussex/index.html">Sussex vineyards</a></li>', t, 1)
    stats['footer'] += n2
    t = t.replace('">Wine trails</a></p>', '">Sussex wine trails</a></p>', 1)
    t = t.replace('The best of Sussex, straight to your inbox', 'The best vineyard days out, straight to your inbox')
    t = re.sub(r'action="(?:\.\./)*thanks\.html"', 'action="/thanks.html"', t)
    t, n4 = re.subn(r'(<div><p class="fh">Guides</p><ul>)', lambda m: m.group(1) + f'<li><a href="{pre}index.html#vineyards">All {N} vineyards on the map</a></li><li><a href="{pre}sussex/index.html">Sussex vineyards</a></li>', t, 1)
    stats['footer'] += n4
    t = t.replace('>England &amp; Wales (new)</a>', '>All regions</a>').replace('">Wine trails</a></li>', '">Sussex wine trails</a></li>')
    t = t.replace('>Kent vineyards</a></li>', '>Kent vineyards</a></li>', 1)
    # Sussex links that used to mean the homepage
    t2 = re.sub(r'<a href="((?:\.\./)*)index\.html">((?:The |All )?Sussex vineyards)</a>', lambda m: f'<a href="{m.group(1)}sussex/index.html">{m.group(2)}</a>', t)
    stats['crumb'] += (t2 != t); t = t2
    t = re.sub(r'href="((?:\.\./)*)index\.html#(planner|autumn|col-[a-z-]+)"', lambda m: f'href="{m.group(1)}sussex/index.html#{m.group(2)}"', t)
    t = re.sub(r'("name": ?"Sussex vineyards", ?"item": ?")https://thatchandtrail\.com/(index\.html)?"', lambda m: m.group(1) + BASE + '/sussex/"', t)
    # icons and logo
    t, n3 = re.subn(r'<link href="(?:\.\./)*favicon\.svg" rel="icon" type="image/svg\+xml"/>', lambda _m: ICONS, t, 1)
    stats['icons'] += n3
    t = t.replace(f'"logo":"{BASE}/favicon.svg"', f'"logo":"{BASE}/icon-512.png"').replace(f'"logo": "{BASE}/favicon.svg"', f'"logo": "{BASE}/icon-512.png"')
    if t != o: open(p, 'w').write(t)
LOG.append(f'site-wide {stats}')
# 404: absolute paths so it works at any depth
t = rd('404.html')
t = re.sub(r'(\s(?:href|src))="(?!https?:|#|/|mailto:|data:)([^"]+)"', lambda m: f'{m.group(1)}="/{m.group(2)}"', t)
t = re.sub(r'<a([^>]*)href="/index\.html"([^>]*)>All \d+ Sussex vineyards →</a>', r'<a\1href="/index.html#vineyards"\2>Find a vineyard on the map →</a>', t)
assert 'Find a vineyard on the map →' in t
wr('404.html', t)
# atlas.js (Sussex map) loads Leaflet from the site root, so it works from /sussex/
a = open(SITE + '/atlas.js').read()
a = a.replace("css.href = 'vendor/leaflet/leaflet.css'", "css.href = '/vendor/leaflet/leaflet.css'").replace("js.src = 'vendor/leaflet/leaflet.js'", "js.src = '/vendor/leaflet/leaflet.js'")
assert "'/vendor/leaflet/leaflet.js'" in a
open(SITE + '/atlas.js', 'w').write(a)
# CSS
open(SITE + '/style.css', 'a').write(open(ASSETS + '/v33.css').read())
# icons
fav = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="{rx}" fill="#4a542c"/><g fill="none" stroke="#f6efdf" stroke-width="5.5" stroke-linecap="round"><path d="M13 53 C20 39 21 26 16 11"/><path d="M32 53 C39 39 40 26 35 11"/><path d="M51 53 C58 39 59 26 54 11"/></g><circle cx="16" cy="11" r="3.2" fill="#e6c88f"/><circle cx="35" cy="11" r="3.2" fill="#e6c88f"/><circle cx="54" cy="11" r="3.2" fill="#e6c88f"/></svg>'
open(SITE + '/favicon.svg', 'w').write(fav.format(rx=14))
os.makedirs(SP + '/icons', exist_ok=True)
open(SP + '/icons/sq.svg', 'w').write(fav.format(rx=0)); open(SP + '/icons/rd.svg', 'w').write(fav.format(rx=14))
open(SP + '/icons/r.js', 'w').write(f'''const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
for (const [f,s,o] of [['rd.svg',48,'f48.png'],['rd.svg',32,'f32.png'],['rd.svg',16,'f16.png'],['sq.svg',180,'apple.png'],['sq.svg',192,'i192.png'],['sq.svg',512,'i512.png']]){{
const p=await b.newPage({{viewport:{{width:s,height:s}},deviceScaleFactor:1}});
await p.setContent('<html><body style="margin:0;background:transparent"><img src="file://{SP}/icons/'+f+'" width="'+s+'" height="'+s+'"></body></html>');
await p.waitForTimeout(150);await p.screenshot({{path:'{SP}/icons/'+o,omitBackground:true}});await p.close();}}
await b.close();}})();''')
r = subprocess.run(['node', SP + '/icons/r.js'], capture_output=True, text=True); LOG.append(f'icons rc={r.returncode} {r.stderr[-200:]}')
Image.open(SP + '/icons/f48.png').save(SITE + '/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
shutil.copy(SP + '/icons/apple.png', SITE + '/apple-touch-icon.png')
Image.open(SP + '/icons/i192.png').convert('RGB').save(SITE + '/icon-192.png')
Image.open(SP + '/icons/i512.png').convert('RGB').save(SITE + '/icon-512.png')
json.dump({'name': 'Thatch & Trail', 'short_name': 'Thatch & Trail', 'start_url': '/', 'display': 'browser', 'background_color': '#fbf7ef', 'theme_color': '#4a542c',
           'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]},
          open(SITE + '/site.webmanifest', 'w'), indent=1)

# ---------- 8. clean canonical URLs + sitemap ----------
def clean(u):
    path = u[len(BASE) + 1:-5]
    if path == 'index': return BASE + '/'
    if path.endswith('/index'): return BASE + '/' + path[:-5]
    return BASE + '/' + path
URL_RE = re.compile(re.escape(BASE) + r'/[A-Za-z0-9/_.-]*?\.html')
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    t = open(p).read(); t2 = URL_RE.sub(lambda m: clean(m.group(0)), t)
    if t2 != t: open(p, 'w').write(t2)
sm = open(f'{SITE}/sitemap.xml').read()
old = {m.group(1): (m.group(3), m.group(4)) for m in re.finditer(r'<url><loc>(.*?)</loc><lastmod>(.*?)</lastmod><changefreq>(.*?)</changefreq><priority>(.*?)</priority></url>', sm)}
pages = []
for p in sorted(glob.glob(SITE + '/**/*.html', recursive=True)):
    rel = os.path.relpath(p, SITE)
    if rel in ('404.html', 'thanks.html') or rel.startswith('badge/') or rel.startswith('google'): continue
    t = open(p).read()
    if 'noindex' in t: continue
    u = clean(BASE + '/' + rel)
    cf, pr = old.get(u, ('weekly' if rel == 'sussex/index.html' else 'monthly', '0.9' if rel == 'sussex/index.html' else ('0.7' if rel.startswith('v/') else '0.8')))
    if rel == 'index.html': cf, pr = 'weekly', '1.0'
    pages.append(f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>')
open(f'{SITE}/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(pages) + '\n</urlset>\n')
LOG.append(f'sitemap {len(pages)} urls (was {len(old)})')
print('\n'.join(LOG))
