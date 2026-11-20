#!/usr/bin/env python3
"""Connecteur local « analyse-video » : laisse Claude lancer le moteur d'analyse sur le Mac et lire ses résultats.

Lancé par l'app Claude (voir claude_desktop_config.json). Rien ne sort du Mac : les outils renvoient du texte et des
chemins de fichiers ; les images et les mesures restent dans le dossier resultats/.
"""
import base64, json, os, re, shutil, subprocess, sys, time

try:
    from mcp.server.mcpserver import MCPServer as Serveur        # mcp 2.x
except ImportError:                                               # mcp 1.x
    from mcp.server.fastmcp import FastMCP as Serveur

LECTURE = {}                                                      # outils qui ne font que lire
try:
    from mcp.types import ToolAnnotations
    for _k in ({"readOnlyHint": True}, {"read_only_hint": True}):    # le nom du champ change selon la version de mcp
        try:
            _a = ToolAnnotations(**_k)
            if _a.model_dump(by_alias=True, exclude_none=True).get("readOnlyHint") is True:
                LECTURE = {"annotations": _a}; break
        except Exception:
            pass
except Exception:
    pass

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
VIDEOS, RESULTATS = os.path.join(RACINE, "videos"), os.path.join(RACINE, "resultats")
EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")

srv = Serveur("analyse-video", instructions=(
    "Moteur d'analyse vidéo d'Unique Plastique, installé sur le Mac d'Alexandre. Déroulé : lister_videos ou un chemin "
    "donné par Alexandre -> lancer_analyse -> etat_analyse jusqu'à termine=true -> lire_paroles, puis lire les planches "
    "et donnees.json dans le dossier de résultats. Suivre le skill emotions-video-unique-plastique pour la lecture. "
    "ecouter_deposer et ecouter_resultat servent à la page « Émotions d'une vidéo », qui y envoie le son d'une vidéo."))


def _nom(video):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", os.path.splitext(os.path.basename(video))[0]).strip("-") or "video"


def _lire(chemin):
    try:
        return json.load(open(chemin, encoding="utf-8"))
    except Exception:
        return None


def _condense(e):
    m, ec = e.get("mesures") or {}, e.get("ecoute") or {}
    r = {"mesures": {k: m.get(k) for k in ("duration", "lufs", "short_term_max_lufs", "lra_lu", "true_peak_dbtp",
                                           "noise_floor_dbfs", "dynamic_range_db", "brightness_hz", "onsets_per_s",
                                           "harmonic_ratio", "bands_db") if k in m}}
    if "ecoute_erreur" in e:
        r["ecoute_erreur"] = e["ecoute_erreur"]
    if ec:
        top = lambda lst, n=2: [f"{t.get('tag')} ({t.get('z')})" for t in (lst or [])[:n]]
        r["resume"] = ec.get("summary")
        r["bruits"] = [{"t": round(x["t"], 1), "indices": [f"{t['tag']} [{t.get('kind')}, {t.get('z')}]" for t in x["tags"][:3]],
                        "force_db": x.get("prominence_db")} for x in ec.get("events", []) if x.get("tags")]
        r["sections"] = [{"debut": s.get("start"), "fin": s.get("end"), "genre": top(s.get("music_genre")),
                          "humeur": top(s.get("music_mood")), "instruments": top(s.get("instruments")),
                          "voix": top(s.get("voice")), "ambiance": top(s.get("ambience"), 1), "etiquette": s.get("label")}
                         for s in ec.get("sections", [])]
        mu = ec.get("music") or {}
        r["musique"] = {k: mu.get(k) for k in ("tempo", "pulse_clarity", "confidence") if k in mu}
        r["coupes"] = ec.get("cuts")
        r["saturation"] = (ec.get("loudness") or {}).get("clipping")
        r["silences"] = (ec.get("loudness") or {}).get("silences")
    return r


@srv.tool(**LECTURE)
def lister_videos() -> dict:
    """Liste les vidéos déposées dans le dossier videos/ du moteur, les plus récentes d'abord."""
    os.makedirs(VIDEOS, exist_ok=True)
    f = [n for n in os.listdir(VIDEOS) if n.lower().endswith(EXT) and not n.startswith(("_", "."))]
    f.sort(key=lambda n: os.path.getmtime(os.path.join(VIDEOS, n)), reverse=True)
    return {"dossier": VIDEOS, "videos": [{"nom": n, "mo": round(os.path.getsize(os.path.join(VIDEOS, n)) / 1e6, 1),
                                           "deja_analysee": os.path.isfile(os.path.join(RESULTATS, _nom(n), "etat.json"))}
                                          for n in f]}


@srv.tool()
def lancer_analyse(video: str, sans_toolbox: bool = False, sans_earshot: bool = False) -> dict:
    """Lance l'analyse complète d'une vidéo en arrière-plan et rend la main tout de suite.

    video : nom d'un fichier du dossier videos/, ou chemin complet sur le Mac. sans_toolbox saute les mesures du
    Aesthetics Toolbox (la partie la plus longue) ; sans_earshot saute l'écoute des bruits et de la musique.
    Suivre ensuite avec etat_analyse(nom)."""
    chemin = os.path.expanduser(video)
    if not os.path.isabs(chemin):
        chemin = os.path.join(VIDEOS, video)
    if not os.path.isfile(chemin):
        return {"erreur": f"vidéo introuvable : {chemin}", "astuce": "déposer le fichier dans " + VIDEOS}
    nom = _nom(chemin); out = os.path.join(RESULTATS, nom); os.makedirs(out, exist_ok=True)
    et = _lire(os.path.join(out, "etat.json"))
    if et and not et.get("termine") and time.time() - os.path.getmtime(os.path.join(out, "etat.json")) < 120:
        return {"nom": nom, "dossier": out, "deja_en_cours": True, "etape": et.get("etape"), "pourcent": et.get("pourcent")}
    cmd = [sys.executable, os.path.join(ICI, "analyse.py"), chemin, "--sortie", out]
    if sans_toolbox:
        cmd.append("--sans-toolbox")
    if sans_earshot:
        cmd.append("--sans-earshot")
    json.dump({"video": chemin, "etape": "lancement", "pourcent": 0, "termine": False, "modules": {}, "erreurs": {}},
              open(os.path.join(out, "etat.json"), "w"), ensure_ascii=False)
    journal = open(os.path.join(out, "journal.txt"), "w")
    subprocess.Popen(cmd, stdout=journal, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    return {"nom": nom, "dossier": out, "lance": True}


@srv.tool(**LECTURE)
def etat_analyse(nom: str) -> dict:
    """Où en est une analyse : étape, pourcentage, modules réussis ou échoués, erreurs, et la fin du journal."""
    out = os.path.join(RESULTATS, _nom(nom))
    et = _lire(os.path.join(out, "etat.json"))
    if not et:
        return {"erreur": f"aucune analyse nommée {nom}", "connues": sorted(os.listdir(RESULTATS)) if os.path.isdir(RESULTATS) else []}
    try:
        et["journal_fin"] = open(os.path.join(out, "journal.txt"), encoding="utf-8", errors="replace").read()[-800:]
    except Exception:
        pass
    et["fichiers"] = sorted(os.listdir(out))
    return et


@srv.tool(**LECTURE)
def lire_paroles(nom: str) -> dict:
    """Les paroles transcrites d'une vidéo analysée : phrases avec leur minutage, mots dits à chaque seconde, et les
    mesures du son par seconde (volume en dB, débit, part de silence)."""
    s = _lire(os.path.join(RESULTATS, _nom(nom), "son.json"))
    if not s:
        return {"erreur": "pas de son.json pour cette analyse"}
    return {"modele": s.get("modele"), "minutage": s.get("minutage"), "phrases": s.get("phrases", []),
            "secondes": s.get("secondes", [])}


@srv.tool(**LECTURE)
def lire_ecoute(nom: str) -> dict:
    """Ce qu'earshot a entendu, en condensé : résumé, mesures objectives (volume normalisé, tempo, brillance), bruits
    reconnus avec leur seconde (les étiquettes sont des indices, pas des certitudes), sections avec le genre et
    l'humeur de la musique, coupes de l'image et saturation. Le détail complet reste dans earshot.json."""
    e = _lire(os.path.join(RESULTATS, _nom(nom), "earshot.json"))
    if not e:
        return {"erreur": "pas de earshot.json pour cette analyse"}
    return _condense(e)


# ---------- son déposé par la page « Émotions d'une vidéo » ----------
PAGE = os.path.join(RESULTATS, "_page")


def _cle(cle):
    c = re.sub(r"[^A-Za-z0-9_-]+", "", str(cle))[:40]
    if not c:
        raise ValueError("clé vide")
    return os.path.join(PAGE, c)


def _menage():
    """Efface les dépôts de la page vieux de plus de deux jours."""
    try:
        for n in os.listdir(PAGE):
            d = os.path.join(PAGE, n)
            if os.path.isdir(d) and time.time() - os.path.getmtime(d) > 2 * 86400:
                shutil.rmtree(d, ignore_errors=True)
    except OSError:
        pass


@srv.tool()
def ecouter_deposer(cle: str, index: int, total: int, format: str, donnees: str, taux: int = 16000,
                    nom: str = "", sans_earshot: bool = False) -> dict:
    """Reçoit de la page le son d'une vidéo, en un ou plusieurs morceaux, puis lance l'écoute en arrière-plan.

    cle : identifiant choisi par la page pour ce dépôt. index, total : rang du morceau (à partir de 0) et nombre de
    morceaux. format : « opus » (paquets Opus 48 kHz mono) ou « pcm16 » (PCM 16 bits mono au taux donné).
    donnees : le morceau en base64. Quand tous les morceaux sont là, la transcription des paroles et l'écoute des
    bruits démarrent ; suivre avec ecouter_resultat(cle). Le son est effacé du disque à la fin de l'écoute."""
    if format not in ("opus", "pcm16"):
        return {"erreur": "format inconnu : " + str(format)}
    if not (0 <= index < total <= 400):
        return {"erreur": "rang de morceau invalide"}
    os.makedirs(PAGE, exist_ok=True); _menage()
    d = _cle(cle); os.makedirs(d, exist_ok=True)
    if os.path.isfile(os.path.join(d, "etat.json")):
        return {"cle": os.path.basename(d), "deja_lance": True}
    try:
        brut = base64.b64decode(donnees, validate=True)
    except Exception:
        return {"erreur": "morceau illisible (base64)"}
    tmp = os.path.join(d, f"partie-{index:03d}.tmp")
    open(tmp, "wb").write(brut); os.replace(tmp, os.path.join(d, f"partie-{index:03d}.bin"))
    recus = sum(os.path.isfile(os.path.join(d, f"partie-{i:03d}.bin")) for i in range(total))
    if recus < total:
        return {"cle": os.path.basename(d), "recus": recus, "total": total, "lance": False}
    json.dump({"format": format, "taux": taux, "total": total, "nom": nom[:200], "sans_earshot": sans_earshot},
              open(os.path.join(d, "meta.json"), "w"), ensure_ascii=False)
    json.dump({"etape": "lancement", "pourcent": 0, "termine": False, "modules": {}, "erreurs": {}},
              open(os.path.join(d, "etat.json"), "w"), ensure_ascii=False)
    journal = open(os.path.join(d, "journal.txt"), "w")
    subprocess.Popen([sys.executable, os.path.join(ICI, "ecoute.py"), d], stdout=journal, stderr=subprocess.STDOUT,
                     stdin=subprocess.DEVNULL, start_new_session=True)
    return {"cle": os.path.basename(d), "recus": recus, "total": total, "lance": True}


@srv.tool(**LECTURE)
def ecouter_resultat(cle: str) -> dict:
    """Où en est l'écoute d'un son déposé par la page, et ce qui est déjà prêt : les paroles (phrases avec leur
    minutage et mots dits à chaque seconde) dès qu'elles sont transcrites, puis le condensé d'earshot (bruits,
    musique, mesures). termine=true quand tout est fini."""
    d = _cle(cle)
    et = _lire(os.path.join(d, "etat.json"))
    if not et:
        return {"erreur": "aucun dépôt avec cette clé"}
    r = {"etape": et.get("etape"), "pourcent": et.get("pourcent"), "termine": bool(et.get("termine")),
         "duree": et.get("duree"), "modules": et.get("modules", {}), "erreurs": et.get("erreurs", {})}
    if not r["termine"] and time.time() - os.path.getmtime(os.path.join(d, "etat.json")) > 600:
        r["termine"] = True; r["erreurs"]["arrêt"] = "l'écoute ne répond plus depuis 10 minutes"
    p = _lire(os.path.join(d, "paroles.json"))
    if p:
        r["paroles"] = {"modele": p.get("modele"), "minutage": p.get("minutage"), "phrases": p.get("phrases", []),
                        "secondes": p.get("secondes", [])}
    e = _lire(os.path.join(d, "earshot.json"))
    if e:
        r["ecoute"] = _condense(e)
    return r


@srv.tool(**LECTURE)
def verifier_moteur() -> dict:
    """Dit ce qui est installé et fonctionnel dans le moteur (résultat de l'installation et du dernier essai)."""
    r = {"racine": RACINE, "python": sys.version.split()[0]}
    try:
        r["installation"] = open(os.path.join(RACINE, "etat-installation.txt"), encoding="utf-8").read().strip().splitlines()
    except Exception:
        r["installation"] = "etat-installation.txt absent : l'installateur n'a pas tourné jusqu'au bout"
    r["essai"] = _lire(os.path.join(RESULTATS, "_essai", "etat.json"))
    r["toolbox"] = os.path.isdir(os.path.join(ICI, "toolbox", "AT"))
    return r


if __name__ == "__main__":
    srv.run("stdio")
