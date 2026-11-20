import glob, os, sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/mots"); import verifier as V
EMOS = "interet surprise intrigue fascination emerveillement amusement joie satisfaction beaute calme soulagement admiration tendresse fierte nostalgie envie excitation anxiete peur douleur malaise degout colere tristesse ennui".split()
FN = "accroche place question pivot montee revelation reponse preuve appel redite digression rien".split()
WIN = {"w02": (0, 3), "w04": (0, 5), "w59": (5, 10), "w10p": (10, 999), "fin3": (-3, None), "tout": (0, 999)}
R = []
for f in sorted(glob.glob("out/v*.csv")):
    v = os.path.basename(f)[:-4]; pro, rows, err = V.lire(f)
    if err or not rows: print("ignoré", v, err[:1]); continue
    n = len(rows); d = {"v": v}
    E = np.array([[r["emo"].get(e, 0) for e in EMOS] for r in rows], float)
    for w, (i, j) in WIN.items():
        sl = slice(i, j) if j is not None else slice(i, None); X = E[sl]
        for k, e in enumerate(EMOS): d[f"{e}|mots|{w}"] = X[:, k].mean() if len(X) else np.nan
        for nm, key in (("ATT", "att"), ("INT", "int"), ("VAL", "val")):
            a = np.array([r[key] for r in rows], float)[sl]; d[f"{nm}|mots|{w}"] = a.mean() if len(a) else np.nan
    for k in ("histoire", "concret", "adresse"): d["MOTS_" + k] = float(pro[k])
    mo = pro["moment"]; d["MOTS_moment"] = 0.0 if mo == "-" else 1.0; d["MOTS_momentpos"] = np.nan if mo == "-" else min(1.0, int(mo) / max(1, n))
    B = [] if pro["boucles"] == "-" else [b.strip().split("-") for b in pro["boucles"].split(",")]
    d["MOTS_nboucles"] = float(len(B)); d["MOTS_boucle3"] = float(any(int(b[0]) <= 2 for b in B)); d["MOTS_ouvertes"] = float(sum(b[1] == "x" for b in B))
    for c in FN: d["MOTS_fn_" + c] = np.mean([r["fn"] == c for r in rows])
    d["MOTS_rien02"] = np.mean([r["fn"] == "rien" for r in rows[:3]])
    R.append(d)
M = pd.DataFrame(R); M.to_csv("large_mots.csv", index=False); print(M.shape)
print(M[[c for c in M.columns if c.startswith("MOTS_")]].describe().loc[["mean", "min", "max"]].round(2).T.to_string())
