import numpy as np, pandas as pd, warnings
from scipy.stats import rankdata
warnings.filterwarnings("ignore"); rng = np.random.default_rng(5)
D = pd.read_csv("/home/claude/correl/large.csv").merge(pd.read_csv("large_mots.csv"), on="v")
print(len(D), "vidéos avec mots lus")
CIB = ["r3", "r5", "r10", "garde5_10", "fin", "lv", "jaime", "partages", "comm", "saves", "abonnes"]
feats = [c for c in D.columns if "|mots|" in c or c.startswith("MOTS_")]
def elig(f, cib):
    if f.startswith("MOTS_"): return f in ("MOTS_boucle3", "MOTS_rien02", "MOTS_histoire", "MOTS_concret", "MOTS_adresse", "MOTS_nboucles") or cib not in ("r3", "r5", "r10", "garde5_10")
    w = f.split("|")[2]
    return {"r3": w == "w02", "r5": w in ("w02", "w04"), "r10": w in ("w02", "w04", "w59"), "garde5_10": w == "w59"}.get(cib, True)
Z0 = np.column_stack([np.ones(len(D)), rankdata(D.dur), (D.an == 2026).astype(float)])
OUT = []
for cib in CIB:
    y = D[cib].values.astype(float); F = [f for f in feats if elig(f, cib) and (D[f].fillna(0) != 0).sum() >= 15 and D[f].nunique() > 2]
    X = np.column_stack([D[f].values.astype(float) for f in F]); X = np.where(np.isnan(X), np.nanmedian(X, 0), X)
    Xr = np.apply_along_axis(rankdata, 0, X); yr = rankdata(y)
    Xe = Xr - Z0 @ np.linalg.lstsq(Z0, Xr, rcond=None)[0]; Xe = (Xe - Xe.mean(0)) / (Xe.std(0) + 1e-12); ye = yr - Z0 @ np.linalg.lstsq(Z0, yr, rcond=None)[0]; ye = (ye - ye.mean()) / ye.std()
    part = Xe.T @ ye / len(ye); mx = []; P = np.zeros(len(F))
    for _ in range(2000): c = Xe.T @ rng.permutation(ye) / len(ye); mx.append(np.abs(c).max()); P += np.abs(c) >= np.abs(part)
    seuil = np.quantile(mx, .95); p = (P + 1) / 2001
    for i, f in enumerate(F): OUT.append(dict(cible=cib, trait=f, n_pos=int((D[f].fillna(0) != 0).sum()), rho_part=round(part[i], 3), p=round(p[i], 4), seuil=round(seuil, 3)))
R = pd.DataFrame(OUT); R.to_csv("correlations_mots.csv", index=False); pd.set_option("display.width", 220)
for cib in CIB:
    r = R[R.cible == cib]; s = r.reindex(r.rho_part.abs().sort_values(ascending=False).index).head(7)
    print(f"\n== {cib} : {len(r)} tests, seuil |{r.seuil.iloc[0]}|, au-dessus : {(r.rho_part.abs() > r.seuil).sum()}"); print(s[["trait", "n_pos", "rho_part", "p"]].to_string(index=False))
