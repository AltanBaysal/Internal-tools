# Video Experiments — İnteraktif ComfyUI Notebook'ları — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Farklı video üretim workflow'larını Colab Pro'da görsel denemek için, her workflow'a bir bağımsız Colab notebook'u üret — notebook ComfyUI + Manager + custom node'lar + modelleri kaynaktan indirir, `cloudflared` ile UI linki verir; kullanıcı `workflow.json`'u UI'a elle yükleyip çalıştırır.

**Architecture:** Tek paylaşılan 7-hücre iskeleti; her notebook yalnızca `NODE_REPOS` + `CIVITAI_MODELS` + `HF_MODELS` listelerinde farklılaşır. Modeller Colab ephemeral diskine (`/content/ComfyUI/models/...`) iner; Drive kapalı. Notebook'lar bağımsız (her biri Colab'a tek başına yüklenir) → iskelet kod her notebook'ta tekrarlanır (Colab kalıbı; paylaşılan .py yok).

**Tech Stack:** Google Colab (A100), Python, ComfyUI + ComfyUI-Manager, `aria2c` (HF), `curl` + Civitai cookie (gated), `cloudflared` (tünel), `.ipynb` (nbformat 4).

**Yürütme modu:** Sıralı + manuel test. Bir notebook üretilir → kullanıcı Colab'da test eder → sonrakine geçilir. (LTX Eros → Painter → All-in-One → DaSiWa.)

## Global Constraints

- **Drive yok:** `USE_GOOGLE_DRIVE = False` sabit; modeller `/content/ComfyUI/models/...` altına iner. (Base notebook'taki Drive kodu silinmez, kullanılmaz.)
- **Civitai gated indirme — kanıtlanmış kalıp (imageToVideo.ipynb):** SADECE `COOKIE_VALUE` = `__Secure-civitai-token` (civitai.red F12). İstek: `civitai_url(version_id)` = `https://civitai.com/api/download/models/{version_id}` + header `Cookie: __Secure-civitai-token={COOKIE_VALUE}`. **`?token=` API key KULLANMA** → gated asset 401 "requires you to be logged in" verir (probe ile kanıtlı: cookie-only 200, token-only 401). Host **civitai.com**, cookie **civitai.red**'den; süresi dolarsa yenile.
- **Fail-fast (kritik):** İnmeme ihtimali en yüksek olan **gated Civitai modeller önce gelir**: (1) her gated asset için **probe** (ilk 1KB range) ile erişim doğrulanır → cookie eksik/expired ise **anında** `RuntimeError` (40GB HF inmeden); (2) sonra gated modeller indirilir; (3) en son HF (`aria2c`).
- **Fail-loud:** her indirme `is_valid_safetensors` ile doğrulanır (HTML/JSON login sayfası = bozuk) → `RuntimeError`; ComfyUI 90 sn'de `127.0.0.1:8188/system_stats`'a cevap vermezse → `RuntimeError`.
- **Verbose loglama (debug için):** her hücre `banner()` ile başlar/biter; GPU bilgisi (CONFIG'te `nvidia-smi`), her node clone sonucu, her model için **boyut + süre + ✓/❌**, hücre sonunda **indirme özeti** (dosya + boyut listesi), ComfyUI başlangıç log tail'i, tünel URL net basılır. Amaç: kullanıcı Colab output'unu yapıştırınca durum tek bakışta belli olsun → hızlı debug.
- **Dil:** markdown + `print`/hata mesajları **Türkçe**; kod yorumları + docstring **İngilizce**.
- **Base:** `collab-toolbox/video_experiments/comfyui_colab_with_manager.ipynb` (repoda mevcut).
- **Tünel:** `cloudflared`; ComfyUI `--listen 127.0.0.1 --port 8188`.

---

## File Structure

| Dosya | Sorumluluk |
|---|---|
| `collab-toolbox/video_experiments/CLAUDE.md` | (create) klasör dokümanı |
| `collab-toolbox/video_experiments/ltx23-eros/ltx23-eros.ipynb` | (create) LTX 2.3 Eros |
| `collab-toolbox/video_experiments/wan22-painter/wan22-painter.ipynb` | (create) PainterI2V |
| `collab-toolbox/video_experiments/wan22-allinone/wan22-allinone.ipynb` | (create) All-in-One |
| `collab-toolbox/video_experiments/wan22-dasiwa/wan22-dasiwa.ipynb` | (create) DaSiWa |
| `CLAUDE.md` (kök) | (modify) Tools listesi |
| `collab-toolbox/CLAUDE.md` | (modify) Notebook'lar tablosu |

`workflow.json` + `instructions.md` her klasörde mevcut — değişmez.

---

## Shared Notebook Skeleton (reference)

7 hücre. **Hücre 1, 2, 3, 4(helpers), 6, 7 birebir aynıdır** (aşağıda tam kod). Her notebook yalnızca **Hücre 5 (custom nodes) `NODE_REPOS`** ve **Hücre 6 (models) `CIVITAI_MODELS`+`HF_MODELS`** verisinde farklılaşır. (Numaralandırma aşağıdaki gibi; `<...>` task'ta verilir.)

**Hücre 1 — markdown:**
```markdown
# <TITLE> — ComfyUI interaktif deneme (Colab)

**Input:** <INPUT>
**Output:** <OUTPUT>

Sıra:
1. **CONFIG** — Civitai cookie
2. **Helpers** — indirme + doğrulama yardımcıları
3. **ComfyUI + Manager + custom node'lar**
4. **Modeller** — önce gated (probe + indir), sonra HF
5. **Başlat + cloudflared tünel** → UI linki

> Drive kullanılmaz; modeller her oturumda kaynaktan iner. **Runtime → Run all** → linke gir → `workflow.json`'u yükle → modelleri seç → Run.
```

**Hücre 2 — code (CONFIG):**
```python
# === CONFIG ===
# Civitai login-gated indirme: civitai.red → giriş → F12 → Application →
# Cookies → __Secure-civitai-token değerini yapıştır (uzun JWT benzeri string).
# SADECE bu cookie; ?token= API key KULLANMA (gated asset 401 verir).
COOKIE_VALUE = ""  # "__Secure-civitai-token" değeri

USE_GOOGLE_DRIVE = False  # Drive kapalı — modeller /content'e iner
COMFY_PORT = 8188

import os
os.environ["COOKIE_VALUE"] = COOKIE_VALUE
assert len(COOKIE_VALUE) > 500, "❌ COOKIE_VALUE boş/çok kısa — civitai.red'den __Secure-civitai-token yapıştır"
print(f"✓ Cookie: {len(COOKIE_VALUE)} char")
print("=== GPU ===")
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

**Hücre 3 — code (helpers):**
```python
# === Shared helpers — log + fail-loud run + safetensors validation + civitai access ===
import os, time, struct, subprocess

def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"{icons.get(level, '·')} [{time.strftime('%H:%M:%S')}] {msg}")

def human(b):
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024: return f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"

def banner(msg):
    """Section banner — makes pasted Colab output easy to read/debug."""
    print(f"\n{'='*60}\n# {msg}\n{'='*60}")

def run(cmd, label, cwd=None, timeout=3600):
    """Run a command; non-zero exit/timeout -> RuntimeError (fail-loud)."""
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{label}: timeout ({timeout}s)")
    if r.returncode != 0:
        tail = "\n".join((r.stderr or r.stdout or "").strip().splitlines()[-5:])
        raise RuntimeError(f"{label}: exit {r.returncode}\n{tail}")
    return r.stdout

def is_valid_safetensors(path):
    """Real model file? -> (ok, msg). Empty/HTML/JSON login pages are caught as corrupt."""
    if not os.path.exists(path): return False, "yok"
    sz = os.path.getsize(path)
    if sz < 1_000_000: return False, f"çok küçük ({human(sz)})"
    with open(path, "rb") as f: head = f.read(8)
    if head.startswith(b"<") or head.startswith(b'{"'): return False, "HTML/JSON hata sayfası"
    try:
        jl = struct.unpack("<Q", head)[0]
        if 100 < jl < 200_000_000: return True, f"valid ({human(sz)})"
    except Exception: pass
    return False, "header bozuk"

# Civitai auth: session cookie ONLY (logged-in user). ?token= API key -> gated 401.
def civitai_url(version_id):
    return f"https://civitai.com/api/download/models/{version_id}"

def cookie_header():
    return f"Cookie: __Secure-civitai-token={COOKIE_VALUE}"

def civitai_probe(version_id, label):
    """Fail-fast: range-download first 1KB of a gated asset to verify access BEFORE heavy downloads.
    Missing/expired cookie -> login wall (HTML or non-2xx) -> RuntimeError immediately."""
    out = "/content/_probe.bin"
    code = (run(["curl", "-sL", "--max-time", "60", "-r", "0-1023",
                 "-H", cookie_header(), "-w", "%{http_code}", "-o", out, civitai_url(version_id)],
                f"probe {label}") or "").strip()[-3:]
    head = b""
    if os.path.exists(out):
        with open(out, "rb") as f: head = f.read(8)
        os.remove(out)
    if not code.startswith("2") or head.startswith(b"<") or head.startswith(b'{"'):
        raise RuntimeError(f"❌ Civitai erişimi başarısız: {label} (HTTP {code}). "
                           f"Cookie eksik/expired → civitai.red'den __Secure-civitai-token yenile, CONFIG'i tekrar çalıştır.")
    log(f"{label}: erişim OK", "OK")

def fetch(url, target_dir, filename, label, *, parallel, headers=None):
    """Download + validate; skip if already valid; raise on invalid (fail-loud).
    parallel=True -> aria2c (HF), False -> curl (Civitai, surfaces HTTP status)."""
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, filename)
    ok, msg = is_valid_safetensors(target)
    if ok: log(f"{label}: zaten var ({msg})"); return
    if os.path.exists(target): os.remove(target)
    log(f"{label}: indiriliyor...")
    t0 = time.time()
    if parallel:
        cmd = ["aria2c", "-x", "16", "-s", "16", "-k", "1M", "--console-log-level=warn",
               "--auto-file-renaming=false", "--allow-overwrite=true", "-d", target_dir, "-o", filename]
        if headers: cmd += ["--header", headers]
        cmd.append(url); run(cmd, label)
    else:
        cmd = ["curl", "-sL", "--max-time", "1800", "-w", "%{http_code}", "-o", target]
        if headers: cmd += ["-H", headers]
        cmd.append(url)
        code = (run(cmd, label) or "").strip()[-3:]
        if not code.startswith("2"):
            snippet = ""
            if os.path.exists(target):
                with open(target, "rb") as f: snippet = f.read(200).decode("utf-8", "replace").replace("\n", " ").strip()
            raise RuntimeError(f"{label}: Civitai HTTP {code} — {snippet}")
    ok, msg = is_valid_safetensors(target)
    if not ok: raise RuntimeError(f"{label}: indirme bozuk ({msg}) — {url.split('?')[0]}")
    log(f"{label}: indirildi ({msg}, {time.time()-t0:.0f}s)", "OK")

print("✓ Helpers hazır (banner, log, run, is_valid_safetensors, civitai_probe, fetch)")
```

**Hücre 4 — code (ComfyUI + Manager + custom nodes):** `NODE_REPOS` task'ta verilir.
```python
banner("3) ComfyUI + Manager + custom node'lar")
%cd /content
!apt-get install -y ffmpeg aria2 > /dev/null 2>&1
![ -d ComfyUI ] || git clone https://github.com/comfyanonymous/ComfyUI.git
%cd /content/ComfyUI
!git pull -q
!pip install -q -r requirements.txt
!echo "ComfyUI commit:" $(git -C /content/ComfyUI rev-parse --short HEAD)

import os
cn = "/content/ComfyUI/custom_nodes"
os.makedirs(cn, exist_ok=True)

# (folder, repo) — ComfyUI-Manager always first (detect missing nodes); rest per workflow.
NODE_REPOS = [
    ("ComfyUI-Manager", "https://github.com/ltdrdata/ComfyUI-Manager.git"),
    # ← task içeriği buraya
]

for name, url in NODE_REPOS:
    dest = os.path.join(cn, name)
    if os.path.isdir(dest) and os.listdir(dest):
        log(f"{name}: zaten var"); continue
    log(f"{name}: cloning...")
    run(["git", "clone", "--depth", "1", url, dest], f"clone {name}", timeout=180)
    req = os.path.join(dest, "requirements.txt")
    if os.path.isfile(req):
        run(["pip", "install", "-q", "-r", req], f"pip {name}", timeout=300)
log(f"{len(NODE_REPOS)} custom node hazır (eksik olursa UI'da Manager → Install Missing Custom Nodes)", "OK")
```

**Hücre 5 — code (modeller — gated önce):** `CIVITAI_MODELS` + `HF_MODELS` task'ta verilir.
```python
banner("4) Modeller — önce gated (probe + indir), sonra HF")
import glob
COMFY = "/content/ComfyUI/models"

# (version_id, subfolder, filename, label) — gated, cookie ile iner
CIVITAI_MODELS = [
    # ← task içeriği buraya
]
# (url, subfolder, filename, label) — public HF/GitHub direct link
HF_MODELS = [
    # ← task içeriği buraya
]

# 1) Fail-fast: gated erişimini önce doğrula (hiçbir büyük dosya inmeden)
log(f"Gated probe: {len(CIVITAI_MODELS)} asset, HF: {len(HF_MODELS)} dosya")
for vid, sub, fn, label in CIVITAI_MODELS:
    civitai_probe(vid, label)

# 2) Gated modelleri önce indir (inmeme ihtimali en yüksek olanlar)
for vid, sub, fn, label in CIVITAI_MODELS:
    fetch(civitai_url(vid), os.path.join(COMFY, sub), fn, label, parallel=False, headers=cookie_header())

# 3) HF modelleri (aria2c)
for url, sub, fn, label in HF_MODELS:
    fetch(url, os.path.join(COMFY, sub), fn, label, parallel=True)

# === Özet — buraya ulaşmak = her şey indi + doğrulandı ===
banner("İndirme özeti")
for f in sorted(glob.glob(f"{COMFY}/**/*", recursive=True)):
    if os.path.isfile(f):
        print(f"   {human(os.path.getsize(f)):>9}  {os.path.relpath(f, COMFY)}")
log("Tüm modeller indirildi ve doğrulandı", "OK")
```

**Hücre 6 — code (launch + cloudflared):**
```python
import subprocess, time, urllib.request, threading, re, os
banner("5) ComfyUI başlat + cloudflared tünel")

if not os.path.isfile("/content/cloudflared"):
    run(["wget", "-q", "-O", "/content/cloudflared",
         "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"], "cloudflared")
    run(["chmod", "+x", "/content/cloudflared"], "chmod cloudflared")

subprocess.run(["pkill", "-f", "main.py"], check=False); time.sleep(2)
logf = open("/content/comfyui.log", "w")
subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", str(COMFY_PORT)],
                 cwd="/content/ComfyUI", stdout=logf, stderr=subprocess.STDOUT)

ok = False
for i in range(45):
    time.sleep(2)
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{COMFY_PORT}/system_stats", timeout=2); ok = True; break
    except Exception: pass
if not ok:
    print("".join(open("/content/comfyui.log").readlines()[-30:]))
    raise RuntimeError("❌ ComfyUI 90 sn içinde başlamadı")
log("ComfyUI ayakta", "OK")

tun = subprocess.Popen(["/content/cloudflared", "tunnel", "--url", f"http://127.0.0.1:{COMFY_PORT}"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
def _url():
    for line in tun.stdout:
        m = re.search(r"https://[-\w.]+trycloudflare\.com", line)
        if m: print("\n🔗 ComfyUI linki:", m.group(0), "\n"); break
threading.Thread(target=_url, daemon=True).start(); time.sleep(8)
print("⬆️ Link yukarıda. Linke gir, workflow.json'u yükle, modelleri seç, Run.")
```

**Hücre 7 — markdown:**
```markdown
## Kullanım
1. Yukarıdaki `trycloudflare.com` linkine gir (ComfyUI UI).
2. **Workflow → Open** ile bu klasördeki `workflow.json`'u yükle (veya dosyayı tarayıcıya sürükle).
3. Her model loader'a tıklayıp dropdown'dan indirilen dosyayı seç (yollar otomatik çözülmez).
4. **Run**. Oturum koparsa Run all tekrar.
```

---

### Task 1: `video_experiments/CLAUDE.md`

**Files:** Create: `collab-toolbox/video_experiments/CLAUDE.md`

- [ ] **Step 1: Yaz** — içerik:
```markdown
# video_experiments

Farklı video üretim workflow'larını Colab Pro'da **görsel** denemek için bağımsız ComfyUI notebook'ları. Her notebook ComfyUI + Manager + custom node'lar + modelleri kaynaktan indirir, `cloudflared` ile UI linki verir; kullanıcı `workflow.json`'u UI'a elle yükleyip çalıştırır. **Drive kullanılmaz.**

## Denemeler

| Klasör | Workflow | Model ailesi |
|---|---|---|
| [ltx23-eros/](ltx23-eros/) | MrXin LTX 2.3 I2V "Eros" V6 | LTX-Video 2.3 |
| [wan22-painter/](wan22-painter/) | PainterI2V (kenpechi) v2.4 | WAN 2.2 I2V |
| [wan22-allinone/](wan22-allinone/) | All-in-One I2V/FLF/Loop (fatberg_slim) | WAN 2.2 I2V |
| [wan22-dasiwa/](wan22-dasiwa/) | DaSiWa FastFidelity C-AiO | WAN 2.2 I2V-A14B |

Her klasörde: `<deneme>.ipynb` + `workflow.json` + `instructions.md` (Civitai özeti).

## Ortak kalıp

- **Base:** [comfyui_colab_with_manager.ipynb](comfyui_colab_with_manager.ipynb) (ComfyUI resmi Manager'lı Colab notebook'u).
- Tek CONFIG (Civitai `__Secure-civitai-token` cookie), Drive kapalı.
- **Civitai gated indirme:** `civitai.com/api/download/models/{version_id}` + sadece cookie (`?token=` yok).
- **Fail-fast:** gated modeller önce probe + indirilir, sonra HF `aria2c`.
- Fail-loud: `is_valid_safetensors` + ComfyUI 90 sn health check → RuntimeError.

## Kullanım

1. Colab → notebook yükle → A100 → CONFIG'e cookie → **Run all**.
2. `trycloudflare` linkine gir → `workflow.json` yükle → modelleri seç → Run.

> Kişisel/NSFW concept LoRA'lar (Painter, DaSiWa) URL'siz; kullanıcı kendi koleksiyonundan ekler.
```

- [ ] **Step 2: Commit** — `git add collab-toolbox/video_experiments/CLAUDE.md && git commit -m "docs(video_experiments): add folder CLAUDE.md"`

---

### Task 2: LTX Eros notebook'u

**Files:** Create: `collab-toolbox/video_experiments/ltx23-eros/ltx23-eros.ipynb`

**Interfaces:** Consumes: Shared Skeleton. `<TITLE>`=`LTX 2.3 I2V — Eros (MrXin) V6`, `<INPUT>`=`Başlangıç görseli + prompt (UI)`, `<OUTPUT>`=`24 FPS video + ses (dual-pass)`.

- [ ] **Step 1: Hücre 4 `NODE_REPOS`** (Manager'dan sonra):
```python
    ("ComfyUI-KJNodes",            "https://github.com/kijai/ComfyUI-KJNodes.git"),
    ("rgthree-comfy",              "https://github.com/rgthree/rgthree-comfy.git"),
    ("ComfyUI-Easy-Use",           "https://github.com/yolain/ComfyUI-Easy-Use.git"),
    ("ComfyUI-mxToolkit",          "https://github.com/Smirnov75/ComfyUI-mxToolkit.git"),
    ("ComfyUI-VideoHelperSuite",   "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"),
    ("ComfyUI-LTXVideo",           "https://github.com/Lightricks/ComfyUI-LTXVideo.git"),
    ("controlaltai-nodes",         "https://github.com/gabe-init/ComfyUI-controlaltai-nodes.git"),
    ("ComfyUI-VFI",                "https://github.com/GACLove/ComfyUI-VFI.git"),
    ("comfyui_memory_cleanup",     "https://github.com/SeniorPikachu/comfyui_memory_cleanup.git"),
    ("ComfyUI-Impact-Pack",        "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"),
```

- [ ] **Step 2: Hücre 5 `CIVITAI_MODELS` + `HF_MODELS`** (URL'ler workflow.json "Model Links" node'undan):
```python
CIVITAI_MODELS = [
    (2892069, "diffusion_models", "ltx2310eros_v1_FP8.safetensors", "LTX Eros checkpoint"),
    (164677,  "upscale_models",   "nmkdSiaxCX_200k.safetensors",    "nmkdSiaxCX upscaler"),
]
HF_MODELS = [
    ("https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/diffusion_models/ltx-2.3-22b-distilled_transformer_only_fp8_input_scaled_v3.safetensors", "diffusion_models", "ltx-2.3-22b-distilled_transformer_only_fp8_input_scaled_v3.safetensors", "LTX distilled"),
    ("https://huggingface.co/GitMylo/LTX-2-comfy_gemma_fp8_e4m3fn/resolve/main/gemma_3_12B_it_fp8_e4m3fn.safetensors", "text_encoders", "gemma_3_12B_it_fp8_e4m3fn.safetensors", "Gemma text encoder"),
    ("https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/text_encoders/ltx-2.3_text_projection_bf16.safetensors", "clip", "ltx-2.3_text_projection_bf16.safetensors", "Text projection"),
    ("https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/vae/LTX23_video_vae_bf16.safetensors", "vae", "LTX23_video_vae_bf16.safetensors", "Video VAE"),
    ("https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/vae/LTX23_audio_vae_bf16.safetensors", "vae", "LTX23_audio_vae_bf16.safetensors", "Audio VAE"),
    ("https://huggingface.co/madebyollin/taehv/resolve/main/safetensors/taeltx2_3.safetensors", "vae", "taeltx2_3.safetensors", "Preview VAE"),
    ("https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-spatial-upscaler-x2-1.1.safetensors", "latent_upscale_models", "ltx-2.3-spatial-upscaler-x2-1.1.safetensors", "Spatial upscaler"),
    ("https://huggingface.co/TenStrip/LTX2.3_Distilled_Lora_1.1_Experiments/resolve/main/ltx-2.3-22b-distilled-lora-1.1_fro90_ceil72_condsafe.safetensors", "loras", "ltx-2.3-22b-distilled-lora-1.1_fro90_ceil72_condsafe.safetensors", "Distilled LoRA first"),
    ("https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-22b-distilled-lora-384-1.1.safetensors", "loras", "ltx-2.3-22b-distilled-lora-384-1.1.safetensors", "Distilled LoRA final"),
]
```

- [ ] **Step 3: Colab kabul testi (kullanıcı)** — A100 → cookie → Run all. Beklenen: gated probe ✓ (LTX Eros + nmkd), modeller iner, ComfyUI linki basılır, `workflow.json` yüklenir, dropdown'larda dosyalar görünür. ✅ = link + workflow yüklendi.

- [ ] **Step 4: Commit** — `git add .../ltx23-eros/ltx23-eros.ipynb && git commit -m "feat(video_experiments): add LTX 2.3 Eros notebook"`

---

### Task 3: Painter notebook'u

**Files:** Create: `collab-toolbox/video_experiments/wan22-painter/wan22-painter.ipynb`

**Interfaces:** `<TITLE>`=`WAN 2.2 I2V — PainterI2V (kenpechi) v2.4`, `<INPUT>`=`Görsel + prompt + LoRA seçimi (UI)`, `<OUTPUT>`=`WAN 2.2 I2V video (kamera hareketi güçlü)`.

- [ ] **Step 1: Hücre 4 `NODE_REPOS`** (Manager'dan sonra):
```python
    ("rgthree-comfy",               "https://github.com/rgthree/rgthree-comfy.git"),
    ("ComfyUI-Custom-Scripts",      "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git"),
    ("ComfyUI-KJNodes",             "https://github.com/kijai/ComfyUI-KJNodes.git"),
    ("ComfyUI-Impact-Pack",         "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"),
    ("ComfyUI-GGUF",                "https://github.com/city96/ComfyUI-GGUF.git"),
    ("ComfyUI-VideoHelperSuite",    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"),
    ("ComfyUI-Easy-Use",            "https://github.com/yolain/ComfyUI-Easy-Use.git"),
    ("ComfyUI-Frame-Interpolation", "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git"),
    ("ComfyUI-PainterI2V",          "https://github.com/princepainter/ComfyUI-PainterI2V.git"),
    ("ComfyUI-PainterI2Vadvanced",  "https://github.com/princepainter/ComfyUI-PainterI2Vadvanced.git"),
    ("FFGO-Video-Customization",    "https://github.com/zli12321/FFGO-Video-Customization.git"),
```

- [ ] **Step 2: Hücre 5 `CIVITAI_MODELS` + `HF_MODELS`**:
```python
CIVITAI_MODELS = [
    (2337890, "loras", "FFGO_merged_lora.safetensors", "FFGO LoRA"),
]
HF_MODELS = [
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors", "diffusion_models", "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors", "Wan2.2 HIGH"),
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors", "diffusion_models", "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors", "Wan2.2 LOW"),
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", "text_encoders", "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "UMT5-XXL"),
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors", "vae", "wan_2.1_vae.safetensors", "Wan2.1 VAE"),
    ("https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_Lightx2v/Wan_2_2_I2V_A14B_HIGH_lightx2v_4step_lora_v1030_rank_64_bf16.safetensors", "loras", "Wan_2_2_I2V_A14B_HIGH_lightx2v_4step_lora_v1030_rank_64_bf16.safetensors", "Lightx2v HIGH"),
    ("https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_Lightx2v/Wan2.2_i2v_A14b_low_noise_lora_rank64_lightx2v_4step_1022.safetensors", "loras", "Wan2.2_i2v_A14b_low_noise_lora_rank64_lightx2v_4step_1022.safetensors", "Lightx2v LOW"),
    ("https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x2plus.pth", "upscale_models", "RealESRGAN_x2plus.pth", "RealESRGAN x2"),
]
```

> **Hücre 7'ye ek not:** Workflow yazarın kişisel NSFW concept LoRA'larını (`HIGH\...`, `LOW\...`) referanslar — URL'siz, inmez. Notebook base + hız + FFGO indirir; concept LoRA Loader'ları kullanıcı kendi dosyalarıyla doldurur veya kapatır. lightx2v dosya adı HF'de farklıysa Manager/HF'den en yakını seçilir.

- [ ] **Step 3: Colab kabul testi (kullanıcı)** — FFGO probe ✓, base modeller iner, link açılır, `workflow.json` yüklenir, concept LoRA'lar boşsa kapatılır. ✅.

- [ ] **Step 4: Commit** — `git commit -m "feat(video_experiments): add PainterI2V notebook"`

---

### Task 4: All-in-One notebook'u

**Files:** Create: `collab-toolbox/video_experiments/wan22-allinone/wan22-allinone.ipynb`

**Interfaces:** `<TITLE>`=`WAN 2.2 I2V — All-in-One (fatberg_slim)`, `<INPUT>`=`Görsel(ler) + prompt; mod I2V/FLF/Loop`, `<OUTPUT>`=`WAN 2.2 video (+upscale/interpolate ops.)`.

- [ ] **Step 1: Hücre 4 `NODE_REPOS`** (Manager'dan sonra):
```python
    ("ComfyUI_essentials",          "https://github.com/cubiq/ComfyUI_essentials.git"),
    ("ComfyUI-KJNodes",             "https://github.com/kijai/ComfyUI-KJNodes.git"),
    ("Derfuu_ComfyUI_ModdedNodes",  "https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes.git"),
    ("rgthree-comfy",               "https://github.com/rgthree/rgthree-comfy.git"),
    ("ComfyUI-Easy-Use",            "https://github.com/yolain/ComfyUI-Easy-Use.git"),
    ("ComfyUI-Frame-Interpolation", "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git"),
    ("ComfyUI-Image-Selector",      "https://github.com/SLAPaper/ComfyUI-Image-Selector.git"),
    ("ComfyUI-GGUF",                "https://github.com/city96/ComfyUI-GGUF.git"),
    ("ComfyUI-VideoHelperSuite",    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"),
    ("ComfyUI_Swwan",               "https://github.com/aining2022/ComfyUI_Swwan.git"),
    ("ComfyUI-Custom-Scripts",      "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git"),
```

- [ ] **Step 2: Hücre 5** (hepsi HF; guide node'daki fp8 yolu):
```python
CIVITAI_MODELS = []
HF_MODELS = [
    ("https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/I2V/Wan2_2-I2V-A14B-HIGH_fp8_e4m3fn_scaled_KJ.safetensors", "diffusion_models", "Wan2_2-I2V-A14B-HIGH_fp8_e4m3fn_scaled_KJ.safetensors", "Wan2.2 HIGH"),
    ("https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/I2V/Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ.safetensors", "diffusion_models", "Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ.safetensors", "Wan2.2 LOW"),
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", "text_encoders", "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "UMT5-XXL"),
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors", "vae", "wan_2.1_vae.safetensors", "Wan2.1 VAE"),
    ("https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_Lightx2v/Wan_2_2_I2V_A14B_HIGH_lightx2v_MoE_distill_lora_rank_64_bf16.safetensors", "loras", "Wan_2_2_I2V_A14B_HIGH_lightx2v_MoE_distill_lora_rank_64_bf16.safetensors", "Lightx2v MoE HIGH"),
    ("https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v/resolve/main/loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors", "loras", "Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors", "Lightx2v rank64"),
]
```

> **Hücre 7'ye ek not:** Guide node ayrıca GGUF (`QuantStack/Wan2.2-I2V-A14B-GGUF`) ve NSFW umt5 (`NSFW-API/NSFW-Wan-UMT5-XXL`) alternatifleri listeler — düşük VRAM/NSFW için workflow loader'ından seçilebilir, gerekirse `HF_MODELS`'e eklenir. RIFE `rife49.pt` Frame-Interpolation ilk kullanımda iner.

- [ ] **Step 3: Colab kabul testi (kullanıcı)** — gated yok (probe atlanır), HF iner, link açılır, `workflow.json` (I2V şubesi) yüklenir, Run çalışır. ✅.

- [ ] **Step 4: Commit** — `git commit -m "feat(video_experiments): add All-in-One WAN2.2 notebook"`

---

### Task 5: DaSiWa notebook'u

**Files:** Create: `collab-toolbox/video_experiments/wan22-dasiwa/wan22-dasiwa.ipynb`

**Interfaces:** `<TITLE>`=`WAN 2.2 I2V — DaSiWa FastFidelity C-AiO`, `<INPUT>`=`Görsel + prompt (UI)`, `<OUTPUT>`=`WAN 2.2 I2V/FLF2V video`.

- [ ] **Step 1: Hücre 4 `NODE_REPOS`** (Manager'dan sonra):
```python
    ("ComfyUI-VideoHelperSuite", "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"),
    ("rgthree-comfy",            "https://github.com/rgthree/rgthree-comfy.git"),
    ("ComfyUI-GGUF",             "https://github.com/city96/ComfyUI-GGUF.git"),
    ("comfyui-WhiteRabbit",      "https://github.com/Artificial-Sweetener/comfyui-WhiteRabbit.git"),
    ("ComfyUI-KJNodes",          "https://github.com/kijai/ComfyUI-KJNodes.git"),
    ("ComfyUI-DaSiWa-Nodes",     "https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes.git"),
    ("ComfyUI-LTXVideo",         "https://github.com/Lightricks/ComfyUI-LTXVideo.git"),
```

- [ ] **Step 2: Hücre 5 `CIVITAI_MODELS` + `HF_MODELS`**:
```python
# ⚠️ DaSiWa checkpoint version ID'leri Civitai models/1981116 sayfasından DOĞRULA:
# "Download" linkine sağ tık → tam api/download/models/<versionId>. HIGH/LOW ayrı ID olabilir.
# Checkpoint yanına Civitai "Config" dosyası da konmalı (UI'da loader bekler).
CIVITAI_MODELS = [
    (2712329, "diffusion_models", "DaSiWa_Wan22_I2V_14B_SnatchKiss_v11_HIGH_fp8_mixed.safetensors", "DaSiWa HIGH"),
    (2712329, "diffusion_models", "DaSiWa_Wan22_I2V_14B_SnatchKiss_v11_LOW_fp8_mixed.safetensors",  "DaSiWa LOW"),
]
HF_MODELS = [
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors", "vae", "wan_2.1_vae.safetensors", "Wan2.1 VAE"),
    ("https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", "text_encoders", "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "UMT5-XXL"),
    ("https://huggingface.co/Kim2091/AnimeSharpV4/resolve/main/2x-AnimeSharpV4_RCAN.safetensors", "upscale_models", "2x-AnimeSharpV4_RCAN.safetensors", "AnimeSharp upscaler"),
]
```

> **Hücre 7'ye ek not:** DaSiWa checkpoint (HIGH/LOW + config) Civitai `models/1981116`/`2151205`'ten. Yukarıdaki version ID kabul testinde doğrulanır; yanlışsa kullanıcı doğru ID'yi verir veya checkpoint'i elle yükler. `rife49.pt`/`rife_v4.26` WhiteRabbit/Frame-Interpolation ilk kullanımda iner.

- [ ] **Step 3: Colab kabul testi (kullanıcı)** — DaSiWa probe (ID doğru mu?), iner, link açılır, `workflow.json` (FastFidelity C-AiO) yüklenir, Run. ID yanlışsa probe fail-loud → kullanıcı ID düzeltir. ✅.

- [ ] **Step 4: Commit** — `git commit -m "feat(video_experiments): add DaSiWa WAN2.2 notebook"`

---

### Task 6: Repo CLAUDE.md index'leri

**Files:** Modify: `CLAUDE.md` (kök), `collab-toolbox/CLAUDE.md`

- [ ] **Step 1: collab-toolbox/CLAUDE.md** "Notebook'lar" tablosuna `watermark_remove` satırından sonra:
```markdown
| [video_experiments/](video_experiments/) | 4 ayrı interaktif ComfyUI deneme notebook'u (LTX 2.3 Eros, PainterI2V, All-in-One, DaSiWa) — kaynaktan indir + cloudflared UI linki, Drive yok | A100 (Colab Pro) |
```
- [ ] **Step 2: kök CLAUDE.md** "Tools" listesine collab-toolbox altına:
```markdown
- **[video_experiments](collab-toolbox/video_experiments/CLAUDE.md)** — Farklı video workflow'larını görsel denemek için bağımsız ComfyUI Colab notebook'ları (cloudflared UI linki, Drive yok).
```
- [ ] **Step 3: Commit** — `git commit -m "docs: register video_experiments in CLAUDE.md indexes"`

---

## Self-Review

**Spec coverage:** İnteraktif notebook + cloudflared (Hücre 6) ✓; Drive kapalı (Hücre 2) ✓; Civitai cookie-only kanıtlı kalıp (Hücre 3 `fetch`/`civitai_url`/`cookie_header`) ✓; **fail-fast probe + gated-first** (Hücre 5) ✓; fail-loud (`is_valid_safetensors` + 90s) ✓; workflow.json elle (Hücre 7) ✓; model/node JSON'dan (Task 2–5) ✓; CLAUDE.md (Task 1, 6) ✓.

**Placeholder scan:** Kod tam; listeler somut. Tek açık doğrulama noktası DaSiWa version ID'leri — kod yorumunda `⚠️ DOĞRULA` + kabul testinde probe ile fail-loud (gizli placeholder değil).

**Type consistency:** `NODE_REPOS`=list[(name,url)]; `CIVITAI_MODELS`=list[(version_id,sub,fn,label)]; `HF_MODELS`=list[(url,sub,fn,label)] — 4 notebook'ta aynı şema; `fetch`/`civitai_probe`/`civitai_url`/`cookie_header`/`is_valid_safetensors` Hücre 3'te tanımlı, her notebook'ta aynı.

**Açık sınır (silent cap değil):** Painter/DaSiWa kişisel NSFW concept LoRA'ları URL'siz → kullanıcı sağlar (Hücre 7 notu).
