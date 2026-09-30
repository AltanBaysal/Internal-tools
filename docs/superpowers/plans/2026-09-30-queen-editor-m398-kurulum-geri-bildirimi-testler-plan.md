# Madde 398 — Ses motorunun kurulum hücresi geri bildirim veriyor, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `run`'ın komutun çıktısını canlı, iki akışı sırasıyla ve satırbaşını koruyarak bastığını,
bugünkü hata ve süre kurallarını koruduğunu, ve ses motoru hücresinin her aşamayı söyleyip `pip`'i
susturmadığını anlatan yedi test — beşi kırmızı, ikisi bekçi.

**Yaklaşım:** `run`'ın testleri gerçek bir komut çalıştırıyor: `sys.executable -c` ile küçük bir Python
programı. Canlılık bir el sıkışmayla: program satırını yazıp bir işaret dosyasını bekliyor, test
dosyayı ancak satırı konsolda görünce yaratıyor. Defterin ses motoru hücresi okunuyor.

**Araçlar:** pytest (`monkeypatch`, `tmp_path`, `capsys`).

**Spec:** [m398 test turu](../specs/2026-09-30-queen-editor-m398-kurulum-geri-bildirimi-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod ve defter değişmiyor.
- Program satırlarını `print` ile yazdığında testler satırları `splitlines` ile bölüyor: Windows'ta
  `print` `\r\n` yazıyor. Satırbaşının kendisi sorulan testte program baytları doğrudan yazıyor.

**Arayüz — uygulama turunun vereceği:**
- `colab.console.run(cmd, label, cwd=None, timeout=3600)` — imza aynı; komutun stdout'u ve stderr'i
  geldiği anda, tek akış olarak `sys.stdout`'a basılıyor; `\r` korunuyor; Python bir komut flush
  etmese de satırı geliyor.
- Başarısız komut: `RuntimeError`, mesajı `<etiket>: exit <kod>` ve komutun son beş satırı. Süre
  aşımı: komut durduruluyor, `RuntimeError("<etiket>: timeout (<sn>s)")`.
- Defterin `# === Ses motoru — MMAudio kütüphanesi ===` hücresinde her `run(` satırının önünde bir
  `log(` satırı; `pip` komutunda `"-q"` yok.

---

## Görev 1: `test_colab_console.py`

**Dosya:** Oluştur: `queen-editor/backend/tests/test_colab_console.py`

- [ ] **Adım 1: Dosya, beş testle.**

```python
"""The notebook's shell call, run rather than read.

Every command the notebook's own code runs goes through run: the custom node installs, the curl and
aria2c downloads, and the sound engine's clone and pip install. Until madde 398 it held a command's
output until the command ended, and a pip install could sit silent for thirty minutes. The command
here is real -- a small Python program standing in for git, pip and curl -- and nothing reaches the
network.
"""
import importlib
import sys
import time

import pytest

# Writes a line without flushing, waits up to five seconds for the test to say it saw the line, and
# tells which way it went. pip is a Python program too, and into a pipe Python holds its lines in a
# buffer until it ends.
WAITS_FOR_ITS_LINE = """
import os, sys, time
print("first")
deadline = time.time() + 5
while not os.path.exists(sys.argv[1]) and time.time() < deadline:
    time.sleep(0.01)
print("seen" if os.path.exists(sys.argv[1]) else "not seen")
"""

# curl's progress line, redrawn in place.
PROGRESS = r"""
import sys
sys.stderr.buffer.write(b"10%\r50%\r100%\n")
sys.stderr.buffer.flush()
"""


@pytest.fixture
def console():
    """The module. Imported here rather than at the top: test_requirements.py reads every top level
    import under backend/ as a package pip installs, and colab/ is this repo's own folder."""
    return importlib.import_module("colab.console")


def _python(code, *args):
    return [sys.executable, "-c", code, *args]


class _Screen:
    """The cell's output, standing in for sys.stdout: it keeps what it is given, and creates the signal
    file once the command's first line has arrived."""

    def __init__(self, signal):
        self.text = ""
        self.signal = signal

    def write(self, text):
        self.text += text
        if "first" in self.text:
            self.signal.touch()
        return len(text)

    def flush(self):
        pass


def test_a_command_s_line_reaches_the_console_while_the_command_runs(console, monkeypatch, tmp_path):
    """The user's words (madde 398): "burda takıldı, output'ta bir şey de yok". A line that arrives
    only when the command ends cannot say where it hung."""
    screen = _Screen(tmp_path / "seen")
    monkeypatch.setattr(sys, "stdout", screen)

    console.run(_python(WAITS_FOR_ITS_LINE, str(tmp_path / "seen")), "canlı")

    assert screen.text.splitlines() == ["first", "seen"], \
        f"Komutun satırı komut sürerken konsola gelmedi: {screen.text!r}"


def test_the_command_s_error_stream_comes_to_the_same_console_in_order(console, capsys):
    """git, pip and curl write their progress and their errors to stderr, and where a command hangs is
    read from the order of the two streams."""
    console.run(_python("import sys\nprint('one')\nprint('two', file=sys.stderr)\nprint('three')"),
                "sıra")

    assert capsys.readouterr().out.splitlines() == ["one", "two", "three"], \
        "Komutun iki akışı konsola sırasıyla gelmedi"


def test_a_carriage_return_stays_a_carriage_return(console, capsys):
    """curl redraws its progress line with a carriage return, and Colab redraws it in place. Turned
    into a line break, a two-hour download prints a new line every second."""
    console.run(_python(PROGRESS), "ilerleme")

    assert "10%\r50%\r100%\n" in capsys.readouterr().out, \
        "Satırbaşı konsola satırbaşı olarak gelmedi"


def test_a_failed_command_says_its_own_last_lines(console):
    """NOTEBOOK-STANDARD, section 2: the error is the command's own words, never a guessed cause. The
    lines before the last few are on the console already."""
    with pytest.raises(RuntimeError) as failure:
        console.run(_python("import sys\nfor n in range(1, 9): print(f'line {n}')\nsys.exit(2)"),
                    "başarısız")

    message = str(failure.value)
    assert "başarısız" in message and "exit 2" in message, \
        f"Hata komutu ve çıkış kodunu söylemiyor: {message}"
    assert "line 8" in message and "line 1" not in message, \
        f"Hata komutun son satırlarını söylemiyor: {message}"


def test_a_command_past_its_time_is_stopped(console):
    """A hung command stops the run at its deadline instead of holding the cell for good."""
    start = time.monotonic()
    with pytest.raises(RuntimeError) as failure:
        console.run(_python("import time\ntime.sleep(60)"), "uyuyan", timeout=1)

    assert "uyuyan" in str(failure.value) and "timeout" in str(failure.value), \
        f"Hata komutu ve süreyi söylemiyor: {failure.value}"
    assert time.monotonic() - start < 30, "Süresi dolan komut durdurulmadı, bitmesi beklendi"
```

## Görev 2: Defter testleri

**Dosya:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

- [ ] **Adım 1: `test_the_freshly_installed_library_is_reachable_from_the_running_kernel`'in hemen
  altına.**

```python
def test_the_sound_engine_cell_says_each_stage_as_it_starts():
    """The user's words (madde 398): "burda takıldı, output'ta bir şey de yok". A line as each stage
    starts -- the clone, the pip install -- says which one the cell is in, and its time says since
    when."""
    cell = _cell("# === Ses motoru — MMAudio kütüphanesi ===")
    lines = [line.strip() for line in cell.splitlines() if line.strip()]
    stages = [i for i, line in enumerate(lines) if line.startswith("run(")]

    assert stages, "Ses motoru hücresi hiçbir komut çalıştırmıyor"
    for i in stages:
        assert lines[i - 1].startswith("log("), f"Bu aşama başlarken bir satır yazılmıyor: {lines[i]}"


def test_the_sound_engine_s_pip_is_not_silenced():
    """pip -q hides every line up to an error, and the install can take thirty minutes (madde 398)."""
    pip = re.search(r'run\(\["pip", "install"[^\]]*\]',
                    _cell("# === Ses motoru — MMAudio kütüphanesi ==="))

    assert pip, "Ses motoru hücresi MMAudio'yu pip ile kurmuyor"
    assert '"-q"' not in pip.group(0), f"Ses motorunun pip'i susturulmuş: {pip.group(0)}"
```

## Görev 3: Koşu ve kırmızı commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi — `queen-editor` pytest'te yalnız bu beş
  kırmızı: üç `run` testi *(konsol boş; ilki programın 5 sn'lik beklemesinden sonra)* ve iki defter
  testi. `test_a_failed_command_says_its_own_last_lines` ile
  `test_a_command_past_its_time_is_stopped` yeşil. Öteki üç satır yeşil.
- [ ] **Adım 2: Kırmızı commit** — iki test dosyası, spec ve bu plan:
  `test(queen-editor): Madde 398 red -- …`.
