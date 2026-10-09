# v11 Görev 1 — xAI anahtarı yoklaması: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `635d26c`'deki sekiz kırmızı testi yeşile çevirmek.

**Architecture:** Defterin CONFIG hücresi anahtarı kırpılmış okur, xAI'a uygulamanın yapacağı
çağrının aynısını gönderir ve cevaba göre durur ya da uyarır. Model adı ile adres artık defterin,
uygulamaya çevre değişkeniyle geçiyor. İstemci kendi header'ını kurarken anahtarı ayrıca kırpıyor.

**Tech Stack:** Colab notebook (Python + `requests`), Flask backend.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-13-queen-editor-v11-gorev-1-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `635d26c`'deki sekiz test sözleşme; biri bile düzenlenirse döngünün
  anlamı kalmaz. Yeşil, koda uyarak gelir.
- Yorum, docstring ve commit mesajı **İngilizce**; defterin `print`/`raise` metinleri **Türkçe**.
- **Sebep uydurulmaz:** yoklama xAI'ın kendi gövdesini basar.
- Defter düzenlemesi `NotebookEdit` ile (`ToolSearch` ile şemasını çek).
- Commit mesajında **çift tırnak yok**.
- Test komutu: `python -m pytest queen-editor/backend/tests -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/backend/services/xai/client.py` | header'ın biçimi | 1 satır |
| `queen-editor/app.ipynb` — CONFIG (`8215086b`) | anahtarı okumak, kırpmak, yoklamak | değişiyor |
| `queen-editor/app.ipynb` — Flask (`e086a5a5`) | uygulamaya ne geçtiği | 2 anahtar eklenir |

---

### Task 1: İstemci anahtarı kırpar

**Files:**
- Modify: `queen-editor/backend/services/xai/client.py`

**Interfaces:**
- Consumes: yok. Produces: yok (davranış değişikliği, imza aynı).

- [ ] **Step 1: `__init__`'te kırp**

```python
    def __init__(self, api_key, model, url, http=requests, timeout=120):
        # Trimmed here because this is what builds the header: a key pasted with a trailing
        # newline would otherwise travel as `Bearer sk-...\n`, which xAI answers 400 to. It also
        # turns a key of nothing but spaces into no key at all, so the sentence written for a
        # missing key is the one the user gets.
        self._api_key = (api_key or "").strip()
```

- [ ] **Step 2: İki istemci testinin yeşile döndüğünü gör**

Run: `python -m pytest queen-editor/backend/tests/test_xai_client.py -q`
Expected: PASS (7 test).

---

### Task 2: CONFIG anahtarı kırparak okur ve yoklar

**Files:**
- Modify: `queen-editor/app.ipynb` — hücre `8215086b`

**Interfaces:**
- Consumes: `INSTALL_VIDEO` (aynı hücre), `userdata`.
- Produces: `XAI_API_KEY` (kırpılmış), `XAI_MODEL`, `XAI_URL` — Flask hücresi üçünü de kullanıyor.

- [ ] **Step 1: Anahtarın okunduğu bloğu değiştir**

Mevcut:

```python
try:
    XAI_API_KEY = userdata.get("XAI_API_KEY")
except Exception:
    XAI_API_KEY = ""
```

Yerine:

```python
try:
    XAI_API_KEY = (userdata.get("XAI_API_KEY") or "").strip()
except Exception:
    XAI_API_KEY = ""
```

Yorumun ilk cümlesi aynı kalır, sonuna eklenir: `Trimmed on the way in: a value pasted with a
trailing newline would travel into the Authorization header and come back as a 400.`

- [ ] **Step 2: Yoklamayı GPU assert'inin altına, print'lerin üstüne ekle**

```python
# The model and the address live here now, not only in the app's defaults: the probe below has to
# ask exactly what the app will ask, and two places holding one model name would drift. The app
# reads both from the environment (see the Flask cell); config.py's literals stay as the fallback
# for a local run.
XAI_MODEL = "grok-4.3"
XAI_URL   = "https://api.x.ai/v1/chat/completions"

def xai_probe(key, *, fatal):
    """Ask xAI the smallest question there is, and report what it answers.

    The probe IS the app's own call: xAI documents no endpoint for checking a key, and asking the
    same question the app will ask proves more anyway -- the key, the model name and the reach of
    the service, in one request. So anything but a 2xx means the app's call would fail the same
    way, and the reason printed is xAI's own body, never a guessed one.

    fatal=True stops the run. A video's prompt is written here and there is no manual path, so
    ~37 GiB of video models installed against a broken key is time spent for nothing. A network
    error stops nothing: a timeout says nothing about the key.
    """
    import requests
    try:
        answer = requests.post(
            XAI_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": XAI_MODEL,
                  "messages": [{"role": "user", "content": "ping"}],
                  "max_tokens": 1},
            timeout=30,
        )
    except Exception as unreachable:
        print(f"⚠️  xAI yoklanamadı ({type(unreachable).__name__}: {unreachable}) — "
              f"anahtar hakkında bir şey söylenemiyor, koşu sürüyor")
        return
    if answer.status_code // 100 == 2:
        print(f"✓ xAI anahtarı çalışıyor (model: {XAI_MODEL})")
        return
    said = (f"xAI anahtarı reddedildi — HTTP {answer.status_code}, "
            f"xAI yanıtı: {answer.text[:400]}")
    if fatal:
        raise RuntimeError(
            f"❌ {said}\nVideo kuruluyor ama video prompt'unu bu anahtar yazıyor, başka yolu yok. "
            f"console.x.ai'dan yeni anahtar al ve Colab Secrets'taki XAI_API_KEY'i güncelle."
        )
    print(f"⚠️  {said}")
    print("   Video üretmeyeceksen sorun değil — foto üretimi anahtarsız da çalışır.")
```

- [ ] **Step 3: Anahtar satırının print'ini yoklamayla değiştir**

Mevcut son print:

```python
print(f"✓ xAI anahtarı: {'okundu' if XAI_API_KEY else 'yok — video prompt yazılamaz'}")
```

Yerine:

```python
# Last of the gates and the only one that costs a request, so everything free runs first.
if not XAI_API_KEY:
    print("✓ xAI anahtarı: yok — video prompt yazılamaz (foto üretimi etkilenmez)")
else:
    xai_probe(XAI_API_KEY, fatal=INSTALL_VIDEO)
```

- [ ] **Step 4: Altı defter testinin yeşile döndüğünü gör**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: PASS (16 test).

---

### Task 3: Uygulama modeli ve adresi defterden alır

**Files:**
- Modify: `queen-editor/app.ipynb` — hücre `e086a5a5`

**Interfaces:**
- Consumes: `XAI_MODEL`, `XAI_URL` (CONFIG).
- Produces: yok.

- [ ] **Step 1: `flask_env`'e iki anahtar ekle**

```python
flask_env = {**os.environ, "QE_DRIVE_ROOT": DRIVE_ROOT, "QE_COMFY_URL": COMFYUI_URL,
             "QE_COMFY_ROOT": COMFY_ROOT, "QE_XAI_API_KEY": XAI_API_KEY or "",
             "QE_XAI_MODEL": XAI_MODEL, "QE_XAI_URL": XAI_URL}
```

Üstündeki yorumun son cümlesine eklenir: `The model and the address travel with the key, so the
probe above and the app ask the same service the same question.`

- [ ] **Step 2: Tam takımı koş**

Run: `python -m pytest queen-editor/backend/tests -q`
Expected: 592 geçen, 0 düşen.

---

### Task 4: Commit

- [ ] **Step 1: Ön yüze dokunulmadığını doğrula**

Run: `git status --short`
Expected: `client.py`, `app.ipynb`, `docs/superpowers` ve (önceki turdan bekleyen) `EKSIKLER.md`.
`frontend/` temiz — `dist/` yeniden derlenmiyor.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/backend queen-editor/app.ipynb queen-editor/EKSIKLER.md docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): ask xAI whether the key works before anything downloads

The eight tests from the previous commit go green.

The notebook checked every outside thing it depends on except this one, so a
dead key surfaced after the install and a batch of photos. It now asks xAI the
app's own question -- same endpoint, same model, one word of body -- because
xAI documents no endpoint for checking a key, and asking what the app will ask
proves the key, the model name and the reach of the service at once. Anything
but a 2xx is reported with xAI's own body; it stops the run when video is being
installed, since a video prompt has no manual path, and only warns otherwise. A
network error stops nothing: a timeout says nothing about a key.

The key is trimmed twice, for two reasons. The notebook trims the paste, so the
probe and the app see the same value. The client trims what it puts in its own
header, so a caller that never touched Colab gets a well-formed one -- and a key
of nothing but spaces now reaches the sentence written for a missing key instead
of xAI's 400.

Also carries the EKSIKLER entries from the Colab round that found this.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** yoklamanın uç noktası ve karar tablosu→Task 2 Step 2 · model/adres tek kaynak→Task
2 Step 2 + Task 3 · defterde kırpma→Task 2 Step 1 · istemcide kırpma→Task 1 · anahtar yoksa
yoklama yok→Task 2 Step 3. Spec'te olup planda olmayan madde yok.

**Sözleşmeye uyum:** testlerin çiviledikleri dört metin bu planda birebir geçiyor — `def xai_probe`,
`xai_probe(XAI_API_KEY, fatal=INSTALL_VIDEO)`, `xAI yanıtı`, `⚠️`, `raise RuntimeError` ve
`XAI_API_KEY = (userdata.get("XAI_API_KEY") or "").strip()`. Testlere dokunulmuyor.

**Dikkat:** `xai_probe` CONFIG hücresinde yaşıyor, dolayısıyla `log()` yok — yardımcılar hücresi
henüz çalışmadı. Uyarılar düz `print`, duruş `raise RuntimeError`.
