# WAN 2.2 T2V — Katmanlı prompt + aksiyon listesi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb` — stil/kamera/mekân/karakter/kalite bir kez tanımlansın, aksiyon listesi verilsin, notebook her aksiyon için bir video üretip üretilmiş olanları atlasın.

**Architecture:** Katmanlar Python'da string olarak birleşir (`STYLE. CAMERA. SCENE. CHARACTER. ACTION. QUALITY.`) ve bugünkü gibi `PromptGenerator` düğümüne basılır — grafiğe dokunulmaz. Yeni bir PROMPTS hücresi katmanları, aksiyon listesini, seed'i ve birleştiriciyi taşır; render hücresi tek üretimden döngüye döner ve Drive'daki `NN.mp4`'e bakarak resume eder.

> ⛔ **Durum: Task 1 geri alındı (2026-07-20).** Plan uygulandı ve A100'de koşuldu; **katmanlama başarısız oldu, çıktı kötü çıktı.** Task 1'in kurduğu katman sistemi (`STYLE`/`CAMERA`/`SCENE`/`CHARACTER`/`QUALITY` + `build_prompt`) tamamen kaldırıldı, yerine düz `PROMPTS` listesi geldi. **Task 2 (render döngüsü + resume) ve Task 3'ün doküman işi ayakta** — onlar katmanlamadan bağımsızdı.
>
> Yürürlükteki tasarım: [2026-07-20-t2v-prompt-list-design.md](../specs/2026-07-20-t2v-prompt-list-design.md). Aşağısı ne yapıldığının kaydıdır, uygulama rehberi değil — Task 1 ve Task 3'teki kod blokları artık notebook'ta olmayan bir yapıyı anlatıyor.

**Tech Stack:** Google Colab (A100), ComfyUI HTTP API, `requests`, Google Drive.

## Global Constraints

- **Branch: `feat/wan22-smooth-t2v-api`.** Yeni branch açma.
- **Commit'i pathspec ile at:** `git commit -- <yollar>` (veya `git commit <yollar> -F msg`). `git add` + çıplak `git commit` **index'in tamamını** alır ve aynı çalışma ağacındaki ikinci Claude oturumunun staged dosyalarını içeri sokar — bu iki kez oldu.
- **`--amend` KULLANMA.** Amend HEAD'i yeniden yazar; diğer oturum araya commit atmışsa onlarınkini ezer. Mesaj yanlışsa düzeltme commit'i at.
- **Çok satırlı commit mesajını dosyaya yaz, `git commit -F` ile ver.** PowerShell here-string içindeki tek bir `"` argüman ayrıştırmasını bozuyor ve git kelimeleri pathspec sanıyor.
- **Shell komutu çalıştırma.** İnceleme için Read/Grep, düzenleme için Edit/NotebookEdit; hücre sayısı doğrulaması Grep ile `"cell_type"` sayımıdır. Notebook'un JSON'ı ayrıca doğrulanmaz — NotebookEdit bozuk JSON'ı ayrıştıramaz, yani başarılı bir düzenleme zaten kanıttır. (PowerShell `ConvertFrom-Json` denendi ve kullanıcı tarafından reddedildi: kök `CLAUDE.md` tool ile yapılabileni komuta çevirmeyi yasaklıyor.)
- **Dil** (kök `CLAUDE.md`): markdown hücreleri + runtime çıktısı (`print`/`log`/`assert`/`RuntimeError`) **Türkçe**; kod yorumları + docstring'ler **İngilizce**.
- **`workflow_api.json` değiştirilmez.** Ne repodaki kopya ne Drive'daki. Bu iş grafiğe dokunmuyor.
- **Kurulum hücrelerine dokunulmaz.** Ortak yardımcılar, custom node'lar, modeller, ComfyUI başlatma (bugünkü 2–5. bölümler) Colab'da A100 ile doğrulandı; hiçbiri bu planın kapsamında değil.
- **Fail-loud:** hata mesajı servisin **ham** çıktısını taşır, sebep uydurulmaz.

---

### Task 1: PROMPTS hücresi + CONFIG'den `PROMPT`'un çıkması

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb` (cell-0 başlık, cell-1 CONFIG markdown, cell-2 CONFIG kod; cell-1'den sonra iki yeni hücre)

**Interfaces:**
- Produces: `STYLE`, `CAMERA`, `SCENE`, `CHARACTER`, `QUALITY`, `ACTIONS` (list[str]), `SEED` (int), `build_prompt(action: str) -> str`. Task 2 hepsini kullanır.
- Consumes: yok (CONFIG'den bağımsız; sadece hücre sırası olarak sonra gelir).

- [ ] **Step 1: cell-2 (CONFIG kod) — `PROMPT` ve onun assert'ini kaldır**

Şu üç parça silinecek:

```python
# === Prompt — değiştirip 6. hücreyi tekrar çalıştır ===
# Üç tırnak: video prompt'ları çok satırlı olur ve içlerinde " geçer; tek tırnak ikisinde de
# "unterminated string literal" verir.
PROMPT = """
"""
```

```python
assert PROMPT.strip(), "❌ PROMPT boş — yukarıya prompt'unu yaz"
```

```python
print(f"✓ Prompt: {PROMPT[:70]}{'…' if len(PROMPT) > 70 else ''}")
```

Hücrenin geri kalanı (Drive mount, `DRIVE_ROOT`, `COOKIE_VALUE`, timeout'lar, türetilmiş yollar, `os.makedirs`, cookie ve workflow assert'leri, GPU satırı) **aynen kalır**.

- [ ] **Step 2: cell-1 (CONFIG markdown) — tek dolduru­lacak yer artık burası değil**

```markdown
## 1) CONFIG

Google Drive **burada** mount edilir: auth istemi ilk saniyede çıksın, 33 GiB'lık model indirmesinin ortasında seni beklemesin.

Burası teknik ayar — bir kez kurulur, sonra dokunulmaz. Karakter, mekân, kamera ve aksiyon listesi **2) PROMPTS** hücresinde. Cookie'nin süresi dolmuşsa (~30 gün) `civitai.red`'den yenile.
```

- [ ] **Step 3: Yeni markdown hücresi — cell-1'den sonra (PROMPTS başlığı)**

```markdown
## 2) PROMPTS

Sürekli düzenlediğin yer burası. `STYLE` / `CAMERA` / `SCENE` / `CHARACTER` / `QUALITY` sabit durur, `ACTIONS`'a yeni satır eklersin.

Katmanlar Python'da birleşir, grafiğe dokunulmaz: WAN metni **UMT5** ile kodluyor — uzun bağlam alan ve düz cümlelerle eğitilmiş bir encoder. SDXL'de katmanları ayrı ayrı encode etmenin sebebi CLIP'in 77-token penceresiydi; burada o sorun yok, ayrı encode etmek modele tanımadığı bir girdi biçimi verirdi.

Birleşme sırası: `STYLE. CAMERA. SCENE. CHARACTER. ACTION. QUALITY.` — stil başta, çünkü çerçeveyi baştan kuruyor; kalite sonda. Bu bir konvansiyon, **doğrulanmadı**; değiştirmesi `build_prompt` içindeki tek bir demet satırı.

Her katman **betimleyici öbeklerle** yazılır, Danbooru tag'leriyle değil: `masterpiece, best quality, 8k` SDXL/CLIP konvansiyonu, UMT5'te çok daha az ağırlık taşıyor.

`STYLE` ve `QUALITY` **boş bırakılabilir** — boş katman tamamen düşer, metinde `. .` artığı oluşmaz. `STYLE = ""` bırakırsan SmoothMix'in kendi estetiği ne veriyorsa o çıkar.

> ⚠️ **Listeye sondan ekle.** Çıktı adı listedeki sıraya bağlı (`01.mp4`, `02.mp4`, …). Ortaya eleman eklersen ya da sırayı değiştirirsen altındaki her şey kayar: `05.mp4` artık başka bir aksiyona aittir ama dosya var diye atlanır. Yeniden sıralaman gerekirse etkilenen çıktıları Drive'dan sil.

Birleşmiş metin yine `PromptGenerator` düğümünden geçiyor, yani **wildcard sözdizimi çalışıyor**: aksiyon içinde `{ kneeling | sitting | squatting }` yazabilirsin. Seed sabit olduğu için seçim her koşuda aynı çıkar.

Hücre çalışınca ilk aksiyonla birleşmiş prompt'u basar — modele gidecek metni render beklemeden görürsün.
```

- [ ] **Step 4: Yeni kod hücresi — PROMPTS**

```python
# === Prompt layers — the cell you edit between runs ===
# Declared in join order: STYLE. CAMERA. SCENE. CHARACTER. ACTION. QUALITY.
# Joined here in Python, not in the graph. WAN encodes with UMT5 (long context, trained on prose),
# so the separate-encode + ConditioningConcat trick that pays for CLIP's 77-token window on SDXL
# would only hand this model an input shape it never saw in training. For the same reason every
# layer reads as descriptive phrases rather than Danbooru tags: "masterpiece, best quality, 8k"
# carries far less weight on UMT5 than it does on SDXL's CLIP.

# Nasıl görünüyor — sabit. Boş bırakırsan SmoothMix'in kendi estetiği ne veriyorsa o çıkar.
STYLE = "anime style, 2D cel shading, clean linework"

# Kamera — sabit
CAMERA = "medium shot, the camera slowly pushes in, shallow depth of field"

# Nerede — sabit
SCENE = "a sunlit bedroom with white wrinkled bedsheets and pink curtains, golden hour light streaming through a large window, warm cozy atmosphere"

# Kim — sabit
CHARACTER = "a young woman with long teal hair in twintails, green eyes, fair skin"

# Ne oluyor — SONA EKLE. Çıktı adı listedeki sıraya bağlı (01.mp4, 02.mp4, ...).
ACTIONS = [
    "she slowly turns toward the camera and smiles",
    "she sits on the edge of the bed and looks out the window",
]

# Kalite — sabit. Boş bırakılabilir.
QUALITY = "highly detailed, sharp focus, smooth natural motion"

# Tüm listeye uygulanır: aynı liste yarın aynı videoları verir.
SEED = 42


def build_prompt(action):
    """Layers -> one WAN prompt.

    Empty layers drop out entirely, so blanking STYLE or QUALITY does not leave a stray '. .'
    behind. Trailing punctuation and spaces are trimmed before joining, so a layer written with a
    final period and one written without it produce the same string.
    """
    parts = [p.strip().rstrip(" .,;") for p in (STYLE, CAMERA, SCENE, CHARACTER, action, QUALITY)]
    body = ". ".join(p for p in parts if p)
    return f"{body}." if body else ""


assert ACTIONS, "❌ ACTIONS boş — en az bir aksiyon yaz"

print(f"✓ {len(ACTIONS)} aksiyon  |  seed {SEED}")
print("\n--- 1. aksiyonla birleşmiş prompt ---")
print(build_prompt(ACTIONS[0]))
```

- [ ] **Step 5: cell-0 (başlık) — 7 bölüm ve yeni akış**

```markdown
# WAN 2.2 Smooth T2V — API (aksiyon listesi → video) — Colab

Stili, kamerayı, mekânı ve karakteri bir kez tanımla, aksiyon listesi ver, çalıştır — her aksiyon için bir video Drive'a düşer. ComfyUI arka planda **API** olarak çalışır; **UI açılmaz, tünel yok.**

> Grafiği elle kurcalamak, ayar denemek istiyorsan bu değil — **`manual.ipynb`**. O ComfyUI'yi tünelle açar.

**Input:** PROMPTS hücresindeki katmanlar + `workflow_api.json` (Drive) · **Output:** `MyDrive/TextToVideo/output/NN.mp4`

```
TextToVideo/                ← Drive'da senin oluşturacağın klasör
├── workflow_api.json   ← manual.ipynb'de Export (API) ile kaydettiğin graf
└── output/             ← 01.mp4, 02.mp4, … (otomatik oluşur)
```

Sıra:
1. **CONFIG** — Drive mount + teknik ayar
2. **PROMPTS** — stil / kamera / mekân / karakter / kalite + aksiyon listesi + seed
3. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
4. **ComfyUI + custom node'lar** (16)
5. **Modeller** — önce gated probe, sonra indir (~33.5 GiB)
6. **ComfyUI'yi başlat** (arka planda, API)
7. **Üret** — listeyi gez, eksikleri üret, Drive'a yaz

> **Yeni aksiyon için:** PROMPTS'taki `ACTIONS` listesine sondan ekle, **2. ve 7. hücreyi** çalıştır. Üretilmiş videolar atlanır, sadece yenisi üretilir.

> **LoRA yok, olması da gerekmiyor.** SmoothMix T2V v3'te lightx2v checkpoint'e merge edilmiş (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*); ayrıca yüklemek iki kez uygular ve çıktıyı bozar. Graf 6 step / cfg 1 ile LoRA'sız çalışır.
```

- [ ] **Step 6: Notebook'un hâlâ geçerli JSON olduğunu ve hücre sayısını doğrula**

Run:
```powershell
$nb = Get-Content 'd:\code\github\internal-tools\collab-toolbox\video_generator\wan22-smooth-t2v\api.ipynb' -Raw | ConvertFrom-Json; $nb.cells.Count
```
Expected: `15` (önceki 13 + PROMPTS'un markdown ve kod hücresi)

- [ ] **Step 7: Kalan `PROMPT` referansı olmadığını doğrula**

Grep tool ile `api.ipynb` içinde `\bPROMPT\b` ara.
Expected: yalnızca `PROMPT_NODE` eşleşmeleri (render hücresindeki node id sabiti). Çıplak `PROMPT` değişkeni kalmamalı.

- [ ] **Step 8: Commit**

```bash
git commit -- collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb -F <mesaj-dosyasi>
```
Mesaj konusu: `feat(wan22-smooth-t2v): layer the prompt into character, scene, camera and action`

---

### Task 2: Render hücresi — tek üretimden döngüye

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb` (son markdown hücresi + son kod hücresi)

**Interfaces:**
- Consumes: Task 1'den `ACTIONS`, `SEED`, `build_prompt(action) -> str`; CONFIG'den `OUTPUT_DIR`, `WORKFLOW_PATH`, `COMFYUI_URL`, `COMFY_OUTPUT_DIR`, `TIMEOUT_PER_RENDER`, `POLL_INTERVAL`; yardımcılardan `log(msg, level="INFO")`, `describe_comfy_error(status) -> (text, tb, is_infra)`.
- Produces: `render(prompt: str, seed: int, save_path: str) -> float` (geçen saniye). Döngü modül düzeyinde çalışır, dışarıya sembol üretmez.

**Değişmeden kalanlar:** `ComfyExecutionError`, `PROMPT_NODE`, `SEED_NODE`, `load_workflow`, `set_prompt`, `set_seed`, `ComfyClient` sınıfının tamamı. Yalnızca `generate` fonksiyonu `render`'a dönüşür ve altına döngü gelir.

- [ ] **Step 1: Son markdown hücresini güncelle**

```markdown
## 7) Üret

**Tekrar çalıştırılacak hücre bu.** Liste gezilir; `output/NN.mp4` zaten varsa o aksiyon atlanır, yoksa üretilip Drive'a yazılır. Oturum koparsa hücreyi tekrar çalıştırmak sadece eksikleri tamamlar.

Seed tüm liste için sabit (`SEED`, PROMPTS hücresinde) — aynı listeyi yarın çalıştırırsan aynı videolar çıkar.

Hata politikası:
- **Model yükleme hatası** → koşu durur. Listenin tamamı aynı hataya çarpacak, 12 kere daha denemenin faydası yok.
- **Üretim hatası** → o aksiyon başarısız işaretlenir, sıradakine geçilir. Sonda index'leri listelenir.
- **Timeout** → koşu durur. Takılmış ComfyUI kendini toparlamaz.

Başarısız aksiyon için dosya yazılmaz; hücreyi tekrar çalıştırınca yeniden denenir.
```

- [ ] **Step 2: Son kod hücresinin import satırını daralt**

```python
import json, os, time, uuid, requests
```

`copy` ve `random` çıkıyor: `load_workflow` dosyayı her çağrıda yeniden okuduğu için kopya gerekmiyor, seed de artık PROMPTS'tan sabit geliyor.

- [ ] **Step 3: `generate`'i `render` ile değiştir**

Mevcut `def generate(prompt, seed=None): ...` ve altındaki `video_path = generate(PROMPT)` satırı silinip yerine bu gelir:

```python
# === One render, end to end ===
def render(prompt, seed, save_path):
    """Queue one prompt, wait for it, write the video to save_path. Returns elapsed seconds.

    Raises ComfyExecutionError (the prompt failed inside ComfyUI) or TimeoutError; the loop below
    decides which of those ends the whole run.
    """
    workflow = load_workflow(WORKFLOW_PATH)
    set_prompt(workflow, prompt)
    set_seed(workflow, seed)

    client = ComfyClient(COMFYUI_URL)
    t0 = time.time()
    prompt_id = client.submit(workflow)
    history = client.wait(prompt_id, TIMEOUT_PER_RENDER)
    produced_name = client.save_output_video(history, save_path)

    # ComfyUI's own copy is dropped as well, so a long list does not fill the Colab disk.
    local_out = os.path.join(COMFY_OUTPUT_DIR, produced_name)
    if os.path.exists(local_out):
        os.remove(local_out)
    return time.time() - t0
```

- [ ] **Step 4: Döngüyü ekle (hücrenin sonu)**

```python
# === Walk the action list; anything already on Drive is skipped ===
total = len(ACTIONS)
done, skipped, failed = 0, 0, []

log(f"{total} aksiyon  |  seed {SEED}  |  çıktı: {OUTPUT_DIR}")

for i, action in enumerate(ACTIONS, start=1):
    save_path = os.path.join(OUTPUT_DIR, f"{i:02d}.mp4")

    if os.path.exists(save_path):
        print(f"[{i}/{total}] ⏭️  {i:02d}.mp4 zaten var — atlanıyor")
        skipped += 1
        continue

    print(f"[{i}/{total}] Üretiliyor: {action[:70]}{'…' if len(action) > 70 else ''}")
    try:
        elapsed = render(build_prompt(action), SEED, save_path)
    except ComfyExecutionError as e:
        print(e.text)
        print(e.traceback_text)
        if e.infra:
            # A model loader failed: every remaining action would hit the identical error.
            raise RuntimeError(
                f"❌ Altyapı hatası, koşu durduruldu ({i}/{total}) — yukarıdaki ComfyUI hatasına bak"
            ) from None
        failed.append(i)
        print(f"        ❌ {i:02d} başarısız — sıradaki aksiyona geçiliyor\n")
        continue
    except TimeoutError as e:
        # A stuck ComfyUI does not recover; each remaining action would burn the full timeout.
        raise RuntimeError(f"❌ {e} — koşu durduruldu ({i}/{total})") from None

    size_mb = os.path.getsize(save_path) / 1024**2
    print(f"        ✓ {i:02d}.mp4  ({int(elapsed // 60)} dk {int(elapsed % 60)} sn, {size_mb:.1f} MB)\n")
    done += 1

log(f"Bitti — yeni: {done}  •  atlanan: {skipped}  •  başarısız: {len(failed)}", "OK")
if failed:
    idx = ", ".join(f"{i:02d}" for i in failed)
    log(f"Başarısız: {idx} — hücreyi tekrar çalıştırınca yeniden denenir", "WARN")
```

- [ ] **Step 5: Notebook'un geçerli JSON olduğunu doğrula**

Run:
```powershell
$nb = Get-Content 'd:\code\github\internal-tools\collab-toolbox\video_generator\wan22-smooth-t2v\api.ipynb' -Raw | ConvertFrom-Json; $nb.cells.Count
```
Expected: `15`

- [ ] **Step 6: `generate` referansı kalmadığını doğrula**

Grep tool ile `api.ipynb` içinde `generate` ara.
Expected: 0 eşleşme. (`instructions.md`'deki `generate(PROMPT, seed=...)` cümlesi Task 3'te düzeltilecek.)

- [ ] **Step 7: Commit**

```bash
git commit -- collab-toolbox/video_generator/wan22-smooth-t2v/api.ipynb -F <mesaj-dosyasi>
```
Mesaj konusu: `feat(wan22-smooth-t2v): render the whole action list, skipping what Drive already has`

---

### Task 3: Dokümanlar — instructions.md ve CLAUDE.md

**Files:**
- Modify: `collab-toolbox/video_generator/wan22-smooth-t2v/instructions.md:66-91` (API modu bölümü)
- Modify: `CLAUDE.md` (notebook tablosundaki `api.ipynb` satırı)

**Interfaces:**
- Consumes: Task 1 ve 2'nin ürettiği davranış (PROMPTS hücresi, `NN.mp4`, sabit seed, resume).
- Produces: yok.

- [ ] **Step 1: `instructions.md` — API modu bölümünü değiştir**

66–91. satırlar arası şununla değişir:

```markdown
## API modu — UI'a girmeden üretmek

[api.ipynb](api.ipynb) aynı grafiği ComfyUI'nin HTTP API'si üzerinden çalıştırır: stili, kamerayı, mekânı ve karakteri bir kez tanımla, aksiyon listesi ver, çalıştır. UI açılmaz, tünel yok.

**Drive kurulumu (bir kez):**

```
MyDrive/TextToVideo/
├── workflow_api.json   ← bu klasördeki workflow_api.json'un kopyası
└── output/             ← otomatik oluşur
```

**Kullanım:**

1. Runtime → **A100 GPU**
2. `api.ipynb` → **PROMPTS** hücresinde `STYLE` / `CAMERA` / `SCENE` / `CHARACTER` / `QUALITY` ve `ACTIONS` listesini doldur → **Run all** (~33.5 GiB iner)
3. Her aksiyon için bir video: `output/01.mp4`, `02.mp4`, …
4. **Yeni aksiyon:** `ACTIONS`'a **sondan** ekle, **2. ve 7. hücreyi** çalıştır — üretilmiş videolar atlanır, sadece yenisi üretilir

**Katmanlar Python'da birleşir, grafiğe dokunulmaz.** Sıra: `STYLE. CAMERA. SCENE. CHARACTER. ACTION. QUALITY.` WAN metni UMT5 ile kodluyor (uzun bağlam, düz cümle); SDXL'de katmanları ayrı encode etmenin sebebi olan CLIP 77-token sınırı burada yok. Aynı sebeple katmanlar betimleyici öbeklerle yazılır, `masterpiece, best quality, 8k` gibi Danbooru tag'leriyle değil.

`STYLE` ve `QUALITY` boş bırakılabilir — boş katman düşer, metinde `. .` artığı oluşmaz.

> ⚠️ **Listeye sondan ekle.** Çıktı adı listedeki sıraya bağlı. Ortaya eleman eklemek veya sırayı değiştirmek altındaki eşleşmeleri kaydırır: `05.mp4` başka bir aksiyona ait olur ama dosya var diye atlanır. Yeniden sıralarsan etkilenen çıktıları Drive'dan sil.

**Grafiği değiştirmek:** `manual.ipynb`'yi çalıştır, UI'da düzenle, **Workflow → Export (API)** → Drive'daki `workflow_api.json`'un üzerine yaz. Notebook'a dokunma.

Notebook grafiğe yalnızca birleşmiş prompt'u ve seed'i basar (`PromptGenerator` **230:229**, `Seed` **82**); çözünürlük, süre, step/cfg, RIFE ayarları grafikte ne yazıyorsa odur.

**Seed:** `SEED` tüm listeye uygulanır (PROMPTS hücresinde). Aynı listeyi tekrar çalıştırmak aynı videoları verir.

**Neden iki notebook:** UI'lı olan ayarı bulmak, API'li olan üretmek için. İkisi aynı grafiği kullanır; API'li olanın gördüğü graf Drive'daki export'tur.
```

- [ ] **Step 2: `CLAUDE.md` — `api.ipynb` tablo satırını değiştir**

Mevcut satırdaki açıklama (`Text-to-video (WAN 2.2 SmoothMix) — prompt in CONFIG, video out to Drive, one per run`) şununla değişir:

```
Text-to-video (WAN 2.2 SmoothMix) — layered prompt (style/camera/scene/character/quality) + action list, one video per action, resumable
```

Satırın geri kalanı (dosya linki ve donanım sütunu `A100 (Colab Pro)`) aynı kalır.

- [ ] **Step 3: Eski akışı anlatan kalıntı kalmadığını doğrula**

Grep tool ile `collab-toolbox/` ve `CLAUDE.md` içinde şu üç ifadeyi ara:
- `CONFIG'de` `PROMPT`
- `zaman damgalı` / `YYYYAAGG`
- `generate(PROMPT`

Expected: 0 eşleşme. Eşleşme çıkarsa o metin eski akışı anlatıyordur (tek prompt / zaman damgalı çıktı / `generate` çağrısı) ve bu task'ın yeni akışına göre düzeltilir — dosya `manual.ipynb` veya `indirilecekler.md` bile olsa.

- [ ] **Step 4: Commit**

```bash
git commit -- collab-toolbox/video_generator/wan22-smooth-t2v/instructions.md CLAUDE.md -F <mesaj-dosyasi>
```
Mesaj konusu: `docs(wan22-smooth-t2v): document the layered prompt and the action list`

---

### Task 4: Colab doğrulaması (kullanıcıda)

**Files:** yok — çalıştırma adımı.

**Interfaces:**
- Consumes: Task 1–3'ün tamamı.

Notebook birim testle doğrulanmıyor; doğrulama Colab koşusu. Kullanıcı A100 ile şunları sırayla yapar:

- [ ] **Step 1: İki aksiyonluk listeyle Run all**

Beklenen: `01.mp4` ve `02.mp4` Drive'a düşer; ikisinde de aynı karakter, aynı mekân ve aynı görsel stil görünür. PROMPTS hücresi ilk aksiyonla birleşmiş prompt'u basmış olur ve o metin `STYLE` ile başlar.

- [ ] **Step 2: 7. hücreyi tekrar çalıştır**

Beklenen:
```
[1/2] ⏭️  01.mp4 zaten var — atlanıyor
[2/2] ⏭️  02.mp4 zaten var — atlanıyor
✅ Bitti — yeni: 0  •  atlanan: 2  •  başarısız: 0
```

- [ ] **Step 3: Listeye üçüncü aksiyonu sondan ekle, 2. ve 7. hücreyi çalıştır**

Beklenen: sadece `03.mp4` üretilir, ilk ikisi atlanır.

- [ ] **Step 4: `STYLE = ""` ile 2. hücreyi çalıştır**

Beklenen: metin doğrudan `CAMERA` ile başlıyor, başta `. ` artığı yok. Aynısını `QUALITY = ""` ile de dene: metin `…ACTION.` ile bitmeli, sonda `. .` olmamalı. (Video üretmeye gerek yok; PROMPTS hücresinin çıktısı yeterli.)

- [ ] **Step 5: Sonucu bildir**

Geçen adımları ve varsa hata çıktısını kullanıcıya ilet. Bir adım kalırsa ilgili task'a dönülür.
