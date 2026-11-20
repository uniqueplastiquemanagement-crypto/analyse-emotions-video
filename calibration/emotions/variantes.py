import numpy as np, pandas as pd, warnings, json
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV, ElasticNetCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RepeatedKFold
from sklearn.metrics import roc_auc_score
warnings.filterwarnings("ignore")
D = pd.read_csv("large.csv"); D["ldur"] = np.log(D.dur); D["an26"] = (D.an == 2026).astype(float)
print("vues médianes 2025 / 2026 :", D[D.an == 2025].vues.median(), D[D.an == 2026].vues.median(), "| ≥100k :", (D[D.an == 2025].vues >= 1e5).mean().round(2), (D[D.an == 2026].vues >= 1e5).mean().round(2))
allf = [c for c in D.columns if "|" in c and not c.startswith(("NBEMO", "CHGT"))]
def cols(layers, ws, minpos=12): return [c for c in allf if c.split("|")[1] in layers and c.split("|")[2] in ws and (D[c].fillna(0) > 0).sum() >= minpos]
W = {"r5": ["w02", "w04"], "r10": ["w02", "w04", "w59"], "fin": ["w02", "w04", "w59", "w10p", "fin3", "tout"], "lv": ["w02", "w04", "w59", "w10p", "fin3", "tout"]}
def cv(X, y, mk, reps=6):
    rk = RepeatedKFold(n_splits=5, n_repeats=reps, random_state=3); P = np.zeros((reps, len(y)))
    for k, (a, b) in enumerate(rk.split(X)): P[k // 5, b] = mk().fit(X[a], y[a]).predict(X[b])
    return P.mean(0), np.mean([spearmanr(p, y)[0] for p in P])
ridge = lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), RidgeCV(alphas=np.logspace(0, 4, 25)))
enet = lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), ElasticNetCV(l1_ratio=[0.5, 0.9], alphas=np.logspace(-2.5, 0, 20), cv=5, max_iter=5000))
for cib in ("r5", "r10", "fin", "lv"):
    y = D[cib].values; y = (y - y.mean()) / y.std(); print(f"\n== {cib}")
    for nm, lay in (("image seule", ["img"]), ("image + son", ["img", "son"]), ("image + son + mix", ["img", "son", "mix"])):
        for extra in ([], ["an26"]):
            c = cols(lay, W[cib]) + ["ldur"] + extra; X = D[c].values.astype(float)
            pm, r = cv(X, y, ridge); pe, re = cv(X, y, enet)
            s = f"  {nm:18s} {'+année' if extra else '      '} {len(c):3d}  ridge {r:+.2f}  enet {re:+.2f}"
            if cib == "lv": s += f"  AUC100k ridge {roc_auc_score(D.vues >= 1e5, pm):.2f} enet {roc_auc_score(D.vues >= 1e5, pe):.2f} | 2026 seul ridge {spearmanr(pm[D.an == 2026], y[D.an == 2026])[0]:+.2f}"
            print(s)

print("\n== 2026 seulement (n=%d) : entraîné et testé dans l'année" % (D.an == 2026).sum())
E = D[D.an == 2026].reset_index(drop=True)
for cib in ("r5", "r10", "fin", "lv"):
    y = E[cib].values; y = (y - y.mean()) / y.std()
    for nm, lay in (("image seule", ["img"]), ("image + son", ["img", "son"])):
        c = [k for k in cols(lay, W[cib]) if (E[k].fillna(0) > 0).sum() >= 8] + ["ldur"]; X = E[c].values.astype(float)
        pm, r = cv(X, y, ridge, reps=10); s2 = f"  {cib:4s} {nm:14s} {len(c):3d} ridge {r:+.2f}"
        if cib == "lv":
            s2 += f"  AUC100k {roc_auc_score(E.vues >= 1e5, pm):.2f}"; q = pd.qcut(pm, 3, labels=["bas", "moyen", "haut"])
            print(s2); print(pd.DataFrame({"q": q, "v": E.vues}).groupby("q").v.agg(n="size", mediane="median", part_100k=lambda s: (s >= 1e5).mean(), part_sous_20k=lambda s: (s < 2e4).mean()).round(2).to_string())
        else: print(s2)
