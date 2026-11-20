import glob, os, re, sys
sys.path.insert(0, "/home/claude/lecture"); import verifier as V
n = 0
for p in sorted(glob.glob("/home/claude/lecture/in/L*/v*/son.txt")):
    L = p.split("/")[-3]; v = p.split("/")[-2]; s = open(p, encoding="utf-8").read()
    head = s.split("\n")[0]; par = s.split("PAROLES")[1].split("\n\n")[0].split("\n")[1:] if "PAROLES" in s else []
    sec = s.split("PAR SECONDE")[1].split("\n")[1:] if "PAR SECONDE" in s else []
    pro, rows, err = V.lire(f"/home/claude/lecture/out/{v}.csv"); img = {r["t"]: r["desc"] for r in rows if r["couche"] == "img"}
    o = [head, "", "PAROLES PAR PHRASE (transcription automatique ; quelques mots peuvent être faux, se fier au sens) :"] + (par or ["(aucune parole)"]) + ["", "PAR SECONDE : seconde | mots dits pendant cette seconde | ce qu'on voit à l'image"]
    k = 0
    for l in sec:
        f = [x.strip() for x in l.split("|")]
        if len(f) < 2 or not f[0].isdigit(): continue
        t = int(f[0]); o.append(f"{t} | {f[1] or '–'} | {img.get(t, '–')}"); k += 1
    os.makedirs(f"in/{L}", exist_ok=True); open(f"in/{L}/{v}.txt", "w", encoding="utf-8").write("\n".join(o) + "\n"); n += 1
print(n, "fichiers"); print(open(sorted(glob.glob("in/L01/*.txt"))[0], encoding="utf-8").read()[:1500])
