"""The notebook's custom node install, run rather than read.

It was a loop in the ComfyUI cell until madde 314, where no test could run it. The cell said 6 dk 2 sn
on the user's run, and 3 dk 13 sn of that was Impact-Pack. git and pip are the one thing faked -- a
clone lands the files the test hands it, a pip install is remembered by the requirement lines it was
given -- and the folders are real.
"""
import importlib
import os
import re

import pytest

IMPACT = "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"
DASIWA = "https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes.git"
MATH = "https://github.com/evanspearman/ComfyMath.git"

SAM2 = "git+https://github.com/facebookresearch/sam2"

# The two lists as they stood on 2026-09-23, word for word.
IMPACT_REQUIREMENTS = """segment-anything
scikit-image
piexif
transformers
opencv-python-headless
scipy
numpy
dill
matplotlib
git+https://github.com/facebookresearch/sam2
"""
DASIWA_REQUIREMENTS = """torch
nvidia-vfx
Pillow
numpy
transformers>=4.45.0
accelerate
psutil>=5.9
av>=18.0
"""


@pytest.fixture
def nodes():
    """The module. Imported here rather than at the top: a module that is not there yet fails each
    test on its own instead of the whole file."""
    return importlib.import_module("colab.nodes")


def _github(monkeypatch, nodes, repos):
    """git and pip, faked. A clone lands the files `repos` holds for its address -- {url: {name:
    text}} -- in the folder the command ends with; a pip install is remembered by the requirement
    lines of the file after -r, read the moment it runs. Every command is remembered too."""
    commands, installed = [], []

    def run(cmd, label, cwd=None, timeout=3600):
        parts = cmd.split() if isinstance(cmd, str) else list(cmd)
        commands.append(parts)
        if parts[:2] == ["git", "clone"]:
            target = os.path.join(cwd or os.getcwd(), parts[-1])
            os.makedirs(target, exist_ok=True)
            for name, text in repos[next(part for part in parts if part in repos)].items():
                with open(os.path.join(target, name), "w", encoding="utf-8") as handle:
                    handle.write(text)
        elif "pip" in parts:
            with open(parts[parts.index("-r") + 1], encoding="utf-8") as handle:
                installed.append([line.strip() for line in handle
                                  if line.strip() and not line.startswith("#")])
        return ""

    monkeypatch.setattr(nodes, "run", run)
    return commands, installed


def test_impact_pack_is_installed_without_sam2(nodes, monkeypatch, tmp_path):
    """sam2 has no ready package to take: pip fetches it from GitHub and builds it on the machine, and
    its build asks for torch, which pip sets up again -- CUDA libraries and all -- in a build
    environment of its own. Our graph loads SAM's first version, sam_vit_b, through
    segment-anything, and Impact-Pack imports sam2 only when it is installed (madde 314)."""
    _, installed = _github(monkeypatch, nodes, {IMPACT: {"requirements.txt": IMPACT_REQUIREMENTS}})

    nodes.install_node("ComfyUI-Impact-Pack", IMPACT, str(tmp_path))

    assert installed == [[line for line in IMPACT_REQUIREMENTS.split() if line != SAM2]], \
        f"Impact-Pack'in listesi böyle kurulmadı: {installed}"


def test_the_console_says_sam2_was_left_out(nodes, monkeypatch, tmp_path, capsys):
    """ComfyUI's own log says SAM2 is unavailable; whoever reads that finds why in the notebook's
    output."""
    _github(monkeypatch, nodes, {IMPACT: {"requirements.txt": IMPACT_REQUIREMENTS}})

    nodes.install_node("ComfyUI-Impact-Pack", IMPACT, str(tmp_path))

    lines = capsys.readouterr().out.splitlines()
    assert any("ComfyUI-Impact-Pack" in line and "sam2" in line for line in lines), \
        "Konsol sam2'nin atlandığını söylemiyor:\n" + "\n".join(lines)


def test_every_other_list_is_installed_whole(nodes, monkeypatch, tmp_path):
    """The skip is one line of one list, not a rule about heavy packages: DaSiWa's list names torch,
    and H3 runs on everything in it."""
    _, installed = _github(monkeypatch, nodes, {DASIWA: {"requirements.txt": DASIWA_REQUIREMENTS}})

    nodes.install_node("ComfyUI-DaSiWa-Nodes", DASIWA, str(tmp_path))

    assert installed == [DASIWA_REQUIREMENTS.split()], f"DaSiWa'nın listesi eksik kuruldu: {installed}"


def test_a_node_without_a_requirements_file_calls_no_pip(nodes, monkeypatch, tmp_path):
    commands, installed = _github(monkeypatch, nodes, {MATH: {"__init__.py": ""}})

    nodes.install_node("ComfyMath", MATH, str(tmp_path))

    assert installed == [] and len(commands) == 1, \
        f"Liste dosyası olmayan node'a pip çağrıldı: {commands}"


def test_a_node_already_in_place_is_left_alone(nodes, monkeypatch, tmp_path, capsys):
    """Run all twice in one session and the second pass clones nothing."""
    (tmp_path / "ComfyMath").mkdir()
    (tmp_path / "ComfyMath" / "__init__.py").write_text("")
    commands, _ = _github(monkeypatch, nodes, {MATH: {"__init__.py": ""}})

    nodes.install_node("ComfyMath", MATH, str(tmp_path))

    assert commands == [], f"Yerinde duran node yeniden kuruldu: {commands}"
    assert "zaten var" in capsys.readouterr().out, "Konsol node'un yerinde olduğunu söylemedi"


def test_a_clone_that_leaves_nothing_stops_the_run(nodes, monkeypatch, tmp_path):
    """An empty folder is a node ComfyUI would start without, and every graph naming it would fail far
    from here. The run stops at the clone instead, and says which node."""
    _github(monkeypatch, nodes, {MATH: {}})

    with pytest.raises(RuntimeError) as failure:
        nodes.install_node("ComfyMath", MATH, str(tmp_path))

    assert "ComfyMath" in str(failure.value), f"Hata hangi node olduğunu söylemiyor: {failure.value}"


def test_a_node_is_cloned_shallow_with_its_submodules_into_its_own_folder(
        nodes, monkeypatch, tmp_path, capsys):
    """Only the latest tree is needed, and some packs carry submodules. The line a node starts with
    carries the time, so the gap to the next one is how long the node took: that is how Impact-Pack's
    3 dk 13 sn was found (madde 314)."""
    commands, _ = _github(monkeypatch, nodes, {MATH: {"__init__.py": ""}})

    nodes.install_node("ComfyMath", MATH, str(tmp_path))

    clone = commands[0]
    assert clone[:2] == ["git", "clone"], f"İlk komut klon değil: {clone}"
    assert "--recurse-submodules" in clone and "--depth" in clone \
        and clone[clone.index("--depth") + 1] == "1", f"Klon sığ ya da alt modüllü değil: {clone}"
    assert (tmp_path / "ComfyMath" / "__init__.py").exists(), "Node kendi adlı klasörüne klonlanmadı"
    assert re.search(r"\[\d\d:\d\d:\d\d\] ComfyMath", capsys.readouterr().out), \
        "Konsol node'un başladığını saatle yazmıyor"
