const fs = require("fs"); const window = {}; global.window = window;
eval(fs.readFileSync("/home/claude/page/pari.js", "utf8")); const PARI = window.PARI; global.PARI = PARI;
const html = fs.readFileSync("/home/claude/page/index.html", "utf8");
const a = html.indexOf("/* ---------- Pari de viralité"), b = html.indexOf("function mille(");
const S = { N:0, F:[], dur:0, recit:null, motsR:[] }; const SON = f => f ? f.s : null; const MOTS = f => f ? f.m : null;
eval(html.slice(a, b) + "; global.pariCompute = pariCompute;");
const ref = JSON.parse(fs.readFileSync("/home/claude/correl/ref.json", "utf8")); let worst = 0;
for (const v of Object.keys(ref)) {
  const L = fs.readFileSync("/home/claude/lecture/out/" + v + ".csv", "utf8").split(/\r?\n/).filter(l => l && !l.startsWith("#") && !l.startsWith("t;"));
  const img = {}, son = {};
  for (const l of L) { const p = l.split(";"); const emo = {}; (p[5] || "").split(",").filter(Boolean).forEach(x => { const [k, n] = x.split(":"); emo[k.trim()] = Number(n); });
    (p[1] === "img" ? img : son)[Number(p[0])] = { att:+p[2], int:+p[3], val:+p[4], emo }; }
  const n = Math.min(Object.keys(img).length, Object.keys(son).length); S.N = n; S.dur = ref[v].dur; S.F = [];
  const ML = fs.readFileSync("/home/claude/mots/out/" + v + ".csv", "utf8").split(/\r?\n/).filter(l => l && !l.startsWith("t;"));
  const H = {}; ML[0].slice(1).split(";").forEach(kv => { const i = kv.indexOf("="); H[kv.slice(0, i)] = kv.slice(i + 1); });
  S.recit = { recit: H.recit, moment: H.moment === "-" ? null : +H.moment, boucles: H.boucles === "-" ? [] : H.boucles.split(",").map(b => { const x = b.trim().split("-"); return [+x[0], x[1] === "x" ? null : +x[1]]; }), histoire: +H.histoire, concret: +H.concret, adresse: +H.adresse };
  const mots = {}; ML.slice(1).forEach(l => { const p = l.split(";"); const emo = {}; (p[4] || "").split(",").filter(Boolean).forEach(x => { const [k, m] = x.split(":"); emo[k.trim()] = +m; }); mots[+p[0]] = { att:+p[1], int:+p[2], val:+p[3], emo, fn:p[5].trim() }; });
  for (let t = 0; t < n; t++) S.F[t] = { t, e: img[t], s: son[t], m: mots[t] };
  const P = pariCompute(); let line = v + " " + P.mode;
  for (const k of ["r5", "r10", "fin", "lv"]) { const d = Math.abs(P[k] - ref[v][P.mode + "_" + k]); worst = Math.max(worst, d); line += ` ${k}=${P[k].toFixed(3)}(${ref[v][P.mode + "_" + k].toFixed(3)})`; }
  for (let t = 0; t < n; t++) { S.F[t].s = null; S.F[t].m = null; } S.recit = null; const Q = pariCompute(); line += " | img";
  for (const k of ["r5", "r10", "fin", "lv"]) { const d = Math.abs(Q[k] - ref[v]["img_" + k]); worst = Math.max(worst, d); line += ` ${k}=${Q[k].toFixed(3)}`; }
  console.log(line, "| niveau", P.tier, Q.mode);
}
console.log("écart maximal JS contre Python :", worst.toExponential(2));
