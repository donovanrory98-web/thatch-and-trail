"""Apply tools/seo_overrides.json to the built site: <title>, meta description,
og/twitter copies, and the first <h1>. Safe to run repeatedly."""
import html, json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, "..", "site")
rules = json.load(open(os.path.join(here, "seo_overrides.json"), encoding="utf-8"))
def esc(s): return html.escape(s, quote=True)
changed = 0
for page, r in rules.items():
    if page.startswith("_"): continue
    p = os.path.join(root, page)
    if not os.path.exists(p):
        print("missing", page); continue
    h = open(p, encoding="utf-8").read(); o = h
    if "title" in r:
        t = esc(r["title"]).replace("&#x27;", "'")
        h = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", h, count=1, flags=re.S)
        for prop in ('property="og:title"', 'name="twitter:title"'):
            h = re.sub(r'(<meta[^>]*content=")[^"]*("[^>]*' + re.escape(prop) + ')', lambda m: m.group(1) + t + m.group(2), h)
            h = re.sub(r'(<meta[^>]*' + re.escape(prop) + r'[^>]*content=")[^"]*(")', lambda m: m.group(1) + t + m.group(2), h)
    if "description" in r:
        d = esc(r["description"]).replace("&#x27;", "'")
        for prop in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
            h = re.sub(r'(<meta[^>]*content=")[^"]*("[^>]*' + re.escape(prop) + ')', lambda m: m.group(1) + d + m.group(2), h)
            h = re.sub(r'(<meta[^>]*' + re.escape(prop) + r'[^>]*content=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), h)
    if "h1" in r:
        h = re.sub(r"(<h1[^>]*>)[^<]*", lambda m: m.group(1) + esc(r["h1"]).replace("&#x27;", "'"), h, count=1)
    if h != o:
        open(p, "w", encoding="utf-8").write(h); changed += 1; print("updated", page)
print(changed, "pages updated")
