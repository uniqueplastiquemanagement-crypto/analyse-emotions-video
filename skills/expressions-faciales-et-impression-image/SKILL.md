---
name: "expressions-faciales-et-impression-image"
description: "Analyser ce qu'un visage montre et l'impression qu'une image dégage : photo, portrait, miniature, image de pub ou image tirée d'une vidéo. Indices visibles, lectures possibles, contexte, comparaison."
---

# Expressions du visage et impression d'une image

Sert à dire, sur une image fournie, ce qui est réellement visible dans un visage, quelles expressions cette configuration peut évoquer, ce qui rend la lecture plus ou moins évidente, ce que le corps, le cadrage, la lumière et le décor y ajoutent, et quelles autres lectures restent possibles. Sert aussi à comparer plusieurs images et à proposer des ajustements pour mieux porter une intention créative.

À charger pour : une photo, un portrait, une miniature, une image de pub ou de marque, un choix entre plusieurs prises, et chaque fois que le skill `emotions-video-unique-plastique` lit une image où un visage compte.

Règles générales : skill `clarifier-avant-d-agir` avant une vraie tâche, skill `lien-pour-voir-et-tester` après toute création ou modification.

## 1. Quatre niveaux à ne jamais mélanger

| Niveau | Ce que c'est | Comment l'écrire |
|---|---|---|
| A. Observation | Ce qu'on voit : sourcils, paupières, joues, lèvres, tête, regard, épaules, mains, lumière, cadrage | Au présent, sans émotion : « commissures remontées, dents visibles » |
| B. Expression apparente | Une lecture de cette configuration par un observateur | « donne une apparence joyeuse », toujours reliée aux indices |
| C. Impression de l'image | L'effet possible sur un public, visage + composition + contexte | Une hypothèse tant qu'un vrai public ne l'a pas notée |
| D. Émotion intérieure | Ce que la personne ressent vraiment | Une photo ne l'établit pas. Ne jamais conclure là-dessus |

Pourquoi : la revue de Barrett et coll. (2019) montre que le lien entre une configuration du visage et un état intérieur est peu fiable et peu spécifique, et qu'il change selon la situation, la personne et la culture. Dire « un sourire » est une observation ; dire « de la joie » est déjà une lecture.

Quatre natures de chiffres, à ne jamais confondre non plus : des votes d'observateurs humains, le score d'un classificateur, une estimation qualitative de Claude, une mesure calibrée et validée. Une lecture faite en regardant l'image est la troisième. Ne jamais lui donner l'allure des autres (pas de « 72 % de joie »).

## 2. La méthode

### A. Vérifier l'image
Netteté, taille du visage dans l'image, angle, éclairage, masquages (lunettes, main, cheveux, masque, texte incrusté), flou de mouvement, déformation du grand-angle, retouche possible. Dire en une ligne quelles régions sont lisibles et lesquelles ne le sont pas. Plusieurs visages : repères neutres (« personne à gauche », « personne au premier plan »). Ne jamais chercher qui c'est, ne nommer personne.

### B. Décrire les indices, région par région
- sourcils et front ;
- paupières : ouverture, tension apparente ;
- joues et plis visibles ;
- nez et sillon entre le nez et la bouche ;
- commissures, lèvres, ouverture de la bouche, mâchoire ;
- tête : orientation, inclinaison ;
- symétrie apparente ;
- regard : vers la caméra, vers un objet visible, hors champ ;
- posture, épaules, mains, rapport à l'objet et au décor.

Sur une image fixe, décrire une configuration, pas un mouvement. Une paupière fermée peut être un clignement saisi au vol. Une bouche ouverte accompagne souvent la parole : si la personne parle (sous-titre à l'écran, paroles connues), le dire et ne pas lire la bouche comme de la surprise. Une caméra en plongée fait lever le regard et les sourcils sans que ça exprime quoi que ce soit.

### C. Unités d'action (AU), avec prudence
Les AU du système FACS décrivent des mouvements visibles, pas des émotions. En proposer seulement quand ça ajoute de la précision, avec : le nom, l'indice vu, l'ambiguïté, et la provenance (« lecture visuelle de Claude » ou « sortie de tel outil, telle version »). C'est indicatif : aucune certification FACS, aucune intensité chiffrée, aucun code forcé sur une région floue ou masquée.

| AU | Ce qu'on voit | Se confond avec |
|---|---|---|
| 1, 2 | sourcils remontés (intérieur, extérieur) | emphase en parlant, regard vers le haut, caméra en plongée |
| 4 | sourcils abaissés et rapprochés | concentration, soleil, effort, lecture d'un texte |
| 5 | paupière supérieure relevée, œil plus ouvert | grand-angle, regard vers le haut |
| 6 | joues remontées, plis au coin des yeux | soleil, rire, effort |
| 7 | paupières tendues, œil rétréci | lumière forte, myopie |
| 9, 10 | nez plissé, lèvre supérieure relevée | odeur, effort, début de rire |
| 12 | commissures tirées vers le haut | sourire de pose, politesse |
| 14 | commissure serrée, fossette | moue, hésitation |
| 15 | commissures abaissées | visage au repos chez certaines personnes |
| 17 | menton remonté | moue, parole |
| 20 | lèvres étirées à l'horizontale | parole, froid |
| 23, 24 | lèvres serrées, pressées | effort, retenue, concentration |
| 25, 26, 27 | lèvres entrouvertes, mâchoire abaissée, bouche grande ouverte | parole, respiration, chant, cri |
| 43, 45 | yeux fermés, clignement | instant saisi au vol |

Ces noms sont ceux d'usage courant. Le manuel FACS est payant : le citer comme référence, ne pas en reconstituer le contenu. Les 52 coefficients de MediaPipe (blendshapes) ne sont pas des AU ; la correspondance est approximative.

### D. Interpréter
Une lecture principale et, si l'image le justifie, une ou deux autres. Pour chacune : les indices qui la portent, les indices qui la fragilisent. Décrire en mots la valence apparente (agréable ou désagréable), l'activation (calme ou vive) et l'intensité expressive quand ça aide. Donner deux confiances séparées : dans l'observation (ce qu'on voit bien ou mal) et dans l'interprétation (ce que ça veut dire).

Privilégier les mélanges aux étiquettes uniques : quand dix personnes notent le même visage, elles ne s'entendent souvent pas (FER+), et beaucoup d'expressions réelles sont composées (RAF-ML).

### E. L'image entière
Cadrage et distance (gros plan, plan large), angle (plongée, contre-plongée), lumière et couleurs, décor, objets, corps, autres personnes, texte à l'écran. Dire ce que le contexte ajoute au visage ou ce qu'il change. Dans l'étude d'Aviezer et coll. (2012), pour des émotions très intenses, des observateurs distinguaient le positif du négatif à partir du corps seul mais pas à partir du visage seul : le visage se lit avec le reste.

Conseils pour une pub, une miniature, un portrait : des changements concrets liés à l'intention (rapprocher le cadrage, tourner le regard vers la caméra ou vers le produit, dégager la bouche, changer l'angle, choisir l'image juste avant ou juste après). Ne jamais prédire un taux de clic ni une réaction universelle sans données.

### F. Comparer plusieurs images
La même grille pour chacune, puis un tableau : observations, expression apparente, contexte, autre lecture possible, adéquation à l'intention donnée. Sans intention donnée, décrire les différences sans en inventer une.

## 3. Limites fermes

- Aucun diagnostic psychologique ou médical.
- Aucune conclusion sur la personnalité, l'honnêteté, la moralité, les intentions cachées. Pas de détecteur de mensonge.
- Aucune déduction d'origine, de religion, d'orientation sexuelle ou d'un autre attribut sensible.
- Aucun pourcentage d'émotion inventé.
- Un sourire ne prouve pas une émotion sincère.
- Pas de « micro-expression » sur une image fixe, ni sur une vidéo lue à une image par seconde : il faut une vidéo à cadence élevée et un protocole.
- Ne jamais dire qu'un outil a mesuré quelque chose s'il n'a pas tourné.
- Ne jamais évoquer une photo d'une banque d'images qu'on n'a pas ouverte.
- Une étude ne prouve pas que la lecture d'une nouvelle image est juste.
- Image peu lisible : continuer sur les régions exploitables et dire en une phrase ce qui reste indéterminé.

Ces limites servent à mieux analyser. Les appliquer sans les réciter : une phrase suffit quand une limite joue, rien quand elle ne joue pas.

## 4. Format de la réponse

Toujours commencer par deux ou trois phrases : l'impression principale et les indices qui la portent le plus. Exemple de formulation (ne décrit aucune photo réelle) : « Les commissures remontées et les joues relevées donnent à l'expression une apparence joyeuse. Le regard hors champ et la bouche entrouverte permettent aussi de lire un instant de conversation. »

Si une analyse approfondie est demandée, poursuivre avec :
1. tableau des indices : région, observation, lecture possible, limite ;
2. AU, seulement si elles apportent quelque chose ;
3. lecture principale et autres lectures ;
4. ce que le contexte et la composition ajoutent ;
5. ce qui manque pour trancher (une autre image, la vidéo, les paroles, l'intention) ;
6. recommandations créatives, si demandées ;
7. références de méthode réellement utilisées, pas une liste pour faire sérieux.

Français du Québec, tutoiement avec Alexandre, phrases courtes.

## 5. Deux modes

**Vision seule (par défaut, complet).** Claude regarde l'image et applique la méthode. Les AU sont des hypothèses visuelles, à dire comme telles.

**Assisté par un outil (facultatif, rien n'est installé).** Avant d'installer quoi que ce soit sur le Mac, demander l'accord d'Alexandre. Licences relevées le 20 nov. 2026, à relire chez le fournisseur avant tout usage :

| Outil | Ce qu'il sort | Pour une entreprise |
|---|---|---|
| MediaPipe Face Landmarker | 478 repères 3D, 52 coefficients de déformation, orientation de la tête | Seul candidat sans restriction commerciale relevée (exemples de code sous Apache 2.0). Lire la fiche du modèle avant usage |
| Py-Feat | AU, repères, scores d'expression | Code MIT, mais les poids récents ne sont pas offerts comme dégagés pour un usage commercial |
| OpenFace | repères, pose, AU, regard | Licence commerciale à demander à part |
| LibreFace | intensité de 12 AU, expressions | Licence de recherche, usage non commercial |
| DeepFace | 7 catégories d'expression | Code MIT ; chaque modèle enveloppé garde sa propre licence. Si utilisé : expression seulement, jamais identification, âge, genre ou origine |

Si un outil tourne : garder les sorties brutes, la version du modèle et la provenance ; couper tout ce qui identifie. Une sortie d'outil reste une estimation, pas une vérité sur l'état de la personne. Une banque d'images « recherche non commerciale » ne s'utilise pas directement dans une entreprise : on garde sa publication comme référence. Ajouter des références à ce skill ne réentraîne pas Claude.

## 6. Sur une vidéo et dans l'outil « Émotions d'une vidéo »

- L'outil lit une image par seconde : on y décrit des configurations, pas des transitions.
- Croiser avec les paroles que le moteur du Mac fournit : une bouche ouverte pendant une phrase est de la parole.
- Ce que la couche visage peut noter par seconde, en 12 mots au plus : présence et taille du visage, regard (caméra, objet, hors champ), bouche (fermée, sourire, ouverte en parlant, grande ouverte), sourcils, mains et objet.
- Ce que nos chiffres disent pour l'instant (193 vidéos TikTok, 20 nov. 2026) : dans les lectures à l'aveugle, la part des 5 premières secondes où une personne est décrite va légèrement contre la rétention à 5 s (−0,16), et les mots d'expression n'ont pas de lien net (−0,11, non significatif). Mesure grossière, par mots-clés. Donc : la couche visage sert à comprendre et à diriger une prise, pas à promettre de la rétention, tant qu'un test propre ne l'a pas montré.

## 7. Références détaillées (docs du projet « Unique Plastique Ads »)

- `technique/expressions-faciales-methode-et-references-2026-11-20.md` : ce que chaque étude permet de dire et sa portée, outils et licences, gabarits de rapport et de comparaison, 12 cas d'évaluation, essai réel. À lire avant une analyse approfondie ou avant d'installer un outil.
- `technique/expressions-faciales-sources-2026-11-20.md` : les 56 sources du catalogue, avec ce qui a été lu, ce qui a échoué et ce qui n'a pas été revérifié. À lire avant de citer une source ou de demander l'accès à une banque d'images.

Ne signer aucun accord et ne soumettre aucune demande d'accès au nom d'Alexandre. Ne pas contourner un accès restreint, ne pas passer par un miroir, ne pas télécharger de gros corpus.

## Journal

- 20 nov. 2026 : création à partir du prompt « expressions faciales, 56 sources ». Sources lues ce jour-là : Barrett 2019 (en partie), FER+, AffectNet, DISFA, EMOTIC (page du projet), résumés d'Aviezer 2012, de Jack 2012 et d'OASIS, licences de Py-Feat, OpenFace, LibreFace, DeepFace, MediaPipe. Un essai réel sur 12 images d'une de nos vidéos (lecture de Claude, non comparée à des annotations). Les 12 cas d'évaluation sont des scénarios de conception, pas encore joués. Aucun outil installé.