# Nova 3DCG foto üretimi — manual notebook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `collab-toolbox/photo_generator/nova-3dcg/` altında Nova 3DCG XL + USNR + Remacri ile fotoğraf üreten manual ComfyUI notebook'u + creator'ın workflow'unun birebir kopyası.

**Architecture:** `wan22-arbuzai/manual.ipynb` kopyalanır, 7 hücresi (0, 1, 6, 7, 8, 9, 11) yeniden yazılır; `comfyuiImage_v37/Basic_V37.json` tek byte değişmeden `workflow_manual.json` olur. Spec: `docs/superpowers/specs/2026-07-21-nova-3dcg-photo-design.md`.

**Tech Stack:** Colab notebook (.ipynb JSON), ComfyUI, Civitai/HF indirmeleri.

## Global Constraints

- **`workflow_manual.json` = `comfyuiImage_v37/Basic_V37.json` birebir; tek byte değişmez.** `comfyuiImage_v37/` klasörüne dokunulmaz (kullanıcının yüklediği kaynak; taşınmaz, silinmez).
- **Dil:** notebook markdown hücreleri ve runtime çıktısı (`print`/`log`/`assert`/`RuntimeError`) Türkçe; kod yorumları ve docstring'ler İngilizce.
- **Python çalıştırma yok.** Dosya inceleme Grep/Read ile.
- **Komut sadece gerekliyse ve gerekçesi söylenerek:** bu planda yalnız 3 komut var (2 dosya kopyası + 1 byte karşılaştırma) — Read+Write bir JSON'u yeniden encode edip byte'ları bozabilir, kopya ancak komutla birebir olur.
- **Git'e hiçbir şey eklenmez** (stage/commit yok) — kullanıcı Colab'da doğrulayıp isteyene kadar. Plandaki hiçbir adım commit içermez.
- Hata mesajlarında neden uydurulmaz; servisin gerçek çıktısı basılır (NOTEBOOK-STANDARD).
- Dosya adları grafiğin `widgets_values`'ındaki adlarla birebir: `nova3DCGXL_ilV90.safetensors` dropdown'da ancak bu adla görünür, `4x_foolhardy_Remacri.pth` / `bbox/face_yolov9c.pt` / `sam_vit_b_01ec64.pth` loader'ların aradığı adlar.

---

### Task 1: Klasör + workflow_manual.json (birebir kopya)

**Files:**
- Create: `collab-toolbox/photo_generator/nova-3dcg/workflow_manual.json`

**Interfaces:**
- Produces: Task 2'nin markdown'larının işaret ettiği `workflow_manual.json`; node künyeleri (cnr_id/aux_id) Task 2'deki CUSTOM_NODES listesinin kaynağı.

- [ ] **Step 1: Kopyala** — komut gerekçesi: byte-birebir kopya Read+Write ile garanti edilemez (JSON re-encode riski).

```bash
mkdir -p "collab-toolbox/photo_generator/nova-3dcg" && cp "comfyuiImage_v37/Basic_V37.json" "collab-toolbox/photo_generator/nova-3dcg/workflow_manual.json"
```

- [ ] **Step 2: Byte-birebir doğrula**

```bash
cmp "comfyuiImage_v37/Basic_V37.json" "collab-toolbox/photo_generator/nova-3dcg/workflow_manual.json" && echo IDENTICAL
```

Expected: `IDENTICAL` (cmp sessiz + exit 0).

---

### Task 2: manual.ipynb

**Files:**
- Create: `collab-toolbox/photo_generator/nova-3dcg/manual.ipynb` (kopya + 7 hücre değişir)

**Interfaces:**
- Consumes: Task 1'in `workflow_manual.json`'ı (markdown yönergeleri ona işaret eder).
- Produces: Kullanıcının Colab'da çalıştıracağı notebook; Export (API) çıktısı sonraki turun (`api.ipynb`) girdisi.

Kaynak `wan22-arbuzai/manual.ipynb` 12 hücre (0-11). **Değişmeyen hücreler: 2 (CONFIG md), 3 (CONFIG kod — cookie olduğu gibi kalır), 4 (helpers md), 5 (helpers kod), 10 (başlat md).** Değişenler aşağıda; her biri NotebookEdit `replace` ile, içerik tam metin.

- [ ] **Step 1: Kopyala** — komut gerekçesi: Task 1 ile aynı (ipynb JSON'unu Read+Write yeniden encode eder).

```bash
cp "collab-toolbox/video_generator/wan22-arbuzai/manual.ipynb" "collab-toolbox/photo_generator/nova-3dcg/manual.ipynb"
```

- [ ] **Step 2: Cell 0 (markdown, başlık) — replace:**

```markdown
# Nova 3DCG foto üretimi — ComfyUI interaktif deneme (Colab)

**Input:** prompt (ComfyUI UI'da) · **Output:** görsel (SaveImage) — beğenilen ayar **Export (API)** ile `MyDrive/photoGenV2/workflow_api.json`'a

Sıra:
1. **CONFIG** — Civitai cookie
2. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
3. **ComfyUI + Manager + custom node'lar** (7)
4. **Modeller** — önce gated probe, sonra indir (~7.5 GiB)
5. **Başlat + cloudflared tünel** → UI linki

> Drive kullanılmaz; modeller her oturumda kaynaktan iner (Colab geçici diski).
>
> **Runtime → Change runtime type → GPU (T4 yeter — SDXL sınıfı model, A100 gerekmez)** → **Run all** →
> en alttaki linke gir → bu klasördeki `workflow_manual.json`'u yükle →
> checkpoint'i `nova3DCGXL_ilV90` seç → **Power Lora Loader**'a USNR **0.8** ekle →
> prompt'u **POSITIVE / NEGATIVE** kutularına yaz → Run.
>
> Ayarların tamamı bir sonraki hücrede.
```

- [ ] **Step 3: Cell 1 (markdown, preset) — replace:**

```markdown
## Nova preset — UI'da ne ayarlanacak

Grafik = creator'ın (Legendaer) Basic V37 workflow'u, birebir. Aşağısı grafiğin kendi künyesinden çıkan tespitler; test ettikçe gerçek gözlemle güncellenir.

| Ayar | Değer |
|---|---|
| Checkpoint | CheckpointLoaderSimple → `nova3DCGXL_ilV90.safetensors` seç (grafik `fabricatedXL_v70` ile geliyor — bizde yok, değiştir) |
| LoRA | **Power Lora Loader boş gelir** → `USNR_STYLE_ILL_V1_lokr3-000024` ekle, ağırlık **0.8** |
| Prompt | **POSITIVE / NEGATIVE** başlıklı kutular (ImpactWildcardProcessor). CLIPTextEncode'lara dokunma — linkten dolduruluyor, kutuları ölü |
| Steps / CFG / Denoise / Çözünürlük / Batch | Soldaki primitive kutular (**Steps**, **CFG**, **Denoise**, **Width**, **Height**, **Batch Size**). KSampler'ın kendi widget'ları da linkle eziliyor — orada değil |
| Yüz düzeltme | **FaceDetailer default AÇIK** (face_yolov9c + SAM hazır iner); önce/sonra karşılaştırma panelinde |
| Kapalı dallar | **Control Center** panelinden tek tık: Ultimate SD Upscale (Remacri), HiresFix, El/Göz/NSFW detailer, ControlNet, VPred... — default hepsi kapalı |

**Bilinmezler ve tuzaklar:**

- Nova 3DCG XL IL v9.0'ın **v-pred olup olmadığı bilinmiyor** — çıktı bozuk/gri gelirse Control Center'dan "VPred Model?" grubunu açıp dene.
- Remacri dalı (**Ultimate SD Upscale** grubu) default kapalı; açtığında dosya hazır, ekstra indirme gerekmez.
- Ayar değiştirdikten sonra **Export (API)'yi yeniden al** — export ayarların fotoğrafıdır, sonradan değişen değeri bilmez.
```

- [ ] **Step 4: Cell 6 (markdown, custom node'lar) — replace:**

```markdown
## 3) ComfyUI + Manager + Custom Node'lar (7)

Liste `workflow_manual.json`'daki node künyelerinden (`cnr_id`/`aux_id`); grafikteki kalan her node comfy-core, kurulum istemez. Bypass'lı dalların paketleri de kurulur — UI grafiği yüklerken eksik node class'ı kırmızı düşer.

Biri başarısız olursa hücre `RuntimeError` ile durur (fail-loud).
```

- [ ] **Step 5: Cell 7 (kod, custom node'lar) — replace:**

```python
%cd /content

# === System deps + ComfyUI ===
!apt-get install -y aria2 > /dev/null 2>&1
![ -d ComfyUI ] || git clone https://github.com/comfyanonymous/ComfyUI.git
%cd /content/ComfyUI
!git pull -q
!pip install -q -r requirements.txt
!pip install -q opencv-python

# === Custom nodes (fail-loud: clone or pip failure -> RuntimeError) ===
import os
%cd /content/ComfyUI/custom_nodes

# (folder, repo) — trailing comment = what the node provides to the Basic V37 graph
CUSTOM_NODES = [
    ("ComfyUI-Manager",         "https://github.com/ltdrdata/ComfyUI-Manager.git"),          # detect missing nodes in the UI
    ("rgthree-comfy",           "https://github.com/rgthree/rgthree-comfy.git"),             # Power Lora Loader, Seed, Fast Groups Bypasser, Image Comparer
    ("ComfyUI-Impact-Pack",     "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"),      # FaceDetailer, wildcard prompts, SAMLoader, switches
    ("ComfyUI-Impact-Subpack",  "https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git"),   # UltralyticsDetectorProvider
    ("ComfyUI-Easy-Use",        "https://github.com/yolain/ComfyUI-Easy-Use.git"),           # easy int/float, easy hiresFix
    ("ComfyUI-Custom-Scripts",  "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git"),  # MathExpression
    ("ComfyUI_UltimateSDUpscale", "https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git"), # UltimateSDUpscale (tiled Remacri upscale)
    ("ComfyUI-KJNodes",         "https://github.com/kijai/ComfyUI-KJNodes.git"),             # ImageResizeKJv2
]

for name, url in CUSTOM_NODES:
    if os.path.exists(name) and os.listdir(name):
        log(f"{name}: zaten var")
        continue
    log(f"{name}: cloning...")
    # --recurse-submodules: UltimateSDUpscale vendors its upstream repo as a git submodule;
    # an empty submodule folder makes the node import fail. Harmless for the others.
    run(["git", "clone", "--depth", "1", "--recurse-submodules", url, name], f"clone {name}", timeout=180)
    if not os.listdir(name):                 # clone reported success but folder is empty
        raise RuntimeError(f"{name}: klon sonrası klasör boş")
    req = f"/content/ComfyUI/custom_nodes/{name}/requirements.txt"
    if os.path.exists(req):
        run(f"pip install -q -r {req}", f"pip install {name}", timeout=300)  # install node deps

log(f"{len(CUSTOM_NODES)} custom node hazır", "OK")
```

- [ ] **Step 6: Cell 8 (markdown, modeller) — replace:**

```markdown
## 4) Modeller — önce gated probe, sonra indir (~7.5 GiB)

Gated erişim **ağır indirmeden önce** doğrulanır (ilk 1 KB): cookie ölmüşse 6.5 GiB'lık checkpoint'e başlamadan, Civitai'nin **gerçek yanıtıyla** durur.

Herhangi bir dosya bozuk/eksik inerse hücre `RuntimeError` ile durur; bozuk dosya **silinmez**, inceleme için diskte kalır.

Dosyalar **grafiğin `widgets_values`'ında yazan adlarla** iner: `nova3DCGXL_ilV90.safetensors` (Civitai'nin verdiği ad zaten bu), `4x_foolhardy_Remacri.pth`, `bbox/face_yolov9c.pt`, `sam_vit_b_01ec64.pth`. Ad tutmazsa dropdown'da/loader'da görünmez.

`.pt`/`.pth` dosyaları safetensors gibi kendi boyutunu beyan etmez → doğrulamaları `check_binary`: hata sayfası değil mi (HTML/JSON başlıyor mu) + taban boyutu aşıyor mu.
```

- [ ] **Step 7: Cell 9 (kod, modeller) — replace:**

```python
import os, glob

# === Target folders ===
COMFY = "/content/ComfyUI"
CKPT = f"{COMFY}/models/checkpoints"
LORA = f"{COMFY}/models/loras"
UPSC = f"{COMFY}/models/upscale_models"
BBOX = f"{COMFY}/models/ultralytics/bbox"   # UltralyticsDetectorProvider lists files as "bbox/<name>"
SAMS = f"{COMFY}/models/sams"
for d in [CKPT, LORA, UPSC, BBOX, SAMS]:
    os.makedirs(d, exist_ok=True)

def check_binary(path, min_bytes):
    """State of a .pt/.pth model -> ("ok" | "partial" | "invalid", msg).

    Torch pickle/zip files carry no self-describing total length (unlike safetensors), so the
    honest cheap checks are: the head is not an HTML/JSON error page, and the size clears a loose
    floor (guards against truncated/error downloads, not an exact size). Below the floor counts
    as "partial" so an interrupted download stays resumable.
    """
    if not os.path.exists(path):
        return "invalid", "missing"
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(16)
    if head[:1] in (b"<", b"{"):
        return "invalid", f"error page? ({human(size)})"
    if size < min_bytes:
        return "partial", f"{human(size)} < taban {human(min_bytes)}"
    return "ok", human(size)

# === Single download function — shared flow for HF (aria2c) and Civitai (curl) (DRY) ===
def fetch(url, target_dir, filename, label, *, parallel, headers=None, validate=None):
    """Download + validate a model; anything invalid stops the run (fail-loud, nothing deleted).

    parallel=True -> aria2c (fast for large HF files), False -> curl (Civitai, login cookie).
    validate -> (path) -> (state, msg); default check_safetensors. .pt/.pth files pass a
    check_binary lambda because they have no self-describing length.
    Downloads land in <target>.part and are renamed only once the validator says "ok", so
    ComfyUI never sees a half-written file under the real model name.

    On failure the raw HTTP exchange is printed, not a summary of it: curl runs with
    --fail-with-body (non-zero exit, but the response body is kept instead of discarded) and -D
    (every response header of the redirect chain), so a Civitai 401/403 shows the server's own
    headers and body verbatim.
    """
    validator = validate or check_safetensors
    target = os.path.join(target_dir, filename)
    part = target + ".part"
    hdrs = f"/tmp/{filename}.headers"

    if os.path.exists(target):
        state, msg = validator(target)
        if state == "ok":
            log(f"{label}: zaten var ({msg})")
            return
        raise RuntimeError(f"{label}: {state} — {msg}\n{target}\n--- file head ---\n{head_text(target)}")

    resume = False
    if os.path.exists(part):
        state, msg = validator(part)
        if state == "invalid":
            # Resuming onto garbage would append good bytes to it and hide the problem.
            raise RuntimeError(f"{label}: .part {state} — {msg}\n{part}\n--- file head ---\n{head_text(part)}")
        if state == "ok":
            log(f"{label}: .part zaten tam ({msg}) — indirilmiyor")
        else:
            log(f"{label}: .part'tan devam ({msg})")
            resume = True

    if not os.path.exists(part) or resume:
        log(f"{label}: iniyor")
        if parallel:
            cmd = ["aria2c", "-x", "16", "-s", "16", "-k", "1M", "--continue=true",
                   "--console-log-level=warn", "--auto-file-renaming=false",
                   "--allow-overwrite=true", "-d", target_dir, "-o", os.path.basename(part)]
            if headers:
                cmd += ["--header", headers]
        else:
            cmd = ["curl", "-L", "-C", "-", "--fail-with-body", "--max-time", "1800",
                   "-D", hdrs, "-o", part]
            if headers:
                cmd += ["-H", headers]
        cmd.append(url)
        try:
            run(cmd, label, timeout=3600)
        except RuntimeError as e:
            raise RuntimeError(
                f"{e}\n{url.split('?')[0]}\n"
                f"--- response headers ---\n{head_text(hdrs)}\n"
                f"--- response body ---\n{head_text(part)}"
            ) from None

    state, msg = validator(part)
    if state != "ok":
        raise RuntimeError(f"{label}: {state} — {msg}\n{part}\n{url.split('?')[0]}\n"
                           f"--- response headers ---\n{head_text(hdrs)}\n"
                           f"--- file head ---\n{head_text(part)}")
    os.replace(part, target)
    log(f"{label}: indirildi ve doğrulandı ({msg})", "OK")

# Civitai auth: session cookie ONLY. A ?token= API key authenticates the request as that key's
# account -> creator-gated assets answer 401.
# Host = civitai.RED: the cookie is same-origin there. Sending it to .com is cross-domain and
# returns the login+turnstile page instead of the file.
def civitai_url(version_id):
    return f"https://civitai.red/api/download/models/{version_id}"

def cookie_header():
    return f"Cookie: __Secure-civ-token={COOKIE_VALUE}"

def civitai_probe(version_id, label):
    """Fail-fast: range-download the first 1KB to verify gated access BEFORE the 6.5GiB checkpoint.
    On non-2xx or a login wall, surface Civitai's ACTUAL response body -- no hardcoded guesses.
    """
    out = "/content/_probe.bin"
    code = (run(["curl", "-sL", "--max-time", "60", "-r", "0-1023",
                 "-H", cookie_header(), "-w", "%{http_code}", "-o", out,
                 civitai_url(version_id)], f"probe {label}") or "").strip()[-3:]
    body = b""
    if os.path.exists(out):
        with open(out, "rb") as f:
            body = f.read(512)
        os.remove(out)
    # success = 2xx AND the body is real binary (safetensors), not an HTML/JSON error page
    if code.startswith("2") and not body.startswith(b"<") and not body.startswith(b'{"'):
        log(f"{label}: erişim OK", "OK")
        return
    raise RuntimeError(f"❌ {label}: HTTP {code} — Civitai yanıtı: "
                       f"{body.decode('utf-8', 'replace').strip() or '(boş gövde — binary değil)'}")

# === Civitai gated models (curl + login cookie) ===
CIVITAI_MODELS = [
    # (version_id, target_dir, filename, label)
    (2744564, CKPT, "nova3DCGXL_ilV90.safetensors",               "Nova 3DCG XL IL v9.0"),
    (1552087, LORA, "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "USNR STYLE ILL v1.0"),
]

# === Open downloads (aria2c, no auth) ===
# The graph's default-ON FaceDetailer branch loads the detector + SAM at startup; the bypassed
# Ultimate SD Upscale branch reads Remacri the moment the user enables it -> all three ship ready.
OPEN_MODELS = [
    # (url, target_dir, filename, label, min_bytes)
    ("https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth",
     UPSC, "4x_foolhardy_Remacri.pth", "Remacri 4x upscaler", 50_000_000),
    ("https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt",
     BBOX, "face_yolov9c.pt", "Yuz dedektoru (yolov9c)", 40_000_000),
    ("https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
     SAMS, "sam_vit_b_01ec64.pth", "SAM ViT-B", 300_000_000),
]

# 1) Fail-fast: verify gated access before spending ~20 minutes on downloads
log(f"Gated probe: {len(CIVITAI_MODELS)} asset")
for vid, d, fn, label in CIVITAI_MODELS:
    civitai_probe(vid, label)

# 2) Open models (aria2c)
for url, d, fn, label, floor in OPEN_MODELS:
    fetch(url, d, fn, label, parallel=True, validate=lambda p, m=floor: check_binary(p, m))

# 3) Civitai — parallel=False: aria2c forwards the cookie to the B2 store on redirect and gets 403,
#    curl drops it cross-host and gets through.
for vid, d, fn, label in CIVITAI_MODELS:
    fetch(civitai_url(vid), d, fn, label, parallel=False, headers=cookie_header())

# === Summary (reaching here means everything downloaded + validated) ===
for title, folder, pattern in [("checkpoints", CKPT, "*.safetensors"), ("loras", LORA, "*.safetensors"),
                               ("upscale_models", UPSC, "*.pth"), ("ultralytics/bbox", BBOX, "*.pt"),
                               ("sams", SAMS, "*.pth")]:
    print(f"\n📂 {title}/")
    for f in sorted(glob.glob(f"{folder}/{pattern}")):
        print(f"   {human(os.path.getsize(f))}  {os.path.basename(f)}")
log("Tüm modeller indirildi ve doğrulandı", "OK")
```

- [ ] **Step 8: Cell 11 (kod, başlat + tünel) — replace.** arbuzai cell 11 ile aynı iskelet; yalnız link sonrası print bloğu değişir. Tam içerik:

```python
import subprocess, time, urllib.request, re, os

if not os.path.isfile("/content/cloudflared"):
    run(["wget", "-q", "-O", "/content/cloudflared",
         "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"], "cloudflared")
    run(["chmod", "+x", "/content/cloudflared"], "chmod cloudflared")

# Re-run safety: kill the previous ComfyUI + tunnel before starting new ones
subprocess.run(["pkill", "-f", "main.py"], check=False)
subprocess.run(["pkill", "-f", "cloudflared"], check=False)
time.sleep(2)

# --enable-manager: on current ComfyUI the Manager is OFF without this flag. The workflow is loaded
# by hand, so missing nodes are likely -> Manager has to stay reachable in the UI.
logf = open("/content/comfyui.log", "w")
subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", str(COMFY_PORT), "--enable-manager"],
                 cwd="/content/ComfyUI", stdout=logf, stderr=subprocess.STDOUT)
ok = False
for i in range(45):
    time.sleep(2)
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{COMFY_PORT}/system_stats", timeout=2)
        ok = True
        break
    except Exception:
        pass
if not ok:
    print("".join(open("/content/comfyui.log").readlines()[-30:]))
    raise RuntimeError("❌ ComfyUI 90 sn içinde başlamadı — yukarıdaki log'a bak")
log(f"ComfyUI ayakta ({(i+1)*2}s)", "OK")

# cloudflared output goes to a file, not a pipe: an unread pipe fills up and blocks the process.
tunlog = "/content/cloudflared.log"
subprocess.Popen(["/content/cloudflared", "tunnel", "--url", f"http://127.0.0.1:{COMFY_PORT}"],
                 stdout=open(tunlog, "w"), stderr=subprocess.STDOUT)
link = None
for _ in range(30):
    time.sleep(1)
    m = re.search(r"https://[-\w.]+trycloudflare\.com", open(tunlog).read()) if os.path.exists(tunlog) else None
    if m:
        link = m.group(0)
        break
if not link:
    print(open(tunlog).read()[-1000:] if os.path.exists(tunlog) else "(cloudflared log yok)")
    raise RuntimeError("❌ cloudflared linki 30 sn içinde alınamadı")

print(f"\n🔗 ComfyUI linki: {link}\n")
print("⬆️  Linke gir → bu klasördeki workflow_manual.json'u yükle")
print("🎨 Checkpoint: nova3DCGXL_ilV90 seç (fabricatedXL ile gelir, bizde yok)")
print("⚠️  Power Lora Loader: USNR_STYLE_ILL_V1_lokr3-000024 @ 0.8 ekle (boş gelir)")
print("📝 Prompt: POSITIVE / NEGATIVE kutuları (CLIPTextEncode'lara dokunma)")
print("🎛  Kapalı dallar (Remacri upscale, hiresfix, el/göz) → Control Center panelinden")
print("💾 Beğenince: Workflow → Export (API) → dosyayı MyDrive/photoGenV2/workflow_api.json olarak koy")
print("    Eksik node olursa: Manager → Install Missing Custom Nodes → Restart\n")

# === Keep the cell OPEN (critical) ===
# ComfyUI + the tunnel run in the background. If this cell ENDS, Colab can call the runtime idle
# and disconnect -> ComfyUI + link die. Streaming the log keeps the cell in the foreground and
# shows generation progress when Run is pressed in the UI.
# To stop: interrupt this cell (■) or Runtime -> Disconnect.
print("📡 ComfyUI çalışıyor — BU HÜCREYİ KAPATMA. Canlı log:\n")
try:
    subprocess.run(["tail", "-n", "+1", "-f", "/content/comfyui.log"])
except KeyboardInterrupt:
    log("Hücre durduruldu — ComfyUI hâlâ arka planda çalışıyor (yeni link için bu hücreyi tekrar çalıştır).", "WARN")
```

---

### Task 3: Doğrulama (grep — commit YOK)

**Files:** yok (salt okuma)

**Interfaces:**
- Consumes: Task 1-2'nin çıktıları.
- Produces: kullanıcıya "Colab'da test edebilirsin" raporu. Commit kullanıcı doğrulaması SONRASI, kullanıcı isteyince.

Grep desenleri **tırnaksız düz token**: `.ipynb` kod hücreleri escaped JSON string tuttuğu için `"287"` gibi tırnaklı desen asla eşleşmez (arbuzai planında kanıtlanmış ders).

- [ ] **Step 1: Olması gerekenler** — her biri `collab-toolbox/photo_generator/nova-3dcg/manual.ipynb` içinde en az 1 kez (Grep, `output_mode: count`):
`nova3DCGXL_ilV90` · `USNR_STYLE_ILL_V1_lokr3-000024` · `2744564` · `1552087` · `4x_foolhardy_Remacri` · `face_yolov9c` · `sam_vit_b_01ec64` · `Impact-Subpack` · `UltimateSDUpscale` · `recurse-submodules` · `photoGenV2` · `workflow_manual.json` · `check_binary` · `T4`

- [ ] **Step 2: Olmaması gerekenler** — `collab-toolbox/photo_generator/nova-3dcg/` altında 0 eşleşme:
`SmoothMix` · `lightx2v` · `wan2` (küçük harf duyarsız aramayla `Wan2_1_VAE` vb. de yakalanır) · `VHS_VideoCombine` · `WanVideoWrapper` · `sageattention` · `arbuzai` · `imageToVideoV2`
**Not:** bu arama `manual.ipynb` için — `workflow_manual.json` aramadan muaf değil ama bu token'lar orada zaten yok; eşleşme çıkarsa kopya yanlış demektir.

- [ ] **Step 3: Değişmemesi gerekenler** — Grep ile `manual.ipynb`'de hâlâ mevcut: `check_safetensors` (helpers hücresi dokunulmamış) · `__Secure-civ-token` (CONFIG dokunulmamış) · `--enable-manager`.

- [ ] **Step 4: Kullanıcıya raporla** — değişen dosya listesi + Colab test adımları (spec'teki Doğrulama bölümü). Stage/commit yapılmaz.

---

## Self-review notu

- Spec kapsaması: klasör+kopya (Task 1), 7 paket + 5 model + T4 + markdown yönergeleri (Task 2), doğrulama (Task 3). Spec'in "Doğrulama" bölümü kullanıcının Colab adımları — plana taşınmadı, rapora girer.
- `min_bytes` tabanları gevşek (gerçek boyutların ~%75'i): hata sayfası/yarım dosyayı yakalar, gerçek dosyayı asla reddetmez.
- Cell 3'teki cookie arbuzai'den olduğu gibi gelir (kullanıcının kendi token'ı, repoda zaten mevcut) — yeniden yapıştırma gerekmez.
