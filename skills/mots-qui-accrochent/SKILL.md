---
name: "mots-qui-accrochent"
description: "Analyser les mots et le récit d'une vidéo d'Unique Plastique (émotion des mots, histoire, boucles, trous) et suggérer quoi déplacer, ajouter ou dire en voice-over, sans rien inventer."
---

# Les mots qui accrochent

Servir à Alexandre un check-up des mots d'une vidéo (paroles et texte à l'écran) : quelle émotion ils dégagent, s'ils racontent une histoire, s'ils suivent un patron reconnu par la recherche, ce qui manque dans le récit, puis des suggestions concrètes pour le montage ou un voice-over. Usages : montage avant publication, pub en cours, vidéo déjà publiée, script avant tournage.

Règles générales : skill `clarifier-avant-d-agir` avant toute vraie tâche ; skill `lien-pour-voir-et-tester` si une page est créée ou modifiée. Transcription, moteur du Mac et émotions seconde par seconde : skill `emotions-video-unique-plastique`. Toute phrase proposée pour un voice-over : skill `voix-alexandre`. Hook et rythme propres à TikTok : skill `tiktok-unique-plastique`.

## 1. La règle d'or : poser, puis suggérer, sans inventer

Demande d'Alexandre (20 nov. 2026) : « je veux pas qu'ils inventent ; juste poser la situation, puis décoder des suggestions de la suite narrative ».

- **Deux temps séparés.** D'abord le constat (ce qui est dit, quand, et ce que ça fait), ensuite les suggestions. Ne jamais mêler les deux.
- **Tout constat pointe vers une seconde et des mots exacts.** Pas de lecture « en général ».
- **Aucun fait inventé.** Pas de chiffre, d'anecdote, de résultat, de citation ni d'émotion que la vidéo ou les faits confirmés ne soutiennent pas. Les faits confirmés viennent de la vidéo elle-même, d'Alexandre ou du skill `unique-plastique-master`.
- **Un trou reste un trou.** Si le récit a besoin d'un fait qu'on n'a pas, on écrit le trou et la question à poser à Alexandre (« [à confirmer : combien de pots dans ce sac?] »). On ne le remplit jamais soi-même.
- **Un mot de transcription qu'on ne peut pas confirmer** se marque (?) : on ne bâtit pas d'analyse dessus.
- **Les patrons de la recherche sont des hypothèses.** On écrit « selon Loewenstein, une question ouverte tend à retenir », jamais « ça va pogner ». Dès que nos propres corrélations existent (section 7), elles passent avant la recherche générale.
- **On ne cite que les sources de la section 8.** Jamais une étude ou une statistique de mémoire.

## 2. Ce qu'il faut avant de commencer

1. **Les paroles minutées mot par mot** : `lire_paroles` du moteur du Mac (voir `emotions-video-unique-plastique`, section 2 bis), corrigées à la main selon ce skill (erreurs connues dans la voix d'Alexandre, sous-titres visibles sur les planches).
2. **Le texte à l'écran**, avec sa seconde (planches-contact).
3. **Ce qu'on voit à chaque seconde** : la description `desc` de l'analyse des émotions si elle est faite, sinon les planches. Un mot n'a pas le même effet selon l'image sous lui.
4. **Si la vidéo est publiée** : la courbe de rétention à la seconde (calibration). Elle permet de relier une phrase au décrochage.
5. **Le but de la vidéo** : faire partager, faire acheter, faire connaître l'usine, un drop. Demander s'il n'est pas clair.

## 3. Étape 1 : poser la situation

**Le récit en trois lignes** : qui, quel enjeu, quel changement entre le début et la fin. S'il est impossible à écrire, c'est déjà un constat : la vidéo montre, mais elle ne raconte pas.

**Le tableau du constat**, une ligne par phrase ou par moment :

| Seconde | Mots dits | Texte à l'écran | Ce qu'on voit | Fonction | Émotion des mots (et pourquoi) |
|---|---|---|---|---|---|

Fonctions possibles : accroche ; mise en place ; question ouverte (boucle) ; pivot (« mais », « sauf que », « pis là ») ; montée ; révélation (le moment de cinq secondes) ; réponse ; preuve ; appel à l'action ; redite ; digression (aucune fonction).

L'émotion des mots reprend les 25 émotions et la façon de noter du skill `emotions-video-unique-plastique` (section 4), avec un pourquoi concret pour chacune.

## 4. Étape 2 : lire avec les grilles

Pour chaque grille : ce qu'on cherche, et comment on le vérifie dans la transcription.

**A. Le moment de cinq secondes (Dicks).** Toute bonne histoire est construite autour d'un moment bref de changement ou de prise de conscience ; tout le reste sert à le mettre au foyer. Dans une vidéo de 30 à 60 s, c'est souvent la révélation (la pince intacte après le crash test, les pots qui deviennent des pinces). Vérifier :
- Y a-t-il un moment de ce genre? À quelle seconde?
- Le début est-il l'opposé de la fin? Chez Dicks, c'est ce qui rend le changement visible.
- Le moment est-il ralenti (le « sablier » : on étire le moment le plus important) ou passé trop vite?
- Les outils d'enjeu de Dicks sont-ils là? L'éléphant (on dit tôt de quoi parle l'histoire), les miettes (on laisse deviner ce qui s'en vient), la boule de cristal (une prédiction qui crée du suspense), le sac à dos (on annonce un plan, puis on regarde s'il tient).

**B. Les boucles de curiosité (Loewenstein, 1994).** La curiosité naît d'un trou perçu dans ce qu'on sait, et la personne reste pour le combler. Pour chaque question ouverte, dite ou implicite, noter la seconde où elle s'ouvre et celle où elle se ferme. Signaux :
- une boucle refermée trop tôt sans qu'une autre s'ouvre ;
- une boucle jamais refermée (frustration) ;
- une réponse qui arrive après la seconde où la rétention s'effondre.

C'est le principe derrière le hook d'Alexandre : on pose l'hypothèse, l'explication vient après.

**C. L'intensité des émotions (Berger et Milkman, 2012).** Le contenu qui active fort est plus partagé, que l'émotion soit positive (émerveillement) ou négative (colère, inquiétude) ; les émotions qui apaisent (tristesse) le sont moins. Repérer les phrases qui montent en activation et celles qui font retomber.

**D. L'arc par les petits mots (Boyd, Blackburn et Pennebaker, 2020).** Dans un récit, les mots changent d'un bout à l'autre :
- **mise en place** : beaucoup d'articles et de prépositions (« le », « un », « dans », « sur ») ;
- **progression** : plus de pronoms et de verbes (« il », « on », « ça ») ;
- **tension** : les mots de réflexion montent vers le point culminant (« penser », « croire », « savoir », « comprendre », « parce que », « pourquoi »).

Compter ces familles par tiers de la vidéo, en incluant les formes québécoises (« pis », « fait que », « genre »). Limite à dire : les auteurs n'ont trouvé aucun lien entre suivre cet arc et la popularité. On s'en sert pour répondre à « est-ce qu'il y a une histoire? », pas pour noter le succès.

**E. La vitesse du récit (Toubia, Berger et Eliashberg, 2021).** Ils mesurent à quelle vitesse une histoire passe d'une idée à l'autre ; pour les films et les séries, aller plus vite aide. Vérifier que chaque phrase apporte quelque chose de neuf. Signaler toute suite de deux phrases ou plus qui piétine ou se répète.

**F. Les mots eux-mêmes (Berger, *Magic Words*).** Vérifier :
- concret plutôt qu'abstrait (« une pince qui casse dans ton char » contre « un produit durable ») ;
- assurance plutôt qu'hésitation (les « je pense », « peut-être » qui affaiblissent une affirmation) ;
- questions posées à la personne qui regarde ;
- mots d'émotion.

## 5. Étape 3 : les trous du récit

Passer cette liste et noter seulement ce qui manque vraiment :
- **L'enjeu** : pourquoi la personne devrait-elle s'en soucier?
- **Le personnage** : qui vit l'histoire?
- **L'avant et l'après** : le changement est-il visible?
- **La preuve** : on le dit ou on le montre?
- **La révélation** : coupée, trop rapide, ou arrivée trop tôt?
- **Une boucle sans réponse.**
- **La conclusion du récit** : elle doit se faire avant la fin, parce que la fin de ses vidéos, c'est seulement le logo avec un petit ding.

Pour chaque trou : la seconde où il manque, la fonction qui manque, puis la matière disponible pour le combler (un plan déjà dans la vidéo, un fait confirmé), ou la question factuelle à poser à Alexandre.

## 6. Étape 4 : les suggestions

Du moins invasif au plus invasif :

1. **Déplacer** des mots ou des plans existants. Par exemple, l'explication après l'hypothèse, la révélation plus tard, l'enjeu plus tôt.
2. **Signaler une redite.** Ne jamais couper soi-même un moment où Alexandre parle (sa règle de montage). On le signale, il décide. Par défaut, proposer un plan d'appoint par-dessus sa voix.
3. **Ajouter du texte à l'écran** : proposer la formulation et la seconde. Il ajoute les captions lui-même à la fin.
4. **Voice-over** : une ou deux phrases au plus par trou, dans la voix d'Alexandre (skill `voix-alexandre`), bâties uniquement sur ce qui est dans la vidéo ou déjà confirmé. Tout fait manquant reste entre crochets [à confirmer]. Donner la seconde et le plan sous lequel elle tombe.

Chaque suggestion porte : la seconde, le geste, la grille qui la justifie (A à F), l'effet attendu (une hypothèse), et une confiance faible, moyenne ou forte. Cinq suggestions au plus, classées de la plus payante à la moins payante. Alexandre veut des suggestions franches qui le poussent : dire clairement laquelle on ferait en premier.

## 7. Ce que nos vidéos nous ont appris

Quand la calibration le permet, relever pour chaque vidéo :
- la seconde de la première boucle et celle de sa fermeture ;
- la présence du moment de cinq secondes et sa seconde ;
- le nombre de pivots et de redites ;
- la part de mots concrets ;
- la courbe des mots de tension.

On compare ensuite ces mesures à la rétention et aux partages. Les résultats vont dans le document de projet `technique/mots-qui-accrochent-apprentissages.md`, puis ici, seulement s'ils sont calculés, avec le nombre de vidéos derrière chaque chiffre.

*(Vide pour l'instant : aucun résultat calculé.)*

## 8. Livrer

Dans le chat, en français du Québec, au tutoiement :
1. Le récit en trois lignes.
2. Le tableau du constat, condensé.
3. Ce qui marche déjà, avec les secondes.
4. Les trous.
5. Les suggestions classées.
6. Les questions factuelles à confirmer par Alexandre.

## 9. Sources (les seules à citer)

- Matthew Dicks, *Storyworthy: Engage, Teach, Persuade, and Change Your Life Through the Power of Storytelling*, 2018. Record de 64 StorySLAM de The Moth gagnés.
- George Loewenstein, « The Psychology of Curiosity: A Review and Reinterpretation », *Psychological Bulletin*, 116(1), 75-98, 1994.
- Jonah Berger et Katherine L. Milkman, « What Makes Online Content Viral? », *Journal of Marketing Research*, 49(2), 192-205, 2012.
- Ryan L. Boyd, Kate G. Blackburn et James W. Pennebaker, « The Narrative Arc: Revealing Core Narrative Structures Through Text Analysis », *Science Advances*, 6(32), eaba2196, 2020.
- Olivier Toubia, Jonah Berger et Jehoshua Eliashberg, « How Quantifying the Shape of Stories Predicts Their Success », *PNAS*, 118(26), e2011695118, 2021.
- Jonah Berger, *Magic Words: What to Say to Get Your Way*, HarperBusiness, 2023.