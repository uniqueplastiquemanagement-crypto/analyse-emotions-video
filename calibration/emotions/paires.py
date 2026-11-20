import numpy as np, pandas as pd, itertools, warnings
from scipy.stats import rankdata
import statsmodels.api as sm
warnings.filterwarnings("ignore"); rng = np.random.default_rng(11)
D = pd.read_csv("large.csv"); S = pd.read_csv("secondes.csv")
EMOS = "interet surprise intrigue fascination emerveillement amusement joie satisfaction beaute calme soulagement admiration tendresse fierte nostalgie envie excitation anxiete peur douleur malaise degout colere tristesse ennui".split()
Z0 = np.column_stack([np.ones(len(D)), rankdata(D.dur), (D.an == 2026).astype(float)])
def res(y):
    y = np.asarray(y, float); m = ~np.isnan(y); r = np.full(len(y), np.nan); yy = y[m]; r[m] = yy - Z0[m] @ np.linalg.lstsq(Z0[m], yy, rcond=None)[0]; return r
print("=== B. PAIRES d'émotions (présentes dans la même tranche, couche image+son) ===")
rows = []
for cib, w, seuilp in (("r5", "w04", 0), ("r10", "w59", 0), ("fin", "tout", 0.10), ("lv", "tout", 0.10), ("partages", "tout", 0.10), ("jaime", "tout", 0.10)):
    y = res(D[cib]); P = {e: (D[f"{e}|mix|{w}"].fillna(0) > seuilp).values for e in EMOS}
    for a, b in itertools.combinations(EMOS, 2):
        both = P[a] & P[b]; ao = P[a] & ~P[b]; bo = ~P[a] & P[b]; nn = ~P[a] & ~P[b]; ok = ~np.isnan(y)
        if both.sum() < 15 or (~both & ok).sum() < 15: continue
        diff = np.nanmean(y[both]) - np.nanmean(y[~both])
        syn = np.nan
        if min(ao.sum(), bo.sum(), nn.sum()) >= 8: syn = np.nanmean(y[both]) - np.nanmean(y[ao]) - np.nanmean(y[bo]) + np.nanmean(y[nn])
        # permutation sur la différence
        yo = y[ok]; bo_ = both[ok]; obs = yo[bo_].mean() - yo[~bo_].mean(); c = 0
        for _ in range(1000):
            yp = rng.permutation(yo); c += abs(yp[bo_].mean() - yp[~bo_].mean()) >= abs(obs)
        rows.append(dict(cible=cib, tranche=w, a=a, b=b, n_deux=int(both.sum()), ecart=diff, synergie=syn, p=(c + 1) / 1001,
                         brut_deux=D.loc[both, cib].median(), brut_autres=D.loc[~both, cib].median()))
B = pd.DataFrame(rows)
for cib, g in B.groupby("cible", sort=False):
    p = g.p.values; o = np.argsort(p); q = np.empty(len(p)); q[o] = np.minimum.accumulate((p[o] * len(p) / (np.arange(len(p)) + 1))[::-1])[::-1]; B.loc[g.index, "q"] = q
B.to_csv("paires.csv", index=False); pd.set_option("display.width", 250)
for cib, g in B.groupby("cible", sort=False):
    print(f"\n-- {cib} ({g.tranche.iloc[0]}) : {len(g)} paires testées, q<0,10 : {(g.q < 0.10).sum()}")
    print(g.reindex(g.ecart.abs().sort_values(ascending=False).index).head(7)[["a", "b", "n_deux", "brut_deux", "brut_autres", "ecart", "synergie", "p", "q"]].round(3).to_string(index=False))

print("\n=== C. Émotion dominante de la seconde 0 (image) et r3 / r5 ===")
dom = []
for _, r in D.iterrows():
    pass
L = pd.read_csv("secondes.csv"); s0 = L[L.t == 0].set_index("v")
cols = [f"{e}|img" for e in EMOS]; d0 = s0[cols].idxmax(axis=1).str.split("|").str[0]; d0[s0[cols].max(axis=1) == 0] = "aucune"
T = D.set_index("v").join(d0.rename("dom0")); T["r5res"] = res(D.r5); T["r3res"] = res(D.r3)
g = T.groupby("dom0").agg(n=("r5", "size"), r3=("r3", "median"), r5=("r5", "median"), r5_ajuste=("r5res", "mean"), vues=("vues", "median")).sort_values("n", ascending=False)
print(g[g.n >= 6].round(3).to_string())
# force de l'émotion à la seconde 0
for e in ("intrigue", "surprise", "interet", "amusement"):
    x = s0[f"{e}|img"].reindex(D.v).values; print(e, "seconde 0 image : niveau 0/1/2/3 → r5 médian", {int(k): (round(float(np.median(D.r5.values[x == k])), 2), int((x == k).sum())) for k in sorted(set(x))})

print("\n=== D. Seconde par seconde : qui reste d'une seconde à la suivante (effets joints, position et vidéo contrôlées) ===")
S = S[(S.t <= 45) & S.garde.notna() & (S.garde > 0)].copy(); S["y"] = np.log(S.garde) * 100
def fe(S, ycol, xcols):
    X = S[xcols].astype(float).copy(); y = S[ycol].astype(float).copy()
    tt = pd.get_dummies(S.t.clip(upper=30), prefix="t", drop_first=True).astype(float); X = pd.concat([X, tt], axis=1)
    Xd = X - X.groupby(S.v).transform("mean"); yd = y - y.groupby(S.v).transform("mean")
    m = sm.OLS(yd, Xd).fit(cov_type="cluster", cov_kwds={"groups": S.v.values}); return m
xc = [f"{e}|{c}" for c in ("img", "son") for e in EMOS if (S[f"{e}|{c}"] > 0).sum() >= 80]
Sb = S.copy(); Sb[xc] = (Sb[xc] > 0).astype(float)
m = fe(Sb, "y", xc); r = pd.DataFrame({"coef_%": m.params[xc], "p": m.pvalues[xc], "n_sec": [int(Sb[c].sum()) for c in xc]}).sort_values("coef_%")
print("variable = émotion présente à la seconde t ; effet = points de % de spectateurs gardés jusqu'à t+1")
print(pd.concat([r.head(7), r.tail(9)]).round(3).to_string())
m2 = fe(S, "y", ["att_img", "att_son", "int_img", "int_son", "val_img", "val_son"]); print(pd.DataFrame({"coef_%": m2.params[:6], "p": m2.pvalues[:6]}).round(3).to_string())
print("\n=== E. Seconde par seconde : où tombent les j'aime ===")
S2 = pd.read_csv("secondes.csv"); S2 = S2[(S2.t <= 45) & S2.jaime.notna()].copy(); S2["y"] = S2.jaime * 100; S2b = S2.copy(); S2b[xc] = (S2b[xc] > 0).astype(float)
m = fe(S2b, "y", xc); r = pd.DataFrame({"coef": m.params[xc], "p": m.pvalues[xc]}).sort_values("coef"); print(pd.concat([r.head(4), r.tail(7)]).round(3).to_string())
