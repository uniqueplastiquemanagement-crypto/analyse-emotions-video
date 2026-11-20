import numpy as np, pandas as pd, warnings, json
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV, LogisticRegressionCV
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RepeatedKFold
from sklearn.metrics import roc_auc_score
warnings.filterwarnings("ignore")
D = pd.read_csv("large.csv"); T = pd.read_csv("/home/claude/lecture/table-traits.csv").set_index("v"); Ty = pd.read_csv("/home/claude/lecture/table-types.csv").set_index("v")
D = D.join(T[["parole_debut", "mots3", "mots5", "vol0", "vol3", "question5", "musique", "anglais", "texte0", "texte5", "visage0", "mains5", "produit5", "matiere5", "machine5", "chgt5"]], on="v").join(Ty[["ent", "obj", "epr"]], on="v")
D["ldur"] = np.log(D.dur)
allf = [c for c in D.columns if "|" in c]
def win(ws): return [c for c in allf if c.split("|")[2] in ws and (D[c].fillna(0) > 0).sum() >= 12]
TR = ["parole_debut", "mots3", "mots5", "vol0", "vol3", "question5", "musique", "anglais", "texte0", "texte5", "visage0", "mains5", "produit5", "matiere5", "machine5", "chgt5", "ent", "obj"]
SETS = {"r5": {"durée seule": ["ldur"], "émotions 0-4 s": win(["w02", "w04"]) + ["ldur"], "émotions + traits": win(["w02", "w04"]) + TR + ["ldur"], "traits seuls": TR + ["ldur"]},
        "r10": {"durée seule": ["ldur"], "émotions 0-9 s": win(["w02", "w04", "w59"]) + ["ldur"], "émotions + traits": win(["w02", "w04", "w59"]) + TR + ["ldur"]},
        "fin": {"durée seule": ["ldur"], "émotions tout": win(["w02", "w04", "w59", "w10p", "fin3", "tout"]) + ["ldur"], "émotions + traits": win(["w02", "w04", "w59", "w10p", "fin3", "tout"]) + TR + ["ldur"]},
        "lv": {"durée seule": ["ldur"], "émotions tout": win(["w02", "w04", "w59", "w10p", "fin3", "tout"]) + ["ldur"], "émotions + traits": win(["w02", "w04", "w59", "w10p", "fin3", "tout"]) + TR + ["ldur"]}}
def cv(X, y, mk, reps=6, grp=None):
    rk = RepeatedKFold(n_splits=5, n_repeats=reps, random_state=3); P = np.zeros((reps, len(y))); i = 0
    for k, (a, b) in enumerate(rk.split(X)):
        m = mk().fit(X[a], y[a]); P[k // 5, b] = m.predict(X[b])
    return P
ridge = lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), RidgeCV(alphas=np.logspace(0, 4, 25)))
rf = lambda: make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=300, min_samples_leaf=4, max_features=0.3, random_state=0, n_jobs=-1))
PRED = {}
for cib, sets in SETS.items():
    y = D[cib].values; print(f"\n== {cib} (hors échantillon, 5 plis × 6) ==")
    for nm, cols in sets.items():
        X = D[cols].values.astype(float)
        for mn, mk in (("ridge", ridge), ("forêt", rf)):
            if nm == "durée seule" and mn == "forêt": continue
            P = cv(X, y, mk); pm = P.mean(0); rs = [spearmanr(p, y)[0] for p in P]
            r26 = spearmanr(pm[D.an == 2026], y[D.an == 2026])[0]; r25 = spearmanr(pm[D.an == 2025], y[D.an == 2025])[0]
            # au-delà de la durée et de l'année
            Z = np.column_stack([np.ones(len(y)), D.ldur, D.an == 2026]).astype(float); e = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
            print(f"  {nm:20s} {mn:6s} {len(cols):3d} traits  rho={np.mean(rs):+.2f} (±{np.std(rs):.2f})  2025={r25:+.2f} 2026={r26:+.2f}  net durée/année={spearmanr(e(pm), e(y))[0]:+.2f}  R²={1 - ((pm - y) ** 2).sum() / ((y - y.mean()) ** 2).sum():+.2f}")
            PRED[(cib, nm, mn)] = pm
# référence : le pari à l'œil du lecteur
print("\nréférence, pari à l'œil : p5~r5 %.2f | p10~r10 %.2f | pfin~fin %.2f | p5~lv %.2f" % (spearmanr(D.p5, D.r5)[0], spearmanr(D.p10, D.r10)[0], spearmanr(D.pfin, D.fin)[0], spearmanr(D.p5, D.lv)[0]))
# classes de vues à partir des prédictions hors échantillon
print("\n== Vues : ce que donnent les prédictions hors échantillon ==")
for key in (("lv", "émotions tout", "ridge"), ("lv", "émotions tout", "forêt"), ("lv", "émotions + traits", "forêt")):
    pm = PRED[key]; y = D.vues.values
    print(key, "AUC ≥100k = %.2f | AUC ≥ médiane = %.2f" % (roc_auc_score(y >= 1e5, pm), roc_auc_score(y >= np.median(y), pm)))
    q = pd.qcut(pm, 4, labels=["bas", "moyen-", "moyen+", "haut"])
    print(pd.DataFrame({"q": q, "v": y}).groupby("q").v.agg(n="size", mediane="median", part_100k=lambda s: (s >= 1e5).mean(), part_sous_10k=lambda s: (s < 1e4).mean()).round(2).to_string())
# combiner : r5, r10, fin prédits -> vues
Xs = np.column_stack([PRED[("r5", "émotions 0-4 s", "ridge")], PRED[("r10", "émotions 0-9 s", "ridge")], PRED[("fin", "émotions tout", "ridge")], D.ldur])
print("corrélation des rétentions PRÉDITES avec les vues réelles :", [round(spearmanr(Xs[:, i], D.lv)[0], 2) for i in range(3)])
np.save("pred.npy", np.column_stack([PRED[("r5", "émotions 0-4 s", "ridge")], PRED[("r10", "émotions 0-9 s", "ridge")], PRED[("fin", "émotions tout", "ridge")], PRED[("lv", "émotions tout", "forêt")]]))
