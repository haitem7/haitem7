# Polices — licences

Les quatre familles utilisées par le site sont sous **SIL Open Font
License 1.1**, qui autorise explicitement l'hébergement sur votre propre
serveur, l'intégration dans un site commercial et la redistribution.

| Famille | Auteur | Licence |
|---|---|---|
| Fraunces | Undercase Type (Phaedra Charles, Flavia Zimbardi) | OFL 1.1 |
| Geist | Vercel | OFL 1.1 |
| IBM Plex Sans Arabic | IBM | OFL 1.1 |
| Reem Kufi | Khaled Hosny | OFL 1.1 |

Les fichiers `.woff2` proviennent de l'API Google Fonts, qui sert ces
mêmes polices sous cette licence. Ils sont maintenant servis depuis
`assets/fonts/` : **aucune requête vers un tiers n'est faite pour afficher
une page**, et donc aucune adresse IP de visiteur n'est transmise.

Le texte complet de la licence : <https://openfontlicense.org>

## Sous-ensembles conservés

Seuls `latin`, `latin-ext` et `arabic` sont embarqués. Le site n'a pas de
version vietnamienne, russe ou grecque, et la règle `unicode-range` de
chaque `@font-face` fait que le navigateur ne télécharge que le fichier
dont il a besoin pour la page affichée.
