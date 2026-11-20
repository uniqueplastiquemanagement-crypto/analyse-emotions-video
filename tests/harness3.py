import json, os, sys, threading, time, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
os.environ["ANALYSE_SHERPA"] = "/home/claude/asr/sherpa-onnx-whisper-small"
os.environ["PYTHONPATH"] = "/home/claude/test/h/fake"
sys.path.insert(0, "/home/claude/test/h/mt/moteur")
import serveur
MODE = sys.argv[1] if len(sys.argv) > 1 else "opus"
calls = []
class H(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        calls.append((body["tool"], len(json.dumps(body["input"]))))
        try:
            out = {"payload": getattr(serveur, body["tool"])(**body["input"])}
            code = 200
        except Exception as e:
            out = {"error": repr(e)}; code = 500
        b = json.dumps(out).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
srv = ThreadingHTTPServer(("127.0.0.1", 8765), functools.partial(H, directory="/home/claude/outil"))
threading.Thread(target=srv.serve_forever, daemon=True).start()

STUB = r"""
(() => {
  const emoFor = t => (t % 3 === 0 ? {intrigue:2, interet:1} : t % 3 === 1 ? {amusement:2} : {});
  const line = (t, kind) => { const emo = emoFor(t), why = {}; Object.keys(emo).forEach(k => why[k] = kind + " raison " + k + " à " + t + " s"); return JSON.stringify({t, desc: kind + " seconde " + t, att: 1 + (t % 3), int: 1 + (t % 2), val: (t % 5) - 2, emo, why}); };
  const sample = async (prompt, opts) => {
    window.__prompts.push(prompt);
    await new Promise(r => setTimeout(r, 150));
    if (prompt.indexOf("Écris un pronostic court") >= 0) { const k = prompt.indexOf("du son seulement") >= 0 ? "SON" : prompt.indexOf("combinent") >= 0 ? "MIX" : "IMG"; const txt = "## Accroche\nPronostic " + k + " de test.\n## Quoi recouper\nRien."; opts && opts.onText && opts.onText({text: txt}); return {text: txt}; }
    if (prompt.indexOf("un constat sur les mots") >= 0) { const txt = "## Le récit en trois lignes\nConstat MOTS de test.\n## Pistes\nRien."; opts && opts.onText && opts.onText({text: txt}); return {text: txt}; }
    if (prompt.indexOf("Tu analyses les MOTS") === 0) { const sec = prompt.split("Secondes à noter maintenant")[1].split("\n\n")[0].split("\n").slice(1).map(l => parseInt(l)); const fns = ["accroche","accroche","question","place","place","pivot","montee","montee","montee","rien","revelation","revelation","reponse","preuve","preuve","rien","appel","appel","redite","rien","rien","rien"];
      const head = prompt.indexOf("- recit :") >= 0 ? JSON.stringify({recit:"Un test raconte une histoire", moment:10, boucles:[[2,10],[5,12],[14,null]], histoire:2, concret:3, adresse:1}) + "\n" : "";
      return {text: head + sec.map(t => JSON.stringify({t, att: t % 4, int: Math.min(3, Math.round(t < 11 ? t / 4 : (22 - t) / 5)), val: 0, emo: t % 2 ? {intrigue:2} : {}, fn: fns[t % 22], why: t % 2 ? {intrigue:"mots de test"} : {}})).join("\n")}; }
    if (prompt.indexOf("Tu analyses le son") === 0) { const sec = prompt.split("Secondes à noter maintenant")[1].split("\n\n")[0].split("\n").slice(1).map(l => parseInt(l)); return {text: sec.map(t => line(t, "son")).join("\n")}; }
    const m = prompt.match(/Secondes : ([0-9, ]+)\./); return {text: m[1].split(",").map(x => line(parseInt(x), "image")).join("\n")};
  };
  sample.limits = async () => ({images: {maxCount: 5}});
  const mcp = { callTool: async (server, tool, input, opts) => {
      window.__calls.push([server, tool]);
      if (window.__failMode === "notconnected") throw {code: "server_not_connected", message: "x"};
      const r = await fetch("/tool", {method: "POST", body: JSON.stringify({tool, input})}); const j = await r.json();
      if (!r.ok) throw {code: "tool_error", message: j.error};
      return {content: [{type: "text", text: JSON.stringify(j.payload)}], payload: j.payload};
  } };
  window.__prompts = []; window.__calls = [];
  window.claude = { use: async name => name === "sample" ? sample : name === "mcp" ? (window.__noMcp ? null : mcp) : null };
  if (window.__MODE === "pcm") { delete window.AudioEncoder; window.AudioEncoder = undefined; }
})();
"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    page = b.new_page(viewport={"width": 1300, "height": 1500})
    errs = []
    page.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
    page.on("console", lambda m: m.type == "error" and errs.append("CONSOLE " + m.text))
    page.add_init_script(f"window.__MODE = {json.dumps(MODE)}; window.__noMcp = {json.dumps(MODE == 'nomcp')}; window.__failMode = {json.dumps('notconnected' if MODE == 'notconnected' else '')};" + STUB)
    page.goto("http://127.0.0.1:8765/index.html")
    page.wait_for_timeout(800)
    print("AudioEncoder:", page.evaluate("typeof window.AudioEncoder"))
    page.set_input_files("#file", "/home/claude/test/h/essai.webm")
    t0 = time.time(); last = ""
    while time.time() - t0 < 240:
        page.wait_for_timeout(2000)
        st = page.evaluate("[document.getElementById('st1').textContent, document.getElementById('st2').textContent, document.getElementById('st3').textContent, document.getElementById('msg').textContent, document.getElementById('msgson').textContent].join(' | ')")
        if st != last: print(round(time.time() - t0), st); last = st
        if ("Son : terminé" in st or "Son : arrêté" in st or "mesures seulement" in st or "sans lecture" in st) and "Lecture des images terminée" in st:
            break
    page.wait_for_timeout(2500)
    info = page.evaluate("""() => ({
      layer: document.querySelector('#seg button[aria-selected="true"]').getAttribute('data-layer'),
      phrases: document.querySelectorAll('#t-par .ph').length, sect: document.querySelectorAll('#t-bru .ph.sec').length, bruits: document.querySelectorAll('#t-bru .ph.br').length,
      bruVisible: getComputedStyle(document.getElementById('t-bru')).display, verdict: document.getElementById('verdict').textContent.slice(0, 120),
      tiles: document.getElementById('tiles').textContent.slice(0, 200), note: document.getElementById('layernote').textContent,
      retryson: document.getElementById('retryson').hidden, stop: document.getElementById('stop').hidden,
      detail: document.getElementById('d-desc').textContent + ' // ' + document.getElementById('d-said').textContent,
      nprompts: window.__prompts.length, calls: window.__calls.length })""")
    print(json.dumps(info, ensure_ascii=False, indent=1))
    page.click('#seg button[data-layer="mots"]'); page.wait_for_timeout(500)
    info2 = page.evaluate("""() => ({ card: !document.getElementById('motscard').hidden, recit: document.getElementById('recit').innerText, nph: document.querySelectorAll('#phrases textarea').length,
      fn: Array.from(document.querySelectorAll('#t-fn .ph')).map(e => e.textContent).slice(0, 6), fnVisible: getComputedStyle(document.getElementById('t-fn')).display, verdict: document.getElementById('verdict').textContent.slice(0, 90),
      detail: document.getElementById('d-desc').textContent, note: document.getElementById('layernote').textContent.slice(0, 90), pari: document.getElementById('pari-tiles').innerText.replace(/\\n/g, ' ').slice(0, 330), elan: document.getElementById('elan').value,
      pnote: document.getElementById('pari-note').innerText.slice(0, 120), nmots: window.__prompts.filter(p => p.indexOf('Tu analyses les MOTS') === 0).length })""")
    print(json.dumps(info2, ensure_ascii=False, indent=1))
    arc = page.evaluate("""() => { const sv = document.querySelector('#arc svg'); return { svg: !!sv, textes: sv ? Array.from(sv.querySelectorAll('text:not(.ax)')).map(t => t.textContent) : [], cap: document.getElementById('arccap').textContent.slice(0, 260) }; }""")
    print("ARC", json.dumps(arc, ensure_ascii=False))
    page.locator('#motscard').screenshot(path="/home/claude/test/h/arc.png")
    bb = page.locator('#arc svg').bounding_box(); page.mouse.move(bb['x'] + bb['width'] * .5, bb['y'] + bb['height'] * .5); page.wait_for_timeout(200)
    print("ARC survol:", page.evaluate("document.getElementById('arccap').textContent.slice(0, 160)"))
    page.mouse.click(bb['x'] + bb['width'] * .8, bb['y'] + bb['height'] * .5); page.wait_for_timeout(200); print("ARC clic → seconde:", page.evaluate("document.getElementById('d-t').textContent"))
    page.screenshot(path="/home/claude/test/h/mots.png", full_page=True)
    if info2["nph"]:
        n0 = page.evaluate("window.__prompts.length")
        page.fill('#phrases textarea >> nth=0', 'Phrase corrigée à la main par le test')
        page.click('#remots')
        for _ in range(40):
            page.wait_for_timeout(1000)
            if "Relu avec" in page.evaluate("document.getElementById('msgmots').textContent") and page.evaluate("document.getElementById('verdict').textContent").startswith("Le récit"): break
        print("après correction:", page.evaluate("""() => ({ msg: document.getElementById('msgmots').textContent, par0: (document.querySelector('#t-par .ph') || {}).textContent, ta0: document.querySelector('#phrases textarea').value,
          newPrompts: window.__prompts.length, corrMots: window.__prompts.filter(p => p.indexOf('Tu analyses les MOTS') === 0 && p.indexOf('corrigée à la main par le fondateur') > 0 && p.indexOf('Phrase corrigée') > 0).length,
          corrSon: window.__prompts.filter(p => p.indexOf('Tu analyses le son') === 0 && p.indexOf('Phrase corrigée') > 0).length, verdict: document.getElementById('verdict').textContent.slice(0, 60), stop: document.getElementById('stop').hidden })"""), "avant:", n0)
        page.fill('#elan', '80000'); page.dispatch_event('#elan', 'change'); page.wait_for_timeout(300)
        print("pari avec élan 80 000:", page.evaluate("document.getElementById('pari-tiles').innerText.replace(/\\n/g, ' ').slice(0, 200)"))
    print("erreurs:", errs[:8])
    print("appels moteur:", [(c[0], c[1]) for c in calls][:6], "… total", len(calls))
    b.close()
