# Queen Tools — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Queen Editor'ün Export dosyasını hareket prompt'una çevirip videoya dönüştüren iki Colab notebook'u eklemek.

**Architecture:** `collab-toolbox/queen-tools/` altında iki bağımsız notebook. Birincisi (CPU) yüklenen export JSON'unun prompt'larını kare kare xAI'ye çevirtir ve ilerlemeyi Drive'a yazar; ikincisi (A100) çıkan dosyayı okuyup ComfyUI ile videoları üretir. İkinci notebook `wan22-arbuzai/api_from_photos.ipynb`'ın kopyasıdır — motor, model indirme ve render döngüsü aynen taşınır, yalnız girdi tarama ve çıktı yolu değişir.

**Tech Stack:** Jupyter/Colab notebook (nbformat), Python 3, `requests`, `google.colab` (`drive`, `files`, `userdata`), ComfyUI HTTP API, WAN 2.2 SmoothMix I2V grafı.

**Tasarım dokümanı:** [2026-08-09-queen-tools-design.md](../specs/2026-08-09-queen-tools-design.md)

## Global Constraints

- **Dil:** kod yorumları, docstring'ler ve commit mesajları **İngilizce**; markdown hücreleri, `print`, `assert` ve `RuntimeError` metinleri **Türkçe** (CLAUDE.md — Notebook Comment Conventions).
- **Yorum ne yapıldığını değil neden yapıldığını anlatır.** `# OLD:` / `# NEW:` izleri ve geçmiş davranış iddiaları yasak.
- **Hatalar yüksek sesle.** `RuntimeError`; mesajda **servisin/komutun kendi çıktısı** basılır, sebep asla uydurulmaz (NOTEBOOK-STANDARD §2).
- **CONFIG tek hücrede ve Drive mount ilk sırada** (NOTEBOOK-STANDARD §1).
- **Resume:** çıktısı olan iş atlanır, yarım kalan koşu kaldığı yerden devam eder (NOTEBOOK-STANDARD §5).
- **Her iki sır da Colab Secrets'tan okunur:** `XAI_API_KEY` (çevirici) ve `CIVITAI_COOKIE` (video). Hiçbiri notebook kaynağına yazılmaz. Bu, NOTEBOOK-STANDARD §4'ün "cookie CONFIG'de durur" kuralından bilinçli bir sapma — standarda da not düşüldü, diğer notebook'lar değişmedi.
- **Sabit değerler:** `XAI_MODEL = "grok-4.3"` · `XAI_URL = "https://api.x.ai/v1/chat/completions"` · `VARIANTS = 1` · Drive kökü `/content/drive/MyDrive/queen-tools`.
- **Node id'leri** (graftan, değiştirilmez): LoadImage `"287"` · PromptGenerator `"233:240"` · Seed `"210"`.
- **Test yok.** `collab-toolbox/` altında test altyapısı yok ve kullanıcı ayrı test istemedi; doğrulama tek bir Colab turudur (son bölüm). Her görevin "doğrula" adımı, notebook'un geçerli nbformat olduğunu Read ile teyit etmektir.

## Dosya yapısı

| Dosya | Sorumluluğu |
|---|---|
| `collab-toolbox/queen-tools/prompt_converter.ipynb` | **Yeni.** Export JSON → hareket prompt'lu `video.json`. CPU, Drive'a yazar, xAI'ye konuşur. ComfyUI/GPU/model bilmez. |
| `collab-toolbox/queen-tools/photo_to_video.ipynb` | **Yeni.** `video.json` → mp4'ler. A100, ComfyUI'yi kurar ve sürer. xAI bilmez. |
| `CLAUDE.md` | **Değişir.** Notebook tablosuna iki satır. |

İki notebook birbirini import etmez, ortak dosya paylaşmaz; aralarındaki tek bağ Drive'daki `video.json`'ın biçimidir.

---

### Task 1: `prompt_converter.ipynb`

**Files:**
- Create: `collab-toolbox/queen-tools/prompt_converter.ipynb`

**Interfaces:**
- Consumes: Queen Editor'ün export dosyası — `{"folder": str, "photos": [{"file": str, "prompt": str}]}`
- Produces: `/content/drive/MyDrive/queen-tools/<proje>/video.json` — aynı şekil, her çevrilmiş satırda ek `"photo_prompt": str` alanı. Task 2 bu dosyayı okur.

Notebook 11 hücre: 6 markdown + 5 kod. Hücreleri sırayla ekle (`NotebookEdit`), her adım bir hücre.

- [ ] **Step 1: Boş notebook'u oluştur**

`collab-toolbox/queen-tools/prompt_converter.ipynb` dosyasını nbformat 4 iskeletiyle yaz:

```json
{
 "cells": [],
 "metadata": {
  "colab": { "provenance": [] },
  "kernelspec": { "display_name": "Python 3", "name": "python3" },
  "language_info": { "name": "python" }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}
```

- [ ] **Step 2: Başlık hücresi (markdown)**

```markdown
# Queen Editor Export → Hareket Prompt'u (Grok)

Queen Editor'ün **Export** dosyasındaki foto prompt'larını video grafının istediği **hareket
prompt'una** çevirir. Türkçe → İngilizce çevirisi de aynı çağrıda olur. GPU gerekmez.

```
Queen Editor ──Export──> dugun-export.json   (bilgisayarına iner)
                              │  bu notebook'a yükle
                     [ bu notebook ]  ── her çeviriden sonra Drive'a yazar
                              │  indir butonu
                        video.json   →   photo_to_video.ipynb
```

**Drive'da nereye yazar:** `MyDrive/queen-tools/<proje>/video.json` — proje adı export'un içindeki
`folder` yolundan gelir, sen bir şey yazmazsın.

**Asıl kopya Drive'dakidir.** İndirilen dosya, video notebook'una vermek için alınmış bir kopyadır.
Elle düzelttiğin bir prompt'un kalıcı olmasını istiyorsan düzeltmeyi Drive'daki dosyada yap.

> **Yarıda kalırsa aynı export'u tekrar yükle.** `photo_prompt` alanı olan kareler çevrilmiştir,
> atlanır; kalanlar üretilir. Colab ölse de kayıp yok, ilerleme Drive'da.

> **Tek kareyi yeniden çevirtmek** için Drive'daki dosyada o satırın `photo_prompt` alanını sil.

**Gerekenler:** Colab **Secrets**'ta `XAI_API_KEY` (notebook erişimi açık).
```

- [ ] **Step 3: CONFIG açıklaması (markdown)**

```markdown
## 1) CONFIG

Google Drive **burada** mount edilir: auth istemi ilk saniyede çıksın.

`INSTRUCTION` Grok'a verilen çeviri talimatı. Dolu geliyor: Wan I2V için kamerayı sabit tutan,
sahneyi yeniden tarif etmeyip **hareketi** yazan bir talimat. Sonuçları gördükçe düzelteceğin asıl
yer burası — talimat değişince yeniden çevirtmek için Drive'daki `video.json`'u sil.

**Boş bırakılırsa hücre durur**: boş talimatla istek atmak para harcayıp anlamsız cevap almaktır.

`XAI_API_KEY` Colab Secrets'tan okunur ve hiçbir çıktıya basılmaz.
```

- [ ] **Step 4: CONFIG hücresi (kod)**

```python
# === Google Drive — en başta mount edilir ===
# The auth prompt has to appear in the first second, not in the middle of a run.
from google.colab import drive, userdata
drive.mount('/content/drive')

# === Çeviri talimatı ===
# Sent as the system message; the photo prompt itself is the user message. It asks for one motion
# prompt as plain text because this notebook sends one request per frame -- a request that carried
# the whole list would be capped by the model's output limit, and a list-shaped answer would add a
# format to parse for no gain.
INSTRUCTION = """
You are an expert prompt engineer specializing in image-to-video generation with the Wan model.
I will give you one SDXL prompt that was used to generate a still image. Convert it into an
optimized Wan image-to-video (I2V) positive prompt.

Follow these rules:

Don't re-describe the static scene in detail — Wan already receives the actual image as input. The
image defines the appearance; your job is to define motion.
Keep the camera static — no camera movement, no zoom, no pan.
Focus primarily on the action in the image — bring the subject's main activity to life as natural,
continuous movement. Build the motion around what the subject is actively doing.
Add subtle secondary motion to support the main action (hair, clothing, breathing, environmental
details like wind or water).
Keep it natural and physically plausible — realistic motion looks better than exaggerated movement
that breaks the image.
Specify pacing and mood.

Output only the motion prompt itself, as one concise paragraph of plain text. No list, no
surrounding quotes, no numbering, no explanations, no markdown code fences, no extra text.
"""

# === xAI ===
# grok-3 retired on 2026-08-15 and its requests were already being routed here, so this is the
# same behaviour under its real name.
XAI_MODEL = "grok-4.3"
XAI_URL   = "https://api.x.ai/v1/chat/completions"
XAI_TIMEOUT = 120                       # seconds per request

# === Drive ===
QUEEN_TOOLS_ROOT = "/content/drive/MyDrive/queen-tools"

import os
os.makedirs(QUEEN_TOOLS_ROOT, exist_ok=True)

# Colab Secrets: the key never appears in the notebook source or in any output.
XAI_API_KEY = userdata.get('XAI_API_KEY')

assert INSTRUCTION.strip(), "❌ INSTRUCTION boş — çeviri talimatını yaz (boş talimat = boşa harcanan istek)"
assert XAI_API_KEY, "❌ XAI_API_KEY okunamadı — Colab Secrets'a ekle ve 'Notebook access' aç"

print(f"✓ Model: {XAI_MODEL}")
print(f"✓ Drive kökü: {QUEEN_TOOLS_ROOT}")
print(f"✓ Talimat: {len(INSTRUCTION.strip())} karakter")
print(f"✓ Anahtar: Secrets'tan okundu ({len(XAI_API_KEY)} karakter)")
```

- [ ] **Step 5: Yükleme açıklaması (markdown)**

```markdown
## 2) Export dosyasını yükle

Queen Editor'de **Export**'a basınca inen dosyayı buraya yükle. **İş emri yüklediğin dosyadır**:
hangi projenin hangi kareleri isteniyor onu bu dosya söyler, Drive'daki dosya yalnız neyin bitmiş
olduğunu söyler.

Dosya elle de düzenlenebildiği için biçimi burada kontrol edilir; eksik alan varsa hücre neyin
eksik olduğunu yazıp durur.
```

- [ ] **Step 6: Yükleme hücresi (kod)**

```python
# === Export dosyasını yükle + biçimini doğrula ===
from google.colab import files
import json, os

uploaded = files.upload()
if len(uploaded) != 1:
    raise RuntimeError(f"❌ Tek dosya yükle — {len(uploaded)} dosya geldi: {list(uploaded)}")

EXPORT_NAME = next(iter(uploaded))
try:
    EXPORT = json.loads(uploaded[EXPORT_NAME].decode("utf-8"))
except (UnicodeDecodeError, json.JSONDecodeError) as e:
    raise RuntimeError(f"❌ {EXPORT_NAME} okunamadı: {type(e).__name__}: {e}") from None

def validate_export(data):
    """Fail-loud on anything that is not a Queen Editor export. The file can be hand-edited and
    can come back from a chat window, so its shape is checked rather than trusted."""
    if not isinstance(data, dict):
        raise RuntimeError(f"❌ JSON bir nesne değil: {type(data).__name__}")
    for key in ("folder", "photos"):
        if key not in data:
            raise RuntimeError(f"❌ '{key}' alanı yok — dosyadaki anahtarlar: {sorted(data)}")
    if not isinstance(data["photos"], list):
        raise RuntimeError(f"❌ 'photos' liste değil: {type(data['photos']).__name__}")
    for i, photo in enumerate(data["photos"]):
        if not isinstance(photo, dict):
            raise RuntimeError(f"❌ photos[{i}] nesne değil: {type(photo).__name__}")
        missing = [k for k in ("file", "prompt") if k not in photo]
        if missing:
            raise RuntimeError(f"❌ photos[{i}] eksik alan: {missing} — var olanlar: {sorted(photo)}")

validate_export(EXPORT)

# The project name comes from the export's own folder path, so it is never typed by hand and can
# never point at a different project than the photos do.
PROJECT     = os.path.basename(EXPORT["folder"].rstrip("/"))
PROJECT_DIR = f"{QUEEN_TOOLS_ROOT}/{PROJECT}"
VIDEO_JSON  = f"{PROJECT_DIR}/video.json"
os.makedirs(PROJECT_DIR, exist_ok=True)

print(f"✓ {EXPORT_NAME}: {len(EXPORT['photos'])} kare")
print(f"✓ Proje: {PROJECT}")
print(f"✓ Fotoğrafların klasörü: {EXPORT['folder']}")
print(f"✓ Yazılacak dosya: {VIDEO_JSON}")
```

- [ ] **Step 7: Plan açıklaması (markdown)**

```markdown
## 3) Birleştir + plan

Drive'da önceki koşudan bir dosya varsa açılır, ama **liste yüklediğin export'tan gelir**: export'a
yeni eklenen kareler listeye girer, export'tan silinenler düşer, daha önce çevrilmiş olanlar
(elle düzelttiklerin dahil) aynen korunur.

Aşağıdaki tablo hangi karenin çevrileceğini, hangisinin neden atlanacağını **tek bir istek
atılmadan** gösterir.
```

- [ ] **Step 8: Plan hücresi (kod)**

```python
# === Birleştir + plan ===
# The plan is printed before a single request is paid for: a stale file or an already-complete
# project shows up here, not on the invoice.
import json, os

def load_done(path):
    """{file: row} from a previous run. A row counts as done only when it carries photo_prompt --
    that field is written in the same step as the translation, so it cannot be true early."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        previous = json.load(f)
    return {p["file"]: p for p in previous.get("photos", []) if p.get("photo_prompt")}

def merge(export, done):
    """The export's photo list, in its own order, carrying over translations we already have.
    A photo the export no longer lists is dropped: the export is what exists."""
    rows = []
    for photo in export["photos"]:
        carried = done.get(photo["file"])
        rows.append(dict(carried) if carried else {"file": photo["file"], "prompt": photo["prompt"]})
    return rows

def action_of(row):
    """(action, reason) for one row -- one place decides, so the table and the loop agree."""
    if row.get("photo_prompt"):
        return "ATLA", "zaten çevrildi"
    if not row["prompt"].strip():
        return "ATLA", "prompt boş"
    return "ÇEVİR", ""

DONE = load_done(VIDEO_JSON)
PLAN = merge(EXPORT, DONE)

print(f"\n{'DOSYA':<14}  {'KARAR':<6}  AÇIKLAMA")
print("-" * 74)
for row in PLAN:
    action, reason = action_of(row)
    detail = reason if reason else row["prompt"].strip().replace("\n", " ")[:44]
    print(f"{row['file']:<14}  {action:<6}  {detail}")

_todo = sum(1 for row in PLAN if action_of(row)[0] == "ÇEVİR")
print("-" * 74)
print(f"Çevrilecek: {_todo}  |  Atlanacak: {len(PLAN) - _todo}")
if DONE:
    print(f"{len(DONE)} kare önceki koşudan geliyor: {VIDEO_JSON}")
```

> Burada `_todo == 0` hata **değildir**: her şeyin zaten çevrilmiş olması geçerli bir durum, o
> koşuda tek istek atılmaz ve dosya indirilir.

- [ ] **Step 9: Çeviri açıklaması (markdown)**

```markdown
## 4) Çevir

Kare başına bir istek gider, cevap düz metin olarak alınır. **Her başarılı çeviriden sonra dosya
Drive'a yazılır** — runtime ölse bile bir sonraki koşu kaldığı yerden devam eder.

Bir istek patlarsa hücre durur ve o ana kadar çevrilenler Drive'da kalır; notebook'u tekrar
çalıştırmak kaldığı yerden devam ettirir. Yeniden deneme yoktur, çünkü tekrar çalıştırmak zaten
odur.

Sonunda eski/yeni prompt tablosu basılır — gözle geçir.
```

- [ ] **Step 10: Çeviri hücresi (kod)**

```python
# === Çevir ===
import json, os, time, requests

def save(path, folder, rows):
    """Rewrite the whole file. It is small and has one writer, and what has to survive is the
    run's progress -- not the number of writes."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"folder": folder, "photos": rows}, f, ensure_ascii=False, indent=2)

def to_motion_prompt(photo_prompt):
    """One photo prompt -> one motion prompt. The answer is plain text: at one prompt per call,
    asking for JSON would add a shape to negotiate for no gain."""
    response = requests.post(
        XAI_URL,
        headers={"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"},
        json={"model": XAI_MODEL,
              "messages": [{"role": "system", "content": INSTRUCTION},
                           {"role": "user",   "content": photo_prompt}]},
        timeout=XAI_TIMEOUT,
    )
    if response.status_code >= 400:
        # The service's own answer, verbatim -- a cause is never invented.
        raise RuntimeError(f"❌ xAI HTTP {response.status_code}\n{response.text}")
    try:
        text = response.json()["choices"][0]["message"]["content"].strip()
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"❌ xAI cevabı beklenen biçimde değil ({type(e).__name__})\n"
                           f"{response.text}") from None
    if not text:
        raise RuntimeError(f"❌ xAI boş cevap döndü:\n{response.text}")
    return text

translated = 0
t_start = time.time()

for row in PLAN:
    if action_of(row)[0] != "ÇEVİR":
        continue
    print(f"  {row['file']}: çevriliyor…")
    try:
        motion = to_motion_prompt(row["prompt"])
    except RuntimeError as e:
        print(e)
        raise RuntimeError(
            f"❌ {row['file']} çevrilemedi — {translated} kare Drive'a yazıldı. "
            f"Aynı export'u tekrar yükle, kaldığı yerden devam eder."
        ) from None
    # photo_prompt is written in the same step as the translation: that is what makes it a
    # trustworthy "already done" marker for the next run.
    row["photo_prompt"] = row["prompt"]
    row["prompt"] = motion
    save(VIDEO_JSON, EXPORT["folder"], PLAN)
    translated += 1

save(VIDEO_JSON, EXPORT["folder"], PLAN)
print(f"\n✅ {translated} kare çevrildi ({time.time() - t_start:.0f} sn) → {VIDEO_JSON}")

print(f"\n{'DOSYA':<14}  {'ESKİ (foto)':<36}  YENİ (hareket)")
print("-" * 100)
for row in PLAN:
    old = (row.get("photo_prompt") or row["prompt"]).strip().replace("\n", " ")[:34]
    new = row["prompt"].strip().replace("\n", " ")[:44] if row.get("photo_prompt") else "—"
    print(f"{row['file']:<14}  {old:<36}  {new}")
```

- [ ] **Step 11: İndirme açıklaması + hücresi**

Markdown:

```markdown
## 5) İndir

Dosya Drive'da zaten duruyor; bu hücre onu bilgisayarına indirir ki `photo_to_video.ipynb`'a
yükleyebilesin.
```

Kod:

```python
# === İndir ===
# The Drive copy stays the master (hand edits belong there); this is the copy that gets handed to
# the video notebook.
from google.colab import files
files.download(VIDEO_JSON)
```

- [ ] **Step 12: Notebook'u Read ile doğrula**

`collab-toolbox/queen-tools/prompt_converter.ipynb` dosyasını Read ile aç. Beklenen: 11 hücre sırasıyla render oluyor (markdown/kod dönüşümlü). Hata verirse JSON bozuk — düzelt.

- [ ] **Step 13: Commit**

```bash
git add collab-toolbox/queen-tools/prompt_converter.ipynb
git commit -m "feat(queen-tools): turn export prompts into motion prompts"
```

---

### Task 2: `photo_to_video.ipynb`

**Files:**
- Create: `collab-toolbox/queen-tools/photo_to_video.ipynb` (kaynak: `collab-toolbox/video_generator/wan22-arbuzai/api_from_photos.ipynb` kopyası)

**Interfaces:**
- Consumes: Task 1'in ürettiği `video.json` — `{"folder": str, "photos": [{"file": str, "prompt": str, "photo_prompt": str}]}`. `photo_prompt` **okunmaz**; notebook yalnız `prompt` alanını kullanır, bu yüzden ham export dosyası da aynı şekilde çalışır.
- Produces: `/content/drive/MyDrive/queen-tools/<proje>/001.mp4` — ad, karenin `photos` dizisindeki 1-tabanlı konumu (üç hane); `VARIANTS > 1` ise `001_<v>.mp4`.

- [ ] **Step 1: Kaynağı kopyala**

Kopyalama için tek komut gerekiyor: 14 hücrelik notebook'u Read + Write ile yeniden yazmak, birebir kalması gereken 10 hücrede sessiz sapma riski demek; `cp` içeriğe hiç dokunmadan taşır.

```bash
mkdir -p collab-toolbox/queen-tools
cp collab-toolbox/video_generator/wan22-arbuzai/api_from_photos.ipynb collab-toolbox/queen-tools/photo_to_video.ipynb
```

- [ ] **Step 2: Başlık hücresini (cell 0, markdown) değiştir**

```markdown
# Queen Editor → Video (WAN 2.2 I2V) — Colab

`prompt_converter.ipynb`'ın ürettiği **`video.json`**'u alır, Queen Editor'ün proje klasöründeki
fotoğrafları o dosyadaki hareket prompt'larıyla videoya çevirir. ComfyUI arka planda **API** olarak
çalışır; **UI açılmaz, tünel yok.**

```
video.json  ──yükle──>  [ bu notebook ]  ──>  MyDrive/queen-tools/<proje>/001.mp4 …
                              │
                    fotoğrafları Queen Editor'ün
                    klasöründen OKUR (oraya yazmaz)
```

**Fotoğraflar kopyalanmaz.** Yol JSON'un içindeki `folder` alanından gelir; notebook o klasörü
yalnız okur, içine hiçbir şey yazmaz.

**Video adı sıradır, fotoğrafın adı değil.** `001.mp4` dosyadaki **birinci** karedir; klasörü
alfabetik sıralayınca videonun sırası çıkar. Hangi fotoğraftan ve hangi prompt'tan geldiğini
`video.json`'daki aynı sıradaki satır söyler (`001.mp4` → `photos[0]`). Atlanan kare de numarasını
harcar, yani boşluk "orada bir şey atlandı" demektir.

**Ham export dosyası da verilebilir** — iki dosyanın şekli aynı. O zaman videolar foto prompt'uyla
üretilir.

```
MyDrive/queen-tools/
├── workflow_api.json   ← grafın kopyası (bir kez konur)
└── <proje>/
    ├── video.json      ← prompt_converter yazar
    └── 001.mp4 …       ← bu notebook yazar
```

> **Graf nereden gelir:** repodaki `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json`'u
> indirip Drive'da `queen-tools/` altına koy. Grafı değiştirmek istersen
> `wan22-arbuzai/manual.ipynb` → **Workflow → Export (API)**.

**Gerekenler:** **A100** runtime · Colab **Secrets**'ta `CIVITAI_COOKIE` (notebook erişimi açık).

Sıra:
1. **CONFIG** — Drive mount + graf/cookie ayarları
2. **Plan dosyasını yükle** — `video.json` · ardından **üretim planı** basılır
3. **Ortak Yardımcılar** — log + fail-loud run + model doğrulama
4. **ComfyUI + custom node'lar** (16)
5. **Modeller** — önce gated probe, sonra indir (~36 GiB)
6. **ComfyUI'yi başlat** (arka planda, API)
7. **Üret** — her kare: yükle, render et, Drive'a yaz

> **Yarıda kalırsa baştan çalıştır.** Çıktısı olan atlanır, kalanlar üretilir. Yeniden üretmek için
> Drive'dan o mp4'ü sil.

> **Video pahalı.** Her render A100'de dakikalar sürer; toplam = kare sayısı × `VARIANTS`.

> **LoRA'lar grafikte.** `wan22-arbuzai/manual.ipynb` + UI'da ayarlayıp Export (API) ile
> dondurursun; bu notebook onlara dokunmaz, yalnız fotoğraf/prompt/seed yazar.
```

- [ ] **Step 3: CONFIG açıklamasını (cell 1, markdown) değiştir**

```markdown
## 1) CONFIG

Google Drive **burada** mount edilir: auth istemi ilk saniyede çıksın, 36 GiB'lık model indirmesinin
ortasında seni beklemesin.

Burada doldurulacak bir prompt listesi **yok** — prompt'lar bir sonraki bölümde yükleyeceğin
`video.json`'dan gelir.

`VARIANTS` her fotoğraf için kaç video üretileceğidir (farklı seed). Video pahalı olduğu için 1.

Civitai cookie'si **Colab Secrets**'tan okunur (`CIVITAI_COOKIE`) — notebook'un içinde durmaz.
Süresi ~30 günde dolar; bittiğinde `civitai.red`'den yeni değeri alıp **sırrı** güncelle.
```

- [ ] **Step 4: CONFIG hücresini (cell 2, kod) değiştir**

`PROMPTS`, `INPUT_DIR`, `OUTPUT_DIR` ve eski `DRIVE_ROOT` çıkar. `COOKIE_VALUE` artık gömülü bir
değer değil, `CIVITAI_COOKIE` sırrından okunur — kopyalanan dosyadaki JWT satırı tamamen silinir.
Hücre baştan yazıldığı için kaynaktan miras kalan Türkçe kod yorumları da İngilizceye çevrilir
(repo kuralı: yorum İngilizce, kullanıcının gördüğü `assert`/`print` metni Türkçe).

```python
# === Google Drive — en başta mount edilir ===
# The auth prompt has to appear in the first second, not in the middle of a 36 GiB download.
from google.colab import drive, userdata
drive.mount('/content/drive')

SEED     = None              # None -> a fresh random seed per variant; a number -> SEED + v
VARIANTS = 1                 # videos per photo (different seeds) -- video is expensive

# === Drive ===
DRIVE_ROOT        = "/content/drive/MyDrive/queen-tools"
WORKFLOW_FILENAME = "workflow_api.json"      # under DRIVE_ROOT, API format

# === Civitai login-gated download ===
# Read from Colab Secrets under the same name Queen Editor uses, so one paste serves both tools and
# the token is not committed with the notebook.
# How to get the value: civitai.red -> log in -> F12 -> Application -> Cookies -> __Secure-civ-token
# (double-click -> Ctrl+A -> Ctrl+C; a single click truncates it and the len > 200 gate still passes).
# NOTE: auth moved to auth.civitai.com -> the cookie NAME is __Secure-civ-token (NOT the old
#   __Secure-civitai-token) and the value is a short ES256 JWT (~420 chars), not the old long JWE.
# Cookie only; never a ?token= API key -> gated assets answer 401.
COOKIE_VALUE = userdata.get('CIVITAI_COOKIE')

# === Render ===
TIMEOUT_PER_RENDER = 30 * 60   # seconds -- a video that misses this fails loud
POLL_INTERVAL      = 5         # seconds -- /history poll interval

# === Derived paths ===
COMFY_PORT       = 8188
COMFYUI_URL      = f"http://127.0.0.1:{COMFY_PORT}"
WORKFLOW_PATH    = f"{DRIVE_ROOT}/{WORKFLOW_FILENAME}"

COMFY_ROOT       = "/content/ComfyUI"
COMFY_OUTPUT_DIR = f"{COMFY_ROOT}/output"
COMFY_LOG        = "/content/comfyui.log"

import os
os.makedirs(DRIVE_ROOT, exist_ok=True)
# Two asserts, not one: a missing secret and a truncated value are different mistakes and a single
# message could not name which one happened.
assert COOKIE_VALUE, "❌ CIVITAI_COOKIE okunamadı — Colab Secrets'a ekle ve 'Notebook access' aç"
assert len(COOKIE_VALUE) > 200, f"❌ CIVITAI_COOKIE çok kısa ({len(COOKIE_VALUE)} karakter) — değer kırpılmış, civitai.red'den __Secure-civ-token'ı çift tıklayıp tamamını kopyala"
assert os.path.exists(WORKFLOW_PATH), f"❌ Workflow yok: {WORKFLOW_PATH} — repodaki wan22-arbuzai/workflow_api.json'u buraya kopyala"
assert VARIANTS >= 1, "❌ VARIANTS en az 1 olmalı"

print(f"✓ Drive: {DRIVE_ROOT}")
print(f"✓ Cookie: Secrets'tan okundu ({len(COOKIE_VALUE)} char)  |  Timeout: {TIMEOUT_PER_RENDER // 60} dk/video")
print(f"✓ Seed: {SEED if SEED is not None else 'varyant başına rastgele'}  |  Varyant: {VARIANTS}")
print("=== GPU ===")
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

- [ ] **Step 5: Plan dosyası bölümünü ekle (CONFIG hücresi ile plan hücresi arasına)**

Önce markdown hücresi:

```markdown
## 2) Plan dosyasını yükle

`prompt_converter.ipynb`'ın indirdiği `video.json`'u buraya yükle. **İş emri yüklediğin dosyadır** —
Drive'dan seçim yapılmaz, böylece bayat bir ayar yanlış projeyi render edemez.

Ham `<proje>-export.json` de yüklenebilir; şekli aynı, o zaman videolar foto prompt'uyla üretilir.

Hemen altındaki hücre **üretim planını** basar: hangi kare üretilecek, hangisi neden atlanacak.
Tablo, 36 GiB'lık indirmeden önce çıkar.
```

Sonra kod hücresi:

```python
# === Plan dosyasını yükle (video.json ya da ham export) + biçimini doğrula ===
# The uploaded file is the work order: whatever you upload is what gets rendered. Nothing is
# picked from Drive, so a stale setting can never point the run at another project.
from google.colab import files
import json, os

uploaded = files.upload()
if len(uploaded) != 1:
    raise RuntimeError(f"❌ Tek dosya yükle — {len(uploaded)} dosya geldi: {list(uploaded)}")

PLAN_NAME = next(iter(uploaded))
try:
    PLAN_JSON = json.loads(uploaded[PLAN_NAME].decode("utf-8"))
except (UnicodeDecodeError, json.JSONDecodeError) as e:
    raise RuntimeError(f"❌ {PLAN_NAME} okunamadı: {type(e).__name__}: {e}") from None

def validate_plan(data):
    """Fail-loud on a file that is not a Queen Editor export / converted plan. Only `prompt` is
    read, so a raw export works too -- what has to exist is `folder`, `file` and `prompt`."""
    if not isinstance(data, dict):
        raise RuntimeError(f"❌ JSON bir nesne değil: {type(data).__name__}")
    for key in ("folder", "photos"):
        if key not in data:
            raise RuntimeError(f"❌ '{key}' alanı yok — dosyadaki anahtarlar: {sorted(data)}")
    if not isinstance(data["photos"], list):
        raise RuntimeError(f"❌ 'photos' liste değil: {type(data['photos']).__name__}")
    for i, photo in enumerate(data["photos"]):
        if not isinstance(photo, dict):
            raise RuntimeError(f"❌ photos[{i}] nesne değil: {type(photo).__name__}")
        missing = [k for k in ("file", "prompt") if k not in photo]
        if missing:
            raise RuntimeError(f"❌ photos[{i}] eksik alan: {missing} — var olanlar: {sorted(photo)}")

validate_plan(PLAN_JSON)

PHOTO_DIR = PLAN_JSON["folder"]
if not os.path.isdir(PHOTO_DIR):
    raise RuntimeError(f"❌ Fotoğraf klasörü yok: {PHOTO_DIR}\n"
                       "Drive aynı hesapla mı mount edildi? Proje silinmiş olabilir.")

# The project name comes from the file itself, so the output folder can never disagree with the
# photos it was built from.
PROJECT    = os.path.basename(PHOTO_DIR.rstrip("/"))
OUTPUT_DIR = f"{DRIVE_ROOT}/{PROJECT}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"✓ {PLAN_NAME}: {len(PLAN_JSON['photos'])} kare")
print(f"✓ Proje: {PROJECT}")
print(f"✓ Fotoğraflar (yalnız okunur): {PHOTO_DIR}")
print(f"✓ Videolar: {OUTPUT_DIR}")
```

- [ ] **Step 6: Plan hücresini (cell 3, kod) baştan yaz**

Eski `scan_photos` / `find_photo` / `photos_without_prompt` tamamen çıkar — girdi taraması artık JSON'dan geliyor.

```python
# === Üretim planı — indirmeden önce, bilerek ===
# loop_maker's rule: decide the whole run before a GPU minute is spent. A stale plan file or an
# already-complete output folder shows up here, not after ~40 minutes of model downloads.
# log()/human() belong to the next section and are not defined yet, so this cell prints plainly.
import os

def out_path(seq, v):
    """Output path for the seq-th frame of the plan (1-based), seed-variant v (0-indexed).
    VARIANTS==1 -> 001.mp4; else a 1-indexed variant suffix (001_1.mp4, 001_2.mp4).

    The name is the frame's POSITION, not the photo's file name, so listing the folder
    alphabetically gives the video order. Which photo and prompt produced 003.mp4 is answered by
    photos[2] of the plan file -- that is where the pairing already lives, and repeating it in the
    file name would be a second copy to keep in agreement.

    Three digits assume fewer than 1000 frames; past that the alphabetical order breaks, which this
    pipeline will not reach."""
    stem = f"{seq:03d}"
    return f"{OUTPUT_DIR}/{stem}.mp4" if VARIANTS == 1 else f"{OUTPUT_DIR}/{stem}_{v + 1}.mp4"

def build_plan(photos, folder):
    """One row per (photo, seed-variant) -> (seq, v, action, image_path, prompt, reason).
    Each photo carries its own prompt: the pairing was done upstream, nothing is matched here.

    A skipped photo still consumes its position (001, 002, 004 when the third is skipped): the gap
    keeps every file lined up with its row in the plan file, which closing it would break."""
    rows = []
    for seq, photo in enumerate(photos, start=1):
        image  = os.path.join(folder, photo["file"])
        prompt = photo["prompt"]
        for v in range(VARIANTS):
            out = out_path(seq, v)
            if not prompt.strip():
                rows.append((seq, v, "ATLA", None, "", "prompt boş"))
            elif not os.path.exists(image):
                # The plan file lists a photo the project no longer has -- it went stale.
                rows.append((seq, v, "ATLA", None, prompt, "fotoğraf klasörde yok"))
            elif os.path.exists(out) and os.path.getsize(out) > 0:
                rows.append((seq, v, "ATLA", image, prompt, "çıktı zaten var"))
            else:
                rows.append((seq, v, "ÜRET", image, prompt, ""))
    return rows

PLAN = build_plan(PLAN_JSON["photos"], PHOTO_DIR)

print(f"\n{'ÇIKTI':>9}  {'KARAR':<6}  {'FOTOĞRAF':<16}  AÇIKLAMA")
print("-" * 78)
for seq, v, action, image, prompt, reason in PLAN:
    disp = f"{seq:03d}" if VARIANTS == 1 else f"{seq:03d}_{v + 1}"
    name = os.path.basename(image) if image else "—"
    detail = reason if reason else prompt.strip().replace("\n", " ")[:34]
    print(f"{disp:>9}  {action:<6}  {name:<16}  {detail}")

_to_render = sum(1 for r in PLAN if r[2] == "ÜRET")
print("-" * 78)
print(f"Üretilecek: {_to_render}  |  Atlanacak: {len(PLAN) - _to_render}")

if _to_render == 0:
    raise RuntimeError("❌ Üretilecek video yok — yukarıdaki tabloya bak (prompt boş, fotoğraf yok ya da hepsi zaten üretilmiş)")
```

- [ ] **Step 7: Kalan bölüm başlıklarını yeniden numaralandır**

Araya "2) Plan dosyasını yükle" girdiği için sonraki markdown başlıkları birer kayar. Başlık
satırları dışında o hücrelerin içeriğine dokunulmaz:

| Eski | Yeni |
|---|---|
| `## 2) Ortak Yardımcılar` | `## 3) Ortak Yardımcılar` |
| `## 3) ComfyUI + Custom Node'lar (16)` | `## 4) ComfyUI + Custom Node'lar (16)` |
| `## 4) Modeller — önce gated probe, sonra indir (~36 GiB)` | `## 5) Modeller — önce gated probe, sonra indir (~36 GiB)` |
| `## 5) ComfyUI'yi Başlat (Arka Planda)` | `## 6) ComfyUI'yi Başlat (Arka Planda)` |
| `## 6) Üret` | `## 7) Üret` |

Bu, Step 2'deki başlık hücresinde yazan yedi adımlı sırayla eşleşir.

- [ ] **Step 8: "7) Üret" açıklamasının ilk paragrafını güncelle**

Hücrenin geri kalanı (yarıda kalma, hata, seed notları) aynen kalır; yalnız ilk paragraf değişir:

```markdown
Plan tablosunda **ÜRET** yazan her çıktı sırayla işlenir: fotoğraf Queen Editor'ün klasöründen
okunup ComfyUI'ya yüklenir, render edilir, `queen-tools/<proje>/` altına yazılır (`001.mp4`,
`VARIANTS > 1` ise `001_<v>.mp4`), ComfyUI'daki kopyalar silinir.
```

- [ ] **Step 9: Render döngüsündeki satır açılımını güncelle (son kod hücresi)**

`process_all` içinde **yalnız** iki satır değişir; fonksiyonun geri kalanı (upload cache, seed, hata sınıflandırması, sayaçlar, loglar) aynen kalır:

```python
    for seq, v, _action, image_path, prompt, _reason in todo:
        save_path = out_path(seq, v)
```

(Eski hâli `for number, letter, v, _action, image_path, prompt, _reason in todo:` ve
`save_path = out_path(number, letter, v)` idi.) `todo` filtresi de indeks kaydığı için güncellenir:

```python
    todo = [row for row in plan if row[2] == "ÜRET"]
```

- [ ] **Step 10: Notebook'u Read ile doğrula**

`collab-toolbox/queen-tools/photo_to_video.ipynb` dosyasını Read ile aç. Kontrol listesi:
- Hücreler render oluyor (JSON bozulmamış)
- `PROMPTS`, `scan_photos`, `find_photo`, `photos_without_prompt`, `INPUT_DIR` **hiçbir yerde geçmiyor**
- Bölüm başlıkları 1'den 7'ye kesintisiz gidiyor
- `IMAGE_NODE = "287"`, `PROMPT_NODE = "233:240"`, `SEED_NODE = "210"` yerinde duruyor
- `MAX_CONSECUTIVE_FAILURES`, `ComfyExecutionError`, `check_safetensors`, `civitai_probe` aynen duruyor
- Notebook'ta **düz metin cookie yok**: `COOKIE_VALUE = userdata.get('CIVITAI_COOKIE')`

- [ ] **Step 11: Commit**

```bash
git add collab-toolbox/queen-tools/photo_to_video.ipynb
git commit -m "feat(queen-tools): render the plan file into videos"
```

---

### Task 3: Dokümantasyon

**Files:**
- Modify: `CLAUDE.md` (collab-toolbox notebook tablosu)

**Interfaces:**
- Consumes: Task 1 ve Task 2'nin dosya yolları
- Produces: yok (doküman)

- [ ] **Step 1: `CLAUDE.md` notebook tablosuna iki satır ekle**

Tablonun sonuna, `watermark/watermark_remove.ipynb` satırından sonra:

`CLAUDE.md` bir geliştirici dokümanı, yani **İngilizce** (repo dil kuralı — Türkçe olan yalnız
notebook'ların içi):

```markdown
| [queen-tools/prompt_converter.ipynb](collab-toolbox/queen-tools/prompt_converter.ipynb) | Queen Editor export → motion prompts (Grok), one request per frame | CPU |
| [queen-tools/photo_to_video.ipynb](collab-toolbox/queen-tools/photo_to_video.ipynb) | That plan file → video, photo by photo (WAN 2.2 I2V) | A100 (Colab Pro) |
```

- [ ] **Step 2: `CLAUDE.md`'ye zinciri anlatan bir paragraf ekle**

Tablonun hemen altına, `Usage:` satırından önce:

```markdown
**queen-tools is one chain, not two tools.** Queen Editor's Export file is turned into motion prompts
by `prompt_converter`, and `photo_to_video` reads the result and writes the videos under
`MyDrive/queen-tools/<project>/`. Queen Editor's own folder is only ever read — the design and its
reasoning: [docs/superpowers/specs/2026-08-09-queen-tools-design.md](../specs/2026-08-09-queen-tools-design.md).
Both notebooks take their work order from a file you upload, so nothing is picked from Drive by name.
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md docs/superpowers/specs/2026-08-09-queen-tools-design.md docs/superpowers/plans/2026-08-09-queen-tools.md
git commit -m "docs(queen-tools): record the export-to-video chain"
```

---

## Colab doğrulaması (kullanıcı, tek turda)

Kod tarafı bittikten sonra. **Önce iki şey:**

- Repodaki `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json`'u indirip Drive'da
  `queen-tools/workflow_api.json` olarak koy
- Colab **Secrets**'ta iki sır da hazır ve notebook erişimi açık olsun: `XAI_API_KEY` (çevirici) ve
  `CIVITAI_COOKIE` (video)

`INSTRUCTION` dolu geliyor, yazacak bir şey yok.

| # | Ne yapılır | Beklenen |
|---|---|---|
| 1 | Queen Editor'de bir projede **Export** | `<proje>-export.json` iner |
| 2 | `prompt_converter` → `INSTRUCTION`'ı geçici olarak boşaltıp çalıştır | İstek atılmadan `RuntimeError` |
| 3 | Talimatı geri koy, export'u yükle | Plan tablosu; her kare için eski/yeni prompt; `queen-tools/<proje>/video.json` oluşur; indir butonu dosyayı indirir |
| 4 | Aynı export'u tekrar yükle | Hepsi "zaten çevrildi" — **tek istek atılmaz** |
| 5 | Drive'daki `video.json`'da bir satırın `photo_prompt`'unu sil, export'u tekrar yükle | **Yalnız o kare** çevrilir |
| 6 | Çeviri sürerken runtime'ı kapat, yeniden aç, export'u yükle | Kalınan yerden devam eder |
| 7 | `photo_to_video` → `video.json`'u yükle | Plan tablosu **modeller inmeden** basılır, her satırda gerçek fotoğraf adı |
| 8 | Koşu biter | `MyDrive/queen-tools/<proje>/001.mp4, 002.mp4 …` — alfabetik sıra videonun sırası; Queen Editor'ün proje klasöründe **yeni hiçbir dosya yok** |
| 9 | Notebook'u tekrar çalıştır | Hepsi "çıktı zaten var" ile atlanır |
| 10 | JSON'a olmayan bir dosya adı yaz, tekrar çalıştır | O satır ATLA + "fotoğraf klasörde yok"; koşu diğerlerini üretir |
| 11 | `queen-tools/workflow_api.json`'u geçici olarak kaldır | CONFIG hücresi yolu yazarak durur |
| 12 | Ham `<proje>-export.json`'u `photo_to_video`'ya yükle | Çalışır — videolar foto prompt'uyla üretilir |
