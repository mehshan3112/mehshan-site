"""Builds the static site: reads content/site.json, writes dist/. Pure standard library."""
import html, json, re, shutil, pathlib
R = pathlib.Path(__file__).parent
def find(*names):
    for n in names:
        if (R/n).exists(): return R/n
    raise SystemExit("MISSING FILE (looked for: " + ", ".join(names) + ") - upload it to the top level of the repository")
SITE = find("content/site.json", "site.json")
c = json.load(open(SITE, encoding="utf-8"))
e = lambda s: html.escape(str(s), quote=True)
def f(s):
    s = e(s)
    s = re.sub(r"\{([^|{}]+)\|([^{}]+)\}", lambda m: "<span style=\"font-family:'" + m.group(1).strip() + "',var(--fb)\">" + m.group(2) + "</span>", s)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
def img(p): return e(p) if p.startswith(("http","/")) else "/"+e(p)

def me():
    a = c["about"]
    figs = "".join(f'<figure class="ph"><img src="{img(p["image"])}" alt="{e(p["alt"])}" loading="lazy"><figcaption>{f(p["caption"])}</figcaption></figure>' for p in a["photos"])
    return f'<section id="me"><p class="big">{"<br>".join(f(x) for x in a["headline"])}</p><p class="sub" style="margin-top:24px">{f(a["text"])}</p><div class="scat">{figs}</div></section>'

def logo(x):
    if x.get("logo"): return f'<span class="lg"><img src="{img(x["logo"])}" alt="{e(x.get("org") or x.get("school", ""))} logo"></span>'
    if x.get("initials"): return f'<span class="lg m" aria-hidden="true">{e(x["initials"])}</span>'
    return ""
def head(title, sub, x): return f'<div class="hd">{logo(x)}<div><h3>{f(title)}<em>{f(sub)}</em></h3></div></div>'
def hd(x): return head(x["role"], x["org"], x)
def auto_initials(name):
    w = [t for t in re.split(r"[\s,.-]+", name) if t and t.lower() not in ("of", "and", "the", "for", "in")]
    return "".join(t[0].upper() for t in w)[:5]
def bl(b): return ("<ul>" + "".join(f"<li>{f(i)}</li>" for i in b) + "</ul>") if b else ""

def act():
    out = ""
    for x in c.get("activities", []):
        ph = "".join(f'<figure><img{' class="crop"' if p.get("fit") == "crop to fill" else ""} src="{img(p["image"])}" alt="{e(p.get("caption") or x["org"])}" loading="lazy">' + (f'<figcaption>{e(p["caption"])}</figcaption>' if p.get("caption") else "") + "</figure>" for p in x.get("photos", []))
        link = f'<p><a href="{e(x["link_url"])}">{e(x["link_text"])}</a></p>' if x.get("link_url") else ""
        out += f'<div class="act">{hd(x)}<p class="dt">{f(x["dates"])}</p>{bl(x.get("bullets", []))}{link}' + (f'<div class="aph">{ph}</div>' if ph else "") + "</div>"
    return f'<section id="activities"><h2>Leadership and extracurricular activities</h2>{out}</section>'

def exp():
    dye = open(find("dye.html"), encoding="utf-8").read().replace("Colour by the ton.", e(c["dye_caption"]))
    sup = open(find("supply.html"), encoding="utf-8").read().replace("Yarn to shelf, end to end.", e(c.get("supply_caption") or "Yarn to shelf, end to end."))
    rows = ""
    for x in c["experience"]:
        w = f(x["dates"]) + (f'<br>{f(x["place"])}' if x.get("place") else "")
        b = x.get("bullets", [])
        body = ("<ul>" + "".join(f"<li>{f(i)}</li>" for i in b) + "</ul>") if len(b) > 1 else (f"<p>{f(b[0])}</p>" if b else "")
        link = f'<p><a href="{e(x["link_url"])}">{e(x["link_text"])}</a></p>' if x.get("link_url") else ""
        an = x.get("animation", "")
        art = sup if an == "supply chain" else "" if an == "none" else dye if (an == "dyeing machine" or x.get("show_dye_machine")) else ""
        d = bool(art)
        rows += f'<div class="row{" dr" if d else ""}"><div class="w">{w}</div><div>{hd(x)}{body}{link}</div>{art}</div>'
    return f'<section id="about"><h2>Experience</h2><p class="sub">{f(c["objective"])}</p><div>{rows}</div></section>'

def edu():
    rows = ""
    for x in c["education"]:
        x = dict(x)
        if not x.get("logo") and not x.get("initials"): x["initials"] = auto_initials(x["school"])
        w = f(x["dates"]) + (f'<br>{f(x["place"])}' if x.get("place") else "")
        note = f'<p>{f(x["note"])}</p>' if x.get("note") else ""
        link = f'<p><a href="{e(x["link_url"])}">{e(x.get("link_text") or x["link_url"])}</a></p>' if x.get("link_url") else ""
        rows += f'<div class="row"><div class="w">{w}</div><div>{head(x["degree"], x["school"], x)}{note}{bl(x.get("bullets", []))}{link}</div></div>'
    return f'<section id="education"><h2>Education</h2>{rows}</section>'

def skills():
    groups = c.get('skills', [])
    g = ''.join('<div><h3>' + f(s.get('title', '')) + '</h3><ul>' + ''.join('<li>' + f(i) + '</li>' for i in s.get('items', []) if i) + '</ul></div>' for s in groups if s.get('title') or s.get('items'))
    return '<section id="skills"><h2>Skills</h2><div class="cols" style="margin-top:36px">' + g + '</div></section>'

def training_projects():
    training = c.get("training_details", [])
    trows = ""
    for x in training:
        title = f(x.get("title", ""))
        provider = f(x.get("provider", ""))
        date = f(x.get("date", ""))
        meta = " · ".join(v for v in [provider, date] if v)
        cert_attr = ' data-cert="' + img(x["certificate"]) + '"' if x.get("certificate") else ""
        link = f'<p><a href="{e(x["link"])}">{f(x.get("link_text") or "View details")}</a></p>' if x.get("link") else ""
        if title or meta or link:
            trows += f'<li class="training-item"{cert_attr} tabindex="0"><div><b>{title}</b>{("<small>" + f(meta) + "</small>") if meta else ""}{link}</div></li>'
    projects = c.get("project_work", [])
    prows = ""
    for p in projects:
        if p.get("title") or p.get("text"):
            prows += f'<article class="project-item">{("<h3>" + f(p["title"]) + "</h3>") if p.get("title") else ""}{("<p>" + f(p["text"]) + "</p>") if p.get("text") else ""}</article>'
    return f'<section id="training-projects"><div class="tp-grid"><div><h2>Training</h2><ul class="training-list">{trows}</ul></div><div><h2>Project Work</h2>{prows}</div></div></section>'


def build_section_layout(parts):
    labels = {'me': 'About', 'about': 'Experience', 'education': 'Education', 'activities': 'Leadership', 'skills': 'Skills', 'training-projects': 'Training & Project Work', 'design': 'Design'}
    registry = c.get('sections')
    if not registry:
        legacy_settings = {x.get('id'): x for x in c.get('section_settings', [])}
        old_order = c.get('section_order') or ['me', 'about', 'education', 'activities', 'skills', 'training-projects', 'design']
        registry = [{'id': sid, **legacy_settings.get(sid, {})} for sid in old_order]

    # Custom sections live in the same ordered list as built-in sections.
    for section in registry:
        if not isinstance(section, dict):
            continue
        sid = re.sub(r'[^a-z0-9-]+', '-', str(section.get('id', 'custom')).lower()).strip('-') or 'custom'
        if sid in parts:
            continue
        title = section.get('title') or 'Section'
        labels[sid] = title
        if not section.get('visible', True):
            continue
        body = ''
        for block in section.get('blocks', []):
            kind = block.get('type', 'text')
            if kind == 'heading' and block.get('heading'):
                body += '<h3>' + f(block['heading']) + '</h3>'
            elif kind == 'text' and block.get('text'):
                body += '<p>' + f(block['text']) + '</p>'
            elif kind == 'image' and block.get('image'):
                body += '<figure><img src="' + img(block['image']) + '" alt="' + e(block.get('alt', '')) + '">' + ('<figcaption>' + f(block.get('caption', '')) + '</figcaption>' if block.get('caption') else '') + '</figure>'
            elif kind == 'gallery' and block.get('images'):
                body += '<div class="custom-gallery">' + ''.join('<figure><img src="' + img(p['image']) + '" alt="' + e(p.get('alt', '')) + '">' + ('<figcaption>' + f(p.get('caption', '')) + '</figcaption>' if p.get('caption') else '') + '</figure>' for p in block['images'] if p.get('image')) + '</div>'
            elif kind == 'list' and block.get('items'):
                body += '<ul>' + ''.join('<li>' + f(v) + '</li>' for v in block['items'] if v) + '</ul>'
            elif kind == 'link' and block.get('url'):
                body += '<p><a href="' + e(block['url']) + '">' + f(block.get('label') or block['url']) + '</a></p>'
        if body:
            parts[sid] = '<section id="' + e(sid) + '"><h2>' + f(title) + '</h2>' + body + '</section>'

    # Existing older data is upgraded transparently; the current editor stores one ordered list.
    settings = {x.get('id'): x for x in c.get('section_settings', [])}
    ordered_ids = [x.get('id') if isinstance(x, dict) else x for x in registry]
    # An explicit section registry is authoritative: deleted sections stay deleted.
    # The legacy fallback above already supplies the historical default order.
    registry_by_id = {x.get('id'): x for x in registry if isinstance(x, dict)}
    output, nav = [], []
    for sid in ordered_ids:
        item = registry_by_id.get(sid, settings.get(sid, {}))
        if sid in parts and item.get('visible', True) and parts[sid]:
            section_html = parts[sid]
            style_bits = []
            if item.get('desktop_spacing') is not None:
                try: style_bits.append('--section-space:' + str(max(0, min(200, float(item['desktop_spacing'])))) + 'px')
                except (TypeError, ValueError): pass
            if item.get('mobile_spacing') is not None:
                try: style_bits.append('--mobile-section-space:' + str(max(0, min(160, float(item['mobile_spacing'])))) + 'px')
                except (TypeError, ValueError): pass
            if style_bits:
                section_html = re.sub(r'<section(?=\s)', '<section style="' + ';'.join(style_bits) + '"', section_html, count=1)
            if item.get('title'):
                section_html = re.sub(r'(<h2\b[^>]*>).*?(</h2>)', lambda m: m.group(1) + f(item['title']) + m.group(2), section_html, count=1)
            output.append(section_html)
            nav.append('<a href="#' + e(sid) + '">' + e(item.get('title') or labels.get(sid, sid.title())) + '</a>')
    return '<div class="st"></div>'.join(output), ''.join(nav)

# ---------------- fonts ----------------
FONT_EXT = (".ttf", ".otf", ".woff", ".woff2")
CUSTOM = {x["name"].strip().lower(): x["file"] for x in c.get("custom_fonts", []) if x.get("name") and x.get("file")}
for p in R.glob("*"):   # the bundled Li Subha Letterpress file, if it sits in the repository
    if p.is_file() and p.name.lower().startswith("li_subha") and p.suffix.lower() in FONT_EXT:
        CUSTOM.setdefault("li subha letterpress", "/images/" + p.name)
GOOGLE = {"fraunces": "Fraunces:opsz,wght@9..144,400;9..144,700;9..144,900", "hanken grotesk": "Hanken+Grotesk:wght@400;500;600",
          "special elite": "Special+Elite", "courier prime": "Courier+Prime:wght@400;700", "playfair display": "Playfair+Display:wght@400;700;900",
          "merriweather": "Merriweather:wght@400;700;900", "inter": "Inter:wght@400;500;600;700",
          "noto serif bengali": "Noto+Serif+Bengali:wght@400;700", "noto sans bengali": "Noto+Sans+Bengali:wght@400;500;700"}
fo = c.get("fonts") or {}
def pick(sel, other, fallback):
    return (other or "").strip() or (sel or "").strip() or fallback
DEF = "Li Subha Letterpress" if "li subha letterpress" in CUSTOM else None
body_font = pick(fo.get("body"), fo.get("body_other"), DEF or "Hanken Grotesk")
head_font = pick(fo.get("headings"), fo.get("headings_other"), DEF or "Fraunces")
used = {body_font, head_font}
def walk(v):
    if isinstance(v, str): used.update(m.strip() for m in re.findall(r"\{([^|{}]+)\|", v))
    elif isinstance(v, list): [walk(i) for i in v]
    elif isinstance(v, dict): [walk(i) for i in v.values()]
walk(c)
faces, links = "", ['<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;700&display=swap">']
for name in sorted(used):
    k = name.lower()
    if k in CUSTOM:
        path = CUSTOM[k] if CUSTOM[k].startswith(("http", "/")) else "/" + CUSTOM[k]
        fmt = {"ttf": "truetype", "otf": "opentype", "woff": "woff", "woff2": "woff2"}.get(path.rsplit(".", 1)[-1].lower(), "truetype")
        faces += "@font-face{font-family:'%s';src:url('%s') format('%s');font-display:swap}" % (name, path, fmt)
    elif k != "noto sans bengali":
        fam = GOOGLE.get(k, name.replace(" ", "+"))
        links.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=%s&display=swap">' % fam)
ty = c.get("typography") or {}
def tnum(key, default, lo, hi, integer=False):
    try: value = float(ty.get(key, default))
    except (TypeError, ValueError): value = default
    value = max(lo, min(hi, value))
    return str(int(value)) if integer else str(value)
typography_css = ":root{--body-size:%spx;--mobile-body-size:%spx;--body-weight:%s;--line-height:%s;--heading-size:%spx;--heading-weight:%s;--section-space:%spx;--mobile-section-space:%spx}" % (
    tnum("body_size",17,12,24,True), tnum("mobile_body_size",17,12,22,True),
    tnum("body_weight",400,300,700,True), tnum("line_height",1.65,1.2,2.2),
    tnum("heading_size",64,28,72,True), tnum("heading_weight",900,500,900,True),
    tnum("section_spacing",84,24,180,True), tnum("mobile_section_spacing",60,20,120,True))
fonts_html = "\n".join(links) + "\n<style>" + faces + ":root{--fb:'%s','Noto Sans Bengali',system-ui,sans-serif;--fh:'%s','Noto Sans Bengali',Georgia,serif}body{font-synthesis:none}" % (body_font, head_font) + typography_css + "</style>"
credit = f'<p class="fc">{f(c["font_credit"])}</p>' if c.get("font_credit") else ""

h, ct = c["hero"], c["contact"]
links = "".join(f'<a href="{e(ct[k])}">{n}</a>' for k, n in [("linkedin","LinkedIn"),("behance","Behance"),("facebook","Facebook")])
page = open(find("template.html"), encoding="utf-8").read()
sections_html, nav_html = build_section_layout({'me': me(), 'about': exp(), 'education': edu(), 'activities': act(), 'skills': skills(), 'training-projects': training_projects(), 'design': design()})
for k, v in {"H1": f(h["title"]) if "{" in h["title"] else " ".join(f'<span class="nw">{e(w)}</span>' for w in h["title"].split()), "SUB": f(h["subtitle"]), "INTRO": f(h["intro"]), "HERO_IMG": img(h["image"]), "HERO_ALT": e(h["image_alt"]),
             "NAV": nav_html, "SECTIONS": sections_html, "SITE_URL": e(c.get("site_url", "").rstrip("/")), "EMAIL": e(ct["email"]), "LINKS": links,
             "FONTS": fonts_html, "CREDIT": credit, "QUOTE": f'“{f(ct["quote"])}”<span>{f(ct["quote_author"])}</span>'}.items():
    page = page.replace(f"[[{k}]]", v)
out = R/"dist"
if out.exists(): shutil.rmtree(out)
out.mkdir()
shutil.copy(R/"_worker.js", out/"_worker.js")
(out/"index.html").write_text(page, encoding="utf-8")
# images: from an images/ folder and/or loose .jpg/.png files at the top level
(out/"images").mkdir()
if (R/"images").is_dir():
    for p in (R/"images").iterdir():
        if p.is_file(): shutil.copy(p, out/"images"/p.name)
for p in R.glob("*"):
    if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".ttf", ".otf", ".woff", ".woff2"):
        shutil.copy(p, out/"images"/p.name)
# editor page: admin/ folder, or loose index.html + config.yml at the top level
(out/"admin").mkdir()
shutil.copy(find("admin/index.html", "index.html"), out/"admin"/"index.html")
shutil.copy(find("admin/config.yml", "config.yml"), out/"admin"/"config.yml")
print("images copied:", len(list((out/"images").iterdir())))
print("built", len(page), "bytes")
