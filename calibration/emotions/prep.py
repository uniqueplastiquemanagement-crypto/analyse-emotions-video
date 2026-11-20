"""Table large : une ligne par vidéo, toutes les émotions par tranche et par couche, plus les cibles."""
import json, os, sys, glob, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/lecture"); import verifier as V
EMOS = "interet surprise intrigue fascination emerveillement amusement joie satisfaction beaute calme soulagement admiration tendresse fierte nostalgie envie excitation anxiete peur douleur malaise degout colere tristesse ennui".split()
cle = json.load(open("/home/claude/lecture/prive/cle-anonyme.json"))
st = {json.loads(l)["t"]: json.loads(l) for l in open("/mnt/user-data/outputs/calibration/tiktok-stats.jsonl") if l.strip()}
lect = {os.path.basename(os.path.dirname(p)): p.split("/")[-3] for p in glob.glob("/home/claude/lecture/in/L*/v*/son.txt")}
WIN = {"w02": (0, 3), "w04": (0, 5), "w59": (5, 10), "w10p": (10, 999), "fin3": (-3, None), "tout": (0, 999)}
R, SEC = [], []
for f in sorted(glob.glob("/home/claude/lecture/out/v*.csv")):
    v = os.path.basename(f)[:-4]; pro, rows, err = V.lire(f); s = st[int(cle[v].split("-")[1])]; a = s["a"]
    ret = np.array(a["ret"], float); lk = np.array(a["likes"] or [], float)
    im = {r["t"]: r for r in rows if r["couche"] == "img"}; so = {r["t"]: r for r in rows if r["couche"] == "son"}; n = min(len(im), len(so))
    if n < 4: continue
    E = {"img": np.array([[im[t]["emo"].get(e, 0) for e in EMOS] for t in range(n)], float), "son": np.array([[so[t]["emo"].get(e, 0) for e in EMOS] for t in range(n)], float)}
    E["mix"] = np.maximum(E["img"], E["son"])
    P = max(1, s["plays"]); g = lambda i: ret[min(i, len(ret) - 1)]
    d = dict(v=v, lecteur=lect.get(v, "?"), an=pd.Timestamp(s["t"], unit="s").year, dur=s["dur"] / 1000, n=n, vues=s["plays"], lv=np.log10(P),
             r1=g(1), r2=g(2), r3=g(3), r5=g(5), r10=g(10), garde5_10=g(10) / g(5) if g(5) > 0 else np.nan, fin=a["fin"], moy_rel=(a["avg"] or 0) / max(1, s["dur"] / 1000),
             jaime=s["likes"] / P, partages=s["shares"] / P, comm=s["comments"] / P, saves=s["saves"] / P, abonnes=(a["nf"] or 0) / P,
             p5=float(pro["p5"]), p10=float(pro["p10"]), pfin=float(pro["pfin"]))
    for c in ("img", "son", "mix"):
        for w, (i, j) in WIN.items():
            X = E[c][i:j] if j is not None else E[c][i:]
            for k, e in enumerate(EMOS):
                d[f"{e}|{c}|{w}"] = X[:, k].mean() if len(X) else np.nan
        A = np.array([(im if c != "son" else so)[t]["att"] for t in range(n)], float)
        I = np.array([(im if c != "son" else so)[t]["int"] for t in range(n)], float)
        Vv = np.array([(im if c != "son" else so)[t]["val"] for t in range(n)], float)
        if c == "mix":
            A = np.maximum(A, [so[t]["att"] for t in range(n)]); I = np.maximum(I, [so[t]["int"] for t in range(n)]); Vv = (Vv + np.array([so[t]["val"] for t in range(n)])) / 2
        for w, (i, j) in WIN.items():
            sl = slice(i, j) if j is not None else slice(i, None)
            for nm, arr in (("ATT", A), ("INT", I), ("VAL", Vv)):
                d[f"{nm}|{c}|{w}"] = arr[sl].mean() if len(arr[sl]) else np.nan
        d[f"NBEMO|{c}|w04"] = (E[c][:5] > 0).any(0).sum()            # variété d'émotions dans les 5 premières s
        d[f"CHGT|{c}|w04"] = sum((E[c][t] > 0).tolist() != (E[c][t - 1] > 0).tolist() for t in range(1, min(5, n)))  # changements d'émotion
    R.append(d)
    m = min(n, len(ret))
    for t in range(0, m - 1):
        row = dict(v=v, t=t, m=m, garde=ret[t + 1] / ret[t] if ret[t] > 0 else np.nan, jaime=lk[t] if t < len(lk) else np.nan,
                   att_img=im[t]["att"], att_son=so[t]["att"], int_img=im[t]["int"], int_son=so[t]["int"], val_img=im[t]["val"], val_son=so[t]["val"])
        for c in ("img", "son"):
            for k, e in enumerate(EMOS): row[f"{e}|{c}"] = E[c][t, k]
        SEC.append(row)
D = pd.DataFrame(R); S = pd.DataFrame(SEC); D.to_csv("large.csv", index=False); S.to_csv("secondes.csv", index=False)
print(D.shape, S.shape, D.lecteur.value_counts().describe()[["count", "min", "max"]].tolist())
print(D[["dur", "n", "r3", "r5", "r10", "fin", "lv", "jaime", "partages", "comm", "saves", "abonnes"]].describe().loc[["min", "50%", "max"]].round(4).to_string())
tot = {e: (D[f"{e}|mix|tout"] > 0).sum() for e in EMOS}; t5 = {e: (D[f"{e}|mix|w04"] > 0).sum() for e in EMOS}
print("vidéos où l'émotion apparaît (toute la vidéo / 5 premières s):"); print({e: (tot[e], t5[e]) for e in EMOS})
