# Ce qu'il reste à photographier

Trois emplacements attendent une image, et une quatrième doit remplacer un
provisoire. Tout peut être fait au téléphone : la photo de ton moulin déjà
en ligne le prouve — c'est la plus crédible du site précisément parce
qu'elle n'est pas mise en scène.

## Photographier plutôt que capturer une vidéo

Une photo de téléphone fait 4000 pixels de large. Une image extraite d'une
vidéo 1080p en fait 1920, avec du flou de mouvement en prime. À qualité
égale de sujet, la photo gagne toujours.

Si tu n'as que de la vidéo : filme en 4K si l'appareil le permet, pose le
téléphone sur un support, et **ne bouge pas** pendant le plan. Envoie-moi
le fichier, j'extrais les images moi-même — je choisirai les plus nettes.

## Les quatre prises

| Fichier attendu | Sujet | Cadrage |
|---|---|---|
| `harvest.jpg` | Cueillette : des mains sur la branche, des olives vertes, un couffin. **Remplace `harvest-placeholder.jpg`, qui n'est pas à nous.** | Vertical |
| `tanks.jpg` | Les cuves de stockage, vue d'ensemble de la salle | Vertical |
| `loading.jpg` | Palettes, cartons, chargement. Un conteneur ou un camion si possible. | Vertical |
| `mill-2.jpg` | Une deuxième vue de l'atelier : le broyeur, le malaxeur, ou la ligne de remplissage | Vertical |

**Vertical**, pas horizontal : les emplacements du site sont en portrait
4:5. Une photo horizontale sera recadrée et tu perdras les bords.

## Quatre règles qui font toute la différence

1. **Lumière du jour.** Près d'une porte ou d'une fenêtre. Pas de flash :
   il écrase le relief et fait briller l'inox.
2. **Nettoie le champ.** Un bidon vide, un carton éventré ou un chiffon au
   sol, et l'acheteur voit une installation négligée. C'est le détail qui
   coûte le plus cher sur ce genre de photo.
3. **Ne mets pas en scène.** Les mains au travail, la machine qui tourne.
   Une pose figée se voit et affaiblit l'image.
4. **Plusieurs prises du même sujet.** Envoie-en cinq, j'en garde une.

## Pour me les envoyer

```bash
cp harvest.jpg tanks.jpg loading.jpg assets/img/
git add assets/img/ && git commit -m "Add mill photographs" && git push
```

Envoie les fichiers **originaux**, pas des captures d'écran ni des images
passées par WhatsApp : la compression y détruit le détail, et je ne peux
pas le récupérer.


## Depuis l'ouverture de la boutique

La page boutique affiche cinq formats et **une seule photo** : le 1 litre.
Les quatre autres cartes sont typographiques. Ça tient, mais une carte
produit sans photo se vend moins bien qu'une carte avec.

| Fichier attendu | Sujet |
|---|---|
| `bottles-250.jpg` | La bouteille 250 ml, seule, de face |
| `bottles-500.jpg` | La bouteille 500 ml, seule, de face |
| `bottles-750.jpg` | La bouteille 750 ml, seule, de face |
| `bottles-5l.jpg` | Le bidon 5 litres, seul, de face |

**Même lumière, même fond, même distance pour les cinq.** Posées côte à côte
sur la grille, cinq photos prises dans cinq conditions différentes se voient
immédiatement et font amateur. Une table près d'une fenêtre, un drap blanc
derrière, le téléphone sur une pile de livres : ça suffit.

Le cadrage est vertical (4/5), la bouteille centrée, un peu d'air au-dessus
et en dessous. Envoie-les, je les recadre et je les intègre — il suffit
ensuite de renseigner `img` dans `shop.catalog.items`.
