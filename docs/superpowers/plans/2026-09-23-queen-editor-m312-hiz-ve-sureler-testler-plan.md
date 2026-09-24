# Madde 312 — Yüksek hız, indirme özeti ve hücre süreleri, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** İndiricinin yüksek hız ayarıyla alındığını, indirmelerin satır verdiğini, özetin tabloyu
bastığını, her hücrenin süresiyle bittiğini ve link satırının süresini söylediğini anlatan on beş test —
kırmızı.

**Yaklaşım:** `colab/downloads.py` 310'un sahteleriyle koşularak sınanıyor. Defterin indirme hücresi
okunuyor. Sayaç CONFIG'den başlığıyla kesilip IPython'un olay yöneticisi ve saat sahteyken
çalıştırılıyor.

**Araçlar:** pytest (`monkeypatch`, `tmp_path`, `capsys`).

**Spec:** [m312 test turu](../specs/2026-09-23-queen-editor-m312-hiz-ve-sureler-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod ve defter değişmiyor.

**Arayüz — uygulama turunun vereceği:**
- `hf_fetch`, `fetch`, `civitai_fetch` → `(etiket, bu koşuda inen bayt, saniye)`, yerinde duran dosya
  için `None`.
- `colab.downloads.download_summary(rows)`; `None` satırları atlıyor.
- CONFIG `# === Cell timer ===` ile başlıyor; bölüm yalnız `time` ve `IPython.get_ipython`'u
  kullanıyor, `cell_elapsed()`'i tanımlıyor, `pre_run_cell` / `post_run_cell` kancalarını takıyor.
- Modeller hücresinde `landed = []`, üç döngü `landed.append(…)`, sonda `download_summary(landed)`.
- Flask hücresinde `cell_elapsed()` ve `hazır` aynı satırda, `🔗 Queen Editor`'dan önce.

---

## Görev 1: İndirme testleri

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_colab_downloads.py` — sonuna.

- [ ] **Adım 1: Yedi test.**

```python
def test_hugging_face_s_downloader_is_taken_in_high_performance_mode(downloads, monkeypatch, tmp_path):
    """HF_XET_HIGH_PERFORMANCE has hf_xet try to fill the machine's bandwidth and use every CPU core
    (madde 312). huggingface_hub reads its variables once, when it is imported, so the switch has to
    be on by the moment the downloader is taken from the library -- whatever the environment held."""
    monkeypatch.setenv("HF_XET_HIGH_PERFORMANCE", "0")
    _hub(monkeypatch, _safetensors())
    hub, seen = sys.modules["huggingface_hub"], []

    class Library:
        @property
        def hf_hub_download(self):
            seen.append(os.environ.get("HF_XET_HIGH_PERFORMANCE"))
            return hub.hf_hub_download

    monkeypatch.setitem(sys.modules, "huggingface_hub", Library())

    downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                       str(tmp_path), "taeh3.safetensors", "H3 TAE")

    assert seen == ["1"], f"HF'nin indiricisi yüksek hız ayarı kapalıyken alındı: {seen}"


def test_a_download_hands_back_its_row_for_the_summary(downloads, monkeypatch, tmp_path):
    """The models cell collects one row per file that came down and ends with a table of them
    (madde 312): the label, the bytes that came down and the seconds they took."""
    _hub(monkeypatch, _safetensors())

    row = downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                             str(tmp_path), "taeh3.safetensors", "H3 TAE")

    assert row and row[:2] == ("H3 TAE", len(_safetensors())), f"Satır bu inişi anlatmıyor: {row}"
    assert row[2] > 0, f"Satırda süre yok: {row}"


def test_a_file_already_in_place_stays_out_of_the_summary(downloads, monkeypatch, tmp_path, capsys):
    """The table is this run's downloads: a file that was already there came down in an earlier one."""
    _hub(monkeypatch, _safetensors())
    _transfer(monkeypatch, downloads, b"")
    (tmp_path / "old.safetensors").write_bytes(_safetensors())
    (tmp_path / "sam.pth").write_bytes(b"\0" * 1000)

    rows = [downloads.hf_fetch("r/old", "old.safetensors", str(tmp_path), "old.safetensors", "Eski"),
            downloads.fetch("https://dl.fbaipublicfiles.com/segment_anything/sam.pth", str(tmp_path),
                            "sam.pth", "SAM", parallel=True, floor=500),
            downloads.hf_fetch("r/new", "new.safetensors", str(tmp_path), "new.safetensors", "Yeni")]
    capsys.readouterr()
    downloads.download_summary(rows)

    table = capsys.readouterr().out
    assert "Yeni" in table, f"Tabloda inen dosya yok:\n{table}"
    assert "Eski" not in table and "SAM" not in table, f"Tabloda yerinde duran dosya var:\n{table}"


def test_a_resumed_download_s_row_counts_only_what_came_down_this_time(downloads, monkeypatch, tmp_path):
    """The row says what the line says: bytes the .part already held did not come down in this run."""
    (tmp_path / "sam.pth.part").write_bytes(b"\0" * 100)
    _transfer(monkeypatch, downloads, b"\0" * 900, append=True)

    row = downloads.fetch("https://dl.fbaipublicfiles.com/segment_anything/sam.pth", str(tmp_path),
                          "sam.pth", "SAM", parallel=True, floor=500)

    assert row and row[:2] == ("SAM", 900), f"Satır bu koşuda ineni saymıyor: {row}"


def test_a_civitai_file_hands_back_the_row_of_the_road_it_took(downloads, monkeypatch, tmp_path):
    """From the mirror or from Civitai, the file came down and is counted. The upload after a Civitai
    download has its own line and is not part of the row."""
    _mirror(monkeypatch, {"3314686/a.safetensors": _safetensors()})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    mirrored = downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "a.safetensors", "Aynadan", "")
    fell_back = downloads.civitai_fetch(MIRROR, 3228867, str(tmp_path), "b.safetensors", "Civitai'den",
                                        COOKIE)

    assert mirrored and mirrored[:2] == ("Aynadan", len(_safetensors())), \
        f"Aynadan inen dosyanın satırı yok: {mirrored}"
    assert fell_back and fell_back[:2] == ("Civitai'den", len(_safetensors())), \
        f"Civitai'den inen dosyanın satırı yok: {fell_back}"


def test_the_summary_lists_each_download_and_a_total(downloads, capsys):
    """One line per file that came down, and a Toplam line under them: the whole download's size, its
    seconds and the average speed -- "ortalama indirme hızını yazalım" (madde 312). The per-file lines
    say the same, scattered between the progress bars; the table is where they are read together."""
    downloads.download_summary([("Kısa", 60 * 2**20, 20.0), None, ("Uzun", 2 * 2**30, 100.0)])

    lines = capsys.readouterr().out.splitlines()
    expected = [("Kısa", "60.0MB", "20 sn", "3.0 MB/s"),
                ("Uzun", "2.0GB", "1 dk 40 sn", "20.5 MB/s"),
                ("Toplam", "2.1GB", "2 dk 0 sn", "17.6 MB/s")]
    found = [next((i for i, line in enumerate(lines) if all(part in line for part in row)), None)
             for row in expected]

    assert any("İndirme özeti" in line for line in lines), f"Tablonun başlığı yok: {lines}"
    assert None not in found and found == sorted(found), "Tablo böyle değil:\n" + "\n".join(lines)


def test_a_run_with_nothing_downloaded_says_so(downloads, capsys):
    """Run all a second time in one session and every file is already there: a Toplam of nothing would
    read like a download that took no time."""
    downloads.download_summary([None, None])

    out = capsys.readouterr().out
    assert "inen dosya yok" in out and "Toplam" not in out, f"Özet boş koşuyu söylemiyor:\n{out}"
```

## Görev 2: İndirme hücresinin testleri

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

- [ ] **Adım 1: `test_huggingface_files_come_down_through_hf_fetch`** — tamamı:

```python
def test_huggingface_files_come_down_through_hf_fetch():
    """hf_fetch is the path around HF's bridge. Without hf_xet installed, huggingface_hub goes back to
    the bridge with nothing but a log line, so installing it is half of the rule. Each download's row
    is kept for the table the cell ends with (madde 312)."""
    assert re.search(r"for [^\n]+ in hf_jobs:\n\s+landed\.append\(hf_fetch\(",
                     _cell("# === Target folders ===")), \
        "HF dosyaları hf_fetch ile inmiyor ya da satırları tutulmuyor"
    assert re.search(r"pip install[^\n]*hf_xet", _source()), "Defter hf_xet'i kurmuyor"
```

- [ ] **Adım 2: `test_civitai_files_come_down_through_the_mirror`** — tamamı:

```python
def test_civitai_files_come_down_through_the_mirror():
    """Each gated file is looked up in the user's own Hugging Face repo first (madde 311), and its row
    is kept for the table (madde 312)."""
    assert re.search(r"for [^\n]+ in civitai_jobs:\n\s+landed\.append\(civitai_fetch\(HF_MIRROR, ",
                     _cell("# === Target folders ===")), \
        "Civitai dosyaları aynadan geçmiyor ya da satırları tutulmuyor"
```

- [ ] **Adım 3: Yeni test**, `test_huggingface_files_come_down_through_hf_fetch`'in altına:

```python
def test_the_models_cell_ends_with_the_download_summary():
    """The rows the downloads hand back are collected in one list and printed as a table once
    everything is down (madde 312)."""
    cell = _cell("# === Target folders ===")
    imported = [name for module, names in _imports_from_code() if module == "colab.downloads"
                for name in names]

    assert -1 < cell.find("landed = []") < cell.find("in hf_jobs:"), \
        "Satır listesi döngülerden önce açılmıyor"
    assert re.search(r"for [^\n]+ in open_jobs:\n\s+landed\.append\(fetch\(", cell), \
        "Açık adresli indirmelerin satırı tutulmuyor"
    assert cell.find("download_summary(landed)") > cell.find("in civitai_jobs:") > -1, \
        "Özet tablosu indirmelerden sonra basılmıyor"
    assert "download_summary" in imported, "Defter özet tablosunu klondan import etmiyor"
```

## Görev 3: Sayacın testleri

**Dosyalar:** Oluştur: `queen-editor/backend/tests/test_notebook_times_its_cells.py`

- [ ] **Adım 1: Dosyanın tamamı.**

```python
"""Every code cell ends with how long it took (madde 312).

The timer is the one piece of the notebook this suite runs. It has to be on before the clone -- the
Drive cell's time is one the user asked for -- so it cannot come from colab/, and it opens CONFIG,
the first code cell. Cut out from its heading to the next one, it runs here alone, with IPython's
event manager and the clock faked. The rest of this file reads the notebook, like the files next to
it.
"""
import json
import os
import sys
import time
import types

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")
HEADING = "# === Cell timer ==="


def _code_cells():
    """Every code cell's source, in the order Run all runs them."""
    with open(NOTEBOOK, encoding="utf-8") as handle:
        doc = json.load(handle)
    return ["".join(cell.get("source", "")) for cell in doc.get("cells", [])
            if cell.get("cell_type") == "code"]


def _cell(marker):
    return next((source for source in _code_cells() if marker in source), "")


def _timer_section():
    """The timer, from its heading to the next one: the part of CONFIG that runs here."""
    config = _cell("# === CONFIG ===")
    start = config.find(HEADING)
    if start == -1:
        return ""
    end = config.find("# ===", start + len(HEADING))
    return config[start:] if end == -1 else config[start:end]


class _Events:
    """IPython's event manager, as much of it as the timer touches."""

    def __init__(self):
        self.callbacks = {"pre_run_cell": [], "post_run_cell": []}

    def register(self, event, function):
        self.callbacks[event].append(function)

    def unregister(self, event, function):
        self.callbacks[event].remove(function)

    def trigger(self, event):
        for function in list(self.callbacks[event]):
            function(None)


def _run_timer(monkeypatch, events):
    """Runs the timer the way CONFIG does, against `events`. Hands back the clock it reads and the
    names it leaves in the notebook's namespace."""
    clock = [0.0]
    monkeypatch.setattr(time, "perf_counter", lambda: clock[0])
    monkeypatch.setitem(sys.modules, "IPython",
                        types.SimpleNamespace(get_ipython=lambda: types.SimpleNamespace(events=events)))
    names = {}
    exec(_timer_section(), names)
    return clock, names


def test_every_cell_ends_with_how_long_it_took(monkeypatch, capsys):
    """Under every cell, as the user asked -- "uzun süren başka cell'ler de var galiba" (madde 312).
    IPython calls one hook as a cell starts and one after it has printed everything else, so the line
    lands last."""
    assert _timer_section(), "CONFIG'de sayaç bölümü yok"
    events = _Events()
    clock, _names = _run_timer(monkeypatch, events)
    capsys.readouterr()

    for start, end in ((100.0, 210.4), (300.0, 308.2)):
        clock[0] = start
        events.trigger("pre_run_cell")
        clock[0] = end
        events.trigger("post_run_cell")

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2 and all(line.startswith("⏱") for line in lines), f"Satırlar: {lines}"
    assert lines[0].endswith("Hücre 1 dk 50 sn sürdü") and lines[1].endswith("Hücre 8 sn sürdü"), \
        f"Satırlar: {lines}"


def test_running_config_again_leaves_one_timer(monkeypatch, capsys):
    """CONFIG is the cell run again after a box is changed. Each run hooks the timer in anew; without
    the old hooks taken off, every cell would print its time twice."""
    events = _Events()
    _run_timer(monkeypatch, events)
    clock, _names = _run_timer(monkeypatch, events)
    capsys.readouterr()

    events.trigger("pre_run_cell")
    clock[0] = 5.0
    events.trigger("post_run_cell")

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1, f"Bir hücre süresini {len(lines)} kez yazdı: {lines}"


def test_the_timer_is_the_first_thing_the_notebook_runs():
    """The Drive cell's time holds the wait for the permission window, and the clone comes before the
    notebook's own code does: only the top of the first code cell runs before both -- and CONFIG's own
    time is counted whole."""
    assert _code_cells()[0].startswith(HEADING), "Sayaç ilk kod hücresinin başında değil"


def test_a_cell_can_ask_how_long_it_has_run_so_far(monkeypatch):
    """The last cell never ends -- it follows the server's log -- so its line would never come. It
    tells its time where the link appears instead, asking the timer (madde 312)."""
    events = _Events()
    clock, names = _run_timer(monkeypatch, events)

    clock[0] = 100.0
    events.trigger("pre_run_cell")
    clock[0] = 114.3

    assert "cell_elapsed" in names, "Sayaç hücrenin o ana kadarki süresini vermiyor"
    assert names["cell_elapsed"]() == "14 sn", f"Süre böyle okunmuyor: {names['cell_elapsed']()}"


def test_the_link_says_how_long_it_took():
    """The line reads "Link 14 sn'de hazır", right above the link (madde 312)."""
    flask = _cell("# === Start Flask")
    said = next((line for line in flask.splitlines() if "cell_elapsed()" in line), "")

    assert "hazır" in said, "Link hücresi süresini söylemiyor"
    assert -1 < flask.find(said) < flask.find("🔗 Queen Editor"), "Süre linkin üstünde değil"
```

## Görev 4: Koşu ve commit

- [ ] **Adım 1: Dört satırı koş.**

- [ ] **Adım 2: Kırmızı commit** — üç test dosyası, spec ve bu plan.

## Beklenen kırmızı

`queen-editor` pytest'inde on beş test: yedi indirme testi — ayar açılmıyor, fonksiyonlar satır
vermiyor, `download_summary` yok; üç indirme hücresi testi — döngüler satır tutmuyor; beş sayaç testi —
CONFIG'de sayaç yok. Başka hiçbir test kıpırdamaz; öteki üç satır yeşil.
