# Madde 312 — Yüksek hız, indirme özeti ve hücre süreleri, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `4524b104`'ün on beş kırmızısı yeşile dönsün.

**Yaklaşım:** `downloads.py`'de dört fonksiyon satır döndürüyor, `hf_fetch` ayarı açıyor, sona
`download_summary` geliyor. Defterde dört hücre değişiyor: hücrelerin JSON'unda hedefli
değiştirmeler yapılıyor, değişmeyen satırlara dokunulmuyor. `git diff` yalnız bu satırları
göstermeli. CODE-STANDARD'a bir paragraf ekleniyor.

**Spec:** [m312 implementasyon turu](../specs/2026-09-23-queen-editor-m312-hiz-ve-sureler-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve docstring İngilizce, konsol metinleri Türkçe.
- Defterin kod hücrelerinde yorum yok, yalnız bölüm başlıkları. Defter 29.000 karakteri geçmiyor.
- Testler dört satırla koşulur.

---

## Görev 1: `colab/downloads.py`

- [ ] **Adım 1: `_landed` satırı döndürüyor.**

```python
def _landed(label, source, size, took, msg):
    """The file's line, and its row for the table the models cell ends with (madde 312)."""
    log(f"{label}: indirildi — {source}, {human(size)}, {took:.0f} sn, "
        f"{size / took / 2**20:.1f} MB/s ({msg})", "OK")
    return label, size, took
```

- [ ] **Adım 2: `fetch`'in son satırı** `return _landed(…)`; docstring'e: *"Its row for the summary,
  or None when the file was already in place."*

- [ ] **Adım 3: `hf_fetch`** — import'tan önce ayar, sonda `return _landed(…)`, docstring'e aynı
  cümle:

```python
    # huggingface_hub reads its variables once, when it is imported, so the switch comes first. It
    # has hf_xet try to fill the machine's bandwidth and use every CPU core (madde 312).
    os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"
    # Imported here: Colab ships it, and this module has to import where it is not installed.
    from huggingface_hub import hf_hub_download
```

- [ ] **Adım 4: `civitai_fetch`** — aynadan `return hf_fetch(…)`; düşüşte `row = fetch(…)`, yükleme,
  `return row`. Docstring'e: *"Either way the row is the download's; the upload has its own line."*

- [ ] **Adım 5: Modülün sonuna.**

```python
def _duration(seconds):
    minutes, seconds = divmod(round(seconds), 60)
    return f"{minutes} dk {seconds} sn" if minutes else f"{seconds} sn"


def download_summary(rows):
    """The table the models cell ends with (madde 312): every file that came down in this run -- one
    already in place hands back None and stays out -- and under them a Toplam, whose speed is the
    average of the whole download. The times are the downloads' own; the cell's own line, under the
    table, has the rest, uploads and probes included."""
    rows = [row for row in rows if row]
    if not rows:
        log("İndirme özeti: bu koşuda inen dosya yok")
        return
    rows.append(("Toplam", sum(size for _, size, _ in rows), sum(took for _, _, took in rows)))
    width = max(len(label) for label, _, _ in rows)
    print("\nİndirme özeti:")
    for label, size, took in rows:
        print(f"   {label:<{width}}  {human(size):>8}  {_duration(took):>11}  "
              f"{size / took / 2**20:6.1f} MB/s")
```

## Görev 2: Defter

**Dosya:** `queen-editor/queeneditor.ipynb` — hücrelerin `source` dizgelerinde hedefli değiştirme.

- [ ] **Adım 1: CONFIG (`8215086b`)** — hücre bu bölümle açılıyor, `# === CONFIG ===`'dan önce:

```python
# === Cell timer ===
import time
from IPython import get_ipython

def _cell_began(*_):
    global _CELL_START
    _CELL_START = time.perf_counter()

def cell_elapsed():
    minutes, seconds = divmod(round(time.perf_counter() - _CELL_START), 60)
    return f"{minutes} dk {seconds} sn" if minutes else f"{seconds} sn"

def _cell_ended(*_):
    print(f"⏱️ Hücre {cell_elapsed()} sürdü")

_events = get_ipython().events
for _event, _hook in (("pre_run_cell", _cell_began), ("post_run_cell", _cell_ended)):
    for _old in [h for h in _events.callbacks[_event] if h.__name__ == _hook.__name__]:
        _events.unregister(_event, _old)
    _events.register(_event, _hook)
_cell_began()

```

- [ ] **Adım 2: Yardımcılar (`df871d38`)** — import satırı:

```python
from colab.downloads import fetch, hf_fetch, civitai_fetch, download_summary
```

- [ ] **Adım 3: Modeller (`f0df85b4`)** — döngüler ve özet:

```python
# === Hugging Face downloads ===
landed = []
for repo, path, d, fn, label, floor in hf_jobs:
    landed.append(hf_fetch(repo, path, d, fn, label, floor=floor))

# === Open downloads ===
for url, d, fn, label, floor in open_jobs:
    landed.append(fetch(url, d, fn, label, parallel=True, floor=floor))

# === Civitai downloads ===
for vid, d, fn, label in civitai_jobs:
    landed.append(civitai_fetch(HF_MIRROR, vid, d, fn, label, COOKIE_VALUE))
```

  klasör listesinin döngüsünden sonra, `if INSTALL_PHOTO:`'dan önce:

```python
download_summary(landed)
```

- [ ] **Adım 4: Flask (`e086a5a5`)** — `🔗 Queen Editor` satırının hemen üstüne:

```python
print(f"✓ Link {cell_elapsed()}'de hazır")
```

- [ ] **Adım 5: `git diff queen-editor/queeneditor.ipynb`** — yalnız bu satırlar değişmiş olmalı.

## Görev 3: CODE-STANDARD

- [ ] **Adım 1:** `## Notebook code (\`colab/\`)` bölümünün sonuna:

```markdown
One piece of the notebook's own code stays in a cell: the timer that opens CONFIG and ends every
cell's output with how long it took (madde 312). The cells it times include the Drive mount and the
clone, and `colab/` arrives with the clone, so the timer could not import it. Its section needs
nothing but `time` and IPython, and the suite cuts it out by its heading and runs it.
```

## Görev 4: Koşu, commit'ler

- [ ] **Adım 1: Dört satırı koş** — dördü de yeşil.
- [ ] **Adım 2: Yeşil commit** — `downloads.py`, defter, CODE-STANDARD, bu spec ve bu plan.
- [ ] **Adım 3: Yol haritası** — 312 ✅, *Kapandı* notu, *Durum: 21/21*; ayrı `docs(m312)` commit'i.
