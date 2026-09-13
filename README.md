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

**`harvest-placeholder.jpg` is not ours and must not go live.** The client
confirmed it will be replaced with their own footage. The filename says so
on purpose, so it cannot ship by accident. See `assets/img/SHOTLIST.md`
for what still needs photographing.

**Every figure on this site is a plausible placeholder, not your data.**
They were written so the design could be judged against realistic
content. Replace all of them, or you will be publishing false claims
about a food product.

| Where | What to replace |
|---|---|
| `gallery.body` | "before filtering" describes what the photograph appears to show; confirm it matches your actual process |
| `variety.facts` | Yield 18–22%, elevation 420–760 m, 180 trees/ha, 45-year-old trees |
| `process.steps[].tag` | ≤ 6 h to mill, 26 °C max, 16 °C storage, tank volumes |
| `specs.rows` | Now shows only the published IOC limits, which are real. Measured values are promised on the certificate of analysis instead. |

| `products.items[].price` | **Empty on purpose.** No price is invented. An empty field renders as "On request" linking to the quotation form. Fill in only with real numbers, and say on what basis — currency, Incoterm, volume band. |
| `products.items[].material` | Glass for 250/500/750 ml is assumed, not confirmed. Only the 1 L PET and the 5 L PET jerrycan are visible in the supplied photographs. |
| `logistics.rows` | Units per pallet, pallets per container, net volumes — including the 1 L PET row (720/pallet is a realistic estimate, not your figure) |
| `logistics.facts` | Lead time, minimum order, private-label threshold |
| `certs.items` | **ISO 22000, HACCP, IOC and organic status** — only claim what you hold |
| `footer` | Phone (`+213 TODO`) and email. The street address (N7, Tlemcen 13000) was supplied by the client. |
| `location.gps` | `34.8708962, -1.1253134` — supplied by the client. Not invented; verify once on the ground that the pin lands on the mill gate, not the road centre line. |
| `assets/video/hero.mp4` | Carries a `tryveo3.ai` watermark, bottom right. The hero scrim dims it heavily but it is still there. |

The COI/IOC method references and the extra-virgin limits in the right-hand
column are real published standards; your measured results are not.

**The acidity is now settled** at `≤ 0.8 %`, matching the label. The
invented 0.28% is gone from every page and from the meta descriptions.

But `≤ 0.8 %` is the definition of the extra virgin grade, not an
achievement: every extra virgin oil on earth meets it. As a headline
figure it tells a buyer nothing. Get a real measured value from a lab and
it becomes the strongest number on the site — a genuine 0.2% is a
sales argument, 0.8% is a category label.

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
| `assets/img/bottles-1l.jpg` | 900 × 1174 | **done** — cropped from the supplied packshot, `.webp` alongside | 1 L PET bottles, packaging section |
| `assets/img/harvest-placeholder.jpg` | 1200 × 1600 | **placeholder, unlicensed** | Hand picking, "Why Sigoise" section — replace before launch |
| `assets/img/mill-extraction.jpg` | 800 × 1070 | **in place** | Oil at the outlet, mill band |
| `assets/img/mark.jpg` | 320 × 320 | **in place** | The seal, footer |

| `assets/img/tanks.jpg` | 4:5 portrait | 800 × 1000, ~160 KB | Stainless storage tanks — still missing |
| `assets/img/loading.jpg` | 4:5 portrait | 800 × 1000, ~160 KB | Pallets going into a container — still missing |

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

Plus Google Fonts (Fraunces, Geist, IBM Plex Sans Arabic, Reem Kufi).
The stylesheet is loaded non-blocking, so the page paints in the fallback
stack immediately and swaps when the webfonts arrive; with the font host
unreachable, first paint is 208 ms rather than 12.7 s. To cut the third-party request and speed up first paint, self-host
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
- **Geist carries no Arabic**, so the Arabic pages are pinned to IBM Plex
  Sans Arabic rather than falling through to whatever the device has.
- **Three layouts, not one that shrinks.** Phone (< 768px): the hero data
  reads down as label-against-value, actions span the column, tables carry
  a fade that shows they scroll. Tablet (768-1088px): the full navigation
  on a row of its own, two-column splits a breakpoint earlier, no
  hamburger. Desktop (1088px+): the navigation returns to one row.
- **Text does not travel on entrance.** A staggered fade-and-slide-up on
  every block is the default of every scroll library; only the
  photographs animate, wiping up from their bottom edge.
- **Logical CSS properties throughout** (`inset-inline-start`,
  `padding-inline`, `border-block-end`) — Arabic mirrors from the same
  stylesheet with no RTL override file.

## Browser support

Modern evergreen browsers. Uses `color-mix()`, `aspect-ratio`, logical
properties and `100svh` — Chrome/Edge 111+, Safari 16.4+, Firefox 113+.
Older browsers get a readable, unstyled-in-places but complete page.
