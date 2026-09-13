# Vidéos du site

Déposez les fichiers vidéo ici.

## Fichier attendu pour le hero

| Fichier | Rôle |
|---|---|
| `hero.mp4` | Fond animé du hero (H.264, sans piste audio) |
| `hero.webm` | Même vidéo en VP9/AV1 — optionnel, ~30 % plus léger |
| `hero-poster.jpg` | Image fixe affichée avant/à la place de la vidéo |

## Cible technique

- Durée : 6 à 12 secondes, bouclable sans coupure visible
- Résolution : 1920 × 1080 maximum (le hero est recadré, pas besoin de 4K)
- Poids : **3 Mo maximum**, 2 Mo de préférence
- Pas de piste audio (un fond muet n'en a pas besoin, et ça allège)
- Sujet lisible en miroir : la page arabe inverse la mise en page

## Ré-encodage

Depuis n'importe quel fichier source, pour tenir la cible ci-dessus :

```bash
ffmpeg -i source.mp4 \
  -an -t 10 \
  -vf "scale=1920:-2,fps=25" \
  -c:v libx264 -profile:v high -crf 28 -preset slow \
  -movflags +faststart \
  hero.mp4

# Image poster, extraite à la 1re seconde
ffmpeg -i hero.mp4 -ss 1 -vframes 1 -q:v 3 hero-poster.jpg

# Version WebM, optionnelle
ffmpeg -i hero.mp4 -an -c:v libvpx-vp9 -crf 36 -b:v 0 hero.webm
```

`-movflags +faststart` place les métadonnées en tête du fichier : la
lecture démarre avant la fin du téléchargement. Sans ça, la vidéo ne
s'affiche qu'une fois entièrement chargée.

## Attention au poids dans Git

Un fichier committé reste dans l'historique du dépôt pour toujours, même
supprimé ensuite. En dessous de 5 Mo, ce n'est pas un problème. Au-delà,
mieux vaut héberger la vidéo ailleurs (Cloudflare R2, Bunny, S3) et ne
garder ici que le poster.
