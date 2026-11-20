# Analyse des émotions d'une vidéo, seconde par seconde

Outil bâti par Unique Plastique (Lévis) avec Claude. On dépose une vidéo courte (TikTok, Reel, pub) et on obtient, pour chaque seconde, ce qu'elle fait ressentir à l'image, au son et dans les mots, la courbe du récit, un pronostic de montage et un pari de viralité.

Dépôt public. État au 20 novembre 2026.

## Ce qu'il y a dedans

| Dossier | Contenu |
|---|---|
| `page/` | La page « Émotions d'une vidéo » : `index.html`, `qips.js` (mesures d'image), `pari.js` (modèle du pari). Elle se publie comme artefact dans Claude. |
| `moteur/` | Le moteur à installer sur un Mac : transcription des paroles (Whisper large-v3-turbo), bruits et musique (earshot), mesures d'image (Aesthetics Toolbox). Il tourne en local ; rien ne quitte le Mac. |
| `skills/` | Les trois skills qui disent à Claude comment se servir de tout ça. Versions prêtes à téléverser dans `skills/zip/`. |
| `calibration/` | Les scripts et les consignes qui ont servi à relier les lectures aux vraies statistiques (corrélations, entraînement du pari). Sans aucune donnée. |
| `tests/` | Le banc d'essai de la page (navigateur sans écran, faux Claude, faux moteur). Chemins à adapter. |

## Ce qu'il faut

- Un abonnement Claude payant et l'app Claude de bureau.
- Pour le son, les mots et la courbe du récit : un Mac à puce Apple, environ 5 Go libres, une connexion pour télécharger les modèles (environ 3 Go).
- Sans Mac à puce Apple, la page lit seulement les images.

## Installer

### 1. Le moteur (Mac)

1. Copie le dossier `moteur/` où tu veux sur ton Mac (par exemple `~/Claude/analyse-video`).
2. Double-clique `Installer.command`. Si macOS refuse : clic droit, puis Ouvrir.
3. Laisse tourner (10 à 20 minutes). L'installateur télécharge Python, les bibliothèques, les modèles et le Aesthetics Toolbox, fait un essai, puis ajoute le connecteur `analyse-video` à la configuration de l'app Claude (avec une copie de sauvegarde).
4. Quitte l'app Claude (Cmd+Q) et rouvre-la.

Le détail de ce que l'installateur touche est dans `moteur/LISEZ-MOI.txt`.

### 2. Les skills

Dans Claude : Personnaliser, puis Skills, puis ajouter un skill par téléversement. Téléverse les trois fichiers de `skills/zip/`.

### 3. La page

Dans l'app Claude de bureau, ouvre une conversation, joins les trois fichiers de `page/` et écris :

> Publie ces trois fichiers comme un artefact (index.html, qips.js, pari.js). Déclare ses capacités : `sample` avec images, et `mcp` vers le serveur local `host:analyse-video` avec les outils `ecouter_deposer` et `ecouter_resultat`.

Ouvre ensuite l'artefact dans l'app Claude du Mac où le moteur est installé, et dépose une vidéo. À la première utilisation, la page demande la permission d'utiliser Claude et le moteur.

### 4. Premier essai

Dépose un MP4 ou un MOV de moins de 3 minutes. Tu dois voir, dans l'ordre : les images extraites, les émotions lues, la ligne « Son » qui avance (envoi, transcription, bruits et musique, lecture du son, lecture des mots), puis les sections Images, Son, Mots et Image + son.

## À savoir avant de tester

- **Le pari de viralité est calé sur Unique Plastique.** Il a été entraîné sur 193 vidéos TikTok d'un seul compte. Les niveaux, les vues estimées et la case « élan du compte » décrivent ce compte-là. Pour un autre compte, c'est un classement indicatif, pas un estimé. Les scripts de `calibration/` permettent de refaire l'entraînement avec ses propres vidéos et ses propres statistiques.
- **Les consignes nomment la marque.** La page dit à Claude que la vidéo vient d'Unique Plastique et s'adresse à une femme au Québec de 18 à 45 ans. Pour une autre marque, il faut changer ces phrases dans `page/index.html` (fonctions `prompt`, `promptSon`, `promptMots`).
- **Les émotions sont une lecture de Claude**, pas une mesure sur de vraies personnes. Les corrélations sont des corrélations, pas des causes.
- **Pas encore vérifié sur un autre compte.** Tout a été bâti et essayé sur un seul abonnement et un seul Mac. La publication de la page et son branchement sur le moteur depuis un autre compte restent à confirmer par le premier essai.
- **La transcription est faite pour le français du Québec et l'anglais.** Elle se corrige dans l'onglet Mots, puis « Refaire l'analyse avec mes corrections ».

## Ce que le dépôt ne contient pas

Aucune vidéo, aucune transcription, aucune statistique brute de compte, aucune clé. Le Aesthetics Toolbox, earshot et les modèles ne sont pas copiés ici : l'installateur les télécharge chez leurs auteurs, chacun sous sa propre licence.

## Composants tiers

- Aesthetics Toolbox : Redies, Bartho et coll., `github.com/rbartho/aesthetics-toolbox`
- earshot : `github.com/Leonxlnx/earshot`
- mlx-whisper et le modèle `mlx-community/whisper-large-v3-turbo`
- uv (Astral), ffmpeg (via static-ffmpeg)

## Droits

© Unique Plastique inc. Tous droits réservés : aucune licence de réutilisation n'est accordée pour l'instant. Les composants tiers gardent leur propre licence.
