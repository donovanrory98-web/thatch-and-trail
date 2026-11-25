# v33 step 1: fresh copy of v32, then add the four new estates everywhere they belong.
import sys, os, re, json, html, glob, shutil, zipfile
SP = '/tmp/claude-0/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/scratchpad'
shutil.rmtree(SP + '/v33', ignore_errors=True)
zipfile.ZipFile('/mnt/user-data/outputs/thatch-and-trail-v32.zip').extractall(SP + '/v33')
sys.path.insert(0, SP)
from build_v33 import *
REPORT = []
def others_from(cards, slug):
    return [(f'{c[0]}.html', card_name(c[1]), re.search(r'<div class="ctown">(.*?)</div>', c[1]).group(1)) for c in cards if c[0] != slug]

# ======== regional hubs (Yorkshire, South West) ========
hubinfo = {}
for rk in ('north', 'southwest', 'east', 'hampshire', 'surrey'):
    es = [e for e in E if e['region'] == rk]
    hubinfo[rk] = build_hub(rk, es)
    R = REG[rk]
    for e in es:
        eb = e['county'] if plain(e['county']) == plain(R['eb']) else f'{e["county"]} · {R["eb"]}'
        wr(f'v/{e["slug"]}.html', estate_page(e, f'../{R["dir"]}/index.html', R['name'], '../index.html', 'Vineyards', eb,
                                             ('Region', f'<a href="../{R["dir"]}/index.html">{R["name"]}</a>'), f'Also in {R["name"]}',
                                             others_from(hubinfo[rk]['cards'], e['slug']), f'{plain(R["name"])} vineyards', f'{BASE}/{R["dir"]}/'))
    REPORT.append(f'hub {rk}: {hubinfo[rk]["n"]}')

# ======== Kent: Nine Oaks into the Kent Weald section ========
nine = next(e for e in E if e['slug'] == 'nine-oaks-vineyard')
s = rd('kent/index.html')
m = re.search(r'(<div class="stn" id="weald">\n<h2><span class="mono">The Kent Weald</span> <i>)(\d+)( vineyards · [^<]*</i></h2>\n<div class="grid">)(.*?)(</div>\n</div>)', s, re.S)
cards = [(cm.group(1), cm.group(0)) for cm in CARD_RE.finditer(m.group(4))]
cards.append(('nine-oaks-vineyard', hub_card(nine, 'The Kent Weald', 'Kent')))
cards.sort(key=lambda c: plain(card_name(c[1])).lower().removeprefix('the '))
s = s[:m.start()] + m.group(1) + str(len(cards)) + m.group(3) + ''.join(c[1] for c in cards) + m.group(5) + s[m.end():]
kn = s.count('<a class="card"')
s = re.sub(r'\b21 Kent (estates|vineyards)', lambda x: f'{kn} Kent {x.group(1)}', s)
s = s.replace('and 12 have confirmed theirs with us directly', 'and 13 have confirmed theirs with us directly')
s = re.sub(r'"numberOfItems": 21', f'"numberOfItems": {kn}', s, 1)
mm = re.search(r'("itemListElement": \[)(.*?)(\]\}\})', s)
items = json.loads('[' + mm.group(2) + ']')
items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': 'Nine Oaks Vineyard', 'url': f'{BASE}/v/nine-oaks-vineyard.html'})
s = s[:mm.start(2)] + ', '.join(ld(i) for i in items) + s[mm.end(2):]
assert 'and 13 have confirmed' in s and f'"numberOfItems": {kn}' in s
wr('kent/index.html', s)
wr('v/nine-oaks-vineyard.html', estate_page(nine, '../kent/index.html', 'Kent', '../index.html', 'Vineyards', 'Kent · The Kent Weald',
                                            ('Area', '<a href="../kent/index.html#weald">The Kent Weald</a>'), 'Also in The Kent Weald',
                                            others_from(cards, 'nine-oaks-vineyard'), 'Kent vineyards', f'{BASE}/kent/'))
REPORT.append(f'kent: {kn} cards')

# ======== Sussex: Rowfant onto the East Grinstead trail ========
def anchors(seg): return re.findall(r'<a href="(\.\./v/[a-z0-9-]+\.html)">(.*?)</a>', seg)
def alist(items): return join_names([f'<a href="{h}">{n}</a>' for h, n in items])
sus = [e for e in E if e['region'] == 'sussex']
for tk in sorted({TRAIL[e['slug']] for e in sus}):
    T = TRAILS[tk]; es = [e for e in sus if TRAIL[e['slug']] == tk]
    s = rd(T['file'])
    fi = s.find('<section class="prose trail-facts"'); gi = s.rfind('</div>', 0, fi)
    s = s[:gi] + ''.join(hub_card(e, T['t'], T['t']) for e in es) + s[gi:]
    gs = s.find('<div class="grid">'); fi = s.find('<section class="prose trail-facts"')
    tcards = [(m.group(1), m.group(0)) for m in CARD_RE.finditer(s[gs:fi])]; n = len(tcards)
    head_end = s.find('</head>')
    s = re.sub(r'\b\d+ vineyards\b', f'{n} vineyards', s[:head_end]) + s[head_end:]
    s = re.sub(r'"numberOfItems": \d+', f'"numberOfItems": {n}', s, 1)
    m = re.search(r'("itemListElement": \[)(.*?)(\]\}\})', s)
    items = json.loads('[' + m.group(2) + ']'); have = {i['url'] for i in items}
    for e in es:
        u = f'{BASE}/v/{e["slug"]}.html'
        if u not in have: items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': plain(e['name']), 'url': u})
    s = s[:m.start(2)] + ', '.join(ld(i) for i in items) + s[m.end(2):]
    s = re.sub(r'<li><b>\d+</b> vineyards</li>', f'<li><b>{n}</b> vineyards</li>', s)
    s = re.sub(r'<strong>Vineyards:</strong> \d+', f'<strong>Vineyards:</strong> {n}', s)
    s = re.sub(r'It takes in \d+ estates', f'It takes in {n} estates', s)
    names = [(f'../v/{c[0]}.html', card_name(c[1])) for c in tcards]
    s = re.sub(r'<p>\d+ estates welcome visitors: .*?\.</p>', lambda _m: f'<p>{n} estates welcome visitors: {alist(names)}.</p>', s, 1)
    s = re.sub(r'"text": "\d+ estates welcome visitors: [^"]*"', lambda _m: f'"text": "{n} estates welcome visitors: {plain(join_names([x[1] for x in names]))}."', s, 1)
    m2 = re.search(r'<li><strong>Estate-verified so far:</strong> (.*?)</li>', s)
    if m2:
        cur = anchors(m2.group(1)) if 'none' not in m2.group(1) else []
        cur += [(f'../v/{e["slug"]}.html', e['name']) for e in es]
        s = s[:m2.start(1)] + alist(cur) + s[m2.end(1):]
    wr(T['file'], s)
    tname = re.search(r'<h1>(.*?)</h1>', s).group(1)
    for e in es:
        wr(f'v/{e["slug"]}.html', estate_page(e, f'../{T["file"]}', tname, '../index.html', 'Sussex vineyards', tname,
                                             ('Trail', f'<a href="../{T["file"]}">{tname}</a>'), f'Also on {"the " if not tname.startswith("The") else ""}{tname.replace("The ", "the ", 1)}',
                                             others_from(tcards, e['slug']), plain(tname), f'{BASE}/{T["file"]}'))
    REPORT.append(f'trail {tk}: {n} cards')

# ======== Sussex homepage (this becomes /sussex/ in step 2) ========
s = rd('index.html')
tag = '<script type="application/json" id="atlas-data">'
ai = s.find(tag) + len(tag); aj = s.find('</script>', ai)
atlas = json.loads(s[ai:aj])
vcards = ''
for e in sus:
    T = TRAILS[TRAIL[e['slug']]]
    img = f'img/plates/{e["slug"]}.svg'
    open(f'{SITE}/img/plates/{e["slug"]}.svg', 'w').write(plate(e['slug'], T['c']))
    tags = '<span class="vc-tag vc-tag--v">&#10003; Estate-verified</span>'
    vcards += (f'<article class="vcard" id="v-{e["slug"]}" data-slug="{e["slug"]}" data-trail="{T["t"]}" data-visit="open" data-food="{"Yes" if e.get("food") else "No"}" '
               f'data-stay="{"Yes" if e.get("stay") else "No"}" data-wed="?" style="--tc:{T["c"]}"><div class="vc-media"><img src="{img}" width="400" height="300" loading="lazy" decoding="async" alt="">'
               '<span class="vc-illus">Illustration</span>'
               f'<p class="vc-trail"><span class="vc-dot" aria-hidden="true"></span>{T["tl"]}</p></div><div class="vc-body"><p class="vc-picked">Selected on the map</p>'
               f'<h3 class="vc-name"><a href="v/{e["slug"]}.html">{e["name"]}</a></h3><p class="vc-town">{e["town"]}</p><p class="vc-hook">{e["hook"]}</p>'
               f'<div class="vc-tags">{tags}</div><div class="vc-foot"><p class="vc-rail"><span class="vc-rail-l">Nearest station</span> {RAIL[e["slug"]]}</p>'
               f'<button type="button" class="vc-map" data-slug="{e["slug"]}" aria-label="Show on map: {html.escape(plain(e["name"]))}">Show on map</button></div></div></article>')
    la, lo = GEO[e['slug']]
    atlas.append({'s': e['slug'], 'n': plain(e['name']), 't': T['t'], 'town': e['town'], 'h': f'v/{e["slug"]}.html', 'lat': la, 'lng': lo,
                  'v': True, 'img': img, 'c': T['c'], 'tl': plain(T['tl'])})
ensure_ascii = '\\u2019' in s[ai:aj]
s = s[:ai] + json.dumps(atlas, ensure_ascii=ensure_ascii) + s[aj:]
k = s.find('<div class="empty" hidden id="empty">'); s = s[:k] + vcards + s[k:]
N_SUS = len(atlas)
m = re.search(r'("name":"Sussex vineyards open to visitors","numberOfItems":)(\d+)(,"itemListElement":\[)(.*?)(\]\})', s)
items = m.group(4); pos = int(m.group(2))
for e in sus:
    pos += 1; items += ',' + json.dumps({'@type': 'ListItem', 'position': pos, 'name': plain(e['name']), 'url': f'{BASE}/v/{e["slug"]}.html'}, ensure_ascii=False, separators=(',', ':'))
s = s[:m.start(2)] + str(N_SUS) + m.group(3) + items + s[m.end(4):]
s = re.sub(r'([Aa]ll |to |of |the )45\b', lambda x: x.group(1) + str(N_SUS), s)
s = re.sub(r'\b45 (Estates|estates|Sussex|vineyards|visitor)', lambda x: f'{N_SUS} {x.group(1)}', s)
s = s.replace('<b id="n">45</b>', f'<b id="n">{N_SUS}</b>').replace('<strong>45</strong><span>Sussex vineyards</span>', f'<strong>{N_SUS}</strong><span>Sussex vineyards</span>')
leftover = [s[max(0, x.start() - 60):x.end() + 30].replace('\n', ' ') for x in re.finditer(r'(?<![\d.,#-])45(?![\d])', s) if not (ai - 10 < x.start() < ai + len(json.dumps(atlas)) + 10)]
REPORT.append(f'sussex home: {N_SUS}; leftover 45s: {len(leftover)}')
REPORT += ['   45? ' + l for l in leftover]
wr('index.html', s)

# ======== verified page ========
s = rd('verified.html')
LABEL = {'sussex': 'Sussex', 'kent': 'Kent'}
for rk, R in REG.items(): LABEL.setdefault(rk, R['name'])
for e in E:
    label = LABEL[e['region']]
    m = re.search(rf'<div><h2>{re.escape(label)} <i>(\d+) estates?</i></h2><ul>(.*?)</ul></div>', s)
    assert m, label
    lis = re.findall(r'<li>.*?</li>', m.group(2)) + [f'<li><a href="v/{e["slug"]}.html">{e["name"]}</a> <i>{e["month"]}</i></li>']
    lis.sort(key=lambda x: plain(re.search(r'>(.*?)</a>', x).group(1)).lower())
    s = s[:m.start()] + f'<div><h2>{label} <i>{len(lis)} estates</i></h2><ul>{"".join(lis)}</ul></div>' + s[m.end():]
m = re.search(r'<select id="vb-pick">(.*?)</select>', s)
opts = re.findall(r'<option value="([^"]+)">(.*?)</option>', m.group(1)) + [(e['slug'], e['name']) for e in E]
opts.sort(key=lambda o: plain(o[1]))
s = s[:m.start(1)] + ''.join(f'<option value="{v}">{n}</option>' for v, n in opts) + s[m.end(1):]
m = re.search(r'var D=(\{.*?\});', s)
D = json.loads(m.group(1))
for e in E: D[e['slug']] = {'n': plain(e['name']), 'c': plain(LABEL[e['region']]), 'm': e['month']}
D = dict(sorted(D.items()))
s = s[:m.start(1)] + json.dumps(D, ensure_ascii=False) + s[m.end(1):]
VER = len(D)
wr('verified.html', s)

# ======== counts everywhere ========
PAGES = len(glob.glob(SITE + '/v/*.html'))
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    t = open(p).read(); o = t
    t = re.sub(r'\b112 (estates|vineyards) so far', lambda x: f'{VER} {x.group(1)} so far', t)
    t = t.replace('87 vineyards across England and Wales so far', f'{VER} vineyards across England and Wales so far')
    t = re.sub(r'\b45 Sussex vineyards', f'{N_SUS} Sussex vineyards', t)
    if t != o: open(p, 'w').write(t); REPORT.append('counts: ' + os.path.relpath(p, SITE))

json.dump({'flags': FLAGS, 'report': REPORT, 'N_SUS': N_SUS, 'VER': VER, 'PAGES': PAGES, 'KENT': kn,
           'hub': {k: v['n'] for k, v in hubinfo.items()}}, open(SP + '/v33_report.json', 'w'), indent=1)
print('\n'.join(REPORT)); print('verified', VER, 'pages', PAGES)
