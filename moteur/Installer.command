#!/bin/bash
# Installateur du moteur d'analyse vidéo d'Unique Plastique.
# À lancer une fois par double-clic. Tout s'installe dans ce dossier ; rien n'est envoyé ailleurs.
# Le journal complet est écrit dans installation.log, juste à côté.

cd "$(dirname "$0")" || exit 1
RACINE="$(pwd)"
LOG="$RACINE/installation.log"
ETAT="$RACINE/etat-installation.txt"
exec > >(tee -a "$LOG") 2>&1
: > "$ETAT"

titre() { printf "\n\033[1m=== %s ===\033[0m\n" "$1"; }
note()  { echo "$1" >> "$ETAT"; echo "  -> $1"; }

echo "Installation lancée le $(date)"
titre "0. Ce Mac"
sw_vers 2>/dev/null
echo "Puce : $(sysctl -n machdep.cpu.brand_string 2>/dev/null) · mémoire : $(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1073741824 )) Go · cœurs : $(sysctl -n hw.ncpu 2>/dev/null)"
if [ "$(uname -s)" != "Darwin" ] || [ "$(uname -m)" != "arm64" ]; then
  note "mac: ÉCHEC (il faut un Mac à puce Apple)"
  read -r -p "Ce moteur demande un Mac à puce Apple. Appuie sur Entrée pour fermer."; exit 1
fi
note "mac: ok ($(sysctl -n machdep.cpu.brand_string 2>/dev/null), $(( $(sysctl -n hw.memsize) / 1073741824 )) Go)"

titre "1. uv (le gestionnaire qui installe Python et les modèles)"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
if command -v uv >/dev/null 2>&1; then note "uv: ok ($(uv --version))"; else
  note "uv: ÉCHEC"; read -r -p "uv n'a pas pu s'installer. Appuie sur Entrée pour fermer."; exit 1
fi

titre "2. Python 3.11 dans ce dossier"
PY="$RACINE/.venv/bin/python"
[ -x "$PY" ] || uv venv --python 3.11 "$RACINE/.venv"
if [ -x "$PY" ]; then note "python: ok ($("$PY" --version))"; else
  note "python: ÉCHEC"; read -r -p "Python n'a pas pu s'installer. Appuie sur Entrée pour fermer."; exit 1
fi
installe() { uv pip install --python "$PY" "$@"; }

titre "3. Bibliothèques (un groupe à la fois : si l'un échoue, les autres continuent)"
installe numpy scipy scikit-image pillow statsmodels pandas tqdm "mcp>=2" static-ffmpeg huggingface_hub \
  && note "base: ok" || note "base: ÉCHEC"
installe mlx-whisper && note "paroles (mlx-whisper): ok" || note "paroles (mlx-whisper): ÉCHEC"
installe torch transformers librosa soundfile soxr pyloudnorm scikit-learn matplotlib \
  && installe "earshot[mcp] @ https://github.com/Leonxlnx/earshot/archive/refs/heads/main.zip" \
  && note "earshot: ok" || note "earshot: ÉCHEC"

titre "4. Aesthetics Toolbox"
if [ ! -d "$RACINE/moteur/toolbox/AT" ]; then
  TMP="$(mktemp -d)"
  # On ne sort de l'archive que le dossier de calcul (AT) : d'autres fichiers ont un émoji dans leur nom,
  # que l'outil unzip du Mac refuse en demandant une réponse au clavier.
  curl -LsSf -o "$TMP/toolbox.zip" https://github.com/rbartho/aesthetics-toolbox/archive/refs/heads/main.zip \
    && "$PY" - "$TMP/toolbox.zip" "$RACINE/moteur/toolbox" <<'PYEOF'
import os, sys, zipfile
z = zipfile.ZipFile(sys.argv[1]); dest = sys.argv[2]
for n in z.namelist():
    reste = n.split("/", 1)[1] if "/" in n else ""
    if (reste.startswith("AT/") or reste == "LICENSE") and not n.endswith("/"):
        p = os.path.join(dest, reste); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(z.read(n))
PYEOF
fi
[ -d "$RACINE/moteur/toolbox/AT" ] && note "toolbox: ok" || note "toolbox: ÉCHEC"

titre "5. ffmpeg"
FF="$("$PY" -c "import sys; sys.path.insert(0, '$RACINE/moteur'); import analyse; print(analyse.binaires()[0])" 2>&1 | tail -1)"
if [ -x "$FF" ]; then note "ffmpeg: ok ($FF)"; else note "ffmpeg: ÉCHEC ($FF)"; fi

titre "6. Modèles (le plus long : environ 3 Go à télécharger)"
"$PY" -c "from huggingface_hub import snapshot_download; print(snapshot_download('mlx-community/whisper-large-v3-turbo'))" \
  && note "modèle de paroles: ok" || note "modèle de paroles: ÉCHEC"
"$PY" -m earshot doctor --fetch && note "modèles d'écoute (earshot): ok" || note "modèles d'écoute (earshot): ÉCHEC"

titre "7. Essai complet sur une petite vidéo fabriquée"
mkdir -p "$RACINE/videos" "$RACINE/resultats"
ESSAI="$RACINE/videos/_essai.mp4"
if [ -x "$FF" ]; then
  say -v Amelie -o "$RACINE/videos/_essai.aiff" "Bonjour, ici Unique Plastique. On fabrique des pinces à cheveux en plastique recyclé, à Lévis." 2>/dev/null \
    || say -o "$RACINE/videos/_essai.aiff" "Bonjour, ici Unique Plastique. On fabrique des pinces à cheveux en plastique recyclé, à Lévis." 2>/dev/null
  if [ -s "$RACINE/videos/_essai.aiff" ]; then
    "$FF" -v error -y -f lavfi -i "testsrc2=size=720x1280:rate=30" -i "$RACINE/videos/_essai.aiff" -shortest -pix_fmt yuv420p "$ESSAI"
  else
    "$FF" -v error -y -f lavfi -i "testsrc2=size=720x1280:rate=30:duration=4" -f lavfi -i "sine=frequency=440:duration=4" -shortest -pix_fmt yuv420p "$ESSAI"
  fi
  rm -rf "$RACINE/resultats/_essai"
  "$PY" "$RACINE/moteur/analyse.py" "$ESSAI" --sortie "$RACINE/resultats/_essai"
  if grep -q '"termine": true' "$RACINE/resultats/_essai/etat.json" 2>/dev/null; then
    note "essai: terminé (détail dans resultats/_essai/etat.json)"
    "$PY" -c "import json; d=json.load(open('$RACINE/resultats/_essai/etat.json')); print('modules :', d['modules']); print('erreurs :', d['erreurs']); s=json.load(open('$RACINE/resultats/_essai/son.json')); print('paroles comprises :', ' '.join(p['texte'] for p in s['phrases']))"
  else
    note "essai: ÉCHEC"
  fi
else
  note "essai: sauté (pas de ffmpeg)"
fi

titre "8. Connecteur dans l'app Claude"
CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
"$PY" - "$CFG" "$PY" "$RACINE/moteur/serveur.py" <<'PYEOF' && note "connecteur: ajouté à la configuration de Claude" || note "connecteur: ÉCHEC (à ajouter à la main, voir LISEZ-MOI.txt)"
import json, os, shutil, sys, time
cfg, py, srv = sys.argv[1:4]
os.makedirs(os.path.dirname(cfg), exist_ok=True)
d = {}
if os.path.exists(cfg):
    shutil.copy(cfg, cfg + ".sauvegarde-" + time.strftime("%Y%m%d-%H%M%S"))
    txt = open(cfg, encoding="utf-8").read().strip()
    d = json.loads(txt) if txt else {}
d.setdefault("mcpServers", {})["analyse-video"] = {"command": py, "args": [srv]}
json.dump(d, open(cfg, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("Configuration mise à jour :", cfg, "(une copie de sauvegarde a été faite si le fichier existait)")
PYEOF

titre "Résumé"
cat "$ETAT"
echo
echo "Dernière étape, à faire toi-même : quitte complètement l'app Claude (Cmd+Q), puis rouvre-la."
echo "Ensuite, dis à Claude dans le chat : « l'installation est faite »."
echo
read -r -p "Appuie sur Entrée pour fermer cette fenêtre."
