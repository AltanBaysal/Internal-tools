"""The notebook installs what the panel counts.

The app reads a producer's group off the disk and the notebook is what puts it there
(FOUNDATION 9). Nothing connects the two lists at runtime, so a file added to the group and
forgotten in the notebook would leave the panel saying "kurulu değil" for good, with nobody able to
see why. This test is that connection.

The notebook is read, never run: a Colab cell cannot execute here. What text can still answer is
exactly what matters -- is every counted file named, and is each group behind its own switch.
"""
import json
import os

from backend.features.producers.domain.model_groups import GROUPS

NOTEBOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app.ipynb")

# Which CONFIG checkbox owns which producer.
SWITCH = {"photo": "INSTALL_PHOTO", "video": "INSTALL_VIDEO", "audio": "INSTALL_AUDIO"}


def _source():
    """Every cell's source as one blob. Parsed rather than read raw: the file is JSON, so a raw
    read would be searching escaped quotes and line breaks instead of the code the cell runs."""
    with open(NOTEBOOK, encoding="utf-8") as handle:
        doc = json.load(handle)
    return "\n".join("".join(cell.get("source", "")) for cell in doc.get("cells", []))


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


def test_every_file_the_panel_counts_is_fetched_by_the_notebook():
    missing = [row["name"] for group in GROUPS.values() for row in group
               if row["name"] not in _source()]

    assert missing == [], f"Defter bu dosyaları indirmiyor: {missing}"


def test_every_producer_has_a_checkbox_of_its_own():
    """Colab draws a `#@param {type:"boolean"}` line as a checkbox: that is how the user picks.
    Default False, so nothing heavy starts by accident."""
    source = _source()

    for kind in GROUPS:
        assert f'{SWITCH[kind]} = False  #@param {{type:"boolean"}}' in source, \
            f"{kind}: CONFIG'de kapalı gelen bir onay kutusu yok"


def test_choosing_nothing_stops_the_notebook():
    """With no producer chosen the app opens and renders nothing -- a queued job waits forever.
    Hearing that in CONFIG costs a second; hearing it in the UI costs the whole setup run."""
    assert "assert INSTALL_PHOTO or INSTALL_VIDEO or INSTALL_AUDIO" in _source()


def test_the_cookie_is_only_demanded_by_the_groups_that_are_gated():
    """Only photo and video pull from Civitai. A sound-only run must not stop for a cookie it
    never sends. Pinned as the two lines together: `if INSTALL_PHOTO or INSTALL_VIDEO` appears
    elsewhere too, so the switch alone would prove nothing about the cookie."""
    assert ('if INSTALL_PHOTO or INSTALL_VIDEO:\n'
            '    assert len(COOKIE_VALUE or "") > 200') in _source()


def test_the_gated_files_are_fetched_the_way_that_works():
    """curl, not aria2c: Civitai redirects to its store, which answers 403 if the login cookie
    travels with the request. aria2c forwards it; curl drops it when the host changes."""
    source = _source()

    assert "civitai_probe" in source, "Ağır indirmeden önce kapılı erişim yoklanmalı"
    assert "civitai.red/api/download/models" in source


def test_an_unticked_group_costs_no_bytes():
    """The whole point of the checkboxes: a group's list is only reached through its own switch."""
    source = _source()

    for names, kind in ((("CIVITAI_PHOTO", "OPEN_PHOTO"), "photo"),
                        (("CIVITAI_VIDEO", "OPEN_VIDEO"), "video"),
                        (("OPEN_AUDIO",), "audio")):
        for name in names:
            assert f"{name} if {SWITCH[kind]} else []" in source, \
                f"{name} kendi anahtarının arkasında değil"


def test_the_disk_is_measured_before_the_download_starts():
    """All three together are ~54 GiB. Finding out the disk was too small halfway through leaves
    half-written files and no explanation."""
    assert "shutil.disk_usage" in _source()


def test_the_sound_box_installs_the_library_not_just_a_weight_file():
    """MMAudio runs inside the app's process, so `import mmaudio` has to work there -- a weight
    file with no library is not a producer. The base weights come with it: warming them here is
    what keeps the first sound job from stalling on a ~7 GiB download."""
    source = _source()

    assert "hkchengrex/MMAudio" in source, "Ses kutusu kütüphaneyi kurmuyor"
    assert "download_if_needed" in source, "MMAudio'nun kendi ağırlıkları öne alınmamış"


def test_the_sound_weights_land_where_the_app_will_look():
    """MMAudio resolves ./weights and ./ext_weights against the working directory, and the app is
    started from APP_DIR. Downloading them anywhere else means the app fetches them again."""
    assert "os.chdir(APP_DIR)" in _source()


def test_the_freshly_installed_library_is_reachable_from_the_running_kernel():
    """`pip install -e .` registers the package with a .pth file, and .pth files are read when a
    Python process starts -- the Colab kernel started long before. Without the clone on sys.path
    the very next line dies with ModuleNotFoundError, which is what happened on 2026-08-13."""
    assert "sys.path.insert(0, MMAUDIO_DIR)" in _source()


def test_the_app_is_told_where_the_notebook_installed():
    """The notebook owns the model tree now, so it is the side that names the path -- rather than
    both sides writing /content/ComfyUI and hoping they stay equal."""
    assert '"QE_COMFY_ROOT": COMFY_ROOT' in _source()


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
    assert "xAI yanıtı" in _cell("def xai_probe"), "Yoklama xAI'ın kendi cevabını basmıyor"


def test_the_key_is_trimmed_where_it_is_read():
    """The paste is what carries the newline, so the value is cleaned at the point it is pasted --
    before the probe uses it and before it is handed to the app."""
    assert 'XAI_API_KEY = (userdata.get("XAI_API_KEY") or "").strip()' in _source(), \
        "Secret'tan okunan anahtar kırpılmıyor"
