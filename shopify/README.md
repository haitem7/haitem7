# Thème Shopify — TLEMCENYA

Thème Online Store 2.0 qui reprend la boutique du site statique : même
design, mêmes polices auto-hébergées, mêmes textes en **français, anglais
et arabe (RTL)**. La seule différence : le panier et la commande sont ceux
de Shopify.

```
shopify/
  tlemcenya-theme.zip   ← le thème, prêt à téléverser
  products.csv          ← les 5 formats, à importer (en brouillon)
  theme/                ← les sources du thème (Liquid, JSON, JS)
  src/shopify.css       ← le CSS propre à Shopify
```

## Installer

1. **Thème** — Boutique en ligne › Thèmes › Ajouter un thème ›
   *Téléverser un fichier zip* › `shopify/tlemcenya-theme.zip`.
   Aperçu, puis *Publier*.
2. **Produits** — Produits › Importer › `shopify/products.csv`.
   Les cinq formats arrivent **en brouillon, à 0 DA**. C'est voulu (voir
   plus bas). Pour chacun : ajoutez la photo, saisissez le prix réel, le
   poids, puis passez-le en *Actif*.
3. **Langues** — Paramètres › Langues : ajoutez l'anglais et l'arabe,
   puis *Publier*. Le thème est déjà traduit ; le sélecteur de langue
   apparaît tout seul dans l'en-tête et le pied de page, et l'arabe passe
   en droite-à-gauche. Les titres et descriptions de **produits** se
   traduisent avec l'app gratuite *Translate & Adapt*.
4. **Paiement à la livraison** — Paramètres › Paiements › Moyens de
   paiement manuels › *Paiement à la livraison (COD)*.
5. **Livraison** — Paramètres › Expédition et livraison : créez une zone
   Algérie et vos tarifs. Pour le retrait sur place, activez
   *Retrait en magasin* sur le site « Huilerie, route nationale N7 ».
   Les tarifs affichés sur la page d'accueil (section *Livraison et
   paiement*) sont indicatifs : **gardez-les identiques** à ceux-ci.
6. **Coordonnées** — Thème › Personnaliser › Paramètres du thème ›
   *Coordonnées* : téléphone (le bouton WhatsApp n'apparaît qu'une fois un
   vrai numéro saisi) et e-mail.
7. **Mentions légales** — Paramètres › Politiques : confidentialité, CGV,
   remboursement, mentions légales. Le pied de page les liste
   automatiquement. Le contenu des pages `legal/`, `privacy/` et `terms/`
   du site statique peut y être recopié.

## Ce qui est repris du site statique

| Site statique | Shopify |
|---|---|
| Hero « champ d'huile » + vidéo optionnelle | Section *Hero* (vidéo ou image au choix, chargement conditionnel conservé) |
| Boutique, 5 formats | Section *Boutique — formats* (tous les produits, ou une collection) |
| Livraison, 4 zones, 58 wilayas | Section *Livraison et paiement* (tarifs dans les réglages) |
| L'huilerie | Section *L'huilerie — photos* (jusqu'à 3 photos) |
| Nous trouver, GPS, Maps / Waze | Section *Nous trouver* |
| Panier en `localStorage` | Tiroir panier Shopify (API AJAX), même apparence |
| Formulaire de commande + `mailto:` | Checkout Shopify |
| Procédé (page export) | Section *Procédé*, masquée par défaut, activable dans l'éditeur |

En plus : fiche produit, collection, recherche, page panier (fonctionne
sans JavaScript), compte client, blog, page 404, page mot de passe,
carte-cadeau.

## Règles gardées

- **Aucun prix inventé.** Un produit à 0 s'affiche « Prix à définir » et
  son bouton reste désactivé, sur la boutique comme sur la fiche. Les
  formats sans prix passent en fin de liste.
- **Pas de faux numéro.** Pas de bouton WhatsApp tant que le téléphone
  n'est pas renseigné.
- **Pas de photo qui n'est pas la vôtre.** `harvest-placeholder.jpg`
  n'est pas copiée dans le thème. `hero.mp4` porte un filigrane
  tryveo3.ai : ne la mettez pas dans la section Hero.
- Les chiffres « placeholder » listés dans le `README.md` principal
  restent à vérifier : ils sont dans les mêmes textes.

## Modifier les textes

Les textes viennent de `content/{fr,en,ar}.json`, comme pour le site
statique. Deux façons :

- **Dans Shopify** : Thèmes › … › *Modifier le contenu par défaut*, langue
  par langue. Ou, section par section, les champs *Titre* / *Chapeau* de
  l'éditeur (vide = texte traduit).
- **Dans le dépôt** : modifiez `content/*.json`, puis

  ```
  python3 build_shopify.py        # ou : npm run shopify
  ```

  et re-téléversez le zip. Attention : cela écrase les modifications faites
  dans *Modifier le contenu par défaut*.

## Pour les développeurs

`build_shopify.py` ne touche pas au Liquid : il copie `assets/css/site.css`
(fonts à plat, pour le CDN Shopify) + `src/shopify.css` dans
`theme/assets/theme.css`, copie polices et photos, génère `theme/locales/`
depuis `content/`, vérifie que les trois langues ont les mêmes clés et que
toute clé `| t` du Liquid existe, génère `products.csv` et le zip.

Après modification du CSS du site : `npm run css` puis `npm run shopify`.

Vérifié : `theme-check` (Shopify) sans erreur ni avertissement ; rendu
local du Liquid (données fictives) contrôlé dans Chromium en FR et AR, sur
ordinateur et téléphone, sans débordement horizontal. Le thème n'a pas
encore tourné sur une vraie boutique : faites un aperçu avant de publier.

Développement en direct avec la CLI Shopify :

```
cd shopify/theme
shopify theme dev --store votre-boutique.myshopify.com
```
