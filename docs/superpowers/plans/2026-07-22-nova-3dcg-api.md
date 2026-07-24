# Nova 3DCG foto üretimi — API modu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `nova-3dcg/api.ipynb` — CONFIG'deki prompt listesinden, prompt başına `VARIANTS` görsel, UI açmadan, `photoGenV2/output/N_a.png...` olarak Drive'a.

**Architecture:** `wan22-arbuzai/api.ipynb` (14 hücre) kopyalanır; 10 hücre değişir, 4 hücre (4, 5, 10, 11) olduğu gibi kalır. Enjeksiyon: POSITIVE **3** + NEGATIVE **4** (ikisine de `wildcard_text` VE `populated_text` — çift alan), Seed **40**. Spec: `docs/superpowers/specs/2026-07-22-nova-3dcg-api-design.md`.

**Tech Stack:** Colab notebook, ComfyUI HTTP API (`POST /prompt`, `GET /history`, `GET /view`), Civitai/HF indirmeleri.

## Global Constraints

- **Dil:** notebook markdown + runtime çıktısı Türkçe; kod yorumları/docstring İngilizce.
- **Python çalıştırma yok**; inceleme Grep/Read. Komut yalnız gerekliyse, gerekçesi söylenerek (bu planda 1: ipynb kopyası).
- **Git'e hiçbir şey eklenmez** — kullanıcı Colab'da doğrulayana kadar stage/commit yok.
- Hata mesajında neden uydurulmaz; servisin gerçek çıktısı basılır.
- `workflow_api.json` (repo + Drive kopyası) **değişmez**; notebook yalnız 3/4/40 node'larına yazar.
- Sabit id'ler: `PROMPT_NODE = "3"`, `NEGATIVE_NODE = "4"`, `SEED_NODE = "40"` — kullanıcının export'undan okundu (LoRA'lı sürüm, USNR 0.8 `lora_1`'de).
- Üretim başına **tam 1** `type=="output"` görseli; değilse fail-loud (grafikte Batch Size 1 kalmalı).
- `SEED = None` → varyant başına rastgele; sayı → `SEED + varyant_sırası` (4 varyant aynı seed'le birebir aynı görsel olurdu).

---

### Task 1: api.ipynb

**Files:**
- Create: `collab-toolbox/photo_generator/nova-3dcg/api.ipynb` (arbuzai api.ipynb kopyası + 10 hücre değişir)

**Interfaces:**
- Consumes: `collab-toolbox/video_generator/wan22-arbuzai/api.ipynb` (iskelet), `collab-toolbox/photo_generator/nova-3dcg/manual.ipynb` (hücre 6-9 içerikleri), `nova-3dcg/workflow_api.json` (id'lerin kaynağı — değişmez).
- Produces: Kullanıcının çalıştıracağı batch notebook. Fonksiyonlar: `build_plan(prompts) -> [(n, letter, action, prompt, reason)]`, `generate_one(client, n, letter, prompt, seed) -> path`, `process_all(plan)`.

- [ ] **Step 1: Kopyala** — komut gerekçesi: ipynb JSON'unu Read+Write yeniden encode eder; kopya ancak komutla birebir olur.

```bash
cp "collab-toolbox/video_generator/wan22-arbuzai/api.ipynb" "collab-toolbox/photo_generator/nova-3dcg/api.ipynb"
```

- [ ] **Step 2: Cell 0 (markdown, başlık) — replace:**

```markdown
# Nova 3DCG foto üretimi — Batch API (prompt listesi × varyant) — Colab

CONFIG'e prompt listesini yaz, çalıştır → her dolu prompt için `VARIANTS` görsel Drive'a düşer. ComfyUI arka planda **API** olarak çalışır; **UI açılmaz, tünel yok.**

> Grafiği kurcalamak, ayar/LoRA denemek istiyorsan bu değil — **`manual.ipynb`**. O ComfyUI'yi tünelle açar; beğendiğin ayarı **Export (API)** ile dondurur, bu notebook o export'u koşar.

```
photoGenV2/                 ← Drive'da senin oluşturacağın klasör
├── workflow_api.json   ← manual.ipynb'de Export (API) ile kaydettiğin graf (USNR 0.8 içinde)
└── output/             ← 0_a.png, 0_b.png, … (otomatik oluşur)
```

**Adlandırma:** `PROMPTS[0]` → `output/0_a.png … 0_d.png` (varyant = aynı prompt, farklı seed). Beğendiğini `imageToVideoV2/input/0.png` diye elle kopyalarsın.

Sıra:
1. **CONFIG** — Drive mount + prompt listesi · ardından **üretim planı** basılır
2. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
3. **ComfyUI + custom node'lar** (8)
4. **Modeller** — önce gated probe, sonra indir (~7.5 GiB)
5. **ComfyUI'yi başlat** (arka planda, API)
6. **Üret** — her prompt × varyant: render, Drive'a yaz

> **Runtime → Change runtime type → GPU (T4)** → Run all.

> **Yarıda kalırsa baştan çalıştır.** Çıktısı olan varyantlar atlanır. Birini yeniden üretmek için Drive'dan o png'yi sil.

> **Prompt'lar düz metin.** `__x__` / `{a|b}` wildcard sözdizimi API modunda işlenmeyebilir (Impact Pack #483) — kullanma. `(kelime:1.3)` ağırlık sözdizimi serbest, o CLIP'te işlenir.

> **Ayarlar grafikte.** Çözünürlük, step, cfg, USNR ağırlığı — hepsi export'tan gelir; bu notebook yalnız prompt/negatif/seed yazar.
```

- [ ] **Step 3: Cell 1 (markdown, CONFIG) — replace:**

```markdown
## 1) CONFIG

Google Drive **burada** mount edilir: auth istemi ilk saniyede çıksın, indirmenin ortasında beklemesin.

Doldurulacak yer `PROMPTS` — **liste sırası çıktı numarasıdır**: `PROMPTS[0]` → `output/0_*.png`. Üç tırnak arasına yazılır; çok satırlı olabilir, `"` geçebilir. Bir numarayı bu turda üretmek istemiyorsan **boş bırak** (`""`) — liste kaymaz, o numara atlanır.

`NEGATIVE` tektir, tüm prompt'lara aynen uygulanır (POSITIVE ile aynı mekanizmayla grafiğe yazılır).

Hemen alttaki hücre **üretim planını basar**: hangi numara/varyant üretilecek, hangisi neden atlanacak — indirmeden önce.

Cookie'nin süresi dolmuşsa (~30 gün) `civitai.red`'den yenile.
```

- [ ] **Step 4: Cell 2 (kod, CONFIG) — replace:**

```python
# === Google Drive — en başta mount edilir ===
# Auth istemi ilk saniyede çıksın: model indirmesinin ortasında beklemesin.
from google.colab import drive
drive.mount('/content/drive')

# === Prompt listesi — index = çıktı numarası (PROMPTS[0] -> output/0_*.png) ===
# Üç tırnak: prompt'lar çok satırlı olur ve içlerinde " geçer.
# Boş madde ("") o numarayı atlar -- listeyi kaydırmadan tek numarayı kapatmanın yolu.
PROMPTS = [
    """
    """,
]

# One negative for the whole batch, injected the same dual-field way as the positive.
NEGATIVE = """censored, lowres, bad quality, worst quality, worst detail, sketch, watermark, jpeg artifacts, signature, username, simple background, anime, 3D,"""

VARIANTS = 4                 # kaç görsel / prompt (a, b, c, ...)
SEED = None                  # None -> varyant başına rastgele; sayı verirsen varyant v için SEED+v

# === Drive ===
DRIVE_ROOT        = "/content/drive/MyDrive/photoGenV2"
WORKFLOW_FILENAME = "workflow_api.json"      # DRIVE_ROOT altında, API format

# === Civitai login-gated download ===
# civitai.red -> log in -> F12 -> Application -> Cookies -> __Secure-civ-token değerini yapıştır
# (çift tıkla -> Ctrl+A -> Ctrl+C; tek tık hücreyi kırpar ve `assert len>200` yine geçer).
# NOTE: auth moved to auth.civitai.com -> the cookie NAME is __Secure-civ-token (NOT the old
#   __Secure-civitai-token) and the value is a short ES256 JWT (~420 chars), not the old long JWE.
# Cookie only; never a ?token= API key -> gated assets answer 401.
COOKIE_VALUE = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImNpdml0YWktZGV2LTIwMjYtMDYtZWMiLCJ0eXAiOiJKV1QifQ.eyJzaWduZWRBdCI6MTc4MjY0Mjc0NjMwMywic3ViIjoiMTE0OTgwOTgiLCJpYXQiOjE3ODI2NDI3NDYsImV4cCI6MTc4NTIzNDc0NiwianRpIjoiNmFkMTcxNTktNWJiMy00YTQ2LWEzYzctYjFjNjRmYzUxMzU4IiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmNpdml0YWkuY29tIn0.FnTlCXmO4fkKXl3nDikNE1VeGGOlNYcmpMcv1bJl4MdazltlcnUVYyluJK9qT68QM_1kuzs6guhpsalRKU9frQ"

# === Render ===
TIMEOUT_PER_RENDER = 15 * 60   # saniye — bir görsel bu sürede bitmezse fail-loud
POLL_INTERVAL      = 5         # saniye — /history yoklama aralığı

# === Derived paths ===
COMFY_PORT       = 8188
COMFYUI_URL      = f"http://127.0.0.1:{COMFY_PORT}"
WORKFLOW_PATH    = f"{DRIVE_ROOT}/{WORKFLOW_FILENAME}"
OUTPUT_DIR       = f"{DRIVE_ROOT}/output"

COMFY_ROOT       = "/content/ComfyUI"
COMFY_OUTPUT_DIR = f"{COMFY_ROOT}/output"
COMFY_LOG        = "/content/comfyui.log"

VARIANT_LETTERS = "abcdefghijklmnopqrstuvwxyz"

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)
assert len(COOKIE_VALUE) > 200, "❌ COOKIE_VALUE boş/çok kısa — civitai.red'den __Secure-civ-token (ES256 JWT) yapıştır"
assert os.path.exists(WORKFLOW_PATH), f"❌ Workflow yok: {WORKFLOW_PATH} — manual.ipynb'de 'Workflow → Export (API)' ile kaydedip Drive'a koy"
assert any(p.strip() for p in PROMPTS), "❌ PROMPTS'ta dolu tek bir prompt yok — yukarıya prompt'larını yaz"
assert 1 <= VARIANTS <= len(VARIANT_LETTERS), f"❌ VARIANTS 1-{len(VARIANT_LETTERS)} arası olmalı (harfle adlandırılıyor)"

print(f"✓ Drive: {DRIVE_ROOT}")
print(f"✓ Cookie: {len(COOKIE_VALUE)} char  |  Timeout: {TIMEOUT_PER_RENDER // 60} dk/görsel")
print(f"✓ Seed: {SEED if SEED is not None else 'varyant başına rastgele'}  |  Varyant: {VARIANTS}")
print(f"✓ {len(PROMPTS)} prompt ({sum(1 for p in PROMPTS if not p.strip())} tanesi boş — atlanacak)")
print("=== GPU ===")
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

- [ ] **Step 5: Cell 3 (kod, üretim planı) — replace:**

```python
# === Üretim planı — indirmeden önce, bilerek ===
# loop_maker's rule: decide the whole run before a GPU minute is spent. An all-empty PROMPTS list
# or an already-complete output folder shows up here, not after minutes of model downloads.
# log()/human() belong to section 2 and are not defined yet, so this cell prints plainly.
import os

def build_plan(prompts):
    """One row per (prompt index, variant letter) -> (n, letter, action, prompt, reason).

    An empty prompt is a deliberate 'skip this number' switch: PROMPTS is a flat list, so blanking
    an entry is the only way to disable one number without shifting every number after it.
    """
    rows = []
    for n, prompt in enumerate(prompts):
        for v in range(VARIANTS):
            letter = VARIANT_LETTERS[v]
            out = f"{OUTPUT_DIR}/{n}_{letter}.png"
            if not prompt.strip():
                rows.append((n, letter, "ATLA", "", "prompt boş"))
            elif os.path.exists(out) and os.path.getsize(out) > 0:
                rows.append((n, letter, "ATLA", prompt, "çıktı zaten var"))
            else:
                rows.append((n, letter, "ÜRET", prompt, ""))
    return rows

PLAN = build_plan(PROMPTS)

print(f"\n{'ÇIKTI':>7}  {'KARAR':<6}  AÇIKLAMA")
print("-" * 60)
for n, letter, action, prompt, reason in PLAN:
    detail = reason if reason else prompt.strip().replace("\n", " ")[:40]
    print(f"{f'{n}_{letter}':>7}  {action:<6}  {detail}")

_to_render = sum(1 for r in PLAN if r[2] == "ÜRET")
print("-" * 60)
print(f"Üretilecek: {_to_render}  |  Atlanacak: {len(PLAN) - _to_render}")

if _to_render == 0:
    raise RuntimeError("❌ Üretilecek görsel yok — yukarıdaki tabloya bak (prompt'lar boş ya da hepsi zaten üretilmiş)")
```

- [ ] **Step 6: Cell 4 ve 5 — DOKUNMA.** (Yardımcılar md + kod: CONFIG kapısı, `log`, `run`, `check_safetensors`, `describe_comfy_error` — arbuzai'den olduğu gibi kalır; foto akışı da aynılarını kullanıyor.)

- [ ] **Step 7: Cell 6 (markdown, custom node'lar) — replace.** İçerik = `nova-3dcg/manual.ipynb` **cell 6** ile birebir aynı (başlık "3) ComfyUI + Manager + Custom Node'lar (8)" olan hücre; Read ile kopyala, NotebookEdit ile yapıştır).

- [ ] **Step 8: Cell 7 (kod, custom node'lar) — replace.** İçerik = `nova-3dcg/manual.ipynb` **cell 7** ile birebir aynı (8 paketlik `CUSTOM_NODES` + `--recurse-submodules` klon döngüsü).

- [ ] **Step 9: Cell 8 (markdown, modeller) — replace.** İçerik = `nova-3dcg/manual.ipynb` **cell 8** ile birebir aynı (~7.5 GiB, `check_binary` açıklaması).

- [ ] **Step 10: Cell 9 (kod, modeller) — replace.** İçerik = `nova-3dcg/manual.ipynb` **cell 9** ile birebir aynı, **tek fark ilk satırlar**: manual'deki

```python
COMFY = "/content/ComfyUI"
```

satırı burada CONFIG'den gelen sabiti kullanır:

```python
COMFY = COMFY_ROOT
```

(gerisi — `CKPT/LORA/UPSC/BBOX/SAMS` klasörleri, `check_binary`, `validate` parametreli `fetch`, `civitai_url/cookie_header/civitai_probe`, 2 Civitai + 3 açık model listesi, probe → indir → özet — birebir).

- [ ] **Step 11: Cell 10 ve 11 — DOKUNMA.** (ComfyUI arka plan başlatma md + kod: arbuzai'den olduğu gibi; tünelsiz, 90 sn fail-loud. Cell 10'daki "manual.ipynb'de düzenle → Export (API) → Drive'a yaz" yönergesi burada da aynen geçerli.)

- [ ] **Step 12: Cell 12 (markdown, üret) — replace:**

```markdown
## 6) Üret

Plan tablosunda **ÜRET** yazan her `N_x` sırayla işlenir: render edilir, `output/N_x.png` olarak Drive'a yazılır, ComfyUI'daki kopya silinir.

Grafiğe yazılan üç yer: POSITIVE **3** (prompt — `wildcard_text` + `populated_text` **iki alana birden**: API modunda sunucunun hangisini okuduğu sürüme göre değişebiliyor, Impact Pack #483; iki dünyada da senin prompt'un gider), NEGATIVE **4** (aynı çift-alan yöntemi), Seed **40**. Diğer her şey — çözünürlük, step, cfg, USNR 0.8 — export'tan gelir.

**Seed:** her varyant için ayrı üretilir ve loglanır. `SEED`'e sayı verirsen varyant `v` için `SEED + v` kullanılır — dört varyant aynı seed'i alsaydı dört kez aynı görsel çıkardı; bu formülle hem tekrarlanabilir hem farklı olurlar. Export'taki `"seed": -1` asla sunucuya gitmez (rgthree -1'i frontend'de çözer, API'de frontend yok).

**Yarıda kalırsa** notebook'u baştan çalıştır: çıktısı olan varyantlar atlanır.

**Hata olursa:** model yükleyici hatası batch'i durdurur (her render aynı hatayı alırdı). Tek renderа özgü hata yalnız o varyantı atlar; üst üste 3 hata batch'i durdurur. Render `TIMEOUT_PER_RENDER` içinde bitmezse `TimeoutError`.
```

- [ ] **Step 13: Cell 13 (kod, üretim döngüsü) — replace:**

```python
import json, os, random, time, uuid, requests

class ComfyExecutionError(RuntimeError):
    """A prompt failed inside ComfyUI. Carries the raw error, plus whether it is infra-level.
    infra=True -> a model loader node failed, so the model is broken or missing."""
    def __init__(self, text, traceback_text, infra):
        super().__init__(text)
        self.text = text
        self.traceback_text = traceback_text
        self.infra = infra

# === Node ids (from workflow_api.json — the user's own export) ===
PROMPT_NODE   = "3"    # ImpactWildcardProcessor, _meta.title "POSITIVE"
NEGATIVE_NODE = "4"    # ImpactWildcardProcessor, _meta.title "NEGATIVE"
SEED_NODE     = "40"   # Seed (rgthree) -> KSampler 41, FaceDetailer 31 and both wildcard seeds

MAX_CONSECUTIVE_FAILURES = 3   # a batch that keeps failing is broken, not unlucky

# === Template I/O + patchers (SRP: one function injects one field) ===
def load_workflow(path):
    with open(path, encoding="utf-8") as f:
        wf = json.load(f)
    if "nodes" in wf:
        raise RuntimeError(
            "workflow_api.json UI formatında — ComfyUI'de 'Workflow → Export (API)' ile kaydet"
        )
    for node_id in (PROMPT_NODE, NEGATIVE_NODE, SEED_NODE):
        if node_id not in wf:
            raise RuntimeError(f"Workflow'da {node_id} node yok — graf değişmiş, node id'leri güncelle")
    return wf

def set_text(workflow, node_id, text):
    """Write BOTH text fields of an ImpactWildcardProcessor.

    Which field the server reads in API mode varies by version (Impact Pack #483: some builds use
    populated_text as-is and never process wildcard_text). Writing the same text to both means the
    render uses this text either way -- the stale-export-prompt trap cannot happen.
    """
    workflow[node_id]["inputs"]["wildcard_text"] = text
    workflow[node_id]["inputs"]["populated_text"] = text

def set_seed(workflow, seed):
    """The graph ships Seed (rgthree) at -1. rgthree randomises in the frontend widget, which does
    not exist in API mode -- sending -1 through would pin every render to the same noise. KSampler,
    FaceDetailer and both wildcard processors all link to this node, so one write covers them."""
    workflow[SEED_NODE]["inputs"]["seed"] = seed

# === ComfyUI HTTP client ===
class ComfyClient:
    def __init__(self, base_url):
        self.base = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())

    def submit(self, workflow):
        r = requests.post(f"{self.base}/prompt",
                          json={"prompt": workflow, "client_id": self.client_id}, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"POST /prompt -> HTTP {r.status_code}\n{r.text}")
        data = r.json()
        if data.get("node_errors"):
            raise RuntimeError("POST /prompt -> node_errors\n"
                               + json.dumps(data["node_errors"], indent=2, ensure_ascii=False))
        return data["prompt_id"]

    def wait(self, prompt_id, timeout):
        start = time.time()
        while True:
            if time.time() - start > timeout:
                raise TimeoutError(f"prompt {prompt_id}: {timeout}s içinde bitmedi")
            history = requests.get(f"{self.base}/history/{prompt_id}", timeout=30).json()
            if prompt_id in history:
                entry = history[prompt_id]
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise ComfyExecutionError(*describe_comfy_error(status))
                return entry
            time.sleep(POLL_INTERVAL)

    def save_output_image(self, history_entry, save_path):
        """Pull THE produced image over /view.

        type=="output" filters out temp previews (the rgthree Image Comparer in this graph
        registers temp files). Exactly one real output is the contract -- the graph has a single
        SaveImage and Batch Size must stay 1; anything else is printed raw and stops the render,
        because silently picking one of N images would hide a mis-set graph.
        """
        outputs = [item
                   for node_output in history_entry.get("outputs", {}).values()
                   for item in node_output.get("images", [])
                   if item.get("type", "output") == "output"]
        if len(outputs) != 1:
            raise RuntimeError(
                f"1 çıktı görseli bekleniyordu, {len(outputs)} geldi — grafikte Batch Size 1 mi?\n"
                + json.dumps(history_entry.get("outputs", {}), indent=2, ensure_ascii=False))
        item = outputs[0]
        r = requests.get(f"{self.base}/view", timeout=300, params={
            "filename":  item["filename"],
            "subfolder": item.get("subfolder", ""),
            "type":      "output",
        })
        r.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(r.content)
        return os.path.join(item.get("subfolder", ""), item["filename"])

# === One image, end to end ===
def generate_one(client, n, letter, prompt, seed):
    """One prompt + seed -> output/<n>_<letter>.png. Returns the saved path."""
    save_path = f"{OUTPUT_DIR}/{n}_{letter}.png"

    workflow = load_workflow(WORKFLOW_PATH)
    set_text(workflow, PROMPT_NODE, prompt)
    set_text(workflow, NEGATIVE_NODE, NEGATIVE)
    set_seed(workflow, seed)

    prompt_id = client.submit(workflow)
    history = client.wait(prompt_id, TIMEOUT_PER_RENDER)
    rel = client.save_output_image(history, save_path)

    local = os.path.join(COMFY_OUTPUT_DIR, rel)   # keep Colab's disk clean over a long batch
    if os.path.exists(local):
        os.remove(local)
    return save_path

# === The batch ===
def process_all(plan):
    """Render every ÜRET row in order. Skips, failures and the reason for each are printed.

    A loader failure stops the batch: the model is broken or missing, so every remaining render
    would hit the identical error. A render-specific failure only costs that variant.
    """
    todo = [row for row in plan if row[2] == "ÜRET"]
    client = ComfyClient(COMFYUI_URL)
    done = skipped = failed = 0
    consecutive = 0
    t_batch = time.time()

    log(f"Batch başlıyor — {len(todo)} görsel")
    for n, letter, _action, prompt, _reason in todo:
        out = f"{OUTPUT_DIR}/{n}_{letter}.png"
        # Re-check the disk: an earlier run of this cell may have produced it already.
        if os.path.exists(out) and os.path.getsize(out) > 0:
            log(f"{n}_{letter}: zaten var — atlandı")
            skipped += 1
            continue

        v = VARIANT_LETTERS.index(letter)
        seed = random.randint(0, 2**31 - 1) if SEED is None else SEED + v
        log(f"{n}_{letter}: seed={seed}  |  {prompt.strip().replace(chr(10), ' ')[:45]}…")
        t0 = time.time()
        try:
            path = generate_one(client, n, letter, prompt, seed)
        except ComfyExecutionError as e:
            print(e.text)
            print(e.traceback_text)
            if e.infra:
                raise RuntimeError(
                    f"Altyapı hatası ({e.text.splitlines()[0]}) — batch durduruldu, kalan görseller denenmedi"
                ) from None
            failed += 1
            consecutive += 1
            log(f"{n}_{letter}: başarısız — atlanıyor ({consecutive}/{MAX_CONSECUTIVE_FAILURES})", "ERR")
            if consecutive >= MAX_CONSECUTIVE_FAILURES:
                raise RuntimeError(f"Üst üste {consecutive} render başarısız — batch durduruldu") from None
            continue

        consecutive = 0
        done += 1
        log(f"{n}_{letter}: bitti ({time.time() - t0:.0f}s, {os.path.getsize(path) / 1024**2:.1f} MB) → {path}", "OK")

    log(f"Batch bitti ({(time.time() - t_batch) / 60:.0f} dk) — "
        f"üretildi: {done}, atlandı: {skipped}, başarısız: {failed}", "OK")

process_all(PLAN)
```

---

### Task 2: Doğrulama (grep — commit YOK)

**Files:** yok (salt okuma)

**Interfaces:**
- Consumes: Task 1'in `api.ipynb`'si.
- Produces: kullanıcıya test raporu. Commit kullanıcı doğrulaması SONRASI.

Grep desenleri **tırnaksız düz token** (`.ipynb` kod hücreleri escaped JSON — tırnaklı desen eşleşmez).

- [ ] **Step 1: Olması gerekenler** — `nova-3dcg/api.ipynb` içinde ≥1 eşleşme:
`PROMPT_NODE` · `NEGATIVE_NODE` · `SEED_NODE` · `wildcard_text` · `populated_text` · `set_text` · `save_output_image` · `VARIANTS` · `VARIANT_LETTERS` · `photoGenV2` · `NEGATIVE` · `nova3DCGXL_ilV90` · `USNR_STYLE_ILL_V1_lokr3-000024` · `check_binary` · `recurse-submodules` · `describe_comfy_error` · `build_plan` · `generate_one` · `process_all`

- [ ] **Step 2: Olmaması gerekenler** — `nova-3dcg/api.ipynb` içinde 0 eşleşme (case-insensitive):
`SmoothMix` · `lightx2v` · `wan2` · `VHS_VideoCombine` · `upload_image` · `LoadImage` · `233:240` · `287` · `210` · `sageattention` · `mp4` · `IMAGE_EXTS` · `find_image`

(`imageToVideoV2` bu listede DEĞİL: hücre 0'ın "beğendiğini `imageToVideoV2/input/0.png` diye kopyala" yönergesi o adı meşru olarak içerir — ilk taslak yasaklamıştı, uygulamada çelişki çıktı ve liste düzeltildi.)

- [ ] **Step 3: Değişmemesi gerekenler** — `api.ipynb`'de hâlâ mevcut: `check_safetensors` · `__Secure-civ-token` · `system_stats` · `COMFY_ROOT` (CONFIG gate assert'i dahil).

- [ ] **Step 4: Kullanıcıya raporla** — Colab test adımları (spec'in Doğrulama bölümü) + hatırlatma: repodaki `workflow_api.json`'un aynısı Drive'a `photoGenV2/workflow_api.json` olarak konmalı. Stage/commit yapılmaz.

---

## Self-review notu

- Spec kapsaması: CONFIG+plan (Step 4-5), çift-alan enjeksiyon (Step 13 `set_text`), seed formülü `SEED + v` (Step 13), tam-1-görsel kontrolü (`save_output_image`), UI-format reddi (`load_workflow`), resume (plan + döngü içi disk kontrolü), infra-stop/3-hata (arbuzai'den korunarak). Kapsam dışı bölümü plana girmedi — doğru.
- `233:240`/`287`/`210` yasak listesinde: arbuzai'nin video node id'leri foto notebook'unda kalmamalı.
- Tip tutarlılığı: `build_plan` satırı `(n, letter, action, prompt, reason)` — `process_all` `row[2] == "ÜRET"` ve 5'li unpack ile uyumlu; cell 3 ile cell 13 aynı imzayı kullanıyor.
