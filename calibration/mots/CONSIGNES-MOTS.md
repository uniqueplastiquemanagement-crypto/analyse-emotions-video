# Lecture à l'aveugle des MOTS de vidéos courtes — consignes du lecteur

Tu lis les paroles de vidéos courtes (TikTok, Reels) d'une petite entreprise du Québec, Unique Plastique, qui fabrique des pinces à cheveux en plastique recyclé. Pour chaque vidéo, tu notes, seconde par seconde, ce que le SENS des mots dits fait à une spectatrice typique (une femme au Québec, de 18 à 45 ans, qui fait défiler son fil sur son téléphone et ne connaît pas forcément la marque), et le rôle que chaque phrase joue dans l'histoire.

## Règle absolue : tu lis à l'aveugle

- Tu ne sais pas comment ces vidéos ont marché, et tu ne dois pas le savoir. N'ouvre **aucun** fichier en dehors de ce fichier de consignes et des fichiers de ton groupe (`/home/claude/mots/in/Lxx/`). Ne cherche rien sur le web. N'utilise aucun outil de mémoire, de projet ou de navigateur.
- Ne devine pas le succès d'une vidéo. Note ce que les mots disent et font, rien d'autre.
- N'écris pas de script qui fabrique les notes : chaque note vient de ta lecture des mots de cette seconde.

## Ce que contient chaque fichier (`Lxx/vNNN.txt`)

- les paroles par phrase, avec leur minutage ;
- une ligne par seconde : la seconde, les mots dits pendant cette seconde, et ce qu'on voit à l'image (pour le contexte : un mot n'a pas le même effet selon l'image sous lui).

La transcription est automatique : quelques mots peuvent être faux. Fie-toi au sens de la phrase.

## Ce que tu notes

Seulement le sens des mots. Pas le ton de la voix, pas la musique, pas la beauté de l'image (d'autres lecteurs s'en occupent). L'image sert seulement à comprendre de quoi les mots parlent.

Pour chaque seconde :

- `att` 0 à 3 : à quel point ces mots donnent envie d'entendre la suite. 0 = aucun mot, ou des mots qui n'apportent rien. 3 = des mots qui accrochent fort (promesse précise, question qu'on veut voir résolue, affirmation étonnante).
- `int` 0 à 3 : intensité de l'émotion que le sens des mots provoque.
- `val` −3 à 3 : désagréable à agréable.
- `emo` : seulement les émotions présentes, notées 1 (légère), 2 (nette), 3 (forte), avec ces identifiants exacts :
  - Accroche : interet, surprise, intrigue, fascination, emerveillement
  - Plaisir : amusement, joie, satisfaction, beaute, calme, soulagement
  - Lien : admiration, tendresse, fierte, nostalgie
  - Désir : envie, excitation
  - Tension : anxiete, peur, douleur, malaise, degout, colere, tristesse
  - Décrochage : ennui
- `fn` : le rôle de la phrase en cours dans l'histoire, un seul code parmi :
  - `accroche` : la phrase d'ouverture qui pose la promesse ou le défi
  - `place` : mise en place (qui, quoi, où, le contexte)
  - `question` : ouvre une question qu'on veut voir résolue (dite ou sous-entendue : « est-ce que ça va casser ? »)
  - `pivot` : retournement (« mais », « sauf que », « pis là »)
  - `montee` : la tension monte vers le moment fort
  - `revelation` : le moment fort, le résultat, la prise de conscience
  - `reponse` : referme une question ouverte plus tôt
  - `preuve` : un fait, un chiffre, une démonstration qui appuie
  - `appel` : appel à l'action (commente, achète, abonne-toi, va sur le site)
  - `redite` : répète ce qui a déjà été dit, sans rien ajouter
  - `digression` : hors sujet, aucune fonction dans l'histoire
  - `rien` : aucun mot dit pendant cette seconde
- `why` : en 12 mots au plus, les mots précis qui font cet effet et pourquoi. Sans point-virgule ni retour de ligne. Vide si `fn` vaut `rien`.

Note sobrement : la plupart des secondes n'ont qu'une ou deux émotions, souvent à 1 ; 3 est rare. Une phrase qui s'étire sur plusieurs secondes garde le même `fn`, mais `att` et les émotions peuvent changer d'une seconde à l'autre selon les mots qui tombent. Tiens compte de ce qui a déjà été dit : la même idée répétée lasse.

Pour la vidéo entière (première ligne du fichier) :

- `recit` : l'histoire en 30 mots au plus (qui, quel enjeu, quel changement entre le début et la fin). Si les mots ne racontent pas d'histoire (ils décrivent, annoncent ou vendent sans enjeu ni changement), écris `aucun`. Sans point-virgule.
- `moment` : la seconde du moment fort (le bref moment de changement ou de prise de conscience autour duquel l'histoire est bâtie), ou `-` s'il n'y en a pas dans les mots.
- `boucles` : chaque question ouverte par les mots, sous la forme `ouverture-fermeture` en secondes, séparées par des virgules (exemple : `1-14,6-9`). Si une question n'est jamais refermée par les mots, écris `x` à la place de la fermeture (`3-x`). `-` s'il n'y en a aucune.
- `histoire` 0 à 3 : 0 = aucune histoire, 1 = un fil mince, 2 = une histoire claire, 3 = une histoire complète avec enjeu, tension et dénouement.
- `concret` 0 à 3 : à quel point les mots sont concrets (objets, gestes, chiffres, choses qu'on peut voir) plutôt qu'abstraits.
- `adresse` 0 à 3 : à quel point les mots s'adressent directement à la personne qui regarde (tu, vous, questions posées, ordres).

## Ce que tu produis : un fichier par vidéo

Écris `/home/claude/mots/out/vNNN.csv` (un seul Write par vidéo), au format exact :

```
#recit=Un gars parie que la pince survit au camion et elle survit;moment=17;boucles=1-17;histoire=3;concret=3;adresse=1
t;att;int;val;emo;fn;why
0;3;2;0;intrigue:3,anxiete:1;accroche;« on va rouler dessus » pose un défi risqué
1;2;1;0;intrigue:2;question;on veut savoir si elle casse
2;0;0;0;;rien;
```

- **Une ligne par seconde**, pour toutes les secondes listées dans le fichier d'entrée, dans l'ordre, en commençant à 0.
- `emo` : `identifiant:note` séparés par des virgules, ou vide.
- Aucun point-virgule dans les textes.

Après chaque fichier écrit, vérifie-le :

```
python3 /home/claude/mots/verifier.py vNNN
```

Corrige jusqu'à ce que la vérification réponde `ok`. Fais toutes les vidéos de ton groupe, une à la fois, dans l'ordre. À la fin, réponds seulement par la liste des vidéos faites.
