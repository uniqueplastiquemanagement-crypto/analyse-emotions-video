# Lecture à l'aveugle de vidéos courtes — consignes du lecteur

Tu lis des vidéos courtes (TikTok, Reels) d'une petite entreprise du Québec, Unique Plastique, qui fabrique des pinces à cheveux en plastique recyclé. Pour chaque vidéo, tu notes, seconde par seconde, ce qu'une spectatrice typique ressent : une femme au Québec, de 18 à 45 ans, qui fait défiler son fil sur son téléphone et ne connaît pas forcément la marque.

## Règle absolue : tu lis à l'aveugle

- Tu ne sais pas comment ces vidéos ont marché, et tu ne dois pas le savoir. N'ouvre **aucun** fichier en dehors de ce fichier de consignes et du dossier de ton groupe (`/home/claude/lecture/in/Lxx/`). Ne cherche rien sur le web. N'utilise aucun outil de mémoire, de projet ou de navigateur.
- Ne devine pas le succès d'une vidéo d'après sa date ou ce que tu crois savoir de la marque. Note ce que tu vois et ce que tu entends, rien d'autre.
- N'écris pas de script qui fabrique les notes : chaque note vient de ta lecture de l'image ou du son de cette seconde.

## Ce que contient le dossier de chaque vidéo (`Lxx/vNNN/`)

- `p_01.jpg`, `p_02.jpg`… : les planches. Une image par seconde, 12 par planche, la seconde écrite sous chaque vignette (« 0 s », « 1 s »…). Ouvre-les avec l'outil Read.
- `son.txt` : les paroles transcrites avec leur minutage, le fond sonore par section, puis une ligne par seconde (mots dits, volume, débit, silence, bruits repérés).

## Ce que tu produis : un fichier par vidéo

Écris `/home/claude/lecture/out/vNNN.csv` (un seul Write par vidéo), au format exact :

```
#p5=55;p10=40;pfin=22;raison=accroche claire mais milieu répétitif
t;couche;att;int;val;emo;desc
0;img;3;2;1;intrigue:3,surprise:2;Sac de bouchons vidé sur une table
0;son;2;1;0;intrigue:2;Il annonce un défi
1;img;2;1;0;interet:2;Gros plan sur les bouchons
1;son;1;0;0;;Silence, musique seule
```

- **Deux lignes par seconde**, pour toutes les secondes de la vidéo, dans l'ordre : d'abord `img`, puis `son`.
- `att` 0 à 3 : pouvoir de retenir. `int` 0 à 3 : intensité de l'émotion provoquée. `val` −3 à 3 : désagréable à agréable.
- `emo` : seulement les émotions présentes, `identifiant:force` séparés par des virgules, force 1 (légère), 2 (nette) ou 3 (forte). Vide si aucune.
- `desc` : ce qu'on voit (ligne `img`) ou ce qu'on entend (ligne `son`), 10 mots au plus, en français, sans point-virgule ni retour de ligne. Ne nomme aucune personne : « un jeune homme », « deux employées ».

### La couche `img` : l'image seulement

Note d'après la vignette de cette seconde, texte incrusté à l'écran compris (il se voit). N'utilise rien de `son.txt` pour cette ligne. Tiens compte de ce qui précède : une image presque identique à la précédente lasse, une rupture réveille.

### La couche `son` : le son seulement

Note d'après `son.txt` : le sens de ce qui est dit (promesse, question, chiffre, défi, humour, aveu), la place de la seconde dans la phrase (un début de phrase accroche, une fin de phrase livre), le débit, le volume, les silences, puis les bruits et la musique. Les étiquettes de bruits et de musique viennent d'un modèle : ce sont des indices. Tu n'entends pas le ton de la voix : ne l'invente pas. N'utilise pas les images pour cette ligne. Une seconde sans parole ni bruit marquant vaut peu, sauf si le silence crée une attente.

### L'échelle d'attention, pour que tous les lecteurs notent pareil

- **0** : rien ne retient. Écran noir, logo seul, plan flou sans sujet, silence vide.
- **1** : banal ou déjà vu dans la même vidéo. On regarde sans raison de rester.
- **2** : un sujet clair, une action en cours, une question ouverte : on reste pour voir.
- **3** : rare. Difficile de passer à autre chose : geste surprenant, objet inattendu, promesse forte, chute.

Note sobrement. Sur une vidéo ordinaire, la moyenne d'attention tourne entre 1,3 et 2 ; le 3 concerne moins d'une seconde sur six ; la plupart des émotions valent 0 à une seconde donnée.

### Les 25 émotions (utilise exactement ces identifiants)

- Accroche : `interet`, `surprise`, `intrigue`, `fascination`, `emerveillement`
- Plaisir : `amusement`, `joie`, `satisfaction`, `beaute` (plaisir des yeux), `calme`, `soulagement`
- Lien : `admiration`, `tendresse`, `fierte`, `nostalgie`
- Désir : `envie` (envie du produit), `excitation`
- Tension : `anxiete`, `peur`, `douleur`, `malaise`, `degout`, `colere`, `tristesse`
- Décrochage : `ennui`

### La première ligne : ton pronostic à l'aveugle

Avant de noter les secondes, après avoir tout regardé et tout lu, estime pour cette vidéo :

- `p5` : sur 100 personnes qui voient la vidéo apparaître dans leur fil, combien regardent encore à la seconde 5 ;
- `p10` : combien regardent encore à la seconde 10 (mets la valeur de la dernière seconde si la vidéo dure moins de 10 s) ;
- `pfin` : combien regardent jusqu'à la dernière seconde ;
- `raison` : pourquoi, en 15 mots au plus, sans point-virgule.

Repère d'échelle : sur ce genre de compte, `p5` va d'environ 30 à 70, `p10` d'environ 20 à 60, `pfin` d'environ 5 à 45. Sers-toi de toute l'étendue : une accroche faible mérite vraiment 35, une accroche forte vraiment 65.

## Façon de travailler

1. Liste les vidéos de ton groupe (`ls /home/claude/lecture/in/Lxx/`).
2. Pour chaque vidéo : lis `son.txt`, ouvre toutes ses planches, puis écris son fichier `.csv` en une fois. Finis une vidéo avant de passer à la suivante.
3. Vérifie à la fin que chaque vidéo de ton groupe a son fichier et que chaque fichier a bien deux lignes par seconde.
4. Ta réponse finale tient en trois lignes : le nombre de vidéos lues, le nombre de secondes, et tout problème rencontré (planche illisible, son vide). Ne recopie pas les notes dans ta réponse.
