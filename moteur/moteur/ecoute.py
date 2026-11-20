#!/usr/bin/env python3
"""Écoute du son envoyé par la page « Émotions d'une vidéo ».

La page dépose le son d'une vidéo (Opus, ou PCM 16 bits en secours) par l'outil ecouter_deposer du connecteur.
Ce script le remet en WAV, transcrit les paroles (mlx-whisper sur le Mac) puis fait écouter les bruits et la
musique par earshot. Il écrit etat.json, paroles.json et earshot.json dans le dossier reçu ; ecouter_resultat les lit.

Usage : python ecoute.py DOSSIER   (DOSSIER contient meta.json et les morceaux partie-000.bin, partie-001.bin…)
"""
import json, os, struct, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import analyse as A  # noqa: E402  (mêmes fonctions que l'analyse complète : paroles, earshot, recollage des mots)


# ---------- Opus brut -> fichier Ogg (que ffmpeg sait lire) ----------
def _table_crc():
    t = []
    for i in range(256):
        r = i << 24
        for _ in range(8):
            r = ((r << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if r & 0x80000000 else (r << 1) & 0xFFFFFFFF
        t.append(r)
    return t


_CRC = _table_crc()


def _crc(data):
    c = 0
    for b in data:
        c = ((c << 8) & 0xFFFFFFFF) ^ _CRC[((c >> 24) ^ b) & 0xFF]
    return c


def _page(serie, numero, granule, paquets, drapeaux):
    lacets = bytearray()
    for p in paquets:
        lacets += b"\xff" * (len(p) // 255) + bytes([len(p) % 255])
    tete = b"OggS" + bytes([0, drapeaux]) + struct.pack("<qIII", granule, serie, numero, 0) + bytes([len(lacets)]) + bytes(lacets)
    corps = b"".join(paquets)
    return tete[:22] + struct.pack("<I", _crc(tete + corps)) + tete[26:] + corps


def lire_paquets(brut):
    """Flux de la page : pour chaque paquet Opus, longueur (u16), nombre d'échantillons à 48 kHz (u16), octets."""
    paquets, o = [], 0
    while o + 4 <= len(brut):
        n, ech = struct.unpack_from("<HH", brut, o); o += 4
        if n == 0 or o + n > len(brut):
            raise ValueError("flux Opus incomplet ou abîmé")
        paquets.append((brut[o:o + n], ech or 960)); o += n
    if not paquets:
        raise ValueError("aucun paquet Opus reçu")
    return paquets


def ogg_opus(paquets, canaux=1, preskip=312):
    serie = 0x55504153
    entete = b"OpusHead" + bytes([1, canaux]) + struct.pack("<HIh", preskip, 48000, 0) + bytes([0])
    marque = b"unique-plastique"
    etiquettes = b"OpusTags" + struct.pack("<I", len(marque)) + marque + struct.pack("<I", 0)
    out = [_page(serie, 0, 0, [entete], 2), _page(serie, 1, 0, [etiquettes], 0)]
    numero, granule, lot, lacets = 2, preskip, [], 0
    for i, (p, ech) in enumerate(paquets):
        besoin = len(p) // 255 + 1
        if lot and (lacets + besoin > 255 or len(lot) >= 50):
            out.append(_page(serie, numero, granule, lot, 0)); numero += 1; lot, lacets = [], 0
        lot.append(p); lacets += besoin; granule += ech
    out.append(_page(serie, numero, granule, lot, 4))
    return b"".join(out)


# ---------- déroulé ----------
def assembler(dossier, meta):
    brut = b""
    for i in range(int(meta["total"])):
        brut += open(os.path.join(dossier, f"partie-{i:03d}.bin"), "rb").read()
    return brut


def main():
    dossier = os.path.abspath(sys.argv[1])
    meta = json.load(open(os.path.join(dossier, "meta.json"), encoding="utf-8"))
    et = A.Etat(dossier, meta.get("nom") or "son déposé par la page")
    try:
        ffmpeg, _ = A.binaires()
        brut = assembler(dossier, meta)
        source = os.path.join(dossier, "source.ogg" if meta["format"] == "opus" else "source.pcm")
        if meta["format"] == "opus":
            open(source, "wb").write(ogg_opus(lire_paquets(brut)))
            entree = ["-i", source]
        else:
            open(source, "wb").write(brut)
            entree = ["-f", "s16le", "-ar", str(int(meta.get("taux") or 16000)), "-ac", "1", "-i", source]
        wav16, wav48 = os.path.join(dossier, "son.wav"), os.path.join(dossier, "son48.wav")
        A.run([ffmpeg, "-v", "error", "-y", *entree, "-ac", "1", "-ar", str(A.SR), wav16])
        A.run([ffmpeg, "-v", "error", "-y", *entree, "-ac", "1", "-ar", "48000", wav48])
        et.d["duree"] = round(os.path.getsize(wav16) / 2 / A.SR, 2)
    except Exception as e:
        et.d["erreurs"]["fatale"] = f"{type(e).__name__}: {e}"[:600]; et.d["termine"] = True
        et.etape("arrêt : le son reçu n'a pas pu être ouvert", 0)
        raise SystemExit(1)

    et.etape("paroles : transcription", 20)
    sherpa = os.environ.get("ANALYSE_SHERPA")
    if sherpa:  # secours hors Mac (essais)
        audio = A.charger_audio(ffmpeg, wav16); ms = A.mesures_son(audio)
        p = et.module("paroles", lambda: A.paroles_sherpa(audio, ms[1], ms[2], sherpa))
    else:
        p = et.module("paroles", lambda: A.paroles_mlx(wav16))
    if p:
        n = int(et.d["duree"]) + 1
        p["secondes"] = [{"t": t, "mots": A.coller([m["mot"] for m in p["mots"] if int(m["debut"]) == t])} for t in range(n)]
        p.pop("mots", None)
        tmp = os.path.join(dossier, "paroles.json.tmp")
        json.dump(p, open(tmp, "w"), ensure_ascii=False); os.replace(tmp, os.path.join(dossier, "paroles.json"))

    if not meta.get("sans_earshot"):
        et.etape("earshot : bruits et musique", 55)
        e = et.module("earshot", lambda: A.earshot(wav48))
        if e:
            tmp = os.path.join(dossier, "earshot.json.tmp")
            json.dump(e, open(tmp, "w"), ensure_ascii=False); os.replace(tmp, os.path.join(dossier, "earshot.json"))
            if "ecoute_erreur" in e:
                et.d["erreurs"]["earshot écoute"] = e["ecoute_erreur"]; et.ecrire()

    for f in os.listdir(dossier):  # le son lui-même ne reste pas sur le disque
        if f.startswith(("partie-", "source.", "son")) and f.endswith((".bin", ".ogg", ".pcm", ".wav")):
            try:
                os.remove(os.path.join(dossier, f))
            except OSError:
                pass
    et.d["termine"] = True
    et.etape("terminé", 100)


if __name__ == "__main__":
    main()
