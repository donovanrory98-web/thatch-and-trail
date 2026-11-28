# v38: five new estate-verified pages (High Clandon, The Grange, Hattingley Valley, Fairmile, Chiltern Valley)
# Facts come only from each estate's emails to Thatch & Trail and their own websites.
import os, re, json, html, sys
from PIL import Image

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
BASE = 'https://thatchandtrail.com'
TODAY = '2026-11-28'
MONTH = 'November 2026'
TR = '/root/.claude/projects/-home-claude/cc7d2f47-bb73-541e-8f22-af5ca5c92b75/tool-results/'

def rd(p): return open(os.path.join(SITE, p), encoding='utf-8').read()
def wr(p, s):
    fp = os.path.join(SITE, p); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w', encoding='utf-8').write(s)
def plain(s): return html.unescape(re.sub(r'<[^>]+>', '', s))
def poss(n): return n + ('’' if plain(n).endswith('s') else '’s')

REGION = {'surrey': ('Surrey', '#6E5C9A'), 'hampshire': ('Hampshire', '#2F6E6A'), 'thames': ('Berkshire, Bucks &amp; Oxfordshire', '#A8853A')}

E = [
 dict(slug='high-clandon', name='High Clandon Estate Vineyard', r='surrey', county='Surrey', sec='surrey', label='Surrey',
      town='East Clandon, near Guildford', lat=51.245, lng=-0.476, site='https://www.highclandon.co.uk', food=False, stay=False,
      rail='Clandon (20 min walk) or Horsley (7 min cab)',
      photo=('mcp-Gmail-blob-1795874997404-9b91c9.jpg', 'Visitors on the lawn at a High Clandon Open Day, with a bronze sculpture among the trees', 'An Open Day at High Clandon', 'Photograph courtesy of Sibylla Tindale, High Clandon'),
      hook='A small sparkling wine estate on the Clandon Downs, with Tour, Talk, Tasting on Open Days, a summer art and sculpture show, and views across the Surrey Hills to the London skyline.',
      lead='High Clandon is an Open Day visit: roughly once a month from late April to October, with tours at noon and 3pm. Book ahead, as each tour takes 15 people.',
      boxes=[('C', 'Tour, Talk, Tasting', 'Twice on each Open Day, at <strong>12 noon and 3pm</strong>, for up to <strong>15 people</strong>. Book through High Clandon’s website.'),
             ('C', '2027 Open Days', '<strong>18 April, 8 May (Surrey Day), 31 May, 19 June, 30 August, 18 September, 2 October and 23 October</strong>. There are no Open Days in July or August apart from the bank holiday.'),
             ('C', 'Art &amp; Sculptures in the Vineyard', 'Runs <strong>27 June to 11 July 2027</strong>.'),
             ('C', 'Jazz in the Vineyard', '<strong>Saturday 12 June 2027</strong>: a matinee from noon (music 12.45 to 3pm) and an evening session from 5.15pm (music 6 to 8.15pm).'),
             ('C', 'Bringing the dog', 'In the estate’s words, <strong>“lovely dogs with lovely owners are welcome”</strong>.'),
             ('C', 'Don’t miss', 'The estate’s own tip: the views across the Surrey Hills to London’s skyline, and the sparkling wine.')],
      getting='The nearest stations are <strong>Clandon</strong>, about a 20-minute walk, and <strong>Horsley</strong>, about 7 minutes by cab.',
      facts=[('Where', 'East Clandon, near Guildford, Surrey'), ('Tours', 'Noon and 3pm on Open Days, max 15'), ('Open Days', 'Late April to October (not July)'),
             ('Dogs', 'Welcome'), ('By train', 'Clandon (20 min walk) or Horsley (7 min cab)'), ('Founded', '2004 (from their website)')],
      faqs=[('When are High Clandon’s Open Days in 2027?', '18 April, 8 May, 31 May, 19 June, 30 August, 18 September, 2 October and 23 October.'),
            ('Do I need to book a tour at High Clandon?', 'Yes. Tour, Talk, Tasting runs at noon and 3pm on Open Days for up to 15 people, booked through the estate’s website.'),
            ('Can I bring my dog to High Clandon?', 'Yes. The estate says lovely dogs with lovely owners are welcome.'),
            ('How do I get to High Clandon by train?', 'Clandon station is about a 20-minute walk; Horsley is about a 7-minute cab ride.')]),
 dict(slug='the-grange', name='The Grange', r='hampshire', county='Hampshire', sec='hampshire', label='Hampshire',
      town='Itchen Stoke, near Alresford', lat=51.095, lng=-1.215, site='https://www.thegrangewine.co.uk', food=False, stay=True,
      rail='Winchester (15 min taxi)',
      photo=('mcp-Gmail-blob-1795875001217-t7i8a6.jpg', 'Rows of vines at The Grange at sunset, looking across the Itchen valley', 'The vineyard at The Grange at sunset', 'Photograph courtesy of The Grange'),
      hook='A family estate above the River Itchen with two-hour vineyard and winery tours from February to December, a cellar door six days a week, holiday cottages and summer Thursday Lates.',
      lead='The Grange is open for most of the year: tours run from February to December, the cellar door is open six days a week, and you can stay on the estate.',
      boxes=[('C', 'Vineyard Tour &amp; Tasting', '<strong>11am to 1pm</strong>, no more than <strong>15 people</strong>, through Burges Field and the 2022 winery and on to the tasting room. Running <strong>February to December 2027</strong>; dates and tickets on The Grange’s tours page.'),
             ('C', 'Cellar door', 'A small shop at the winery, open to anyone: <strong>Monday to Friday 10am to 4pm</strong> and <strong>Saturday 11am to 4pm</strong>.'),
             ('C', 'Thursday Lates', 'From <strong>May to September</strong> the winery opens on Thursday evenings, pouring wine by the glass (magnums included) with a different local food hero each week. The estate’s pick for a first visit.'),
             ('C', 'Staying on the estate', 'Holiday cottages on the estate: <strong>Abbotstone Farm House, Lake House Cottage, Garden Cottage and the Clock Tower</strong>, bookable through The Grange’s estate website.'),
             ('C', 'Dogs and children', 'Both are <strong>welcome on the tours</strong>.')],
      getting='Take the train to <strong>Winchester</strong>; the vineyard and winery are about <strong>15 minutes by taxi</strong>.',
      facts=[('Where', 'Itchen Stoke, near Alresford, Hampshire'), ('Tours', '11am–1pm, Feb–Dec, max 15'), ('Cellar door', 'Mon–Fri 10–4, Sat 11–4'),
             ('Thursday Lates', 'May–September'), ('Stay', 'Four holiday cottages on the estate'), ('Dogs &amp; children', 'Welcome on tours'), ('By train', 'Winchester, then 15 min taxi')],
      faqs=[('When do The Grange’s vineyard tours run?', 'From February to December 2027, 11am to 1pm, for up to 15 people. Book through The Grange’s tours page.'),
            ('Can I visit The Grange’s cellar door without a tour?', 'Yes. It is open to anyone, Monday to Friday 10am to 4pm and Saturday 11am to 4pm.'),
            ('Can you stay at The Grange?', 'Yes: Abbotstone Farm House, Lake House Cottage, Garden Cottage and the Clock Tower are holiday cottages on the estate.'),
            ('Are dogs and children allowed on The Grange tours?', 'Yes, both are welcome.')]),
 dict(slug='hattingley-valley', name='Hattingley Valley', r='hampshire', county='Hampshire', sec='hampshire', label='Hampshire',
      town='Lower Wield, near Alresford', lat=51.147, lng=-1.103, site='https://hattingleyvalley.com', food=False, stay=False,
      rail='Check with the estate', photo=None,
      hook='An award-winning Hampshire sparkling wine producer with behind-the-scenes winery tours and tastings on Saturdays and Sundays, plus Fridays from spring to harvest.',
      lead='Hattingley Valley is a winery visit: pre-book a weekend tour (or a Friday from spring to harvest), or call in at the cellar door on a weekday.',
      boxes=[('C', 'Winery Tour &amp; Tasting', 'Behind the scenes at the winery on <strong>Saturdays and Sundays</strong>, and <strong>Fridays from spring to harvest</strong>. <strong>Pre-book</strong> on Hattingley Valley’s website to be sure of a place.'),
             ('C', 'Cellar door', '<strong>Monday to Friday 9am to 5pm</strong>; <strong>Saturdays and Sundays by appointment</strong>.'),
             ('S', 'The wines', 'A sparkling range including the Classic Reserve NV, a rosé and a Blanc de Blancs, plus a dessert wine, Entice. The winery says it has won over 230 medals.')],
      getting=None,
      facts=[('Where', 'Lower Wield, near Alresford, Hampshire'), ('Tours', 'Sat &amp; Sun; Fridays spring to harvest'), ('Booking', 'Pre-book online'),
             ('Cellar door', 'Mon–Fri 9–5; weekends by appointment')],
      faqs=[('When are Hattingley Valley’s winery tours?', 'On Saturdays and Sundays, and on Fridays from spring to harvest. Pre-book to be sure of a place.'),
            ('Can I visit Hattingley Valley without booking a tour?', 'The cellar door is open Monday to Friday, 9am to 5pm. At weekends it is by appointment.')]),
 dict(slug='fairmile-vineyard', name='Fairmile Vineyard', r='thames', county='Oxfordshire', sec='oxfordshire', label='Oxfordshire',
      town='Henley-on-Thames', lat=51.552, lng=-0.918, site='https://www.fairmilevineyard.co.uk', food=False, stay=False,
      rail='Henley-on-Thames (30 min walk)',
      photo=('mcp-Gmail-blob-1795875010680-bsr0kn.jpg', 'A group raising glasses of sparkling wine at sunset on the slope at Fairmile Vineyard, looking over the Chilterns', 'Raising a glass on the slope at Fairmile', 'Photograph courtesy of Jan Mirkowski, Fairmile Vineyard'),
      hook='A dog- and child-friendly vineyard on the Fairmile above Henley, with tours by appointment every day of the year and a 30-minute walk from the station along what William Morris called “the loveliest approach to any town in England”.',
      lead='Fairmile is open all year: tours by appointment any day, and a short cellar door window three days a week. It is one of the few vineyards you can easily walk to from a station.',
      boxes=[('C', 'Tours by appointment', 'Every day of the year. The estate prefers <strong>a day or two’s notice</strong>, but if a tour is already running (especially on summer weekends) they can sometimes fit you in at much shorter notice.'),
             ('C', 'Cellar door', '<strong>Tuesdays and Saturdays 10am to noon</strong>, and <strong>Thursdays noon to 2pm</strong>, with no change planned for next year.'),
             ('S', 'On the tour', 'About an hour through the vines, ending with a tutored tasting of the sparkling Rosé and Classic Cuvée on a slope overlooking the Chilterns, where red kites circle below.'),
             ('C', 'Dogs and children', 'The vineyard is fully deer- and rabbit-fenced, so it is <strong>dog- and child-friendly</strong>.'),
             ('C', 'Regatta week', 'The vineyard stays open, but driving through Henley isn’t advisable. Come from the <strong>Bix, Nettlebed or Oxford (northern) side</strong>, or walk up from town. Henley Lions Club normally runs all-day parking on the Fairmile’s grass verges that week.')],
      getting='From <strong>Henley-on-Thames station</strong> it is about a <strong>30-minute walk</strong> through the town or alongside the Regatta course. William Morris called the Fairmile “the loveliest approach to any town in England”.',
      facts=[('Where', 'The Fairmile, Henley-on-Thames, Oxfordshire'), ('Tours', 'By appointment, every day'), ('Cellar door', 'Tue &amp; Sat 10–12, Thu 12–2'),
             ('Dogs &amp; children', 'Welcome (fully fenced)'), ('By train', 'Henley-on-Thames, 30 min walk')],
      faqs=[('Can you walk to Fairmile Vineyard from Henley station?', 'Yes, it is about a 30-minute walk through the town or alongside the Regatta course.'),
            ('How much notice does Fairmile need for a tour?', 'A day or two is preferred, though they can sometimes add visitors to a tour that is already running.'),
            ('Are dogs allowed at Fairmile Vineyard?', 'Yes. The vineyard is fully deer- and rabbit-fenced, so it is dog- and child-friendly.'),
            ('Is Fairmile open during Henley Regatta?', 'Yes. Avoid driving through town and approach from the Bix, Nettlebed or Oxford side, or walk up from Henley.')]),
 dict(slug='chiltern-valley', name='Chiltern Valley Winery', r='thames', county='Oxfordshire', sec='oxfordshire', label='Oxfordshire',
      town='Old Luxters, near Henley-on-Thames', lat=51.595, lng=-0.889, site='https://www.chilternvalley.co.uk', food=True, stay=True,
      rail='Henley-on-Thames, then taxi',
      photo=('mcp-Gmail-blob-1795875022009-g89fzj.jpg', 'The brick courtyard at Old Luxters with barrels, parasols and the blue food truck', 'The courtyard at Old Luxters', 'Photograph courtesy of Chiltern Valley'),
      hook='A winery, brewery and liqueur maker at Old Luxters in the Chiltern Hills, with tours most days that head out into the vines, a shop open seven days a week and a food truck in the courtyard.',
      lead='Chiltern Valley is an easy drop-in as well as a tour: the shop and food truck are open every day, and the tours run most days of the week.',
      boxes=[('C', 'Winery, brewery and liqueur tour', 'Runs <strong>most days, weekdays and weekends</strong>: about 1.5 to 2 hours behind the scenes, finishing with a tutored tasting. Book on Chiltern Valley’s tours page.'),
             ('C', 'Out among the vines', 'The tour <strong>virtually always goes into the vineyard</strong>, unless, in the estate’s words, it’s blowing a hooley.'),
             ('C', 'Shop and food truck', 'The shop is open <strong>7 days a week, 9am to 5pm</strong>. The food and coffee truck is open <strong>every day 10am to 4pm</strong> (10am to 1pm on event days). No booking needed.'),
             ('C', 'Tours are adults only', '<strong>No dogs and no under-18s</strong> on tours.'),
             ('S', 'Stay the night', 'There is a B&amp;B on site, and a room can be added to a tour booking.')],
      getting='There is no station nearby: take the train to <strong>Henley-on-Thames</strong> and a taxi from there. The estate uses Henley Taxi.',
      facts=[('Where', 'Old Luxters, near Henley-on-Thames, Oxfordshire'), ('Tours', 'Most days, 1.5–2 hours'), ('Shop', 'Daily 9–5'),
             ('Food truck', 'Daily 10–4 (10–1 on event days)'), ('Tours', 'Over-18s only, no dogs'), ('Stay', 'B&amp;B on site (from their website)'), ('By train', 'Henley-on-Thames, then taxi')],
      faqs=[('Do Chiltern Valley tours go into the vineyard?', 'Virtually always, unless the weather is very wild.'),
            ('Can I visit Chiltern Valley without booking a tour?', 'Yes. The shop is open 7 days a week, 9am to 5pm, and the food truck every day 10am to 4pm.'),
            ('Are children or dogs allowed on Chiltern Valley tours?', 'No. Tours are for over-18s only, and dogs aren’t allowed.'),
            ('How do I get to Old Luxters without a car?', 'Take the train to Henley-on-Thames and a taxi from the station.')]),
]
SLUGS = {e['slug'] for e in E}

# ---------- photos ----------
for e in E:
    if not e['photo']: continue
    src = TR + e['photo'][0]
    im = Image.open(src).convert('RGB')
    if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(os.path.join(SITE, f'img/{e["slug"]}-1.jpg'), quality=82, optimize=True, progressive=True)
    im.save(os.path.join(SITE, f'img/{e["slug"]}-1.webp'), quality=80)
    e['dims'] = im.size

# ---------- estate pages ----------
TPL = rd('v/greyfriars-vineyard.html')
VNOTE = re.search(r'<p class="verified-note">.*?</p>', TPL, re.S).group(0).replace('October 2026', MONTH)
LBL = {'C': 'Confirmed by the estate', 'S': 'From their website'}
reg_map = json.loads(re.search(r'id="hub-map-data">(.*?)</script>', rd('regions/index.html'), re.S).group(1))
reg_map = [x for x in reg_map if x['s'] not in SLUGS]

def sub1(pat, rep, s, flags=0):
    s2, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n == 1, pat
    return s2

def page(e):
    s = e['slug']; canon = f'{BASE}/v/{s}'
    rname, _ = REGION[e['r']]
    rhref = f'/{e["r"]}/'
    phero = ''
    if e['photo']:
        w, h = e['dims']
        phero = (f'<div class="phero"><picture><source srcset="../img/{s}-1.webp" type="image/webp"><img src="../img/{s}-1.jpg" alt="{html.escape(e["photo"][1])}" '
                 f'loading="lazy" width="{w}" height="{h}"></picture><div class="phcap">{e["photo"][2]} · {e["photo"][3]}</div></div>\n')
    boxes = ''.join(f'<div class="estate-answer"><span>{LBL[t]}</span><h3>{hd}</h3><p>{p}</p></div>\n' for t, hd, p in e['boxes'])
    getting = f'<div class="visit"><div class="lbl">Getting there</div><p>{e["getting"]}</p></div>\n' if e['getting'] else ''
    faqs = ''.join(f'<div class="fq"><h3>{q}</h3><p>{a}</p></div>' for q, a in e['faqs'])
    facts = f'<div><dt>Region</dt><dd><a href="{rhref}">{rname}</a></dd></div>' + ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in e['facts'])
    others = sorted([x for x in reg_map if x['r'] == e['r']], key=lambda x: (x['lat'] - e['lat']) ** 2 + (x['lng'] - e['lng']) ** 2)[:3]
    others = [dict(s=o['slug'], n=o['name'], t=o['town']) for o in E if o['r'] == e['r'] and o is not e] + others
    also = '<div class="sec"><h2>Also in ' + rname + '</h2><ul class="near">' + ''.join(f'<li><a href="/v/{o["s"]}">{o["n"]}</a> <span>{o["t"]}</span></li>' for o in others[:5]) + '</ul></div>'
    main = f'''<main id="main">
<div class="wrap">
<nav aria-label="Breadcrumb" class="crumb"><a href="/">Vineyards</a> <i>/</i> <a href="{rhref}">{rname}</a> <i>/</i> <span aria-current="page">{e["name"]}</span></nav>
<article>
<div class="lhead">
<p class="eyebrow">{e["county"]}</p>
<h1>{e["name"]}</h1>
<p class="lmeta">{e["town"]} · {e["county"]}</p>
{VNOTE}
<p class="lhook">{e["hook"]}</p>
</div>
{phero}<div class="cols">
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
    winery = {'@context': 'https://schema.org', '@type': 'Winery', 'name': plain(e['name']), 'description': plain(e['hook']),
              'address': {'@type': 'PostalAddress', 'addressLocality': plain(e['town']), 'addressRegion': e['county'], 'addressCountry': 'GB'},
              'geo': {'@type': 'GeoCoordinates', 'latitude': e['lat'], 'longitude': e['lng']},
              'publicAccess': True, 'subjectOf': {'@type': 'WebPage', 'url': canon}, 'sameAs': [e['site']]}
    if e['photo']: winery['image'] = f'{BASE}/img/{s}-1.jpg'
    ld = [winery,
          {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': 'Vineyards', 'item': BASE + '/'},
              {'@type': 'ListItem', 'position': 2, 'name': plain(rname) + ' vineyards', 'item': BASE + rhref},
              {'@type': 'ListItem', 'position': 3, 'name': plain(e['name']), 'item': canon}]},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
              {'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in e['faqs']]}]
    title = f'{e["name"]}: tours &amp; tastings in {e["county"]}'
    if len(plain(title)) > 60: title = f'{e["name"]}: visiting {e["county"]}'
    desc = plain(e['hook'])
    if len(desc) > 155: desc = desc[:desc.rfind(' ', 0, 140)].rstrip(',') + '. Estate-verified.'
    else: desc += '' if len(desc) > 138 else ' Estate-verified.'
    desc = html.escape(desc, quote=True)
    t = TPL
    t = sub1(r'<title>.*?</title>', f'<title>{title}</title>', t, re.S)
    t = sub1(r'<meta content="[^"]*" name="description"/>', f'<meta content="{desc}" name="description"/>', t)
    t = sub1(r'<link href="[^"]*" rel="canonical"/>', f'<link href="{canon}" rel="canonical"/>', t)
    for prop in ('og:title', 'twitter:title'):
        t = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda m: f'<meta content="{title}" {m.group(1)}="{prop}"/>', t)
    for prop in ('og:description', 'twitter:description'):
        t = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda m: f'<meta content="{desc}" {m.group(1)}="{prop}"/>', t)
    t = re.sub(r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{canon}" property="og:url"/>', t)
    if e['photo']:
        t = re.sub(r'<meta content="[^"]*" (property="og:image"|name="twitter:image")/>', lambda m: f'<meta content="{BASE}/img/{s}-1.jpg" {m.group(1)}/>', t)
    t = sub1(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', t, re.S)
    t = sub1(r'<main id="main">.*?</main>', main, t, re.S)
    left = [l for l in t.split("\n") if "reyfriars" in l and "class=\"near\"" not in l]; assert not left, (s, [l[:200] for l in left])
    return t

for e in E: wr(f'v/{e["slug"]}.html', page(e))

# ---------- cards + map entries ----------
def card(e, label):
    tags = '<span class="tag verified">Verified</span>' + ('<span class="tag on">Food</span>' if e['food'] else '') + ('<span class="tag on">Stay</span>' if e['stay'] else '')
    return (f'<a class="card" data-food="{"Yes" if e["food"] else "No"}" data-stay="{"Yes" if e["stay"] else "No"}" data-trail="{label}" data-visit="open" data-wed="?" href="/v/{e["slug"]}">\n'
            f'<div class="ctrail">{label}</div>\n<div class="cname">{e["name"]}</div>\n<div class="ctown">{e["town"]}</div>\n'
            f'<div class="tags">{tags}</div>\n<div class="crail">&#8614; {e["rail"]}</div>\n<p class="chook">Estate-verified: {e["hook"]}</p>\n</a>')
def mapent(e): return {'s': e['slug'], 'n': e['name'], 't': e['town'], 'h': f'/v/{e["slug"]}', 'lat': e['lat'], 'lng': e['lng'], 'v': True, 'c': REGION[e['r']][1], 'r': e['r']}
def cname(c): return plain(re.search(r'<div class="cname">(.*?)</div>', c).group(1)).lower().removeprefix('the ')
def town_tok(t): return t.split('near ')[-1] if 'near ' in t else t.split(', ')[-1]

# ---------- region hubs ----------
for r in ('surrey', 'hampshire', 'thames'):
    p = f'{r}/index.html'; s = rd(p)
    new = [e for e in E if e['r'] == r]
    if any(f'href="/v/{e["slug"]}"' in s for e in new): print('already in', r); continue
    md = json.loads(re.search(r'id="hub-map-data">(.*?)</script>', s, re.S).group(1)) + [mapent(e) for e in new]
    md.sort(key=lambda x: x['n'].lower().removeprefix('the '))
    s = re.sub(r'(id="hub-map-data">).*?(</script>)', lambda m: m.group(1) + json.dumps(md, ensure_ascii=False, separators=(',', ':')) + m.group(2), s, 1, re.S)
    for e in new:
        sid = e['sec']
        m = re.search(rf'<div class="stn" id="{sid}">\n<h2><span class="mono">(.*?)</span> <i>(.*?)</i></h2>\n<div class="grid">(.*?)</div>\n</div>', s, re.S)
        if not m:  # new county section, appended after the last section
            last = list(re.finditer(r'<div class="stn" id="[^"]+">\n<h2>.*?</h2>\n<div class="grid">.*?</div>\n</div>', s, re.S))[-1]
            s = s[:last.end()] + f'\n<div class="stn" id="{sid}">\n<h2><span class="mono">{e["label"]}</span> <i>0 vineyards · </i></h2>\n<div class="grid"></div>\n</div>' + s[last.end():]
            m = re.search(rf'<div class="stn" id="{sid}">\n<h2><span class="mono">(.*?)</span> <i>(.*?)</i></h2>\n<div class="grid">(.*?)</div>\n</div>', s, re.S)
        label, info, grid = m.groups()
        cards = re.findall(r'<a class="card".*?</a>', grid, re.S) + [card(e, label)]
        cards.sort(key=cname)
        towns = [t for t in (info.split(' · ', 1)[1].split(', ') if ' · ' in info else []) if t]
        tk = town_tok(e['town'])
        if tk not in towns: towns.append(tk)
        towns.sort()
        n = len(cards)
        block = f'<div class="stn" id="{sid}">\n<h2><span class="mono">{label}</span> <i>{n} vineyard{"s" if n != 1 else ""} · {", ".join(towns)}</i></h2>\n<div class="grid">{"".join(cards)}</div>\n</div>'
        s = s[:m.start()] + block + s[m.end():]
    tot = len(md)
    s = re.sub(r'(\d+) estates so far', f'{tot} estates so far', s, 1)
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    ld[0]['description'] = re.sub(r'^\d+', str(tot), ld[0]['description'])
    ld[0]['mainEntity']['numberOfItems'] = tot
    ld[0]['mainEntity']['itemListElement'] = [{'@type': 'ListItem', 'position': i + 1, 'name': x['n'], 'url': BASE + x['h']} for i, x in enumerate(md)]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', s, 1, re.S)
    # meta descriptions / titles that carry the count
    s = re.sub(r'(content=")(\d+)( (?:Surrey|Hampshire|Berkshire)[^"]*")', lambda m: m.group(1) + str(tot) + m.group(3), s)
    wr(p, s)
    print(r, 'now', tot)

# ---------- regions page ----------
p = 'regions/index.html'; s = rd(p)
if not any(f'"s":"{e["slug"]}"' in s for e in E):
    md = json.loads(re.search(r'id="hub-map-data">(.*?)</script>', s, re.S).group(1)) + [mapent(e) for e in E]
    md.sort(key=lambda x: x['n'].lower())
    s = re.sub(r'(id="hub-map-data">).*?(</script>)', lambda m: m.group(1) + json.dumps(md, ensure_ascii=False, separators=(',', ':')) + m.group(2), s, 1, re.S)
    s = s.replace('77 so far, with more every week', '82 so far, with more every week')
    for r, old, new in (('hampshire', 8, 10), ('surrey', 4, 5), ('thames', 5, 7)):
        s = re.sub(rf'(<a class="card" href="/{r}/">.*?<span class="tag verified">){old} verified', rf'\g<1>{new} verified', s, 1, re.S)
    s = s.replace('<div class="ctown">Berkshire, Buckinghamshire</div>', '<div class="ctown">Berkshire, Buckinghamshire, Oxfordshire</div>')
    wr(p, s)

# ---------- homepage ----------
p = 'index.html'; s = rd(p)
if not any(f'"s": "{e["slug"]}"' in s or f'"s":"{e["slug"]}"' in s for e in E):
    m = re.search(r'(id="uk-data">)(.*?)(</script>)', s, re.S)
    ud = json.loads(m.group(2))
    sep = (', ', ': ') if '", "' in m.group(2)[:200] else (',', ':')
    ud += [{'s': e['slug'], 'n': e['name'], 't': e['town'], 'r': e['r'], 'h': f'/v/{e["slug"]}', 'lat': e['lat'], 'lng': e['lng'], 'v': True, 'f': e['food'], 'st': e['stay']} for e in E]
    ud.sort(key=lambda x: x['n'].lower())
    s = s[:m.start(2)] + json.dumps(ud, ensure_ascii=False, separators=sep) + s[m.end(2):]
    # the homepage ItemList
    def fix_ld(mm):
        txt = mm.group(1)
        try: ld = json.loads(txt)
        except Exception: return mm.group(0)
        changed = False
        for x in (ld if isinstance(ld, list) else [ld]):
            me = x.get('mainEntity') if isinstance(x, dict) else None
            if isinstance(me, dict) and me.get('@type') == 'ItemList' and me.get('numberOfItems') == 145:
                me['numberOfItems'] = len(ud)
                me['itemListElement'] = [{'@type': 'ListItem', 'position': i + 1, 'name': u['n'], 'url': BASE + u['h']} for i, u in enumerate(ud)]
                changed = True
        if not changed: return mm.group(0)
        return '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(',', ':')) + '</script>'
    s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, s, flags=re.S)
    wr(p, s)
    print('homepage entries', len(ud))

# ---------- tours guide ----------
p = 'guide/vineyard-tours.html'; s = rd(p)
if 'href="/v/high-clandon"' not in s:
    m = re.search(r'(<div class="grid">)(.*?)(</div>\n</div>)', s, re.S)
    cards = re.findall(r'<a class="card".*?</a>', m.group(2), re.S)
    cards = [re.sub(r'(<div class="ctown">[^<]*?) · \d+ miles(</div>)', r'\1\2', c) for c in cards]
    cards += [card(e, e['label']) for e in E]
    cards.sort(key=lambda c: ('tag verified' not in c, cname(c)))
    s = s[:m.start(2)] + '\n'.join(cards) + s[m.end(2):]
    n = len(cards)
    s = re.sub(r'\b120 (Estates|vineyards)', lambda mm: f'{n} {mm.group(1)}', s)
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    hrefs = re.findall(r'<a class="card"[^>]*href="(/v/[a-z0-9-]+)">\n<div class="ctrail">.*?</div>\n<div class="cname">(.*?)</div>', s, re.S)
    ld[0]['mainEntity']['numberOfItems'] = n
    ld[0]['mainEntity']['itemListElement'] = [{'@type': 'ListItem', 'position': i + 1, 'name': plain(nm), 'url': BASE + h} for i, (h, nm) in enumerate(hrefs)]
    ld[0]['dateModified'] = TODAY
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda mm: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', s, 1, re.S)
    wr(p, s)
    print('tours guide', n)

# ---------- counts everywhere, and the Thames region name ----------
pairs = [('All 145 vineyards', 'All 150 vineyards'), ('All 145 estates', 'All 150 estates'), ('145 vineyards', '150 vineyards'), ('145 Estates', '150 Estates'),
         ('of the 145 estates', 'of the 150 estates'), ('<b id="uk-n">145</b>', '<b id="uk-n">150</b>'),
         ('122 checked with the estate', '127 checked with the estate'), ('122 estates', '127 estates'), ('122 of the', '127 of the'),
         ('122 vineyards so far', '127 vineyards so far'), ('122 of them', '127 of them'),
         ('Berkshire &amp; Buckinghamshire', 'Berkshire, Bucks &amp; Oxfordshire'), ('Berkshire & Buckinghamshire', 'Berkshire, Bucks & Oxfordshire')]
nfiles = 0
for d, _, fs in os.walk(SITE):
    for f in fs:
        if not f.endswith(('.html', '.txt')): continue
        fp = os.path.join(d, f); s = open(fp, encoding='utf-8').read(); o = s
        for a, b in pairs: s = s.replace(a, b)
        if s != o: open(fp, 'w', encoding='utf-8').write(s); nfiles += 1
print('count/name updates in', nfiles, 'files')

# thames hub wording
p = 'thames/index.html'; s = rd(p)
s = s.replace('Thames Valley and North Wessex Downs estates, from Marlow to Newbury.', 'Thames Valley, Chilterns and North Wessex Downs estates, from Henley and Marlow to Newbury.')
wr(p, s)
p = 'regions/index.html'; s = rd(p)
s = s.replace('Thames Valley and North Wessex Downs estates, from Marlow to Newbury.', 'Thames Valley, Chilterns and North Wessex Downs estates, from Henley and Marlow to Newbury.')
wr(p, s)

# llms.txt: list the new estates
p = 'llms.txt'; s = rd(p)
if 'high-clandon' not in s:
    s = s.rstrip('\n') + '\n\n## Newly verified (November 2026)\n' + ''.join(f'- [{plain(e["name"])}]({BASE}/v/{e["slug"]}): {plain(e["hook"])}\n' for e in E)
    wr(p, s)

# sitemap
p = 'sitemap.xml'; s = rd(p)
add = ''.join(f'  <url><loc>{BASE}/v/{e["slug"]}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n' for e in E if f'/v/{e["slug"]}<' not in s)
s = s.replace('</urlset>', add + '</urlset>')
for u in ('/', '/regions/', '/surrey/', '/hampshire/', '/thames/', '/guide/vineyard-tours', '/v/ridgeview-wine-estate', '/sussex/'):
    s = re.sub(rf'(<loc>{re.escape(BASE + u)}</loc><lastmod>)[^<]+', rf'\g<1>{TODAY}', s)
wr(p, s)
print('done')
