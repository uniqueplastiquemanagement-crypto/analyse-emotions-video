"""Vérifie les lectures : format, deux lignes par seconde, identifiants d'émotions, étendue des notes."""
import os, re, glob, sys, json
EMO = set("interet surprise intrigue fascination emerveillement amusement joie satisfaction beaute calme soulagement admiration tendresse fierte nostalgie envie excitation anxiete peur douleur malaise degout colere tristesse ennui".split())
IN, OUT = "/home/claude/lecture/in", "/home/claude/lecture/out"
def secondes(vdir):
    return sum(1 for l in open(vdir + "/son.txt", encoding="utf-8") if re.match(r"^\d+ \| ", l))
def lire(f):
    L = open(f, encoding="utf-8").read().strip().split("\n"); pro = {}; rows = []; err = []
    if L and L[0].startswith("#"):
        for kv in L[0][1:].split(";"):
            if "=" in kv: k, v = kv.split("=", 1); pro[k.strip()] = v.strip()
    for l in L:
        if l.startswith("#") or l.startswith("t;"): continue
        p = l.split(";")
        if len(p) < 7: err.append("colonnes: " + l[:60]); continue
        try:
            t, couche, att, it, val = int(p[0]), p[1], int(p[2]), int(p[3]), int(p[4])
            emo = {}
            for kv in filter(None, p[5].split(",")):
                k, v = kv.split(":"); k = k.strip()
                if k not in EMO: err.append("émotion inconnue: " + k); continue
                emo[k] = int(v)
            if couche not in ("img", "son") or not (0 <= att <= 3 and 0 <= it <= 3 and -3 <= val <= 3): err.append("valeurs: " + l[:60]); continue
            rows.append(dict(t=t, couche=couche, att=att, int=it, val=val, emo=emo, desc=";".join(p[6:])))
        except Exception as e:
            err.append(f"{type(e).__name__}: {l[:60]}")
    return pro, rows, err
if __name__ == "__main__":
    groupes = sys.argv[1:] or sorted(os.listdir(IN)); tot = ok = 0
    for g in groupes:
        for v in sorted(os.listdir(f"{IN}/{g}")):
            tot += 1; f = f"{OUT}/{v}.csv"; n = secondes(f"{IN}/{g}/{v}")
            if not os.path.isfile(f): print(g, v, "MANQUE"); continue
            pro, rows, err = lire(f)
            im = sorted(r["t"] for r in rows if r["couche"] == "img"); so = sorted(r["t"] for r in rows if r["couche"] == "son")
            pb = []
            if im != list(range(n)): pb.append(f"img {len(im)}/{n}")
            if so != list(range(n)): pb.append(f"son {len(so)}/{n}")
            for k in ("p5", "p10", "pfin"):
                if not re.fullmatch(r"\d+(\.\d+)?", pro.get(k, "")): pb.append("pronostic " + k)
            if err: pb.append(f"{len(err)} erreurs: {err[:2]}")
            if pb: print(g, v, "; ".join(pb))
            else: ok += 1
    print(f"{ok} fichiers bons sur {tot}")
