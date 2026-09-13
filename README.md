# TLEMCENYA

Static trilingual export site for an olive mill in Tlemcen, Algeria.
French (default), English and Arabic (RTL), built for B2B buyers: lot
analysis, packaging formats, Incoterms and a quotation request.

```
index.html          French   (/)
en/index.html       English  (/en/)
ar/index.html       Arabic   (/ar/, dir="rtl")
content/*.json      all copy and every number — edit here, not in the HTML
src/site.css        Tailwind source + design tokens
build.py            renders the three pages from content/
assets/             compiled css, js, images, documents
```

---

## ⚠️ Read this before the site goes live

**Every figure on this site is a plausible placeholder, not your data.**
They were written so the design could be judged against realistic
content. Replace all of them, or you will be publishing false claims
about a food product.

| Where | What to replace |
|---|---|
| `hero.data` | Free acidity 0.28%, peroxide 7.2, polyphenols 412 mg/kg — **the bottle label says < 0.8%; see below** |
| `variety.facts` | Yield 18–22%, elevation 420–760 m, 180 trees/ha, 45-year-old trees |
| `process.steps[].tag` | ≤ 6 h to mill, 26 °C max, 16 °C storage, tank volumes |
| `specs.rows` | **The entire analysis table** — all eight parameters and results |
| `specs.lot_value` | Lot number `TLM-25-114` and campaign `2025/26` |
| `logistics.rows` | Units per pallet, pallets per container, net volumes — including the 1 L PET row (720/pallet is a realistic estimate, not your figure) |
| `logistics.facts` | Lead time, minimum order, private-label threshold |
| `certs.items` | **ISO 22000, HACCP, IOC and organic status** — only claim what you hold |
| `footer` | Address, phone (`+213 TODO`), email |

The COI/IOC method references and the extra-virgin limits in the right-hand
column are real published standards; your measured results are not.

**The acidity conflict.** The retail label reads `ACIDITÉ < 0,8 %`. That is
the legal ceiling for the extra virgin category, not a measured value. The
site currently claims 0.28%. Both cannot be the claim you stand behind: if
the oil actually runs near 0.8%, every acidity figure on this site is
false, and an importer's own lab test is where that surfaces.

---

## Editing content

All text and numbers live in `content/fr.json`, `content/en.json` and
`content/ar.json`. The three files share the same shape, so a key added to
one must be added to all three. Then:

```bash
python3 build.py          # re-renders the three HTML pages
```

Arabic numeric ranges are wrapped in Unicode bidi isolates at build time,
so `18 – 22٪` does not render as `22٪ – 18`. Write ranges normally in the
JSON; `build.py` handles it.

## Photographs

Drop files at these exact paths. Nothing else needs to change: each slot
already reserves its aspect ratio, so adding a photo cannot shift the
layout. Until a file exists, the slot shows a deep olive gradient panel —
no broken-image icon.

| Path | Ratio | Suggested export | Subject |
|---|---|---|---|
| `assets/img/grove-beni-snous.jpg` | 4:5 portrait | 900 × 1125, ~180 KB | Terraced grove, Beni Snous |
| `assets/img/mill-floor.jpg` | 4:5 portrait | 800 × 1000, ~160 KB | Milling / malaxation line |
| `assets/img/tanks.jpg` | 4:5 portrait | 800 × 1000, ~160 KB | Stainless storage tanks |
| `assets/img/loading.jpg` | 4:5 portrait | 800 × 1000, ~160 KB | Pallets going into a container |

Export as WebP if you can (`.webp`, and update the filename in the JSON) —
roughly 30% smaller at the same quality. The alt text is in the JSON; keep
it descriptive if you change the photo.

Drop an `.avif` or `.webp` next to the `.jpg` under the same base name and
the build picks it up automatically as a `<source>`, with the JPEG left as
the fallback. A format is only offered when its file is actually on disk:
a `<source>` is chosen on format support, not on the file existing, so
listing an AVIF that 404s would break the image entirely.

Every photograph is graded into the palette on the way in — a soft-light
wash toward the oil greens and golds, a vignette, and a slow settle from
1.04 to 1.0 on hover that resolves to full colour. A photograph that keeps
its own colour cast sits on a design; one that is graded belongs to it.
Nothing needs doing to opt in: drop the file and it happens.

`assets/doc/coa-tlm-25-114.pdf` — the signed certificate of analysis the
Analysis section links to. Until it exists, the link 404s; either add the
file or remove the `cta` key from `specs`.

## The quotation form

By default the form validates in the browser and then opens the visitor's
mail client pre-filled to the address in `footer.email`. That works
everywhere but depends on the visitor having a mail client.

For a real inbox, set an endpoint in `build.py` (the `data-endpoint`
attribute in `rfq()`) to any service that accepts a JSON POST — Formspree,
Basin, Web3Forms, a Netlify function. The form POSTs JSON and falls back to
mailto if the request fails, so a submission is never silently lost.

On Netlify you can instead add `netlify` and `name="rfq"` attributes to the
`<form>` tag and let Netlify Forms capture it.

## Build and deploy

```bash
npm install          # only needed to recompile CSS
npm run build        # tailwind -> assets/css/site.css, then build.py
npm run serve        # http://localhost:8080
```

The compiled CSS is committed, so **deploying needs no build step**: upload
the repository as-is to Netlify, Vercel, GitHub Pages, OVH, or any shared
host. Point the domain at the root; `/en/` and `/ar/` work as directories.

Update the domain in `sitemap.xml` and `robots.txt` before launch.

## What it weighs

| File | Transferred (gzip) |
|---|---|
| `index.html` | ~6.3 KB |
| `assets/css/site.css` | ~12.7 KB |
| `assets/js/site.js` | ~2.9 KB |

Plus Google Fonts (Fraunces, IBM Plex Sans, IBM Plex Sans Arabic, Reem
Kufi). To cut the third-party request and speed up first paint, self-host
them: download the woff2 files into `assets/fonts/`, replace the
`<link>` in `build.py` with local `@font-face` rules, and keep
`font-display: swap`.

## Decisions worth knowing

- **No animation library.** Entrances use one IntersectionObserver; the
  hero's oil field is four CSS gradients. GSAP would have added ~70 KB and
  main-thread scroll cost for the same result. The JS is additive: with
  scripts blocked, every section renders in its final state.
- **The observer uses `rootMargin: 0`.** A negative bottom margin strands
  anything sitting in that band at maximum scroll, permanently invisible.
  A scroll listener also force-reveals everything at the foot of the page.
- **Three pages, not a JS language switcher.** Correct `hreflang`, no flash
  of the wrong language, indexable per language, works with JS off.
- **`prefers-reduced-motion`** stops the oil field, the reveals and the
  process rail, and renders every section in its final state.
- **Logical CSS properties throughout** (`inset-inline-start`,
  `padding-inline`, `border-block-end`) — Arabic mirrors from the same
  stylesheet with no RTL override file.

## Browser support

Modern evergreen browsers. Uses `color-mix()`, `aspect-ratio`, logical
properties and `100svh` — Chrome/Edge 111+, Safari 16.4+, Firefox 113+.
Older browsers get a readable, unstyled-in-places but complete page.
