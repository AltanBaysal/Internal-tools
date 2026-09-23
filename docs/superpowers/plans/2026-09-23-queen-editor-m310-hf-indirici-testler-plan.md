# Madde 310 — HF indiricisi, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Defterin HF dosyalarını adresle değil HF'nin kendi indiricisiyle indirdiğini, damgayı o
yolda da kestiğini ve her dosya için kaynağı ve hızı bastığını söyleyen testler — kırmızı.

**Yaklaşım:** Defter koşulamıyor, okunuyor *(dosyanın kendi docstring'i)*. Testler hücrelerin metnine
bakıyor; iki indirme fonksiyonunun gövdesi bölüm başlıklarıyla kesiliyor, bugünkü damga testinin
yaptığı gibi.

**Araçlar:** pytest; defter JSON olarak okunuyor.

**Spec:** [m310 test turu](../specs/2026-09-23-queen-editor-m310-hf-indirici-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe** *(CODE-STANDARD, Language)*.
- Testler **dört satırla** koşulur, [CLAUDE.md](../../../CLAUDE.md)'de yazıldığı gibi; parçalanmaz,
  süzülmez, tek dosyaya daraltılmaz.
- `skip` / `xfail` yok.
- Bu turda defter değişmiyor; yalnız test dosyası.

---

## Görev 1: Testler

**Dosyalar:**
- Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

**Arayüzler — uygulama turunun uyacağı adlar:**
- `hf_fetch(...)` — `# === Hugging Face ===` başlığının altında, `# === Civitai ===`'den önce.
- `fetch(...)` — yerinde; gövdesi `# === Hugging Face ===`'ye kadar.
- Listeler: `HF_PHOTO`, `HF_VIDEO`, `HF_H3`, `HF_AUDIO`; `OPEN_PHOTO` yalnız SAM'i tutuyor.

- [ ] **Adım 1: Yardımcı.** `_cell`'in altına:

```python
def _between(start, end):
    """The text of the one cell carrying `start`, from `start` up to `end` -- a function and nothing
    after it, when `end` is the section header that follows. "" when either marker is missing, so a
    function that is not there yet fails the assertion that reads it instead of erroring."""
    cell = _cell(start)
    head, tail = cell.find(start), cell.find(end)
    return cell[head:tail] if -1 < head < tail else ""
```

- [ ] **Adım 2: `test_an_unticked_group_costs_no_bytes`'ın tablosu.**

```python
    for names, switch in ((("CIVITAI_PHOTO", "OPEN_PHOTO", "HF_PHOTO"), SWITCH["photo"]),
                          (("CIVITAI_VIDEO", "HF_VIDEO"), 'VIDEO_MODEL == "wan"'),
                          (("CIVITAI_H3", "HF_H3"), 'VIDEO_MODEL == "h3"'),
                          (("HF_AUDIO",), SWITCH["audio"])):
```

- [ ] **Adım 3: `test_the_h3_files_from_huggingface_come_down_over_one_connection`'ı sil**, yerine:

```python
def test_no_huggingface_file_is_fetched_by_its_address():
    """An address sends the file through HF's bridge, which cuts a plain download to 8.7 MB/s on most
    of its servers (xet-core #821) -- the user timed H3's install at about a hundred minutes (madde
    310). Named by repo and path, a file can only come down through HF's own downloader."""
    cell = _cell("# === Target folders ===")

    assert cell, "İndirme hücresi bulunamadı"
    assert "huggingface.co" not in cell, "İndirme hücresinde hâlâ HF adresi var"


def test_huggingface_files_come_down_through_hugging_face_s_own_downloader():
    """hf_xet pulls a file's Xet chunks from storage in parallel and never touches the bridge -- the
    same parallel ranges sent to the bridge by aria2c were answered 403. Without hf_xet installed,
    huggingface_hub falls back to the bridge with nothing but a log line, so installing it is half of
    the rule."""
    assert "hf_hub_download(" in _between("def hf_fetch(", "# === Civitai ==="), \
        "hf_fetch HF'nin kendi indiricisini çağırmıyor"
    assert re.search(r"pip install[^\n]*hf_xet", _source()), "Defter hf_xet'i kurmuyor"


def test_the_quantizer_stamp_is_cut_before_a_huggingface_file_is_judged():
    """The int4 text encoder H3 takes from HF arrives stamped (NOTEBOOK-STANDARD, section 3). A path
    that judged it uncut would call a whole file too long and stop the run."""
    assert "strip_unreferenced_tail(" in _between("def hf_fetch(", "# === Civitai ==="), \
        "hf_fetch damgayı kesmiyor"


def test_every_download_prints_where_it_came_from_and_how_fast():
    """The user compares the sources by reading the console (madde 310, "ama lütfen console
    basılsın"): one line per file saying where it came from and how fast it came."""
    by_address = _between("def fetch(", "# === Hugging Face ===")
    by_repo = _between("def hf_fetch(", "# === Civitai ===")

    assert re.search(r"log\([^\n]*MB/s", by_address), "fetch hızı basmıyor"
    assert re.search(r"log\([^\n]*HF[^\n]*MB/s", by_repo), "hf_fetch kaynağı ve hızı basmıyor"
```

- [ ] **Adım 4: Dört satırı koş** — paralel, CLAUDE.md'de yazıldığı gibi.

- [ ] **Adım 5: Kırmızı commit** — test dosyası, spec ve bu plan.

## Beklenen kırmızı

Beş test, `queen-editor` pytest'inde:

| Test | Neden düşüyor |
|---|---|
| `test_an_unticked_group_costs_no_bytes` | `HF_PHOTO` ve diğerleri yok |
| `test_no_huggingface_file_is_fetched_by_its_address` | Hücrede HF adresleri duruyor |
| `test_huggingface_files_come_down_through_hugging_face_s_own_downloader` | `hf_fetch` yok |
| `test_the_quantizer_stamp_is_cut_before_a_huggingface_file_is_judged` | `hf_fetch` yok |
| `test_every_download_prints_where_it_came_from_and_how_fast` | `fetch` hız basmıyor, `hf_fetch` yok |

Öteki üç satır yeşil kalır; `queen-editor` pytest'inde başka hiçbir test kıpırdamaz.
