---
name: "emotions-video-unique-plastique"
description: "Analyser les émotions qu'une vidéo dégage seconde par seconde, à l'image, au son et dans les mots (moteur sur le Mac d'Alexandre, outil où déposer la vidéo, pronostic, pari de viralité). Charge pour tester un montage, une pub ou un Reel."
---

# Émotions d'une vidéo, seconde par seconde

Servir à Alexandre une lecture image par image d'une vidéo : ce qu'elle fait ressentir, quand, et ce que ça laisse prévoir sur les réseaux (accroche, tenue, partages, fin). Trois usages : un montage avant publication (export CapCut), une pub Meta en cours, une vidéo TikTok ou Reel déjà publiée.

Règles générales à appliquer : skill `clarifier-avant-d-agir` avant toute vraie tâche, skill `lien-pour-voir-et-tester` après toute page créée ou modifiée. Pour juger un hook ou un rythme de montage, s'appuyer sur `tiktok-unique-plastique`. Dès qu'un visage compte dans une image, appliquer le skill `expressions-faciales-et-impression-image`. Pour analyser les mots et le récit (histoire, boucles, trous, suggestions de voice-over), appliquer le skill `mots-qui-accrochent`.

## 1. Ce que ça mesure, et ce que ça ne mesure pas

- **Le Aesthetics Toolbox ne mesure pas des émotions.** Il calcule des propriétés physiques de l'image (contraste, entropie, couleur, équilibre, symétrie, pente de Fourier, fractalité, similarité, etc.). Source : Redies, Bartho et coll., Behavior Research Methods, 2025 ; dépôt `github.com/rbartho/aesthetics-toolbox`. Ne jamais écrire qu'une mesure du Toolbox « est » une émotion.
- **Les émotions sont une lecture faite par Claude** en regardant une image par seconde. Ce n'est pas une mesure sur de vraies personnes.
- **Trois sections** (demande d'Alexandre, 19 nov. 2026) : Images (ce que l'œil voit, sans le son), Son (ce qui est dit et comment c'est dit), Les deux (à chaque seconde, le plus fort de l'image et du son, avec l'origine de chaque émotion). Le texte incrusté dans l'image compte comme image.
- **Chaque émotion porte son pourquoi** (demande d'Alexandre) : ce qui, dans l'image ou dans la phrase, la provoque. Au survol ou au clic d'un bloc, la page l'affiche. Ne jamais noter une émotion sans sa raison concrète.
- **Paroles en québécois : il faut un gros modèle.** Test du 19 nov. 2026 sur trois vidéos d'Alexandre : Whisper « small » (375 Mo) rend « on va les recycler en pinces à cheveux » par « on va les restreiner en point de sachefe » ; Whisper « turbo » (1 Go) sort presque tout juste. Ne pas utiliser un petit modèle pour sa voix.
- **Le pronostic est une hypothèse** (V1 sans calibration, choix d'Alexandre). Toujours l'étiqueter ainsi ; ne promettre aucun chiffre de vues, de partages ou de ventes.

## 2. Chemin A : l'outil où déposer la vidéo (par défaut)

Page « Émotions d'une vidéo » : https://claude.ai/artifact/AgPz4DcwBC2bsZSb4k19ty (slug `4e626b4f-e0b0-4f2c-a0f4-5bbdbdacb676`, fichiers `index.html`, `qips.js` et `pari.js`, capacités déclarées `sample` avec images et `mcp` vers le connecteur local `host:analyse-video`, outils `ecouter_deposer` et `ecouter_resultat`).

Alexandre y dépose un MP4 ou un MOV. Dans son navigateur, la page :
1. prend une image par seconde (côté long 512 px) et quatre petites images par seconde pour le mouvement et les coupes (méthode du dérush, coupe si la différence moyenne dépasse 30 sur 255) ;
2. calcule 12 mesures du Toolbox, portées en JavaScript et vérifiées identiques au code Python sur 15 images test (écart relatif maximal 5e-7) : contraste RMS, entropie de luminosité, entropie de couleur, moyennes L*, a*, b*, S, V, Balance, DCM, symétrie miroir, homogénéité ;
3. envoie les images à Claude par lots de 8, avec la seconde inscrite dans une bande noire sous l'image, et reçoit la note de chaque seconde ;
4. dessine les pistes au fur et à mesure, calcule quatre repères, puis fait écrire un pronostic court ;
5. calcule les mesures du son sur la piste audio (volume en dB, débit en attaques par seconde, part de silence), même calcul que le script du chat.

Les trois sections se choisissent en haut des pistes.

**Le son en dépôt direct (depuis le 19 nov. 2026 au soir).** La page compresse le son de la vidéo en Opus (48 kHz mono, environ 300 ko la minute ; secours en PCM 16 kHz par morceaux de 450 ko si le navigateur n'a pas d'encodeur Opus) et l'envoie au moteur du Mac par `ecouter_deposer`. Elle suit ensuite `ecouter_resultat` : les paroles arrivent d'abord (ligne Paroles), puis les bruits et la musique d'earshot (ligne « Bruits et musique »). Claude lit alors les émotions du son par tranches de 20 secondes (texte seulement : mots dits, volume, débit, silences, indices de bruits), la page passe à « Les deux » et écrit un pronostic par section. Le son ne quitte pas le Mac et il est effacé du disque à la fin de l'écoute.

Conditions à rappeler à Alexandre quand le son ne vient pas : la page doit être ouverte dans l'app Claude du Mac (dans un navigateur ou sur le téléphone, le moteur n'est pas joignable et la page garde seulement les mesures du son) ; l'app doit avoir été redémarrée (Cmd+Q) depuis la dernière retouche de `serveur.py` ; au premier dépôt la page demande la permission d'utiliser le moteur, et l'app peut demander de confirmer l'envoi ; le bouton « Réessayer le son » relance sans redéposer la vidéo. La ligne « Son » sous la vidéo dit où ça en est et pourquoi ça bloque.

Limites à dire : Claude n'entend pas le ton de la voix ; la transcription se trompe sur quelques mots ; les étiquettes de bruits sont des indices en anglais.

Limites à dire quand elles jouent : 180 premières secondes au plus ; la première lecture demande à Alexandre d'autoriser la page à utiliser Claude ; un MOV HEVC d'iPhone peut ne pas se lire dans Chrome (exporter en MP4 H.264 ou ouvrir dans Safari) ; « Copier le résumé » donne un texte à coller dans le chat pour en discuter.

Quand Alexandre colle un résumé de l'outil : répondre sur le montage (quoi couper, quoi déplacer, quoi garder), en citant les secondes, selon ses règles de montage déjà connues.

## 2 bis. Le moteur sur le Mac d'Alexandre (à préférer dès que son Mac répond)

Installé le 19 nov. 2026 dans `~/Claude/analyse-video/` (Mac M5, 24 Go). Tout est gratuit et local : les vidéos ne quittent pas le Mac. Fiche : `technique/moteur-analyse-video-mac-2026-11-19.md` dans le projet.

**Outils du connecteur local « analyse-video »** (préfixe `mcp__remote-devices__analyse-video__`, à charger par ToolSearch) : `lister_videos`, `lancer_analyse(video)`, `etat_analyse(nom)`, `lire_paroles(nom)`, `lire_ecoute(nom)`, `verifier_moteur`. Deux outils servent à la page et non au chat : `ecouter_deposer` et `ecouter_resultat` (script `moteur/ecoute.py`, dépôts dans `resultats/_page/<clé>/`, journal dans `journal.txt` du dépôt pour diagnostiquer).

**Déroulé :**
1. `lancer_analyse` avec le nom d'un fichier déposé dans `videos/`, ou un chemin complet sur le Mac. Un chemin dans la photothèque (`~/Pictures/Photos Library.photoslibrary/originals/<lettre>/<UUID>.mov`) fonctionne tel quel.
2. `etat_analyse` jusqu'à `termine: true`. Repère : une vidéo de 41 s prend environ 3 min 30, dont 2 min 45 pour les mesures du Toolbox.
3. `lire_paroles` (phrases et mots par seconde, minutage mot par mot) et `lire_ecoute` (résumé d'earshot, bruits reconnus avec leur seconde, genre et humeur de la musique, coupes, saturation).
4. Pour voir les images : `device_stage_files` sur `resultats/<nom>/planches/p_01.jpg` (12 images par planche, la seconde écrite sous chaque vignette), puis `donnees.json`, déjà au format de la page.
5. Lire les émotions (sections 3 bis et 4), remplir `e`, `s`, `verdict`, publier la page (section 3, étape 5).

**Ce que le moteur contient :** images et planches, mouvement et coupes, les mesures du Aesthetics Toolbox, volume, débit et silences, paroles par Whisper large-v3-turbo (mlx-whisper), earshot (mesures objectives et écoute des bruits et de la musique). Chaque module est indépendant : un échec est noté dans `etat.json` sans arrêter les autres.

**Vérifié le 19 nov. 2026 sur le crash test :** les 49 colonnes de mesures d'image calculées sur le Mac concordent avec celles de l'espace de travail (écart médian sous 1 % partout). La transcription sort le texte presque complet avec les bons temps.

**À corriger à la main quand même.** Erreurs relevées dans sa voix : « un casseur » pour « incassable », « 140 litres » pour « livres », « si c'était tanné » pour « si t'es tanné », et le modèle remet des « ne » qu'il ne dit pas (« N'achetez pas » pour « Achetez pas »). Corriger avec les sous-titres visibles sur les planches. Les étiquettes de bruits d'earshot sont des indices : le crash test ressort surtout en sons d'interface (« notification ding », « chat message pop ») et une « goutte d'eau » à 21 s, au moment du bocal.

**Limites connues :** Claude ne peut pas taper dans le Terminal du Mac ; l'installation et toute réinstallation passent par un double-clic d'Alexandre sur `Installer.command`. Une retouche de `moteur/analyse.py` prend effet à l'analyse suivante ; une retouche de `moteur/serveur.py` demande de redémarrer l'app Claude. Pas encore de modèles d'expression du visage ni de ton de voix.

## 3. Chemin B : analyse complète dans le chat (les 43 mesures)

À prendre seulement quand le Mac d'Alexandre ne répond pas.

À prendre quand il faut les mesures que le navigateur ne calcule pas (Gabor, Fourier, fractales, PHOG, CNN), quand on analyse plusieurs vidéos pour les comparer, ou pour une future calibration.

**Il faut le fichier vidéo.** L'espace de travail ne peut pas télécharger une vidéo depuis Meta ou TikTok. Sources possibles : fichier joint, dossier du Mac, skill `phototheque-unique-plastique`.

Étapes :
1. Cloner le dépôt dans un dossier vide : `git clone --depth 1 https://github.com/rbartho/aesthetics-toolbox.git`. Installer ce qui manque : `pip install --break-system-packages statsmodels scikit-image scipy pillow numpy`.
2. Écrire le script ci-dessous dans un autre dossier et lancer : `python3 analyse_video.py VIDEO SORTIE --toolbox CHEMIN_DU_DEPOT`. Compter environ 25 s par image et par cœur (une vidéo de 30 s : 6 à 7 minutes sur 2 cœurs). Lancer en arrière-plan si c'est long.
3. Lire les planches-contact de `SORTIE/planches/` (l'heure est incrustée sur chaque vignette) et noter chaque seconde selon la grille de la section 4.
4. Faire le son (section 3 bis), puis remplir pour chaque seconde `e` (image), `s` (son), `w` (mots dits), `a` (mesures du son), et au niveau du fichier `phrases` et `verdict`.
5. Publier une page par vidéo : lire `index.html` et `qips.js` de l'outil (read_artifact et read_file sur le slug ci-dessus), insérer `<script>window.PRELOAD = {contenu de donnees.json};</script>` juste avant `<script src="qips.js"></script>` (remplacer `</` par `<\/` dans le JSON), publier comme un NOUVEL artifact nommé d'après la vidéo, puis déclarer `{"sample": {"images": true}}`. Ne pas écraser l'outil.
6. Donner le lien dans le chat, avec trois à cinq lignes : accroche, creux, moment fort, quoi recouper.

```python
#!/usr/bin/env python3
"""Analyse complète d'une vidéo avec le vrai Aesthetics Toolbox.
Usage : python3 analyse_video.py VIDEO SORTIE --toolbox CHEMIN_DU_DEPOT [--fps 1]
Sorties : images/ (une par seconde, côté long 1024), planches/ (planches-contact horodatées),
mesures.csv (mesures du Toolbox + mouvement + coupes), donnees.json (format window.PRELOAD de la page)."""
import argparse, base64, csv, io, json, os, subprocess, sys
from multiprocessing import Pool

MOTION_FPS = 4
CUT_THRESHOLD = 30.0


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def probe(video):
    out = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,color_transfer:format=duration", "-of", "json", video]))
    s = out["streams"][0]
    return float(out["format"]["duration"]), s["width"], s["height"], s.get("color_transfer", "")


def extract(video, out, fps, hdr):
    os.makedirs(f"{out}/images", exist_ok=True)
    os.makedirs(f"{out}/planches", exist_ok=True)
    tone = ""
    if hdr:  # iPhone HLG / PQ : ramener en SDR, sinon couleur et contraste sont faussés
        tone = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable,"
                "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")
    scale = "scale='if(gt(iw,ih),min(1024,iw),-2)':'if(gt(iw,ih),-2,min(1024,ih))'"
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"{tone}fps={fps},{scale}",
         "-start_number", "0", f"{out}/images/s_%04d.png"])
    stamp = "drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6"
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
         f"{tone}fps={fps},scale=-2:480,{stamp},tile=5x4", f"{out}/planches/p_%02d.jpg"])


def motion(video):
    import numpy as np
    w, h = 64, 64
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={MOTION_FPS},scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], check=True, capture_output=True).stdout
    f = np.frombuffer(raw, dtype=np.uint8).reshape(-1, h * w).astype(float)
    d = np.abs(np.diff(f, axis=0)).mean(axis=1)
    per_sec = {}
    for i, v in enumerate(d):
        sec = int((i + 1) / MOTION_FPS)
        m, c = per_sec.get(sec, (0.0, 0))
        per_sec[sec] = (m + v / MOTION_FPS, c + (1 if v >= CUT_THRESHOLD else 0))
    return per_sec


def qips(args):
    path, toolbox = args
    sys.path.insert(0, toolbox)
    import numpy as np
    from PIL import Image
    from skimage import color
    from AT import (balance_qips as bq, CNN_qips as cq, color_and_simple_qips as cs, edge_entropy_qips as eq,
                    fourier_qips as fq, fractal_dimension_qips as fd, PHOG_qips as pq)
    kernel, bias = np.load(open(os.path.join(toolbox, "AT/bvlc_alexnet_conv1.npy"), "rb"),
                           encoding="latin1", allow_pickle=True)
    pil = Image.open(path)
    rgb = np.asarray(pil.convert("RGB")); gray = np.asarray(pil.convert("L"))
    lab = color.rgb2lab(rgb); hsv = color.rgb2hsv(rgb)
    r = {"image": os.path.basename(path)}
    r["Image size"] = cs.image_size(rgb); r["Aspect ratio"] = cs.aspect_ratio(rgb)
    r["RMS contrast"] = cs.std_channels(lab)[0]
    r["Lightness entropy"] = cs.shannonentropy_channels(lab[:, :, 0])
    r["Color entropy"] = cs.shannonentropy_channels(hsv[:, :, 0])
    for name, arr in (("RGB", rgb), ("Lab", lab), ("HSV", hsv)):
        m, s = cs.mean_channels(arr), cs.std_channels(arr)
        for i, c in enumerate(name):
            r[f"mean {c} ({name})"] = m[i]; r[f"std {c} ({name})"] = s[i]
    r["mean H (HSV)"], r["std H (HSV)"] = cs.circ_stats(hsv)
    r["1st-order EOE"], r["2nd-order EOE"], r["Edge density"] = eq.do_first_and_second_order_entropy_and_edge_density(gray)
    r["Balance"] = bq.Balance(gray); r["DCM distance"], r["DCM x"], r["DCM y"] = bq.DCM(gray)
    r["Mirror symmetry"] = bq.Mirror_symmetry(gray); r["Homogeneity"] = bq.Homogeneity(gray)
    r["CNN symmetry left-right"], r["CNN symmetry up-down"], r["CNN symmetry lr & ud"] = cq.CNN_symmetry(rgb, kernel, bias)
    resp = cq.conv2d(rgb, kernel, bias)
    r["Sparseness"] = cq.CNN_Variance(cq.max_pooling(resp, patches=22)[1], kind="sparseness")
    r["Variability"] = cq.CNN_Variance(cq.max_pooling(resp, patches=12)[1], kind="variability")
    r["Self-similarity (CNN)"] = cq.CNN_selfsimilarity(cq.max_pooling(resp, patches=1)[1], cq.max_pooling(resp, patches=8)[1])
    r["Fourier sigma"], r["Slope Redies"] = fq.fourier_redies(gray, bin_size=2, cycles_min=10, cycles_max=256)
    r["Slope Spehar"] = fq.fourier_slope_branka_Spehar_Isherwood(gray)
    r["Slope Mather"] = fq.fourier_slope_mather(rgb)
    r["2D Fractal dimension"] = fd.fractal_dimension_2d(gray); r["3D Fractal dimension"] = fd.fractal_dimension_3d(gray)
    r["Self-similarity (PHOG)"], r["Complexity"], r["Anisotropy"] = pq.PHOGfromImage(
        rgb, section=2, bins=16, angle=360, levels=3, re=-1, sesfweight=[1, 1, 1])
    return {k: (float(v) if not isinstance(v, str) else v) for k, v in r.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--toolbox", required=True); ap.add_argument("--fps", type=float, default=1.0)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()
    dur, w, h, trc = probe(a.video)
    hdr = trc in ("arib-std-b67", "smpte2084")
    print(f"{dur:.1f} s, {w}x{h}, HDR={hdr}")
    extract(a.video, a.out, a.fps, hdr)
    frames = sorted(os.listdir(f"{a.out}/images"))
    mot = motion(a.video)
    with Pool(a.jobs) as pool:
        rows = pool.map(qips, [(f"{a.out}/images/{f}", os.path.abspath(a.toolbox)) for f in frames])
    for i, r in enumerate(rows):
        r["t (s)"] = round(i / a.fps, 2); r["Mouvement"], r["Coupes"] = mot.get(int(i / a.fps), (0.0, 0))
    cols = ["t (s)", "image"] + [k for k in rows[0] if k not in ("t (s)", "image")]
    with open(f"{a.out}/mesures.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols); wr.writeheader(); wr.writerows(rows)
    from PIL import Image
    page = {"name": os.path.basename(a.video), "dur": dur, "verdict": "", "frames": []}
    for i, r in enumerate(rows):
        im = Image.open(f"{a.out}/images/{r['image']}").convert("RGB"); im.thumbnail((240, 240))
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=72)
        page["frames"].append({
            "t": i, "thumb": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(),
            "q": {"rms_contrast": r["RMS contrast"], "lightness_entropy": r["Lightness entropy"],
                  "color_entropy": r["Color entropy"], "mean_S": r["mean S (HSV)"], "mean_L": r["mean L (Lab)"],
                  "balance": r["Balance"], "dcm": r["DCM distance"], "mirror_symmetry": r["Mirror symmetry"],
                  "homogeneity": r["Homogeneity"]},
            "motion": r["Mouvement"], "cuts": r["Coupes"], "e": None})
    json.dump(page, open(f"{a.out}/donnees.json", "w"), ensure_ascii=False)
    print(f"{len(rows)} images -> {a.out}/mesures.csv et donnees.json (remplir e et verdict)")


if __name__ == "__main__":
    main()
```

Format de `e` pour une seconde : `{"desc": "Sac de bouchons vidé sur une table", "att": 3, "int": 2, "val": 1, "emo": {"intrigue": 3, "interet": 2}, "why": {"intrigue": "un sac vidé d'un coup, sans explication", "interet": "des bouchons qu'on reconnaît de la maison"}}`. `s` a la même forme sans `desc`. `a` : `{"vol": -16.2, "debit": 6, "silence": 0.1}`. `w` : les mots dits pendant cette seconde. `phrases` : `[{"t0": 0, "t1": 1, "texte": "..."}]`. `verdict` peut être un texte, ou un objet `{"img": ..., "son": ..., "mix": ...}` avec un pronostic par section. Format de `verdict` : texte brut, quatre sections dont le titre commence par `## ` (Accroche ; Où ça tient, où ça tombe ; Partages et interactions ; Quoi recouper).

## 3 bis. Le son dans le chat

1. `pip install --break-system-packages sherpa-onnx`, puis télécharger le modèle depuis GitHub (Hugging Face n'est pas joignable d'ici) : `https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-turbo.tar.bz2` (564 Mo), `tar xjf`.
2. Écrire le script ci-dessous et lancer : `python3 analyse_son.py VIDEO SORTIE --modele DOSSIER_TURBO`. Environ une seconde de calcul par seconde de vidéo. Sortie : `SORTIE/son.json` (texte, morceaux, et par seconde : mots, vol, debit, silence).
3. **Corriger la transcription à la main** avec les sous-titres incrustés visibles sur les planches-contact : ils donnent le mot juste et la seconde exacte. Un mot qu'on ne peut pas confirmer se laisse tel qu'entendu ou se retire ; ne jamais inventer une phrase d'Alexandre.
4. Découper le texte corrigé en phrases avec leur seconde de début et de fin, et lire chaque phrase : attention, intensité, ton, émotions avec leur pourquoi (les mots, mais aussi la voix : volume, débit, pauses mesurés). Les secondes sans paroles reçoivent une lecture basse (attention 1, aucune émotion).
5. Dans les recommandations de montage, ne jamais proposer de couper un moment où Alexandre parle : proposer un plan d'appoint par-dessus sa voix.

```python
#!/usr/bin/env python3
"""Piste son d'une vidéo : paroles (Whisper turbo via sherpa-onnx) et mesures du son, seconde par seconde.
Usage : python3 analyse_son.py VIDEO SORTIE --modele DOSSIER_SHERPA_WHISPER_TURBO
Le minutage des mots est approximatif (à une seconde près)."""
import argparse, json, os, subprocess
import numpy as np

SR = 16000
HOP = 160            # 10 ms


def load(video):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def envelope(a):
    n = len(a) // HOP
    return np.sqrt((a[:n * HOP].reshape(n, HOP) ** 2).mean(axis=1) + 1e-12)


def chunks(env, max_s=26.0, min_s=14.0):
    cuts, start, n = [0], 0, len(env)
    sm = np.convolve(env, np.ones(15) / 15, mode="same")
    while n - start > max_s * 100:
        lo, hi = start + int(min_s * 100), start + int(max_s * 100)
        cut = lo + int(np.argmin(sm[lo:hi]))
        cuts.append(cut); start = cut
    cuts.append(n)
    return list(zip(cuts[:-1], cuts[1:]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out"); ap.add_argument("--modele", required=True)
    ap.add_argument("--langue", default="fr")
    a = ap.parse_args()
    import sherpa_onnx
    m = a.modele; pre = [f for f in os.listdir(m) if f.endswith("-tokens.txt")][0][:-len("-tokens.txt")]
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=f"{m}/{pre}-encoder.int8.onnx", decoder=f"{m}/{pre}-decoder.int8.onnx",
        tokens=f"{m}/{pre}-tokens.txt", language=a.langue, task="transcribe", num_threads=2)
    audio = load(a.video); env = envelope(audio)
    seuil = max(10 ** (-45 / 20), np.percentile(env, 95) * 0.08)
    voix = env > seuil
    nsec = int(np.ceil(len(audio) / SR))
    mots_par_sec = [[] for _ in range(nsec)]; phrases = []
    for c0, c1 in chunks(env):
        s = rec.create_stream(); s.set_option("max_tokens_per_second", "14")   # débit rapide : ne pas tronquer
        s.accept_waveform(SR, audio[c0 * HOP:c1 * HOP]); rec.decode_stream(s)
        texte = s.result.text.strip()
        if not texte or set(texte) <= set(".* "):
            continue
        phrases.append({"debut": round(c0 / 100, 2), "fin": round(c1 / 100, 2), "texte": texte})
        v = np.flatnonzero(voix[c0:c1]) + c0
        if len(v) == 0:
            v = np.arange(c0, c1)
        mots = texte.split(); total = sum(len(w) for w in mots); pos = 0
        for w in mots:
            t = v[min(len(v) - 1, int((pos + len(w) / 2) / total * len(v)))] / 100
            mots_par_sec[min(nsec - 1, int(t))].append(w); pos += len(w)
    sm = np.convolve(env, np.ones(5) / 5, mode="same")
    pics = (sm[1:-1] > sm[:-2]) & (sm[1:-1] >= sm[2:]) & (sm[1:-1] > seuil * 1.5)
    idx = np.flatnonzero(pics) + 1
    keep = [i for k, i in enumerate(idx) if k == 0 or i - idx[k - 1] >= 9]
    secondes = []
    for t in range(nsec):
        e = env[t * 100:(t + 1) * 100]
        if len(e) == 0:
            break
        secondes.append({"t": t, "mots": " ".join(mots_par_sec[t]),
                         "vol": round(float(20 * np.log10(e.mean() + 1e-9)), 1),
                         "debit": int(sum(1 for i in keep if t * 100 <= i < (t + 1) * 100)),
                         "silence": round(float((e <= seuil).mean()), 2)})
    os.makedirs(a.out, exist_ok=True)
    json.dump({"texte": " ".join(p["texte"] for p in phrases), "phrases": phrases, "secondes": secondes},
              open(f"{a.out}/son.json", "w"), ensure_ascii=False, indent=1)
    print(len(phrases), "morceaux,", len(secondes), "secondes ->", f"{a.out}/son.json")


if __name__ == "__main__":
    main()
```

## 4. La grille de lecture

Pour chaque seconde, se demander ce qu'une spectatrice typique (femme au Québec, qui fait défiler son fil sur son téléphone) ressent en voyant cette image à ce moment de la vidéo.

- `desc` : ce qu'on voit, 12 mots au plus.
- `att` 0 à 3 : pouvoir d'arrêter le pouce et de retenir le regard.
- `int` 0 à 3 : intensité de l'émotion provoquée.
- `val` −3 à 3 : désagréable à agréable.
- `emo` : seulement les émotions présentes, notées 1 (légère), 2 (nette), 3 (forte).

Les 25 émotions (identifiants entre parenthèses), adaptées des 27 catégories de Cowen et Keltner (2017) pour de courtes vidéos, sans désir sexuel, horreur ni romance, avec la fierté ajoutée :

- **Accroche** : Intérêt (interet), Surprise (surprise), Intrigue (intrigue), Fascination (fascination), Émerveillement (emerveillement)
- **Plaisir** : Amusement (amusement), Joie (joie), Satisfaction (satisfaction), Plaisir des yeux (beaute), Calme (calme), Soulagement (soulagement)
- **Lien** : Admiration (admiration), Attendrissement (tendresse), Fierté (fierte), Nostalgie (nostalgie)
- **Désir** : Envie du produit (envie), Excitation (excitation)
- **Tension** : Inquiétude (anxiete), Peur (peur), Douleur ressentie (douleur), Malaise (malaise), Dégoût (degout), Colère (colere), Tristesse (tristesse)
- **Décrochage** : Ennui (ennui)

**Quand un visage est à l'image.** Applique le skill `expressions-faciales-et-impression-image` : décrire d'abord ce qu'on voit (regard, bouche, sourcils, mains), puis seulement ce que ça peut évoquer. À une image par seconde, on lit des configurations, pas des micro-expressions. Une bouche ouverte pendant une phrase est de la parole : croiser avec les paroles du moteur. Ne jamais conclure sur ce que la personne ressent vraiment. Depuis le 20 nov. 2026, la lecture des images de la page a un champ `vis` (ce que le visage montre, « parle » si la bouche est ouverte en parlant), affiché à côté de la description.

Règles de notation : chaque émotion notée reçoit son pourquoi dans `why`, en 14 mots au plus, concret (un geste, un objet, un cadrage, un mot à l'écran, une phrase dite), jamais une généralité ; noter sobrement (la plupart des émotions valent 0 sur une image, 3 est rare) ; tenir compte de ce qui précède (une image identique à la précédente lasse, une rupture réveille) ; ne rien déduire du son ; ne nommer personne dans `desc`.

## 5. Le pronostic (repères provisoires)

| Repère | Calcul | Forte | Moyenne |
|---|---|---|---|
| Accroche | attention moyenne des secondes 0 à 2 | 2,3 et plus | 1,5 et plus |
| Tenue | part des secondes suivantes à attention 2 ou 3 ; signaler le plus long creux (attention 0 ou 1 pendant 2 s ou plus) | 60 % et plus | 35 % et plus |
| Envie de partager | part des secondes avec surprise, émerveillement, amusement, admiration, fierté ou excitation à 2 ou 3 | 30 % et plus | 12 % et plus |
| Fin | intensité des 2 dernières secondes moins la moyenne | +0,3 et plus : finit fort | −0,4 et plus : finit égal |

L'idée derrière « envie de partager » : les émotions vives et positives font davantage partager que les émotions calmes (Berger et Milkman, 2012). Les seuils sont posés à la main et n'ont pas été comparés à nos chiffres.

Le texte du pronostic : français du Québec, tutoiement, phrases courtes, secondes précises, trois gestes de montage au plus, 170 mots au plus.

## 5 bis. Le pari de viralité (calé sur nos vidéos)

Section « Pari de viralité » de la page, ajoutée le 20 nov. 2026 à la demande d'Alexandre : il ne veut pas d'un pari à l'œil, il veut un pari tiré des corrélations entre les émotions et les chiffres de nos anciennes vidéos.

- Modèle : régression pénalisée entraînée sur 193 vidéos TikTok lues à l'aveugle. Entrées : intensité moyenne de chaque émotion, de l'attention, de l'intensité et du ton, par tranche (0-2 s, 0-4 s, 5-9 s, 10 s et plus, 3 dernières secondes, tout), à l'image et au son, plus la durée. Trois versions dans `pari.js` : images seules ; images et son ; images, son et mots (utilisée quand les trois sont lus). Les vues tiennent aussi compte de l'élan du compte (vues médianes des 5 dernières vidéos publiées depuis 3 jours ou plus ; case modifiable dans la page, 9 400 au 19 nov. 2026).
- Sorties : pari de vues en trois niveaux (bas, moyen, haut), part encore là à 5 s, à 10 s, regardée jusqu'au bout, et les émotions qui poussent le pari vers le haut ou vers le bas.
- Justesse sur des vidéos de 2026 jamais vues : niveau haut = 56 % passent 100 000 vues, niveau bas = 20 % ; lien prévu-réel +0,37 à 5 s (faible), +0,52 à 10 s, +0,71 pour la fin. Toujours dire que c'est un pari qui départage, pas une promesse de vues.
- Ce que les corrélations disent, à utiliser dans les conseils : l'intrigue à l'image dans les 3 premières secondes va avec la rétention à 5 s ; la satisfaction entre 5 et 9 s et sur toute la vidéo va avec la rétention à 10 s et la fin ; l'ennui fait l'inverse ; la tension (inquiétude) et la satisfaction à l'image vont avec les vues ; la surprise entre 5 et 9 s avec les partages ; l'admiration avec les j'aime et les abonnés. Aucune paire d'émotions ne fait mieux que la somme des deux. Ce sont des corrélations, pas des causes.
- Détail, tableaux et limites : doc du projet `technique/correlations-emotions-et-pari-viralite-2026-11-20.md`. Scripts et modèle : `/mnt/user-data/outputs/calibration/correlations/`.
- Pour réentraîner : refaire `prep.py` puis `export.py` (écrit `pari.js`), vérifier que la page donne les mêmes chiffres que Python, republier `index.html` et `pari.js`.
- Pas encore vérifié : que la lecture faite par la page note comme les lectures d'entraînement. À contrôler sur quelques vidéos dont on connaît les chiffres.

**Règle d'Alexandre pour le pari (20 nov. 2026).** Le pari est la partie où on a le droit d'oser : « tu peux prendre des guesses, l'overshoot plus ou moins ». Il veut un estimé de vues même imprécis, pour avoir une base. La page affiche donc un chiffre avec sa fourchette : le classement du modèle étiré sur l'étendue réelle de nos vues de 2026 (5 000 à 1,6 million). L'erreur typique est d'environ 2 fois ; répondre la médiane à chaque fois ferait aussi bien pour le chiffre, mais pas pour le classement. Partout ailleurs dans l'outil : des faits, et il fait l'analyse lui-même.

**Justesse avec les mots** (vidéos de 2026 jamais vues) : +0,45 à 5 s, +0,57 à 10 s, +0,72 pour la fin, +0,48 pour les vues. Pour réentraîner : `prep.py`, `/home/claude/mots/prep_mots.py`, puis `export2.py` (remplace `export.py`).

## 5 ter. La section Mots

Onglet « Mots » de la page (20 nov. 2026) : le sens de ce qui est dit, seconde par seconde, et le rôle de chaque phrase dans l'histoire. Applique le skill `mots-qui-accrochent`. La carte « Mots et récit » donne le récit, le moment fort, les questions ouvertes et les secondes par rôle. Alexandre corrige les paroles dans la page ; « Refaire l'analyse avec mes corrections » relit le son, les mots, le pronostic et le pari, sans relire les images. La lecture des mots se lance après celle du son.

**Courbe du récit** (demande d'Alexandre, 20 nov. 2026 : « un graphique qui monte en intensité, comme le Hero's Journey, où on voit le climax, mais pas forcément dans l'ordre enseigné »). Dans la carte « Mots et récit » : l'intensité à chaque seconde (le plus fort de l'image, du son et des mots, lissé sur 3 secondes), les mots seuls en pointillé, chaque étape de l'histoire étiquetée à la seconde où elle arrive vraiment, le moment fort relevé dans les mots, le sommet d'intensité, et sous la courbe chaque question ouverte tracée de son ouverture à sa fermeture (pointillé si jamais refermée). Survol : rôle, intensité, mots et image de la seconde ; clic : aller à cette seconde. La courbe montre des faits ; elle n'impose aucun ordre d'étapes. Fonctions `arcData` et `renderArc` de la page. L'onglet « Les deux » s'appelle maintenant « Image + son ». Résultats des corrélations des mots (mots concrets, histoire, appel à l'action, moment fort) : doc du projet `technique/mots-qui-accrochent-apprentissages.md`. Consignes de lecture des mots, les mêmes que pour les 193 vidéos : `/mnt/user-data/outputs/calibration/mots/CONSIGNES-MOTS.md`.

## 6. Modifier l'outil

- Lire la page (read_artifact) et `qips.js` (read_file), modifier, republier avec publish_files sur le même slug et la version courante. Garder la déclaration `{"sample": {"images": true}, "mcp": {"servers": [{"server": "host:analyse-video", "tools": ["ecouter_deposer", "ecouter_resultat"]}]}}` (lire d'abord read_declaration ; pour ajouter une capacité, déclarer avant de publier le code qui s'en sert).
- Le pont entre la page et le moteur ne s'essaie pas depuis l'espace de travail. Pour vérifier une retouche : servir la page en local, remplacer `window.claude` par un faux (`sample` qui renvoie des lignes JSON, `mcp.callTool` qui appelle les fonctions de `serveur.py` par une petite passerelle HTTP), lancer Chrome sans écran avec une vidéo WebM, et utiliser `ANALYSE_SHERPA` pour la transcription de secours. Dire à Alexandre que le vrai pont reste à confirmer par son essai.
- Les pronostics écrits ne proposent jamais de couper un moment où il parle : un plan d'appoint par-dessus sa voix (règle d'Alexandre, déjà dans les consignes de la page).
- Toute retouche de `qips.js` se revérifie contre le Toolbox Python sur les mêmes pixels avant de publier.
- Si la grille d'émotions change, la changer à trois endroits : la liste `EMOS` de la page, la section 4 de ce skill, et la note de méthode au bas de la page.

## 7. À faire plus tard : calibrer

**Fait en partie les 19 et 20 nov. 2026** (263 vidéos TikTok relevées à la seconde, 193 lues à l'aveugle). Lire avant tout pronostic les docs du projet `technique/calibration-tiktok-premiers-resultats-2026-11-19.md` et `technique/calibration-lecture-aveugle-resultats-2026-11-20.md`. En bref : la part de spectateurs encore là à 5 s suit les vues (+0,61) ; la lecture à l'aveugle prévoit bien la fin (+0,71) et mal les 5 premières secondes (+0,30) ; « Envie de partager » ne prévoit rien (+0,12) ; une ouverture sur un objet ou une matière en main tient mieux qu'une ouverture sur l'entreprise ou un média. Reste à faire : Facebook, Instagram, pubs Meta, corrections de l'outil.

Passer nos vidéos déjà publiées (pubs Meta, 135 vidéos TikTok) par le chemin B, puis comparer les repères à leur rétention, leurs partages et leur rendement réels. Tant que ce n'est pas fait, le pronostic reste une hypothèse. Les trois vidéos virales testées le 19 nov. 2026 sortent toutes « accroche forte », mais elles ont été lues en sachant qu'elles avaient marché : il faut lire aussi des vidéos qui ont floppé, sans regarder leurs chiffres avant, pour savoir si l'outil fait la différence.

**Transcription dans la page (demande ouverte d'Alexandre).** Il veut que les paroles se lisent dans la page elle-même et que le québécois soit bien compris. Ce qui est établi : la page ne peut envoyer que des images à Claude, pas du son ; la capacité `dictation` écoute le micro, pas un fichier ; un petit modèle embarqué comprend mal sa voix ; le modèle qui la comprend pèse environ 1 Go. Piste à essayer : embarquer un modèle de cette taille en morceaux de moins de 20 Mo dans les fichiers de la page et le faire tourner avec onnxruntime-web. Rien n'est vérifié : ni la taille que l'hébergement accepte, ni la vitesse dans le navigateur. Depuis le 19 nov. 2026, Alexandre a choisi une autre voie : le moteur sur son Mac (section 2 bis), où la taille des modèles n'est plus une limite. Le soir même, la demande a été réglée par là : la page envoie le son au moteur et reçoit les paroles (section 2). Écart connu entre les deux chemins : l'outil mesure sur 512 px de côté long, le script sur 1024 px ; les valeurs ne sont pas comparables d'un chemin à l'autre.

## Journal

- 20 nov. 2026 (4 h 15) : courbe du récit ajoutée à la section Mots (version `1795165999-6678`). Essayée dans un navigateur de test avec une histoire fictive ; pas encore vue sur une vraie vidéo.

- 20 nov. 2026 (4 h) : section Mots avec correction de la transcription, lecture à l'aveugle des mots des 193 vidéos, mots ajoutés au pari, estimé de vues qui ose et élan du compte. Chaîne essayée de bout en bout avec un faux Claude ; la vraie lecture des mots par la page attend l'essai d'Alexandre.

- 20 nov. 2026 (3 h 40) : gros calcul des corrélations (25 émotions, 3 couches, 6 tranches, 12 cibles, paires, seconde par seconde, avec garde-fou contre le hasard) et section « Pari de viralité » publiée dans la page avec le champ `vis`. Calcul de la page vérifié identique au modèle Python ; la vraie lecture de la page avec ces ajouts attend l'essai d'Alexandre.

- 20 nov. 2026 : renvoi vers le nouveau skill `expressions-faciales-et-impression-image` pour la lecture des visages. Premier contrôle sur les 193 lectures à l'aveugle : la présence d'une personne dans les 5 premières secondes ne va pas avec une meilleure rétention (−0,16, mesure par mots-clés). La couche visage n'est pas encore dans la page.

- 19 nov. 2026 (21 h) : le son est analysé dans la page. Alexandre : « Il analyse pas le son encore. » La page appelle maintenant le moteur du Mac (capacité `mcp`, `host:analyse-video`) : paroles, bruits et musique, lecture des émotions du son, section « Les deux », pronostic par section. Essayé de bout en bout dans un navigateur de test avec un faux pont ; le vrai pont dans l'app Claude du Mac attend le premier essai d'Alexandre.

- 19 nov. 2026 (18 h 30) : moteur installé sur le Mac et premier essai réussi sur le crash test. Leçon de l'installation : l'outil `unzip` du Mac bloque sur les noms de fichiers avec émoji et attend une réponse au clavier ; l'installateur extrait maintenant l'archive avec Python.
- 19 nov. 2026 (soir) : ajout des trois sections (Images, Son, Les deux), du pourquoi de chaque bloc, des mesures du son dans la page, et du son dans le chat (Whisper turbo). Test sur les trois vidéos TikTok les plus vues (masques 1,6 M, crash test 1,2 M, défi couleur 660 700), retrouvées dans la photothèque par la date de publication ; pages publiées à part.
- 19 nov. 2026 : création. Outil publié, port de 12 mesures vérifié contre le Toolbox, script complet testé sur une vidéo générique de 7 s. Pas encore essayé sur une vraie vidéo d'Unique Plastique ni avec la lecture de Claude en conditions réelles.