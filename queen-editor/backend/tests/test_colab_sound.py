"""The sound engine's install, run rather than read (madde 438).

These were the notebook's two sound cells, and the suite could only check what they said: that the
clone was written down, that os.chdir(APP_DIR) was there. git and pip are faked here, MMAudio's own
weight download is a stand-in module, and the folders are real.
"""
import importlib
import os
import sys
import types

import pytest


@pytest.fixture
def sound():
    """The module. Imported here rather than at the top: a module that is not there yet fails each
    test on its own instead of the whole file."""
    return importlib.import_module("colab.sound")


def _commands(monkeypatch, sound):
    """console.run, faked. Each command is remembered with its folder and its deadline, and each line
    the console printed before it is remembered too, so a test can ask what was said as it started."""
    events = []

    def run(cmd, label, cwd=None, timeout=3600):
        events.append(("run", cmd, cwd, timeout))

    def log(msg, level="INFO"):
        events.append(("log", msg, level))

    monkeypatch.setattr(sound, "run", run)
    monkeypatch.setattr(sound, "log", log)
    return events


def test_mmaudio_is_cloned_then_installed_each_stage_said_as_it_starts(sound, monkeypatch, tmp_path):
    """The user's words (madde 398): "burda takıldı, output'ta bir şey de yok". A line as each stage
    starts says which one the cell is in. pip is not silenced: the install can take thirty minutes."""
    folder = str(tmp_path / "MMAudio")
    events = _commands(monkeypatch, sound)

    sound.install_mmaudio(folder)

    assert events == [
        ("log", "MMAudio klonlanıyor…", "INFO"),
        ("run", ["git", "clone", "--depth", "1", "https://github.com/hkchengrex/MMAudio.git", folder],
         None, 300),
        ("log", "MMAudio kuruluyor…", "INFO"),
        ("run", ["pip", "install", "-e", "."], folder, 1800),
        ("log", "MMAudio kütüphanesi kuruldu", "OK"),
    ], f"MMAudio böyle kurulmadı: {events}"


def test_an_mmaudio_already_cloned_is_only_installed(sound, monkeypatch, tmp_path):
    events = _commands(monkeypatch, sound)

    sound.install_mmaudio(str(tmp_path))

    assert [event[1] for event in events if event[0] == "run"] == [["pip", "install", "-e", "."]], \
        f"Yerinde duran MMAudio yeniden klonlandı: {events}"


class _Weights:
    """MMAudio's large_44k config, as much of it as the cell touches: where the download ran."""

    def __init__(self, fail=False):
        self.ran_in, self.fail = [], fail

    def download_if_needed(self):
        self.ran_in.append(os.getcwd())
        if self.fail:
            raise OSError("indirme düştü")


def _mmaudio(monkeypatch, weights):
    """MMAudio's package, faked in sys.modules; sys.path is the test's own copy."""
    monkeypatch.setitem(sys.modules, "mmaudio", types.ModuleType("mmaudio"))
    monkeypatch.setitem(sys.modules, "mmaudio.eval_utils",
                        types.SimpleNamespace(all_model_cfg={"large_44k": weights}))
    monkeypatch.setattr(sys, "path", list(sys.path))


def test_the_weights_land_where_the_app_will_look(sound, monkeypatch, tmp_path, capsys):
    """MMAudio resolves ./weights and ./ext_weights against the working directory, and the app is
    started from APP_DIR. Downloading them anywhere else means the app fetches them again."""
    weights, app, before = _Weights(), tmp_path / "queen-editor", os.getcwd()
    app.mkdir()
    _mmaudio(monkeypatch, weights)

    sound.fetch_mmaudio_weights(str(tmp_path / "MMAudio"), str(app))

    assert weights.ran_in == [str(app)], f"Ağırlıklar burada indi: {weights.ran_in}"
    assert os.getcwd() == before, "Çalışma klasörü geri dönmedi"
    assert f"MMAudio ağırlıkları hazır → {app}" in capsys.readouterr().out


def test_the_working_folder_comes_back_when_the_download_fails(sound, monkeypatch, tmp_path):
    app, before = tmp_path / "queen-editor", os.getcwd()
    app.mkdir()
    _mmaudio(monkeypatch, _Weights(fail=True))

    with pytest.raises(OSError):
        sound.fetch_mmaudio_weights(str(tmp_path / "MMAudio"), str(app))

    assert os.getcwd() == before, "Düşen indirmeden sonra çalışma klasörü geri dönmedi"


def test_the_freshly_installed_library_is_reachable_from_the_running_kernel(sound, monkeypatch,
                                                                            tmp_path):
    """`pip install -e .` registers the package with a .pth file, and .pth files are read when a
    Python process starts -- the Colab kernel started long before. Without the clone on sys.path the
    import dies with ModuleNotFoundError, which is what happened on 2026-08-13. Put there once: a
    second Run all adds nothing."""
    folder, app = str(tmp_path / "MMAudio"), tmp_path / "queen-editor"
    app.mkdir()
    _mmaudio(monkeypatch, _Weights())

    sound.fetch_mmaudio_weights(folder, str(app))
    sound.fetch_mmaudio_weights(folder, str(app))

    assert sys.path[0] == folder and sys.path.count(folder) == 1, \
        f"MMAudio'nun klonu yolda değil ya da birden çok kez: {sys.path[:3]}"


def test_no_app_folder_stops_the_cell_before_anything_downloads(sound, monkeypatch, tmp_path):
    weights = _Weights()
    _mmaudio(monkeypatch, weights)
    app = str(tmp_path / "yok")

    with pytest.raises(RuntimeError) as failure:
        sound.fetch_mmaudio_weights(str(tmp_path / "MMAudio"), app)

    assert str(failure.value) == f"❌ Uygulama klasörü yok: {app} — önce klon hücresini çalıştır"
    assert weights.ran_in == [], "Uygulama klasörü yokken ağırlıklar indi"
