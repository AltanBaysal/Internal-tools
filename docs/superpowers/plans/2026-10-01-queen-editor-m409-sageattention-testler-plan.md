# Madde 409 — Fotoğraf üretimi SageAttention ile, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. **Commit yok** — sahibi
> değişikliği VS Code'un Changes'inde okur *(kullanıcı, 1 Ekim)*.

**Hedef:** Kutunun CONFIG'de işaretli geldiğini, kararın `colab/attention.py`'de koşarak tutulduğunu —
destekleyen kart kurar ve bayrağı alır, T4 ve kapalı kutu bugünkü gibi, başarısız kurulum bayraksız ve
pip'in sözleriyle — ve defterin bayrağı yalnız fonksiyondan aldığını anlatan testler.

**Yaklaşım:** Modül bir fixture'da içe aktarılıyor; `nvidia-smi` `subprocess.run` sahtelenerek, pip
modülün `run`'ı sahtelenerek cevaplanıyor. Defter okunuyor.

**Araçlar:** pytest (`monkeypatch`, `capsys`, `parametrize`).

**Spec:** [m409 test turu](../specs/2026-10-01-queen-editor-m409-sageattention-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod ve defter değişmiyor.
- `colab.attention` dosyanın başında değil fixture'da içe aktarılır.

**Arayüz — uygulama turunun vereceği:**
- `colab.attention.sage_attention_flags(wanted)` → `list[str]`: `["--use-sage-attention"]` ya da `[]`.
  Kartı `subprocess.run(["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"], …)`
  ile sorar, ve `stdout`'u `"<ad>, <compute capability>"` olarak okur; kurulumu modülün `run`'ı ile
  yapar *(`from colab.console import log, run`)*.
- Defter: CONFIG'de `SAGE_ATTENTION = True  #@param {type:"boolean"}`, `#@markdown ### SageAttention`
  başlığı altında; ComfyUI hücresinde `SAGE_FLAGS = sage_attention_flags(SAGE_ATTENTION)`; başlatma
  hücresinde `[...] + SAGE_FLAGS`; yardımcılar hücresinde `from colab.attention import sage_attention_flags`.

---

## Görev 1: `test_colab_attention.py`

**Dosya:** Oluştur: `queen-editor/backend/tests/test_colab_attention.py`

- [ ] **Adım 1: Dosya, altı testle** *(1'i üç kartla parametreli)*.

```python
"""SageAttention for ComfyUI, run rather than read (madde 409).

The owner's trial: a CONFIG box, ticked by default, that turns SageAttention on where the card can run
it and leaves every other card as it was. The card and pip are the two things faked -- nvidia-smi
answers with the line it prints on Colab, and a pip install is remembered by its command or fails with
pip's own words -- and the rest runs.
"""
import importlib
import subprocess

import pytest

A100 = ("NVIDIA A100-SXM4-40GB", "8.0")
T4 = ("Tesla T4", "7.5")

# A failed install, the way run hands it on: its label, pip's exit code and pip's last line.
PIP_FAILED = ("pip install sageattention: exit 1\n"
              "ERROR: No matching distribution found for sageattention==1.0.6")


@pytest.fixture
def attention():
    """The module. Imported here rather than at the top: a module that is not there yet fails each
    test on its own instead of the whole file, and test_requirements.py reads every top level import
    under backend/ as a package pip installs."""
    return importlib.import_module("colab.attention")


def _machine(monkeypatch, attention, card, pip_says=None):
    """nvidia-smi and pip, faked. nvidia-smi answers `--query-gpu=name,compute_cap
    --format=csv,noheader` the way it does on Colab, one line for the one card; pip is remembered by
    its command, or fails with `pip_says` the way run fails. Hands back what nvidia-smi was asked and
    what was run."""
    asked, commands = [], []

    def smi(cmd, *args, **kwargs):
        asked.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout=f"{card[0]}, {card[1]}\n", stderr="")

    def run(cmd, label, cwd=None, timeout=3600):
        commands.append(list(cmd))
        if pip_says:
            raise RuntimeError(pip_says)

    monkeypatch.setattr(subprocess, "run", smi)
    monkeypatch.setattr(attention, "run", run)
    return asked, commands


@pytest.mark.parametrize("card", [A100, ("NVIDIA L4", "8.9"), ("NVIDIA H100 80GB HBM3", "9.0")])
def test_a_card_that_runs_it_installs_the_pypi_build_and_gets_the_flag(attention, monkeypatch, card):
    """Compute capability 8.0 and up: Ampere and later, the cards SageAttention's kernels are written
    for. 1.0.6 is the build PyPI holds -- a small wheel that leaves torch alone; 2.x would be built
    from source on every fresh machine."""
    _, commands = _machine(monkeypatch, attention, card)

    flags = attention.sage_attention_flags(True)

    assert flags == ["--use-sage-attention"], \
        f"{card[0]}: ComfyUI SageAttention ile başlamıyor: {flags}"
    assert len(commands) == 1 and commands[0][:2] == ["pip", "install"] \
        and "sageattention==1.0.6" in commands[0], \
        f"{card[0]}: SageAttention böyle kurulmadı: {commands}"


def test_a_t4_installs_nothing_and_starts_comfyui_as_before(attention, monkeypatch):
    """The user's words (madde 409): "iki gpuda da çalışması lazım". A T4 is 7.5, below the cards the
    kernels are written for, so it starts the way it did before the box."""
    _, commands = _machine(monkeypatch, attention, T4)

    flags = attention.sage_attention_flags(True)

    assert flags == [], f"T4'te ComfyUI bayrakla başlıyor: {flags}"
    assert commands == [], f"T4'e bir şey kuruldu: {commands}"


def test_the_console_says_why_a_t4_is_left_out(attention, monkeypatch, capsys):
    """The box is ticked and nothing happens: the line under the cell names the card and what it
    measures at."""
    _machine(monkeypatch, attention, T4)

    attention.sage_attention_flags(True)

    out = capsys.readouterr().out
    assert "Tesla T4" in out and "7.5" in out, f"Konsol T4'ün neden atlandığını söylemiyor:\n{out}"


def test_an_unticked_box_asks_nothing_and_starts_comfyui_as_before(attention, monkeypatch, capsys):
    """Unticked is every card exactly as before madde 409: no question to the card, nothing installed.
    The console still says so -- the box comes ticked, and unticking it is a choice."""
    asked, commands = _machine(monkeypatch, attention, A100)

    flags = attention.sage_attention_flags(False)

    assert flags == [] and asked == [] and commands == [], \
        f"Kutu kapalıyken bir şey yapıldı: bayrak {flags}, nvidia-smi {asked}, komut {commands}"
    assert "SageAttention" in capsys.readouterr().out, \
        "Konsol SageAttention'ın kapalı olduğunu söylemiyor"


def test_a_failed_install_starts_comfyui_without_it(attention, monkeypatch):
    """Given the flag without the package, ComfyUI exits while it starts
    (comfy/ldm/modules/attention.py). So the flag goes on only after pip said yes, and a failed
    install costs the speed-up, never the session."""
    _machine(monkeypatch, attention, A100, pip_says=PIP_FAILED)

    flags = attention.sage_attention_flags(True)

    assert flags == [], f"Kurulum başarısızken ComfyUI bayrakla başlıyor: {flags}"


def test_a_failed_install_says_pip_s_own_words(attention, monkeypatch, capsys):
    """NOTEBOOK-STANDARD, section 2: the message is the command's own words, never a guessed cause."""
    _machine(monkeypatch, attention, A100, pip_says=PIP_FAILED)

    attention.sage_attention_flags(True)

    out = capsys.readouterr().out
    assert "No matching distribution found for sageattention==1.0.6" in out, \
        f"Konsol pip'in kendi sözlerini basmıyor:\n{out}"
```

## Görev 2: Defter testleri

**Dosya:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

- [ ] **Adım 1: `test_the_form_leaves_the_model_section_at_its_heading` model bölümlerini
  SageAttention'ın ayracında bitirir.** Docstring'in sonuna bir paragraf; `tail` şöyle kesilir:

```python
    drawn = _drawn(_cell("# === CONFIG ===")).splitlines()

    assert "#@markdown ---" in drawn, "Formda iki grubu ayıran çizgi yok"
    start = drawn.index("#@markdown ---")
    end = (drawn.index(SAGE_HEADING) - 1 if SAGE_HEADING in drawn else len(drawn))
    tail = drawn[start:end]
```

`SAGE_HEADING = "#@markdown ### SageAttention"` dosyanın başında, `SWITCH`'in altında.

- [ ] **Adım 2: Dosyanın sonuna beş test.**

```python
def test_config_has_a_sage_attention_box_ticked_by_default():
    """The owner's call (madde 409): "a100 check box olsun dediğin gibi defaultu açık olsun test edelim
    iyi çalışmıyorsa silicem". Unlike the producer boxes it costs no disk and starts nothing heavy, so
    it comes ticked."""
    assert 'SAGE_ATTENTION = True  #@param {type:"boolean"}' in _cell("# === CONFIG ==="), \
        "CONFIG'de işaretli gelen bir SageAttention kutusu yok"


def test_the_sage_attention_box_has_a_section_of_its_own_after_the_video_models():
    """Pinned by position, like the model sections: its own divider and heading under the video
    boxes, so it does not read as one more video model."""
    config = _cell("# === CONFIG ===")
    video_box = config.find("VIDEO_H3 = ")
    heading = config.find(SAGE_HEADING)
    divider = config.rfind("#@markdown ---", 0, heading)
    box = config.find("SAGE_ATTENTION = ")

    assert heading != -1, "SageAttention başlığı yok"
    assert -1 < video_box < divider < heading < box, \
        "SageAttention kutusu kendi ayracı ve başlığıyla video modellerinin altında değil"


def test_the_sage_attention_section_says_what_it_changes():
    """The box changes what comes out: a photo and a WAN video from the same seed come out very close
    rather than identical, and a T4 is left as it was. The owner reads that in the form, before the
    run -- the run cannot say it in time. The words stay free; the two facts cannot quietly go."""
    config = _cell("# === CONFIG ===")
    section = _drawn(config[config.find(SAGE_HEADING):config.find("SAGE_ATTENTION = ")])

    assert section, "SageAttention bölümü yok"
    for fact in ("T4", "WAN"):
        assert fact in section, f"SageAttention bölümü {fact}'ı anmıyor:\n{section}"


def test_comfyui_starts_with_the_flags_the_install_handed_back():
    """The flag is decided in colab/attention.py, where it runs under test: the ComfyUI cell asks for
    it with the box, and the start cell adds what came back."""
    imported = [name for module, names in _imports_from_code() if module == "colab.attention"
                for name in names]

    assert "SAGE_FLAGS = sage_attention_flags(SAGE_ATTENTION)" in \
        _cell("# === System deps + ComfyUI ==="), "ComfyUI hücresi bayrakları kutuyla istemiyor"
    assert '["python", "main.py", "--listen", "127.0.0.1", "--port", str(COMFY_PORT)] + SAGE_FLAGS' \
        in _cell("# === Start ComfyUI ==="), "ComfyUI dönen bayraklarla başlamıyor"
    assert "sage_attention_flags" in imported, "Defter sage_attention_flags'i klondan import etmiyor"


def test_the_notebook_never_names_the_flag_itself():
    """Given --use-sage-attention without the package, ComfyUI exits while it starts. The flag comes
    only from the function, which hands it over after pip said yes."""
    assert "--use-sage-attention" not in _source(), "Defter SageAttention bayrağını kendisi yazıyor"
```

## Görev 3: Koşu

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi. `queen-editor` pytest'inde kırmızı:
  `test_colab_attention.py`'nin sekizi *(fixture: `colab.attention` yok)*, ve dört defter testi —
  kutu, bölüm, bölümün metni, bayrakların yolu. Yeşil: `test_the_notebook_never_names_the_flag_itself`
  ve değişen `test_the_form_leaves_the_model_section_at_its_heading`. Öteki üç satır yeşil.
- [ ] **Adım 2: Commit yok.** Testler, spec ve bu plan çalışma ağacında kalır.
