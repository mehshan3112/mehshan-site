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
def f(s): return re.sub(r"\*(.+?)\*", r"<i>\1</i>", e(s))
def img(p): return e(p) if p.startswith(("http","/")) else "/"+e(p)

def me():
    a = c["about"]
    figs = "".join(f'<figure class="ph"><img src="{img(p["image"])}" alt="{e(p["alt"])}" loading="lazy"><figcaption>{e(p["caption"])}</figcaption></figure>' for p in a["photos"])
    return f'<section id="me"><p class="big">{"<br>".join(e(x) for x in a["headline"])}</p><p class="sub" style="margin-top:24px">{e(a["text"])}</p><div class="scat">{figs}</div></section>'

def exp():
    dye = open(find("dye.html"), encoding="utf-8").read().replace("Colour by the ton.", e(c["dye_caption"]))
    rows = ""
    for x in c["experience"]:
        w = e(x["dates"]) + (f'<br>{e(x["place"])}' if x.get("place") else "")
        b = x.get("bullets", [])
        body = ("<ul>" + "".join(f"<li>{f(i)}</li>" for i in b) + "</ul>") if len(b) > 1 else (f"<p>{f(b[0])}</p>" if b else "")
        link = f'<p><a href="{e(x["link_url"])}">{e(x["link_text"])}</a></p>' if x.get("link_url") else ""
        d = x.get("show_dye_machine")
        rows += f'<div class="row{" dr" if d else ""}"><div class="w">{w}</div><div><h3>{e(x["role"])}<em>{e(x["org"])}</em></h3>{body}{link}</div>{dye if d else ""}</div>'
    return f'<section id="about"><h2>Experience</h2><p class="sub">{e(c["objective"])}</p><div>{rows}</div></section>'

def edu():
    rows = "".join(f'<div class="row"><div class="w">{e(x["dates"])}</div><div><h3>{e(x["degree"])}<em>{e(x["school"])}</em></h3></div></div>' for x in c["education"])
    return f'<section id="education"><h2>Education</h2>{rows}</section>'

def skills():
    g = "".join(f'<div><h3>{e(s["title"])}</h3><ul>' + "".join(f"<li>{e(i)}</li>" for i in s["items"]) + "</ul></div>" for s in c["skills"])
    tr = "".join(f"<li>{e(i)}</li>" for i in c["training"])
    p = c["project"]
    return (f'<section id="skills"><h2>Skills and training</h2><div class="cols" style="margin-top:36px">{g}</div>'
            f'<div class="cols" style="margin-top:44px;grid-template-columns:1fr 1fr"><div><h3>Training programs</h3><ul>{tr}</ul></div>'
            f'<div><h3>Project work</h3><p style="margin:0"><b>{e(p["title"])}.</b> {e(p["text"])}</p></div></div></section>')

def design():
    d = c["designs"]; it = d["items"]; n = len(it)
    lst = "".join(f'<li><button type="button" data-i="{i}"><span class="n">#{i+1:04d}/{n}</span><span class="t">{e(x["title"])}</span><span class="k">{e(x["kind"])}</span></button></li>' for i, x in enumerate(it))
    figs = "".join(f'<figure><button type="button" data-l="{e(x["link"])}" data-t="{e(x["title"])}"><img src="{img(x["image"])}" alt="{e(x["title"])} {e(x["kind"]).lower()} by Mehshan" loading="lazy"></button><figcaption><b>{e(x["title"])}</b><span>{e(x["kind"])}</span></figcaption></figure>' for x in it)
    return (f'<section id="design"><h2 style="letter-spacing:.3em">Design</h2><p class="sub" style="max-width:46em;margin-top:0">{e(d["intro"])}</p>'
            f'<ol class="wl">{lst}</ol><div id="pv" aria-hidden="true"><img alt=""></div>'
            f'<p class="sub" style="margin:56px 0 18px">All pieces, in one strip. Scroll sideways.</p><div class="strip">{figs}</div>'
            f'<p style="margin-top:12px"><a class="btn" href="{e(d["behance"])}">Full portfolio on Behance</a></p></section>')

h, ct = c["hero"], c["contact"]
links = "".join(f'<a href="{e(ct[k])}">{n}</a>' for k, n in [("linkedin","LinkedIn"),("behance","Behance"),("facebook","Facebook")])
page = open(find("template.html"), encoding="utf-8").read()
for k, v in {"H1": e(h["title"]), "SUB": e(h["subtitle"]), "INTRO": e(h["intro"]), "HERO_IMG": img(h["image"]), "HERO_ALT": e(h["image_alt"]),
             "ME": me(), "EXP": exp(), "EDU": edu(), "SKILLS": skills(), "DESIGN": design(), "EMAIL": e(ct["email"]), "LINKS": links,
             "QUOTE": f'“{e(ct["quote"])}”<span>{e(ct["quote_author"])}</span>'}.items():
    page = page.replace(f"[[{k}]]", v)
out = R/"dist"
if out.exists(): shutil.rmtree(out)
out.mkdir()
(out/"index.html").write_text(page, encoding="utf-8")
# images: from an images/ folder and/or loose .jpg/.png files at the top level
(out/"images").mkdir()
if (R/"images").is_dir():
    for p in (R/"images").iterdir():
        if p.is_file(): shutil.copy(p, out/"images"/p.name)
for p in R.glob("*"):
    if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
        shutil.copy(p, out/"images"/p.name)
# editor page: admin/ folder, or loose index.html + config.yml at the top level
(out/"admin").mkdir()
shutil.copy(find("admin/index.html", "index.html"), out/"admin"/"index.html")
shutil.copy(find("admin/config.yml", "config.yml"), out/"admin"/"config.yml")
print("images copied:", len(list((out/"images").iterdir())))
print("built", len(page), "bytes")
