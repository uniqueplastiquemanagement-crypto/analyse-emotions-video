import numpy as np, pandas as pd, itertools, json, warnings
from scipy.stats import rankdata, spearmanr
warnings.filterwarnings("ignore")
D = pd.read_csv("large.csv"); rng = np.random.default_rng(7)
EMOS = "interet surprise intrigue fascination emerveillement amusement joie satisfaction beaute calme soulagement admiration tendresse fierte nostalgie envie excitation anxiete peur douleur malaise degout colere tristesse ennui".split()
CIB = ["r3", "r5", "r10", "garde5_10", "fin", "moy_rel", "lv", "jaime", "partages", "comm", "saves", "abonnes"]
feats = [c for c in D.columns if "|" in c]
print("années:", D.an.value_counts().to_dict(), "| vues>=100k:", int((D.vues >= 1e5).sum()), "| durée<10 s:", int((D.dur < 10).sum()))
# contrôles : durée (rang), année, lecteur
Z = np.column_stack([np.ones(len(D)), rankdata(D.dur), (D.an == 2026).astype(float)] + [(D.lecteur == l).astype(float) for l in sorted(D.lecteur.unique())[1:]])
Z0 = np.column_stack([np.ones(len(D)), rankdata(D.dur), (D.an == 2026).astype(float)])
def resid(y, Z): 
    b = np.linalg.lstsq(Z, y, rcond=None)[0]; return y - Z @ b
def prep(col, Z):
    x = D[col].values.astype(float); ok = ~np.isnan(x); r = np.full(len(x), np.nan); r[ok] = rankdata(x[ok]); return r
def eligible(f, cib):
    w = f.split("|")[2]
    if cib in ("r3",): return w == "w02"
    if cib == "r5": return w in ("w02", "w04")
    if cib == "r10": return w in ("w02", "w04", "w59")
    if cib == "garde5_10": return w == "w59"
    return True
OUT = []
for cib in CIB:
    y = D[cib].values.astype(float)
    F = [f for f in feats if eligible(f, cib) and (D[f].fillna(0) > 0).sum() >= 15 and D[f].notna().sum() >= 150 and D[f].nunique() > 3]
    X = np.column_stack([D[f].values.astype(float) for f in F]); ok = ~np.isnan(X).any(1) & ~np.isnan(y)
    # sous-ensemble commun pour la permutation : remplacer NaN par médiane (fenêtres absentes des vidéos courtes)
    Xf = np.where(np.isnan(X), np.nanmedian(X, 0), X); m = ~np.isnan(y)
    Xr = np.apply_along_axis(rankdata, 0, Xf[m]); yr = rankdata(y[m])
    def corrs(Xr, yr, Zm):
        Xe = Xr - Zm @ np.linalg.lstsq(Zm, Xr, rcond=None)[0]; ye = yr - Zm @ np.linalg.lstsq(Zm, yr, rcond=None)[0]
        Xe = (Xe - Xe.mean(0)) / (Xe.std(0) + 1e-12); ye = (ye - ye.mean()) / ye.std(); return Xe.T @ ye / len(ye)
    brut = corrs(Xr, yr, np.ones((m.sum(), 1))); part = corrs(Xr, yr, Z0[m]); partL = corrs(Xr, yr, Z[m])
    # permutation (max |rho| partiel) pour le seuil familial 5 %
    mx = []
    Xe = Xr - Z0[m] @ np.linalg.lstsq(Z0[m], Xr, rcond=None)[0]; Xe = (Xe - Xe.mean(0)) / (Xe.std(0) + 1e-12)
    ye = yr - Z0[m] @ np.linalg.lstsq(Z0[m], yr, rcond=None)[0]; ye = (ye - ye.mean()) / ye.std()
    P = np.zeros(len(F))
    for _ in range(2000):
        yp = rng.permutation(ye); c = Xe.T @ yp / len(yp); mx.append(np.abs(c).max()); P += (np.abs(c) >= np.abs(part))
    seuil = np.quantile(mx, 0.95); p = (P + 1) / 2001
    # BH
    o = np.argsort(p); q = np.empty(len(p)); q[o] = np.minimum.accumulate((p[o] * len(p) / (np.arange(len(p)) + 1))[::-1])[::-1]
    for i, f in enumerate(F):
        OUT.append(dict(cible=cib, trait=f, n_pos=int((D[f].fillna(0) > 0).sum()), rho=round(brut[i], 3), rho_part=round(part[i], 3), rho_lect=round(partL[i], 3), p=round(p[i], 4), q=round(min(1, q[i]), 3), seuil=round(seuil, 3), ntests=len(F)))
R = pd.DataFrame(OUT); R.to_csv("correlations.csv", index=False)
pd.set_option("display.width", 250)
for cib in CIB:
    r = R[R.cible == cib]; s = r.reindex(r.rho_part.abs().sort_values(ascending=False).index).head(9)
    print(f"\n== {cib} : {len(r)} tests, seuil familial 5 % = |{r.seuil.iloc[0]}|, q<0,10 : {(r.q < 0.10).sum()}, |rho|>seuil : {(r.rho_part.abs() > r.seuil).sum()}")
    print(s[["trait", "n_pos", "rho", "rho_part", "rho_lect", "p", "q"]].to_string(index=False))
