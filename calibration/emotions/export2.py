"""Modèles du pari, version 2 : élan du compte + estimé de vues « qui ose » (calage par quantiles sur 2026).
Si /home/claude/mots/large_mots.csv existe, ajoute les traits des mots (modèle imgsonmots)."""
import numpy as np, pandas as pd, warnings, json, os
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import RepeatedKFold
from sklearn.metrics import roc_auc_score
warnings.filterwarnings("ignore")
D = pd.read_csv("large.csv"); D["ldur"] = np.log(D.dur); D["an26"] = (D.an == 2026).astype(float)
st = sorted([json.loads(l) for l in open("/mnt/user-data/outputs/calibration/tiktok-stats.jsonl") if l.strip()], key=lambda s: s["t"])
T = np.array([s["t"] for s in st]); LV = np.log10(np.maximum(1, [s["plays"] for s in st]))
cle = json.load(open("/home/claude/lecture/prive/cle-anonyme.json")); D["t"] = D.v.map(lambda v: int(cle[v].split("-")[1]))
def elan(t, k=5, gap=3 * 86400):
    x = LV[T < t - gap][-k:]; return np.median(x) if len(x) >= 3 else np.nan
D["elan"] = D.t.map(elan); ELAN0 = float(elan(T.max() + 1))
MOTS = os.path.exists("/home/claude/mots/large_mots.csv")
if MOTS: D = D.merge(pd.read_csv("/home/claude/mots/large_mots.csv"), on="v", how="left")
allf = [c for c in D.columns if "|" in c and not c.startswith(("NBEMO", "CHGT"))]
def cols(layers, ws): return [c for c in allf if c.split("|")[1] in layers and c.split("|")[2] in ws and (D[c].fillna(0) != 0).sum() >= 12]
W = {"r5": ["w02", "w04"], "r10": ["w02", "w04", "w59"], "fin": ["w02", "w04", "w59", "w10p", "fin3", "tout"], "lv": ["w02", "w04", "w59", "w10p", "fin3", "tout"]}
AL = np.logspace(0, 4, 25)
class M:
    def fit(s, X, y):
        s.med = np.nanmedian(X, 0); X = np.where(np.isnan(X), s.med, X); s.mu = X.mean(0); s.sd = X.std(0); s.sd[s.sd == 0] = 1
        s.r = RidgeCV(alphas=AL).fit((X - s.mu) / s.sd, y); return s
    def predict(s, X): X = np.where(np.isnan(X), s.med, X); return s.r.predict((X - s.mu) / s.sd)
def oos(X, y, reps=10):
    rk = RepeatedKFold(n_splits=5, n_repeats=reps, random_state=3); P = np.zeros((reps, len(y)))
    for k, (a, b) in enumerate(rk.split(X)): P[k // 5, b] = M().fit(X[a], y[a]).predict(X[b])
    return P.mean(0)
r4 = lambda a: [float(f"{v:.4g}") for v in a]
OUT = {"n": len(D), "n26": int((D.an == 2026).sum()), "date": "2026-11-20", "elan0": round(ELAN0, 3), "models": {}}; a26 = (D.an == 2026).values
modes = [("img", ["img"]), ("imgson", ["img", "son"])] + ([("imgsonmots", ["img", "son", "mots"])] if MOTS else [])
QS = np.linspace(0, 1, 21)
for mode, lay in modes:
    OUT["models"][mode] = {}
    for cib in ("r5", "r10", "fin", "lv"):
        extra = [c for c in D.columns if c.startswith("MOTS_")] if "mots" in lay else []
        lay2 = [l for l in lay if l != "mots"] if ("mots" in lay and cib in ("fin", "lv")) else lay   # fin et vues : émotions image + son, plus les traits du récit seulement
        c = cols(lay2, W[cib]) + extra + ["ldur", "an26"] + (["elan"] if cib == "lv" else []); X = D[c].values.astype(float); y = D[cib].values.astype(float)
        p = oos(X, y); m = M().fit(X, y); res = (y - p)[a26]
        o = {"f": c, "med": r4(m.med), "mu": r4(m.mu), "sd": r4(m.sd), "w": r4(m.r.coef_), "b": float(f"{m.r.intercept_:.5g}"),
             "rho": round(float(spearmanr(p, y)[0]), 2), "rho26": round(float(spearmanr(p[a26], y[a26])[0]), 2), "lo": round(float(np.quantile(res, .1)), 3), "hi": round(float(np.quantile(res, .9)), 3)}
        if cib == "lv":
            pv = p[a26]; ya = y[a26]; v = D.vues.values[a26]; c1, c2 = np.quantile(pv, [1 / 3, 2 / 3]); o["cuts"] = [round(float(c1), 3), round(float(c2), 3)]; o["auc26"] = round(float(roc_auc_score(v >= 1e5, pv)), 2); o["tiers"] = []
            for lo_, hi_ in ((-9, c1), (c1, c2), (c2, 99)):
                s = v[(pv > lo_) & (pv <= hi_)]; o["tiers"].append({"n": int(len(s)), "med": int(np.median(s)), "p100k": round(float((s >= 1e5).mean()), 2), "p20k": round(float((s < 2e4).mean()), 2), "q1": int(np.quantile(s, .25)), "q3": int(np.quantile(s, .75))})
            o["qp"] = r4(np.quantile(pv, QS)); o["qv"] = r4(np.quantile(ya, QS))      # calage par quantiles : rang prévu -> vues réelles de 2026
            est = np.interp(pv, np.quantile(pv, QS), np.quantile(ya, QS)); e = ya - est; o["e"] = [round(float(x), 3) for x in np.quantile(e, [.1, .25, .75, .9])]
            f = np.abs(e); f0 = np.abs(ya - pv)
            print(f"  {mode} vues : rho26 {o['rho26']} auc {o['auc26']} | prudent : erreur ×{10**np.median(f0):.2f}, <×2 {(f0 <= np.log10(2)).mean():.0%}, <×3 {(f0 <= np.log10(3)).mean():.0%} | qui ose : erreur ×{10**np.median(f):.2f}, <×2 {(f <= np.log10(2)).mean():.0%}, <×3 {(f <= np.log10(3)).mean():.0%} | étendue {10**est.min():,.0f} à {10**est.max():,.0f}")
            big = ya >= np.log10(3e5); print(f"    vidéos à 300k+ (n={big.sum()}) : estimé prudent médian {10**np.median(pv[big]):,.0f}, qui ose {10**np.median(est[big]):,.0f} | vidéos sous 15k (n={(ya < np.log10(1.5e4)).sum()}) : prudent {10**np.median(pv[ya < np.log10(1.5e4)]):,.0f}, qui ose {10**np.median(est[ya < np.log10(1.5e4)]):,.0f}")
        OUT["models"][mode][cib] = o
        print(mode, cib, len(c), {k: o[k] for k in ("rho", "rho26", "lo", "hi")})
json.dump(OUT, open("pari.json", "w"), ensure_ascii=False, separators=(",", ":"))
open("/home/claude/page/pari.js", "w").write("window.PARI=" + json.dumps(OUT, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(os.path.getsize("/home/claude/page/pari.js"), "octets | élan actuel", round(10**ELAN0))
ref = {}
for v in D.v.iloc[[0, 7, 50, 99, 150, 192]]:
    i = D.index[D.v == v][0]; ref[v] = {"dur": float(D.loc[i, "dur"])}
    for mode, _ in modes:
        for cib in ("r5", "r10", "fin", "lv"):
            o = OUT["models"][mode][cib]; x = D.loc[i, o["f"]].values.astype(float)
            for j, nm in enumerate(o["f"]):
                if nm == "an26": x[j] = 1.0
                if nm == "elan": x[j] = OUT["elan0"]
            x = np.where(np.isnan(x), o["med"], x); ref[v][mode + "_" + cib] = float(o["b"] + (np.array(o["w"]) * (x - np.array(o["mu"])) / np.array(o["sd"])).sum())
json.dump(ref, open("ref.json", "w"))
