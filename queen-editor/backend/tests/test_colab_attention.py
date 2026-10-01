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
