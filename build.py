#!/usr/bin/env python3
"""
Render the TLEMCENYA site: one template, three locales, static HTML out.

    python3 build.py

Writes index.html (fr), en/index.html, ar/index.html. No runtime build step:
the generated files are plain HTML and ship as-is.
"""
from __future__ import annotations

import html
import json
import re
import pathlib

ROOT = pathlib.Path(__file__).parent
LOCALES = ["fr", "en", "ar"]
BRAND_DEFAULT = "TLEMCENYA"

# ---------------------------------------------------------------- helpers

# A range is "<number> <dash> <number>" with whitespace around the dash,
# so a hyphenated code such as TLM-25-114 is never matched.
RANGE = re.compile(r"\d[\d.,\u202f]*\s[–—-]\s\d[\d.,]*\s?[%\u066a]?")
LRI, PDI = "\u2066", "\u2069"


def e(s: object) -> str:
    return html.escape(str(s), quote=True)


def num(s: object, lang: str) -> str:
    """Escape, and in RTL pin numeric ranges to LTR.

    Arabic is an RTL paragraph, and digits are bidi-weak: without an
    explicit isolate the browser renders "18 - 22%" as "22% - 18".
    """
    if lang != "ar":
        return e(s)
    # Unicode isolates rather than markup: these survive inside <option>,
    # attribute values and plain text, where a <span> cannot go.
    return e(RANGE.sub(lambda m: LRI + m.group(0) + PDI, str(s)))


def icon(name: str, size: int = 20) -> str:
    """Inline stroke icons. One family, one stroke width (1.6), no emoji."""
    paths = {
        "download": '<path d="M12 3v12m0 0 4.5-4.5M12 15l-4.5-4.5M4 19.5h16"/>',
        "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.5h.01"/>',
        "check": '<path d="M4.5 12.5 9 17 19.5 6.5"/>',
        "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
        "close": '<path d="M6 6l12 12M18 6 6 18"/>',
        "seal": '<path d="M12 3.2 14.3 5l2.8-.3 1 2.6 2.4 1.5-.8 2.7.8 2.7-2.4 1.5-1 2.6-2.8-.3L12 20.8 9.7 19l-2.8.3-1-2.6L3.5 15.2l.8-2.7-.8-2.7 2.4-1.5 1-2.6 2.8.3z"/><path d="M9 12.2l2.1 2.1L15.3 10"/>',
        "drop": '<path d="M12 3.5c3.2 4 5.2 6.6 5.2 9.2a5.2 5.2 0 0 1-10.4 0c0-2.6 2-5.2 5.2-9.2z"/>',
    }
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
        f'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" focusable="false">{paths[name]}</svg>'
    )


def datagrid(items: list[dict], cols: str, lang: str = "fr") -> str:
    cells = "".join(
        f'<div><dt>{e(i["label"])}</dt><dd class="tnum">{num(i["value"], lang)}</dd></div>'
        for i in items
    )
    return f'<dl class="datagrid {cols}">{cells}</dl>'


def table(head: list[str], rows: list[list[str]], caption: str, lang: str = "fr") -> str:
    th = "".join(f"<th scope=\"col\">{e(h)}</th>" for h in head)
    body = ""
    for r in rows:
        cells = f'<th scope="row">{num(r[0], lang)}</th>' + "".join(
            f'<td>{num(c, lang)}</td>' for c in r[1:]
        )
        body += f"<tr>{cells}</tr>"
    return (
        f'<div class="scroll-x"><table class="spec"><caption>{e(caption)}</caption>'
        f"<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>"
    )

# ---------------------------------------------------------------- sections

def head_tag(c: dict, assets: str, alts: list[dict]) -> str:
    m = c["meta"]
    hreflang = "".join(
        f'<link rel="alternate" hreflang="{a["lang"]}" href="/{a["path"]}">' for a in alts
    )
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(m["title"])}</title>
<meta name="description" content="{e(m["description"])}">
<meta name="theme-color" content="#151a10">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(m["title"])}">
<meta property="og:description" content="{e(m["description"])}">
<meta property="og:locale" content="{e(m["og_locale"])}">
{hreflang}<link rel="alternate" hreflang="x-default" href="/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,300..700,0..100,0..1&family=IBM+Plex+Sans:wght@300;400;450;600&family=IBM+Plex+Sans+Arabic:wght@300;400;600&family=Reem+Kufi:wght@400..700&display=swap">
<link rel="icon" href="{assets}img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{assets}css/site.css">"""


def header(c: dict, assets: str, alts: list[dict]) -> str:
    links = "".join(
        f'<li><a class="navlink" href="{e(l["href"])}">{e(l["label"])}</a></li>' for l in c["nav"]
    )
    langs = "".join(
        f'<li><a href="/{a["path"]}" lang="{a["lang"]}" hreflang="{a["lang"]}"'
        + (' aria-current="true"' if a["lang"] == c["lang"] else "")
        + f'>{e(a["label"])}</a></li>'
        for a in alts
    )
    brand = e(c.get("brand", BRAND_DEFAULT))
    return f"""<a class="skip" href="#main">{e(c["skip"])}</a>
<header class="site-head on-dark" data-head>
  <div class="shell head-row">
    <a class="brand display" href="/{c["path"]}">{brand}</a>
    <button class="nav-toggle btn btn-quiet" type="button" data-nav-toggle
            aria-expanded="false" aria-controls="nav-panel"
            data-label-close="{e(c["nav_menu_close"])}">
      <span data-nav-label>{e(c["nav_menu_open"])}</span>
      <span data-nav-icon>{icon("menu")}</span>
    </button>
    <div class="nav-panel" id="nav-panel" data-nav-panel>
      <nav aria-label="{e(c["nav"][0]["label"])}">
        <ul class="navlist">{links}</ul>
      </nav>
      <nav class="langnav" aria-label="{e(c["footer"]["lang_label"])}">
        <ul>{langs}</ul>
      </nav>
      <a class="btn btn-primary head-cta" href="#{e(c["rfq"]["id"])}">{e(c["nav_cta"])}</a>
    </div>
  </div>
</header>"""


def hero(c: dict) -> str:
    h = c["hero"]
    lines = "".join(f"<span>{e(l)}</span>" for l in h["title_lines"])

    # Optional scroll-scrubbed frame sequence. Nothing is fetched until
    # site.js decides the viewport, connection and motion preference allow
    # it, and the section only grows tall once scrubbing is actually on.
    fr = h.get("frames")
    canvas = ""
    scroll_attrs = ""
    if fr and fr.get("count"):
        canvas = '<canvas class="hero-canvas" data-hero-canvas aria-hidden="true"></canvas>'
        scroll_attrs = (
            f' data-hero-scroll data-frame-base="{e(fr["base"])}"'
            f' data-frame-ext="{e(fr["ext"])}" data-frame-count="{fr["count"]}"'
            f' data-frame-pad="{fr.get("pad", 3)}"'
        )

    return f"""<div class="hero-scroll"{scroll_attrs}>
<section class="hero on-dark grain" data-oil>
  <div class="oil-field" aria-hidden="true"><span></span><span></span><span></span><span></span></div>
  {canvas}
  <div class="shell hero-inner">
    <h1 class="display hero-title">{lines}</h1>
    <p class="hero-lede measure">{e(h["lede"])}</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="#{e(c["rfq"]["id"])}">{e(h["cta_primary"])}</a>
      <a class="btn btn-quiet" href="#{e(c["specs"]["id"])}">{e(h["cta_secondary"])}</a>
    </div>
    {datagrid(h["data"], "hero-data", c["lang"])}
  </div>
</section>
</div>"""


def variety(c: dict) -> str:
    v = c["variety"]
    s = v["slot"]
    body = "".join(f'<p class="measure">{e(p)}</p>' for p in v["body"])
    return f"""<section class="band band-stone" id="{e(v["id"])}">
  <div class="shell split">
    <div class="split-text reveal">
      <h2 class="display sec-title">{e(v["title"])}</h2>
      {body}
      {datagrid(v["facts"], "facts-grid", c["lang"])}
    </div>
    <figure class="split-media reveal">
      <div class="slot" style="aspect-ratio: {e(s["ratio"])}">
        <img src="{e(s["file"])}" alt="{e(s["alt"])}" width="900" height="1125"
             loading="lazy" decoding="async" onerror="this.remove()">
      </div>
      <figcaption class="media-note">{e(s["caption"])}</figcaption>
    </figure>
  </div>
</section>"""


def process(c: dict) -> str:
    p = c["process"]
    steps = ""
    for n, s in enumerate(p["steps"], 1):
        steps += f"""<li class="step reveal">
  <span class="step-n tnum" aria-hidden="true">{n}</span>
  <div class="step-body">
    <h3 class="step-title">{e(s["title"])}</h3>
    <p>{e(s["body"])}</p>
    <p class="step-tag tnum">{e(s["tag"])}</p>
  </div>
</li>"""
    return f"""<section class="band band-ink on-dark" id="{e(p["id"])}">
  <div class="shell">
    <div class="sec-head reveal">
      <h2 class="display sec-title">{e(p["title"])}</h2>
      <p class="measure sec-lede">{e(p["lede"])}</p>
    </div>
    <div class="rail-wrap">
      <div class="rail" aria-hidden="true"><div class="rail-fill"></div></div>
      <ol class="steps">{steps}</ol>
    </div>
  </div>
</section>"""


def gallery(c: dict) -> str:
    g = c["gallery"]
    shots = ""
    for i, sh in enumerate(g["shots"]):
        shots += f"""<figure class="shot reveal">
  <div class="slot" style="aspect-ratio: 4 / 5">
    <img src="{e(sh["file"])}" alt="{e(sh["alt"])}" width="800" height="1000"
         loading="lazy" decoding="async" onerror="this.remove()">
  </div>
  <figcaption class="media-note">{e(sh["caption"])}</figcaption>
</figure>"""
    return f"""<section class="band band-stone">
  <div class="shell">
    <h2 class="display sec-title reveal">{e(g["title"])}</h2>
    <div class="shots">{shots}</div>
  </div>
</section>"""


def specs(c: dict) -> str:
    s = c["specs"]
    meta = datagrid(
        [
            {"label": s["lot_label"], "value": s["lot_value"]},
            {"label": s["campaign_label"], "value": s["campaign_value"]},
        ],
        "lot-grid",
        c["lang"],
    )
    return f"""<section class="band band-paper" id="{e(s["id"])}">
  <div class="shell">
    <div class="sec-head reveal">
      <h2 class="display sec-title">{e(s["title"])}</h2>
      <p class="measure sec-lede">{e(s["lede"])}</p>
      {meta}
    </div>
    <div class="reveal">{table(s["head"], s["rows"], s["caption"], c["lang"])}</div>
    <p class="reveal coa">
      <a class="btn btn-quiet" href="{e(s["cta_file"])}" download>{icon("download")}<span>{e(s["cta"])}</span></a>
    </p>
  </div>
</section>"""


def logistics(c: dict) -> str:
    l = c["logistics"]
    return f"""<section class="band band-stone" id="{e(l["id"])}">
  <div class="shell">
    <div class="sec-head reveal">
      <h2 class="display sec-title">{e(l["title"])}</h2>
      <p class="measure sec-lede">{e(l["lede"])}</p>
    </div>
    <div class="reveal">{table(l["head"], l["rows"], "", c["lang"])}</div>
    <div class="reveal">{datagrid(l["facts"], "logi-grid", c["lang"])}</div>
  </div>
</section>"""


def certs(c: dict) -> str:
    k = c["certs"]
    items = "".join(
        f'<li class="cert reveal"><span class="cert-mark" aria-hidden="true">{icon("seal", 22)}</span>'
        f'<h3 class="cert-name">{e(i["name"])}</h3><p>{e(i["body"])}</p></li>'
        for i in k["items"]
    )
    return f"""<section class="band band-stone band-tight">
  <div class="shell">
    <h2 class="display sec-title reveal">{e(k["title"])}</h2>
    <ul class="certs">{items}</ul>
  </div>
</section>"""


def field(f: dict, lang: str) -> str:
    req = f.get("required", False)
    star = ' <span class="req" aria-hidden="true">*</span>' if req else ""
    attrs = [f'id="f-{f["name"]}"', f'name="{f["name"]}"']
    if req:
        attrs.append("required")
    for a in ("autocomplete", "inputmode"):
        if f.get(a):
            attrs.append(f'{a}="{f[a]}"')
    described = []
    if f.get("hint"):
        described.append(f'h-{f["name"]}')
    described.append(f'e-{f["name"]}')
    attrs.append(f'aria-describedby="{" ".join(described)}"')
    A = " ".join(attrs)

    if f["type"] == "select":
        opts = "".join(f'<option value="{e(o)}">{num(o, lang)}</option>' for o in f["options"])
        control = f'<select {A}><option value="">—</option>{opts}</select>'
    elif f["type"] == "textarea":
        control = f"<textarea {A} rows=\"4\"></textarea>"
    else:
        control = f'<input type="{f["type"]}" {A}>'

    hint = f'<p class="hint" id="h-{f["name"]}">{e(f["hint"])}</p>' if f.get("hint") else ""
    err = e(f.get("error", ""))
    wide = " field-wide" if f["type"] == "textarea" else ""
    return f"""<div class="field{wide}" data-field data-invalid="false">
  <label for="f-{f["name"]}">{e(f["label"])}{star}</label>
  {control}
  {hint}
  <p class="err" id="e-{f["name"]}" data-msg="{err}">{icon("alert", 16)}<span></span></p>
</div>"""


def rfq(c: dict) -> str:
    r = c["rfq"]
    fields = "".join(field(f, c["lang"]) for f in r["fields"])
    return f"""<section class="band band-ink on-dark" id="{e(r["id"])}">
  <div class="shell rfq-grid">
    <div class="rfq-intro reveal">
      <h2 class="display sec-title">{e(r["title"])}</h2>
      <p class="measure sec-lede">{e(r["lede"])}</p>
      <p class="req-note">{e(r["required_note"])}</p>
    </div>
    <form class="rfq-form reveal" data-rfq novalidate
          data-endpoint=""
          data-mailto="{e(c["footer"]["email"])}">
      <div class="summary" data-summary hidden tabindex="-1" role="alert">
        <p class="summary-title">{icon("alert", 18)}<span>{e(r["error_summary_title"])}</span></p>
        <ul data-summary-list></ul>
      </div>
      <div class="fields">{fields}</div>
      <button class="btn btn-primary submit" type="submit" data-submit
              data-idle="{e(r["submit"])}" data-busy="{e(r["submitting"])}">{e(r["submit"])}</button>
      <div class="done" data-done hidden tabindex="-1">
        <p class="done-title">{icon("check", 18)}<span>{e(r["success_title"])}</span></p>
        <p>{e(r["success_body"])}</p>
      </div>
      <p class="sr-live" data-live aria-live="polite"></p>
    </form>
  </div>
</section>"""


def footer(c: dict, alts: list[dict]) -> str:
    f = c["footer"]
    addr = "<br>".join(e(l) for l in f["address"])
    langs = "".join(
        f'<li><a href="/{a["path"]}" lang="{a["lang"]}" hreflang="{a["lang"]}"'
        + (' aria-current="true"' if a["lang"] == c["lang"] else "")
        + f'>{e(a["label"])}</a></li>'
        for a in alts
    )
    return f"""<footer class="site-foot band-paper">
  <div class="shell foot-grid">
    <div>
      <p class="foot-label">{e(f["address_label"])}</p>
      <address class="foot-addr">{addr}</address>
    </div>
    <div>
      <p class="foot-label">{e(f["phone_label"])}</p>
      <p><a class="wrap-any" href="tel:{e(f["phone"].replace(" ", ""))}">{e(f["phone"])}</a></p>
      <p class="foot-label foot-label-gap">{e(f["email_label"])}</p>
      <p><a class="wrap-any" href="mailto:{e(f["email"])}">{e(f["email"])}</a></p>
    </div>
    <div>
      <p class="foot-label">{e(f["hours_label"])}</p>
      <p class="tnum">{e(f["hours"])}</p>
    </div>
    <div>
      <p class="foot-label">{e(f["lang_label"])}</p>
      <ul class="foot-langs">{langs}</ul>
    </div>
  </div>
  <div class="shell foot-legal"><p>{e(f["legal"])}</p></div>
</footer>"""

# ---------------------------------------------------------------- page

def page(c: dict, alts: list[dict]) -> str:
    assets = "assets/" if c["path"] == "" else "../assets/"
    body = "\n".join(
        [
            header(c, assets, alts),
            '<main id="main">',
            hero(c),
            variety(c),
            process(c),
            gallery(c),
            specs(c),
            logistics(c),
            certs(c),
            rfq(c),
            "</main>",
            footer(c, alts),
        ]
    )
    return f"""<!doctype html>
<html lang="{c["lang"]}" dir="{c["dir"]}" class="no-js">
<head>
{head_tag(c, assets, alts)}
<script>document.documentElement.classList.remove('no-js')</script>
</head>
<body>
{body}
<script src="{assets}js/site.js" defer></script>
</body>
</html>
"""


def main() -> None:
    data = {l: json.loads((ROOT / "content" / f"{l}.json").read_text("utf-8")) for l in LOCALES}
    alts = [
        {"lang": d["lang"], "path": d["path"], "label": d["label"]} for d in data.values()
    ]
    for l, c in data.items():
        out = ROOT / "index.html" if c["path"] == "" else ROOT / c["path"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(c, alts), "utf-8")
        print(f"  {out.relative_to(ROOT)}  ({len(out.read_text('utf-8')):,} bytes)")


if __name__ == "__main__":
    print("TLEMCENYA — rendering pages")
    main()
