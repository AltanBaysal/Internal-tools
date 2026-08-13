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


def test_the_app_is_told_where_the_notebook_installed():
    """The notebook owns the model tree now, so it is the side that names the path -- rather than
    both sides writing /content/ComfyUI and hoping they stay equal."""
    assert '"QE_COMFY_ROOT": COMFY_ROOT' in _source()
