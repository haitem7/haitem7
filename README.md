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


## Sécurité, SEO technique et déploiement

Tout ce qui suit est **généré par `build.py`** : ne pas éditer à la main, les
fichiers sont réécrits à chaque `python3 build.py`.

| Fichier | Rôle |
|---|---|
| `_headers` | En-têtes pour Netlify / Cloudflare Pages |
| `.htaccess` | Les mêmes pour Apache / cPanel, + redirection HTTPS forcée |
| `robots.txt` | Autorise tout ; pointe vers le sitemap dès que `SITE_URL` existe |
| `sitemap.xml` | Écrit uniquement si `SITE_URL` est défini (un sitemap en URLs relatives est rejeté) |
| `src/_ratios.css` | Les `aspect-ratio` en classes CSS, pour qu'aucune page ne porte de `style=""` |

### Le domaine

Canonical, hreflang, `og:image` et `sitemap.xml` ont besoin d'URLs absolues.
Tant que le domaine n'existe pas, `SITE_URL` reste vide et ces éléments sont
soit relatifs, soit omis — une URL qui pointe vers un domaine qu'on ne possède
pas est pire que pas d'URL. Une fois le domaine acheté :

```sh
SITE_URL=https://tlemcenya.dz python3 build.py
```

### Content-Security-Policy

La politique est calculée depuis les constantes `JS_NOJS`, `JS_FONT_SWAP` et
`JS_IMG_FALLBACK` de `build.py` : les hachages SHA-256 ne peuvent pas se
désynchroniser des pages. Pas de `'unsafe-inline'`, ni pour les scripts ni
pour les styles. Vérifié dans Chromium sous les en-têtes réels : zéro
violation sur les trois langues.

Si `rfq.endpoint` reçoit une URL tierce (Formspree, EmailJS…), son origine est
ajoutée automatiquement à `connect-src` et `form-action` — sinon le navigateur
bloquerait l'envoi et l'acheteur verrait un échec silencieux.

### Données structurées (JSON-LD)

Un graphe `Organization` + `Place` + `Product` dans chaque page, avec les
coordonnées GPS réelles. Deux absences volontaires :

- **Pas d'`aggregateRating`.** Google interdit le balisage d'avis qui ne sont
  pas affichés sur la page. Inventer des étoiles fait perdre les rich results,
  définitivement.
- **Pas d'`offers` tant que `products.items[].price` est vide.** Une offre est
  un engagement commercial public. Dès qu'un prix réel est saisi, l'offre est
  émise automatiquement — rien d'autre à faire.

### Bouton WhatsApp

Rendu uniquement quand `footer.phone` est un vrai numéro. Tant qu'il vaut
`+213 TODO`, le bouton n'existe pas : un bouton qui ouvre une discussion avec
un numéro inexistant coûte plus de confiance qu'il n'en rapporte.

### Réception des demandes de cotation

`rfq.endpoint` est vide : le formulaire retombe sur `mailto:`. C'est un
**vrai trou** — le client doit avoir un client mail configuré. À brancher sur
Formspree, EmailJS ou un endpoint maison.



## Deux publics, deux pages

Le site rend **six pages** : trois langues × deux publics.

| URL | Public | Contenu |
|---|---|---|
| `/`, `/en/`, `/ar/` | Particuliers | Boutique, panier, livraison, commande |
| `/export/`, `/en/export/`, `/ar/export/` | Professionnels | Variété, procédé, spécification, logistique, cotation |

Un acheteur qui cherche « huile d'olive Tlemcen » arrive sur la boutique ;
un importateur qui cherche des spécifications arrive sur `/export/`. Chaque
page porte un lien vers l'autre dans son menu, et le sélecteur de langue
reste **sur la même page** : passer de l'arabe au français depuis la boutique
mène à la boutique française, pas à la page export.

Le contenu vit dans `content/{fr,en,ar}.json`. La clé `shop` porte la page
grand public, le reste porte la page export. **Les formats du catalogue sont
copiés depuis `products.items` par position** : les deux pages ne peuvent pas
diverger sur ce qui est vendu.

### Le panier

Entièrement côté client : `localStorage`, clé `tly.cart.v1`. Il survit à un
rechargement et à un changement de langue sans serveur, sans cookie et sans
compte. Seule la commande finalisée quitte le navigateur.

**Chaque prix vient du balisage**, que `build.py` écrit depuis les fichiers de
contenu. Rien n'est inventé, arrondi ni converti dans le JavaScript, et un
format sans prix n'a pas de bouton « Ajouter » : personne ne peut mettre au
panier un article dont il découvrira le prix plus tard.

Vérifié dans Chromium : ajout, incrément, retrait, persistance après
rechargement, fermeture par Échap, piège de focus dans le tiroir, bascule
« retrait sur place » qui masque et dé-obligatoirise les champs d'adresse,
et le tiroir qui s'ouvre à gauche en arabe.

### Les 58 wilayas

`content/wilayas.json` — code, nom latin, nom arabe, zone. Généré avec une
assertion sur la continuité des codes 1 à 58 et l'unicité des noms.

Les **zones sont un découpage géographique de départ** (Ouest / Centre / Est /
Sud), pas votre grille de transport : ajustez l'appartenance des wilayas et
les quatre tarifs dans `shop.delivery.zones` selon ce que votre transporteur
vous facture réellement.

### Ce que le panier ne fait pas

Il ne **stocke** pas les commandes. À l'envoi, la commande part vers
`shop.checkout.endpoint` s'il est renseigné, sinon vers `mailto:`. Pour un
véritable historique de commandes il faut une fonction serveur (Netlify
Functions, Cloudflare Workers) et une base — ce n'est plus un site statique.

### Le paiement

**Paiement à la livraison, en espèces.** Aucun paiement en ligne : encaisser
par carte en Algérie passe par SATIM (CIB / Edahabia), ce qui exige un contrat
marchand et une intégration serveur.


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
