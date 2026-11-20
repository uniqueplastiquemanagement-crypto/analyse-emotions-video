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
    if (prompt.indexOf("Tu analyses le son") === 0) { const sec = prompt.split("Secondes à noter maintenant")[1].split("\n\n")[0].split("\n").slice(1).map(l => parseInt(l)); return {text: sec.map(t => line(t, "son")).join("\n")}; }
    const m = prompt.match(/Secondes : ([0-9, ]+)\./); return {text: m[1].split(",").map(x => line(parseInt(x), "image")).join("\n")};
  };
  sample.limits = async () => ({images: {maxCount: 5}});
  const mcp = { callTool: async (server, tool, input, opts) => {
      window.__calls.push([server, tool]);
      if (window.__failMode === "notconnected") throw {code: "server_not_connected", message: "x"};
      if (window.__flaky > 0) { window.__flaky--; window.__echecs = (window.__echecs || 0) + 1; throw {code: window.__flakyCode || "server_not_connected", message: "pas encore prêt"}; }
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
    page.add_init_script(f"window.__MODE = {json.dumps(MODE)}; window.__noMcp = {json.dumps(MODE == 'nomcp')}; window.__failMode = {json.dumps('notconnected' if MODE == 'notconnected' else '')}; window.__flaky = {3 if MODE.startswith('flaky') else 0}; window.__flakyCode = {json.dumps('approval_required' if MODE == 'flaky2' else 'server_not_connected')};" + STUB)
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
    print("échecs simulés:", page.evaluate("window.__echecs || 0"), "| bouton réessayer caché:", page.evaluate("document.getElementById('retryson').hidden"), "| son:", page.evaluate("document.getElementById('st3').textContent"), "| msg:", page.evaluate("document.getElementById('msgson').textContent"))
    print("erreurs:", errs[:8])
    print("appels moteur:", [(c[0], c[1]) for c in calls][:6], "… total", len(calls))
    b.close()
