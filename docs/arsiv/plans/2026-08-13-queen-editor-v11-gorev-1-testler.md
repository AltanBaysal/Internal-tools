# v11 Görev 1 — xAI anahtarı yoklaması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sekiz test eklemek; hepsi düşecek. Kod bu döngüde değişmiyor.

**Architecture:** İki gerçek test istemciyi çalıştırıyor (anahtarın kırpılması), altı test defterin
metnini okuyor (yoklamanın varlığı, yeri ve kuralı). Defter testleri için tek hücrenin kaynağını
veren bir yardımcı ekleniyor — "nerede" sorusunu sormanın başka yolu yok.

**Tech Stack:** pytest.

**Tasarım:** [v11 Görev 1 test spec'i](../specs/2026-08-13-queen-editor-v11-gorev-1-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** Bu döngü yalnız test dosyalarına dokunur. `client.py`, `app.ipynb` ve
  `config.py` bu commit'te olduğu gibi kalır.
- **Kırmızı bırakılır.** `xfail`/`skip` yok; testler düpedüz düşer ve commit mesajı bunu söyler.
- Dil: test adları, docstring'ler ve commit mesajı **İngilizce**; assert mesajları **Türkçe**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (repo kökünden, `cd` yok): `python -m pytest queen-editor/backend/tests -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/backend/tests/test_xai_client.py` | istemcinin dışarıya ne gönderdiği | 2 test eklenir |
| `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py` | defterin ne yaptığı, metin üzerinden | 1 yardımcı + 6 test eklenir |

---

### Task 1: İstemci — anahtar kırpılır

**Files:**
- Test: `queen-editor/backend/tests/test_xai_client.py`

**Interfaces:**
- Consumes: `XaiClient`, `NotConfigured` (mevcut), dosyanın kendi `FakeHttp` / `client()`
  yardımcıları.
- Produces: yok.

- [ ] **Step 1: İki testi dosyanın sonuna ekle**

```python
def test_the_key_reaches_the_header_without_the_whitespace_around_it():
    """A key pasted into Colab's secret store can carry a trailing newline, and a header reading
    `Bearer sk-...\\n` is what xAI answers 400 to. The client owns the shape of its own header."""
    http = FakeHttp(answering("x"))

    client(http, api_key="\n k-1 \n").complete("talimat", "prompt")

    assert http.calls[0]["headers"]["Authorization"] == "Bearer k-1"


def test_a_key_that_is_only_whitespace_counts_as_no_key():
    """There is a carefully written sentence for a missing key, and a single space must not slip
    past it into xAI's own 400 -- which says far less about what to do."""
    http = FakeHttp(answering("x"))

    with pytest.raises(NotConfigured):
        client(http, api_key="   ").complete("talimat", "prompt")

    assert http.calls == []
```

- [ ] **Step 2: İkisinin de düştüğünü gör**

Run: `python -m pytest queen-editor/backend/tests/test_xai_client.py -q`
Expected: FAIL ×2 — birincisi `Bearer \n k-1 \n` alır, ikincisi istek gönderildiği için
`NotConfigured` yükselmez.

---

### Task 2: Defter — yoklamanın varlığı, yeri ve kuralı

**Files:**
- Test: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

**Interfaces:**
- Consumes: dosyanın mevcut `NOTEBOOK` sabiti ve `_source()` yardımcısı.
- Produces: `_cell(marker)` — bir sonraki döngü de kullanabilir.

- [ ] **Step 1: Tek hücrenin kaynağını veren yardımcıyı ekle**

`_source()`'un hemen altına:

```python
def _cell(marker):
    """The source of the one cell that carries `marker`, or "".

    Some questions are about WHERE something is, not whether it exists -- and the blob `_source()`
    returns cannot tell one cell from another.
    """
    with open(NOTEBOOK, encoding="utf-8") as handle:
        doc = json.load(handle)
    for cell in doc.get("cells", []):
        source = "".join(cell.get("source", ""))
        if marker in source:
            return source
    return ""
```

- [ ] **Step 2: Altı testi dosyanın sonuna ekle**

```python
def test_the_xai_key_is_probed_like_everything_else_from_outside():
    """Everything the notebook needs from outside is checked before the heavy work -- the GitHub
    token by an assert, the Civitai cookie by a 1 KB probe, the disk by measurement. The xAI key
    was the one that was not, so on 2026-08-13 a dead key surfaced only after the whole install
    and a batch of photos, as `xAI HTTP 400 -- Incorrect API key provided`."""
    assert "def xai_probe" in _source(), "Defter xAI anahtarını yoklamıyor"


def test_the_xai_probe_runs_in_config_not_after_the_downloads():
    """CONFIG is the first cell. Anywhere later and the answer costs an install."""
    assert "xai_probe(" in _cell("# === CONFIG ==="), "Yoklama CONFIG hücresinde çağrılmıyor"


def test_a_dead_key_stops_a_run_that_is_installing_video():
    """A video's prompt is written by the language model and there is no manual path, so installing
    ~37 GiB of video models against a dead key is time spent for nothing."""
    assert "xai_probe(XAI_API_KEY, fatal=INSTALL_VIDEO)" in _cell("# === CONFIG ==="), \
        "Yoklamanın durdurup durdurmayacağı video seçimine bağlanmamış"


def test_a_dead_key_only_warns_when_video_is_not_being_installed():
    """A photo-only run never asks the language model anything, so a dead key is worth saying and
    not worth stopping for."""
    probe = _cell("def xai_probe")

    assert "raise RuntimeError" in probe, "Yoklama hiç durdurmuyor"
    assert "⚠️" in probe, "Yoklama, durdurmadığı durumda uyarmıyor"


def test_the_probe_says_what_xai_answered_rather_than_guessing_why():
    """A 400 can be a wrong key, a spent quota or a revoked one, and only the body knows which --
    the same rule the Civitai probe follows."""
    assert "xAI yanıtı" in _cell("def xai_probe"), \
        "Yoklama xAI'ın kendi cevabını basmıyor"


def test_the_key_is_trimmed_where_it_is_read():
    """The paste is what carries the newline, so the value is cleaned at the point it is pasted --
    before the probe uses it and before it is handed to the app."""
    assert 'XAI_API_KEY = (userdata.get("XAI_API_KEY") or "").strip()' in _source(), \
        "Secret'tan okunan anahtar kırpılmıyor"
```

- [ ] **Step 3: Altısının da düştüğünü gör**

Run: `python -m pytest queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py -q`
Expected: FAIL ×6. `_cell(...)` boş dönüyor ya da aranan metin defterde yok — hiçbiri
`NameError`/`SyntaxError` gibi bir yazım hatasından düşmemeli.

---

### Task 3: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Tam takımı koş**

Run: `python -m pytest queen-editor/backend/tests -q`
Expected: 584 geçen + 8 düşen. Düşenlerin adları Task 1 ve 2'de yazılanların aynısı.

- [ ] **Step 2: Frontend'e dokunulmadığını doğrula**

Run: `git status --short`
Expected: yalnız iki test dosyası değişmiş; `app.ipynb`, `client.py`, `frontend/` temiz.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): pin what a dead xAI key should cost, before fixing it

THESE EIGHT TESTS FAIL ON PURPOSE. The fix is the next commit.

Two run the client: a key pasted with a trailing newline must not reach the
Authorization header carrying it, and a key of nothing but spaces must count
as no key rather than slip past the sentence written for a missing one.

Six read the notebook: the xAI key is the only outside thing it never probes,
so a dead key surfaces after the install and a batch of photos instead of in
the first second. They pin that the probe exists, runs in CONFIG, stops a run
that is installing video, only warns when it is not, prints xAI's own answer
rather than a guessed cause, and that the key is trimmed where it is read.

Tests come in their own commit from now on: written in the same breath as the
code, a test inherits the code's blind spots -- which is how a suite of 584
kept missing bugs at the seams.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** A1→Task 1 birinci test · A2→Task 1 ikinci test · B1, B2, B3, B4, B5, B6→Task 2'nin
altı testi · spec'in istediği "tek hücreyi veren yardımcı"→Task 2 Step 1. Spec'te olup planda
olmayan vaka yok.

**Ad tutarlılığı:** Testlerin beklediği isimler — `xai_probe`, `fatal=INSTALL_VIDEO`, `"xAI yanıtı"`,
`XAI_API_KEY = (userdata.get("XAI_API_KEY") or "").strip()` — bir sonraki döngünün uyması gereken
sözleşme. Implementasyon spec'i bunları veri olarak alır, yeniden karar vermez.

**Yakalanan tuzak:** yoklama CONFIG hücresinde, `log()` ise yardımcılar hücresinde tanımlı ve o
CONFIG'den sonra çalışıyor. Yoklama `log()` kullanamaz; uyarısı düz `print` olmak zorunda. B4 bu
yüzden `"WARN"` değil `"⚠️"` arıyor.

**Bilerek zayıf:** altı defter testi metin okuyor, davranış çalıştırmıyor. Yoklamanın gerçekten
işlediğini yalnız kullanıcının Colab turu söyleyebilir; bu testlerin işi, yoklamanın sessizce
kaldırılmasını ya da ağır indirmeden sonraya kaydırılmasını engellemek.