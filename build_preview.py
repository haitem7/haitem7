#!/usr/bin/env python3
"""
Repackage the built site for a hosted preview.

The artifact host wraps the main file in its own <html>/<head>/<body>, and
does not serve root-relative paths. So: strip the wrapper from the French
page, keep the other two locales as complete documents, and rewrite the
language links to relative paths.

    python3 build.py && python3 build_preview.py
"""
import pathlib, re, shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "preview"

LINKS = {
    "":    {'href="/"': 'href="index.html"',    'href="/en/"': 'href="en/index.html"',    'href="/ar/"': 'href="ar/index.html"'},
    "en/": {'href="/"': 'href="../index.html"', 'href="/en/"': 'href="index.html"',       'href="/ar/"': 'href="../ar/index.html"'},
    "ar/": {'href="/"': 'href="../index.html"', 'href="/en/"': 'href="../en/index.html"', 'href="/ar/"': 'href="index.html"'},
}

def relink(html: str, where: str) -> str:
    for old, new in LINKS[where].items():
        html = html.replace(old, new)
    # hreflang alternates point at a domain that does not exist yet
    return re.sub(r'<link rel="alternate"[^>]*>', "", html)

if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "en").mkdir(parents=True)
(OUT / "ar").mkdir(parents=True)
(OUT / "assets" / "css").mkdir(parents=True)
(OUT / "assets" / "js").mkdir(parents=True)
(OUT / "assets" / "img").mkdir(parents=True)

# French: unwrapped, because the host supplies the document shell.
src = relink((ROOT / "index.html").read_text("utf-8"), "")
head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", src, re.S).group(1)
head = re.sub(r'<meta charset[^>]*>|<meta name="viewport"[^>]*>', "", head)
head = re.sub(r"<title>.*?</title>", "<title>TLEMCENYA</title>", head, flags=re.S)
(OUT / "index.html").write_text(head.strip() + "\n" + body.strip() + "\n", "utf-8")

# English and Arabic stay complete documents: they are served as files.
for loc in ("en", "ar"):
    (OUT / loc / "index.html").write_text(
        relink((ROOT / loc / "index.html").read_text("utf-8"), loc + "/"), "utf-8"
    )

for f in ("assets/css/site.css", "assets/js/site.js", "assets/img/favicon.svg"):
    shutil.copy(ROOT / f, OUT / f)

# Video files placed in preview/assets/video by hand are kept, not wiped.
_keep = ROOT / ".preview-video"
if _keep.is_dir():
    shutil.copytree(_keep, OUT / "assets" / "video", dirs_exist_ok=True)

for p in sorted(OUT.rglob("*")):
    if p.is_file():
        print(f"  {p.relative_to(OUT)}  ({p.stat().st_size:,} B)")
