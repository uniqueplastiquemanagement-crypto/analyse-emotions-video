#!/usr/bin/env python3
"""Moteur d'analyse vidéo d'Unique Plastique : tout ce qui se mesure sur une vidéo, sur le Mac, sans rien envoyer ailleurs.

Usage : python analyse.py VIDEO [--sortie DOSSIER] [--sans-earshot] [--sans-toolbox]

Produit dans resultats/<nom>/ :
  etat.json          où en est l'analyse (étape, pourcentage, erreurs par module)
  images/            une image par seconde (côté long 1024 px)
  planches/          planches-contact horodatées, 12 images par planche, pour la lecture des émotions
  mesures.csv        par seconde : mesures du Aesthetics Toolbox + mouvement + coupes
  son.json           paroles (Whisper large-v3-turbo, minutage mot par mot), phrases, volume, débit, silences
  earshot.json       mesures objectives du son et écoute seconde par seconde (bruits, musique, synchro aux coupes)
  donnees.json       le tout au format de la page « Émotions d'une vidéo » ; il reste à remplir e, s et verdict

Chaque module est indépendant : si l'un échoue, les autres continuent et l'erreur est notée dans etat.json.
"""
import argparse, base64, csv, io, json, os, re, shutil, subprocess, sys, time, traceback
from multiprocessing import Pool

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
TOOLBOX = os.environ.get("ANALYSE_TOOLBOX") or os.path.join(ICI, "toolbox")
MODELE_PAROLES = "mlx-community/whisper-large-v3-turbo"
AMORCE = "Vidéo québécoise d'Unique Plastique, à Lévis : des pinces à cheveux faites de plastique recyclé."
MOTION_FPS, CUT_THRESHOLD = 4, 30.0
SR, HOP = 16000, 160


# ---------- outils ----------
def binaires():
    """ffmpeg et ffprobe : ceux du Mac s'ils existent, sinon ceux fournis par static-ffmpeg."""
    os.environ["PATH"] = os.pathsep.join([os.environ.get("PATH", ""), "/opt/homebrew/bin", "/usr/local/bin"])
    f, p = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not (f and p):
        from static_ffmpeg import run as sf
        f, p = sf.get_or_fetch_platform_executables_else_raise()
        os.environ["PATH"] = os.path.dirname(f) + os.pathsep + os.environ["PATH"]
    return f, p


def run(cmd, binaire=False):
    r = subprocess.run(cmd, check=True, capture_output=True)
    return r.stdout if binaire else r.stdout.decode("utf-8", "replace")


class Etat:
    def __init__(self, out, video):
        self.f = os.path.join(out, "etat.json")
        self.d = {"video": video, "debut": time.strftime("%Y-%m-%d %H:%M:%S"), "etape": "démarrage", "pourcent": 0,
                  "termine": False, "modules": {}, "erreurs": {}}
        self.ecrire()

    def ecrire(self):
        tmp = self.f + ".tmp"
        json.dump(self.d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, self.f)

    def etape(self, nom, pct):
        self.d.update(etape=nom, pourcent=pct); self.ecrire(); print(f"[{pct:3d} %] {nom}", flush=True)

    def module(self, nom, fn):
        t0 = time.time()
        try:
            r = fn(); self.d["modules"][nom] = f"ok, {time.time() - t0:.0f} s"; self.ecrire(); return r
        except Exception as e:
            self.d["modules"][nom] = "échec"; self.d["erreurs"][nom] = f"{type(e).__name__}: {e}"[:600]; self.ecrire()
            print(f"  ! {nom} a échoué : {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            return None


# ---------- image ----------
def probe(ffprobe, video):
    out = json.loads(run([ffprobe, "-v", "error", "-show_entries",
                          "stream=codec_type,width,height,color_transfer:format=duration", "-of", "json", video]))
    v = next(s for s in out["streams"] if s.get("codec_type") == "video")
    audio = any(s.get("codec_type") == "audio" for s in out["streams"])
    return float(out["format"]["duration"]), v["width"], v["height"], v.get("color_transfer", ""), audio


def extraire(ffmpeg, video, out, hdr):
    os.makedirs(f"{out}/images", exist_ok=True); os.makedirs(f"{out}/planches", exist_ok=True)
    tone = ""
    if hdr:  # iPhone HLG / PQ : ramener en SDR, sinon couleur et contraste sont faussés
        tone = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable,"
                "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")
    scale = "scale='if(gt(iw,ih),min(1024,iw),-2)':'if(gt(iw,ih),-2,min(1024,ih))'"
    run([ffmpeg, "-v", "error", "-y", "-i", video, "-vf", f"{tone}fps=1,{scale}", "-start_number", "0",
         f"{out}/images/s_%04d.png"])
    # l'heure est écrite sous chaque vignette avec PIL (pas besoin de police dans ffmpeg)
    from PIL import Image, ImageDraw, ImageFont
    try:
        police = ImageFont.load_default(22)
    except TypeError:
        police = ImageFont.load_default()
    noms = sorted(os.listdir(f"{out}/images"))
    for p in range(0, len(noms), 12):
        vig = []
        for i, n in enumerate(noms[p:p + 12]):
            im = Image.open(f"{out}/images/{n}").convert("RGB"); im.thumbnail((360, 640))
            c = Image.new("RGB", (360, 672), "black"); c.paste(im, ((360 - im.width) // 2, 0))
            ImageDraw.Draw(c).text((8, 643), f"{p + i} s", fill="white", font=police); vig.append(c)
        pl = Image.new("RGB", (360 * 4, 672 * ((len(vig) + 3) // 4)), "black")
        for i, c in enumerate(vig):
            pl.paste(c, (360 * (i % 4), 672 * (i // 4)))
        pl.save(f"{out}/planches/p_{p // 12 + 1:02d}.jpg", quality=85)
    return noms


def mouvement(ffmpeg, video):
    import numpy as np
    raw = run([ffmpeg, "-v", "error", "-i", video, "-vf", f"fps={MOTION_FPS},scale=64:64,format=gray",
               "-f", "rawvideo", "-"], binaire=True)
    f = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 4096).astype(float)
    d = np.abs(np.diff(f, axis=0)).mean(axis=1)
    par_sec = {}
    for i, v in enumerate(d):
        s = int((i + 1) / MOTION_FPS); m, c = par_sec.get(s, (0.0, 0))
        par_sec[s] = (m + v / MOTION_FPS, c + (1 if v >= CUT_THRESHOLD else 0))
    return par_sec


def base_image(path):
    """Les mesures simples, sans le Toolbox : toujours disponibles."""
    import numpy as np
    from PIL import Image
    from skimage import color
    rgb = np.asarray(Image.open(path).convert("RGB")); lab = color.rgb2lab(rgb); hsv = color.rgb2hsv(rgb)
    return {"image": os.path.basename(path), "RMS contrast": float(lab[:, :, 0].std()),
            "mean L (Lab)": float(lab[:, :, 0].mean()), "mean S (HSV)": float(hsv[:, :, 1].mean())}


def qips(path):
    """Les mesures du Aesthetics Toolbox pour une image."""
    sys.path.insert(0, TOOLBOX)
    import numpy as np
    from PIL import Image
    from skimage import color
    from AT import (balance_qips as bq, CNN_qips as cq, color_and_simple_qips as cs, edge_entropy_qips as eq,
                    fourier_qips as fq, fractal_dimension_qips as fd, PHOG_qips as pq)
    kernel, bias = np.load(open(os.path.join(TOOLBOX, "AT/bvlc_alexnet_conv1.npy"), "rb"),
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


# ---------- son ----------
def charger_audio(ffmpeg, video):
    import numpy as np
    raw = run([ffmpeg, "-v", "error", "-i", video, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], binaire=True)
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def mesures_son(audio):
    """Par seconde : volume (dB), débit (attaques par seconde), part de silence."""
    import numpy as np
    n = len(audio) // HOP
    env = np.sqrt((audio[:n * HOP].reshape(n, HOP) ** 2).mean(axis=1) + 1e-12)
    seuil = max(10 ** (-45 / 20), np.percentile(env, 95) * 0.08)
    sm = np.convolve(env, np.ones(5) / 5, mode="same")
    pics = (sm[1:-1] > sm[:-2]) & (sm[1:-1] >= sm[2:]) & (sm[1:-1] > seuil * 1.5)
    idx = np.flatnonzero(pics) + 1
    keep = [i for k, i in enumerate(idx) if k == 0 or i - idx[k - 1] >= 9]
    out = []
    for t in range(int(np.ceil(n / 100))):
        e = env[t * 100:(t + 1) * 100]
        if len(e) == 0:
            break
        out.append({"t": t, "vol": round(float(20 * np.log10(e.mean() + 1e-9)), 1),
                    "debit": int(sum(1 for i in keep if t * 100 <= i < (t + 1) * 100)),
                    "silence": round(float((e <= seuil).mean()), 2)})
    return out, env, seuil


def paroles_mlx(wav):
    """Transcrit en détectant la langue. Les vidéos sont en français du Québec ou en anglais : toute autre langue
    détectée est traitée comme une erreur de détection et reprise en français."""
    import mlx_whisper
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=MODELE_PAROLES, word_timestamps=True, condition_on_previous_text=False)
    langue = r.get("language") or "fr"
    if langue != "en":
        langue = "fr"
        r = mlx_whisper.transcribe(wav, path_or_hf_repo=MODELE_PAROLES, language="fr", word_timestamps=True,
                                   initial_prompt=AMORCE, condition_on_previous_text=False)
    phrases, mots = [], []
    for s in r.get("segments", []):
        t = s["text"].strip()
        if t:
            phrases.append({"debut": round(float(s["start"]), 2), "fin": round(float(s["end"]), 2), "texte": t})
        for w in s.get("words", []):
            mots.append({"mot": w["word"].strip(), "debut": round(float(w["start"]), 2), "fin": round(float(w["end"]), 2)})
    return {"modele": MODELE_PAROLES, "langue": langue, "minutage": "mot par mot", "phrases": phrases, "mots": mots}


def paroles_sherpa(audio, env, seuil, dossier):
    """Secours hors Mac : Whisper via sherpa-onnx, minutage approximatif (réparti sur le temps de voix)."""
    import numpy as np, sherpa_onnx
    pre = [f for f in os.listdir(dossier) if f.endswith("-tokens.txt")][0][:-len("-tokens.txt")]
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=f"{dossier}/{pre}-encoder.int8.onnx", decoder=f"{dossier}/{pre}-decoder.int8.onnx",
        tokens=f"{dossier}/{pre}-tokens.txt", language="fr", task="transcribe", num_threads=2)
    cuts, start, n = [0], 0, len(env); sm = np.convolve(env, np.ones(15) / 15, mode="same")
    while n - start > 2600:
        cut = start + 1400 + int(np.argmin(sm[start + 1400:start + 2600])); cuts.append(cut); start = cut
    cuts.append(n); voix = env > seuil; phrases, mots = [], []
    for c0, c1 in zip(cuts[:-1], cuts[1:]):
        s = rec.create_stream(); s.set_option("max_tokens_per_second", "14")
        s.accept_waveform(SR, audio[c0 * HOP:c1 * HOP]); rec.decode_stream(s)
        t = s.result.text.strip()
        if not t or set(t) <= set(".* "):
            continue
        phrases.append({"debut": c0 / 100, "fin": c1 / 100, "texte": t})
        v = np.flatnonzero(voix[c0:c1]) + c0
        v = v if len(v) else np.arange(c0, c1)
        ws = t.split(); total = sum(len(w) for w in ws); pos = 0
        for w in ws:
            tt = float(v[min(len(v) - 1, int((pos + len(w) / 2) / total * len(v)))] / 100)
            mots.append({"mot": w, "debut": round(tt, 2), "fin": round(tt, 2)}); pos += len(w)
    return {"modele": "sherpa-onnx " + pre, "minutage": "approximatif, à une seconde près", "phrases": phrases, "mots": mots}


def earshot(video, sans_modeles=False):
    """Mesures objectives (sans modèle) et écoute seconde par seconde (avec modèles) d'earshot."""
    r = {}
    r["mesures"] = json.loads(run([sys.executable, "-m", "earshot", "measure", video, "--json"]))
    if not sans_modeles:
        try:
            r["ecoute"] = json.loads(run([sys.executable, "-m", "earshot", "timeline", video, "--detail", "normal", "--json"]))
        except subprocess.CalledProcessError as e:
            r["ecoute_erreur"] = (e.stderr or b"").decode("utf-8", "replace")[-600:]
    return r


def coller(mots):
    """Recolle les morceaux de mots autour des apostrophes et des traits d'union (« c » + « 'est » -> « c'est »)."""
    out = ""
    for m in mots:
        out += m if (not out or m[:1] in "'’-" or out[-1:] in "'’-") else " " + m
    return out


# ---------- lot ----------
def exporter_phototheque(uuid, dossier):
    """Demande à l'app Photos d'exporter l'original d'une vidéo (elle le télécharge d'iCloud au besoin)."""
    os.makedirs(dossier, exist_ok=True)
    deja = [f for f in os.listdir(dossier) if f.lower().endswith((".mov", ".mp4", ".m4v"))]
    if deja:
        return os.path.join(dossier, deja[0])
    if not re.fullmatch(r"[0-9A-Fa-f-]{36}", uuid):
        raise ValueError("identifiant de photothèque invalide")
    script = ('with timeout of 900 seconds\n tell application "Photos"\n  set m to media item id "%s/L0/001"\n'
              '  export {m} to POSIX file "%s" with using originals\n end tell\nend timeout' % (uuid, dossier))
    r = subprocess.run(["/usr/bin/osascript", "-e", script], capture_output=True, text=True, timeout=1000)
    if r.returncode != 0:
        raise RuntimeError("Photos n'a pas exporté la vidéo : " + (r.stderr or r.stdout).strip()[-300:])
    for _ in range(120):                      # Photos écrit le fichier un peu après avoir rendu la main
        f = [x for x in os.listdir(dossier) if x.lower().endswith((".mov", ".mp4", ".m4v"))]
        if f:
            p = os.path.join(dossier, f[0]); t = os.path.getsize(p); time.sleep(1.5)
            if t > 0 and os.path.getsize(p) == t:
                return p
        time.sleep(1)
    raise RuntimeError("Photos a répondu, mais aucun fichier vidéo n'est arrivé dans " + dossier)


def lot(manifeste, out):
    """Analyse en lot. manifeste : {"sortie": dossier, "options": [...], "videos": [{"cle", "uuid", "chemin"}]}.
    Chaque vidéo a son dossier de résultats <sortie>/<cle> ; une vidéo déjà terminée est sautée (reprise possible)."""
    m = json.load(open(manifeste, encoding="utf-8"))
    verrou = os.path.join(out, "verrou.pid")
    try:
        os.kill(int(open(verrou).read().strip()), 0)
        print("un lot tourne déjà : arrêt", flush=True); return
    except Exception:
        pass
    open(verrou, "w").write(str(os.getpid()))
    try:
        subprocess.Popen(["/usr/bin/caffeinate", "-i", "-w", str(os.getpid())])     # le Mac ne s'endort pas pendant le lot
    except Exception:
        pass
    racine = os.path.expanduser(m.get("sortie") or os.path.join(RACINE, "resultats", "calibration"))
    exports = os.path.expanduser(m.get("exports") or os.path.join(RACINE, "videos", "phototheque"))
    vids, opts = m["videos"], list(m.get("options") or [])
    et = Etat(out, manifeste); et.d.update(total=len(vids), faits=0, sautes=0, echecs={}, courant=None, durees=[])
    for i, v in enumerate(vids):
        cle = re.sub(r"[^A-Za-z0-9_-]+", "-", str(v["cle"])); sortie = os.path.join(racine, cle)
        try:
            e = json.load(open(os.path.join(sortie, "etat.json")))
            if e.get("termine") and not (e.get("erreurs") or {}).get("fatale"):
                et.d["sautes"] += 1; et.d["faits"] += 1; continue
        except Exception:
            pass
        et.d["courant"] = cle; et.etape(f"vidéo {i + 1} sur {len(vids)} : {cle}", int(100 * i / len(vids)))
        t0 = time.time()
        try:
            chemin = v.get("chemin")
            if not (chemin and os.path.isfile(os.path.expanduser(chemin))):
                chemin = exporter_phototheque(v["uuid"], os.path.join(exports, v["uuid"]))
            os.makedirs(sortie, exist_ok=True)
            json.dump(v, open(os.path.join(sortie, "source.json"), "w"), ensure_ascii=False)
            r = subprocess.run([sys.executable, os.path.abspath(__file__), os.path.expanduser(chemin), "--sortie", sortie] + opts,
                               stdout=open(os.path.join(sortie, "journal.txt"), "w"), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            if r.returncode != 0:
                raise RuntimeError("l'analyse s'est arrêtée (voir journal.txt)")
            et.d["faits"] += 1; et.d["durees"] = (et.d["durees"] + [round(time.time() - t0)])[-30:]
        except Exception as e:
            et.d["echecs"][cle] = f"{type(e).__name__}: {e}"[:300]
            print(f"  ! {cle} : {e}", flush=True)
            if "-1743" in str(e) or "not authorized" in str(e).lower() or "autoris" in str(e).lower():
                et.d["erreurs"]["permission"] = "macOS n'a pas autorisé l'app Claude à contrôler Photos (Réglages > Confidentialité et sécurité > Automatisation)"
                break
        et.ecrire()
    et.d.update(termine=True, courant=None, fin=time.strftime("%Y-%m-%d %H:%M:%S")); et.etape("lot terminé", 100)
    try:
        os.remove(verrou)
    except OSError:
        pass


# ---------- assemblage ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--sortie")
    ap.add_argument("--sans-earshot", action="store_true"); ap.add_argument("--sans-toolbox", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    video = os.path.abspath(a.video)
    if video.lower().endswith(".json"):          # un manifeste de lot au lieu d'une vidéo
        out = os.path.abspath(a.sortie or os.path.join(RACINE, "resultats", "lot")); os.makedirs(out, exist_ok=True)
        return lot(video, out)
    nom = re.sub(r"[^A-Za-z0-9_-]+", "-", os.path.splitext(os.path.basename(video))[0]).strip("-") or "video"
    out = os.path.abspath(a.sortie or os.path.join(RACINE, "resultats", nom)); os.makedirs(out, exist_ok=True)
    et = Etat(out, video)
    try:
        if not os.path.isfile(video):
            raise FileNotFoundError(f"vidéo introuvable : {video}")
        ffmpeg, ffprobe = binaires()
        dur, w, h, trc, a_son = probe(ffprobe, video)
    except Exception as e:
        et.d["erreurs"]["fatale"] = f"{type(e).__name__}: {e}"[:600]; et.d["termine"] = True; et.etape("arrêt : la vidéo n'a pas pu être ouverte", 0)
        raise SystemExit(1)
    et.d.update(duree=round(dur, 2), taille=f"{w}x{h}", piste_son=a_son)

    et.etape("images : une par seconde et planches-contact", 5)
    noms = et.module("images", lambda: extraire(ffmpeg, video, out, trc in ("arib-std-b67", "smpte2084"))) or []
    mot = et.module("mouvement", lambda: mouvement(ffmpeg, video)) or {}

    son = {"phrases": [], "mots": [], "secondes": []}
    if a_son:
        et.etape("son : volume, débit, silences", 15)
        audio = charger_audio(ffmpeg, video)
        ms = et.module("mesures du son", lambda: mesures_son(audio))
        if ms:
            son["secondes"] = ms[0]
        et.etape("paroles : transcription", 20)
        sherpa = os.environ.get("ANALYSE_SHERPA")
        if sherpa and ms:
            p = et.module("paroles", lambda: paroles_sherpa(audio, ms[1], ms[2], sherpa))
        else:
            wav = os.path.join(out, "son.wav")
            run([ffmpeg, "-v", "error", "-y", "-i", video, "-ac", "1", "-ar", str(SR), wav])
            p = et.module("paroles", lambda: paroles_mlx(wav))
        if p:
            son.update(p)
        if not a.sans_earshot:
            et.etape("earshot : mesures et écoute du son", 35)
            e = et.module("earshot", lambda: earshot(video))
            if e:
                json.dump(e, open(f"{out}/earshot.json", "w"), ensure_ascii=False, indent=1)
                if "ecoute_erreur" in e:
                    et.d["erreurs"]["earshot écoute"] = e["ecoute_erreur"]; et.ecrire()
    for s in son["secondes"]:
        s["mots"] = coller([m["mot"] for m in son["mots"] if int(m["debut"]) == s["t"]])
    json.dump(son, open(f"{out}/son.json", "w"), ensure_ascii=False, indent=1)

    et.etape("images : mesures du Aesthetics Toolbox", 45)
    chemins = [f"{out}/images/{n}" for n in noms]
    lignes = None
    if chemins and not a.sans_toolbox and os.path.isdir(os.path.join(TOOLBOX, "AT")):
        def toolbox():
            res = []
            with Pool(a.jobs) as pool:
                for i, r in enumerate(pool.imap(qips, chemins)):
                    res.append(r); et.etape(f"images : mesures du Toolbox ({i + 1} sur {len(chemins)})", 45 + int(50 * (i + 1) / len(chemins)))
            return res
        lignes = et.module("toolbox", toolbox)
    if lignes is None and chemins:
        lignes = et.module("mesures de base", lambda: [base_image(c) for c in chemins]) or []
    lignes = lignes or []
    for i, r in enumerate(lignes):
        r["t (s)"] = i; r["Mouvement"], r["Coupes"] = mot.get(i, (0.0, 0))
    if lignes:
        cols = ["t (s)", "image"] + [k for k in lignes[0] if k not in ("t (s)", "image")]
        with open(f"{out}/mesures.csv", "w", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=cols); wr.writeheader(); wr.writerows(lignes)

    et.etape("assemblage", 97)
    from PIL import Image
    page = {"name": os.path.basename(video), "dur": dur, "verdict": "", "frames": [],
            "phrases": [{"t0": int(p["debut"]), "t1": max(int(p["debut"]), int(max(p["debut"], p["fin"] - 0.01))), "texte": p["texte"]}
                        for p in son["phrases"]]}
    for i, r in enumerate(lignes):
        im = Image.open(f"{out}/images/{r['image']}").convert("RGB"); im.thumbnail((240, 240))
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=72)
        s = son["secondes"][i] if i < len(son["secondes"]) else None
        page["frames"].append({
            "t": i, "thumb": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(),
            "q": {"rms_contrast": r.get("RMS contrast"), "lightness_entropy": r.get("Lightness entropy"),
                  "color_entropy": r.get("Color entropy"), "mean_S": r.get("mean S (HSV)"), "mean_L": r.get("mean L (Lab)"),
                  "balance": r.get("Balance"), "dcm": r.get("DCM distance"), "mirror_symmetry": r.get("Mirror symmetry"),
                  "homogeneity": r.get("Homogeneity")},
            "motion": r["Mouvement"], "cuts": r["Coupes"], "e": None,
            "a": {"vol": s["vol"], "debit": s["debit"], "silence": s["silence"]} if s else None,
            "w": s["mots"] if s else "", "s": None})
    json.dump(page, open(f"{out}/donnees.json", "w"), ensure_ascii=False)
    et.d.update(termine=True, fin=time.strftime("%Y-%m-%d %H:%M:%S"), dossier=out,
                images=len(noms), mots=len(son["mots"]))
    et.etape("terminé", 100)


if __name__ == "__main__":
    main()
