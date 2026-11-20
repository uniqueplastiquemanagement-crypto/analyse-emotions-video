import sys, glob, os
EMOS = set("interet surprise intrigue fascination emerveillement amusement joie satisfaction beaute calme soulagement admiration tendresse fierte nostalgie envie excitation anxiete peur douleur malaise degout colere tristesse ennui".split())
FN = set("accroche place question pivot montee revelation reponse preuve appel redite digression rien".split())
def nsec(v):
    p = glob.glob(f"/home/claude/mots/in/L*/{v}.txt")[0]; s = open(p, encoding="utf-8").read().split("PAR SECONDE")[1].split("\n")[1:]
    return sum(1 for l in s if l.split("|")[0].strip().isdigit())
def lire(path):
    L = [l.rstrip("\n") for l in open(path, encoding="utf-8") if l.strip()]; err = []; pro = {}
    if not L or not L[0].startswith("#"): return {}, [], ["première ligne : doit commencer par #recit="]
    for kv in L[0][1:].split(";"):
        if "=" in kv: k, x = kv.split("=", 1); pro[k.strip()] = x.strip()
    for k in ("recit", "moment", "boucles", "histoire", "concret", "adresse"):
        if k not in pro: err.append(f"en-tête : il manque {k}")
    for k in ("histoire", "concret", "adresse"):
        if k in pro and pro[k] not in "0123": err.append(f"en-tête : {k} doit valoir 0 à 3")
    if pro.get("moment", "-") != "-" and not pro["moment"].isdigit(): err.append("en-tête : moment doit être une seconde ou -")
    if pro.get("boucles", "-") != "-":
        for b in pro["boucles"].split(","):
            x = b.strip().split("-")
            if len(x) != 2 or not x[0].isdigit() or not (x[1].isdigit() or x[1] == "x"): err.append(f"en-tête : boucle mal écrite « {b} »")
    rows = []
    for i, l in enumerate(L[1:], 2):
        if l.startswith("t;"): continue
        p = l.split(";")
        if len(p) != 7: err.append(f"ligne {i} : {len(p)} champs au lieu de 7"); continue
        try: t, att, it, val = int(p[0]), int(p[1]), int(p[2]), int(p[3])
        except ValueError: err.append(f"ligne {i} : nombre illisible"); continue
        if not (0 <= att <= 3 and 0 <= it <= 3 and -3 <= val <= 3): err.append(f"ligne {i} : note hors bornes")
        emo = {}
        for x in [x for x in p[4].split(",") if x.strip()]:
            try: k, n = x.split(":"); k = k.strip(); n = int(n)
            except ValueError: err.append(f"ligne {i} : émotion mal écrite « {x} »"); continue
            if k not in EMOS or not 1 <= n <= 3: err.append(f"ligne {i} : émotion inconnue ou note hors 1-3 « {x} »")
            emo[k] = n
        if p[5].strip() not in FN: err.append(f"ligne {i} : fn inconnu « {p[5]} »")
        rows.append(dict(t=t, att=att, int=it, val=val, emo=emo, fn=p[5].strip(), why=p[6]))
    return pro, rows, err
if __name__ == "__main__":
    v = sys.argv[1]; path = f"/home/claude/mots/out/{v}.csv"
    if not os.path.exists(path): print("fichier absent :", path); sys.exit(1)
    pro, rows, err = lire(path); n = nsec(v)
    if [r["t"] for r in rows] != list(range(n)): err.append(f"il faut une ligne par seconde de 0 à {n - 1} ; reçu {len(rows)} lignes")
    print("ok" if not err else "\n".join(err[:12]))
