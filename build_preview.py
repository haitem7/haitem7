#!/usr/bin/env python3
"""
Repackage the built site for a hosted preview.

The artifact host wraps the main file in its own <html>/<head>/<body> and
does not serve root-relative paths. So: strip the wrapper from the French
retail page, keep the other five as complete documents, and rewrite every
internal link to a relative path that works from a static folder.

    python3 build.py && python3 build_preview.py
"""
import os
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "preview"

# Site path -> file, in the order build.py writes them.
PAGES = ["", "en", "ar", "export", "en/export", "ar/export"]


def target(path: str) -> str:
    return (path + "/" if path else "") + "index.html"


def relink(html: str, here: str) -> str:
    """Rewrite absolute site links, then the two relative cross-links.

    Done longest-first: rewriting "/en/" before "/en/export/" would leave a
    dangling "index.html/export/" behind.
    """
    here_dir = here or "."
    for path in sorted(PAGES, key=len, reverse=True):
        rel = os.path.relpath(target(path), here_dir).replace(os.sep, "/")
        html = html.replace(f'href="/{path + "/" if path else ""}"', f'href="{rel}"')

    # The shop <-> export link is already relative, but it points at a
    # directory, and a directory index is exactly what the host will not
    # serve. Aim it at the file instead.
    other = ("" if here.endswith("export") else
             (here + "/export" if here else "export"))
    other = other.strip("/")
    if here.endswith("export"):
        other = here[: -len("export")].strip("/")
    rel = os.path.relpath(target(other), here_dir).replace(os.sep, "/")
    html = re.sub(r'(<a class="crosslink" href=)"[^"]*"', r'\1"%s"' % rel, html)

    # hreflang alternates point at a domain that does not exist yet.
    return re.sub(r'<link rel="alternate"[^>]*>|<link rel="canonical"[^>]*>', "", html)


if OUT.exists():
    shutil.rmtree(OUT)
for sub in ("assets/css", "assets/js", "assets/img", "assets/video"):
    (OUT / sub).mkdir(parents=True, exist_ok=True)

for path in PAGES:
    src = relink((ROOT / target(path)).read_text("utf-8"), path)
    dest = OUT / target(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path == "":
        # The host supplies the document shell for the entry file only.
        head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
        body = re.search(r"<body>(.*?)</body>", src, re.S).group(1)
        head = re.sub(r'<meta charset[^>]*>|<meta name="viewport"[^>]*>', "", head)
        head = re.sub(r"<title>.*?</title>", "<title>TLEMCENYA</title>", head, flags=re.S)
        dest.write_text(head.strip() + "\n" + body.strip() + "\n", "utf-8")
    else:
        dest.write_text(src, "utf-8")

for f in ("assets/css/site.css", "assets/js/site.js", "assets/img/favicon.svg"):
    shutil.copy(ROOT / f, OUT / f)

# OUT is wiped on every run, so copying the media here is what keeps a
# rebuild from publishing broken links.
for src in sorted((ROOT / "assets" / "img").glob("*.*")):
    if src.suffix.lower() in (".jpg", ".webp", ".png", ".avif"):
        shutil.copy(src, OUT / "assets" / "img" / src.name)
for name in ("hero.mp4", "hero-poster.jpg", "hero.webm"):
    src = ROOT / "assets" / "video" / name
    if src.exists():
        shutil.copy(src, OUT / "assets" / "video" / name)

_keep = ROOT / ".preview-video"
if _keep.is_dir():
    shutil.copytree(_keep, OUT / "assets" / "video", dirs_exist_ok=True)

for p in sorted(OUT.rglob("*")):
    if p.is_file():
        print(f"  {p.relative_to(OUT)}  ({p.stat().st_size:,} B)")
