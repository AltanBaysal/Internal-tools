"""What the notebook's text has to say.

The notebook is the only thing that installs, configures and serves this app, and none of that
can run here -- a Colab cell does not execute in pytest. What text can still answer is whether
the notebook still says the things it must: every file the panel counts is named (FOUNDATION 9),
each producer sits behind its own switch, the outside world is probed before the heavy work,
and the tunnel is opened the way that measured fast.

The notebook is read, never run.
"""
import json
import os
import re

from backend.features.producers.domain.model_groups import GROUPS

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")

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


def _drawn(cell):
    """The part of a CONFIG cell Colab draws into the form: #@markdown lines only.

    A plain # comment never reaches the form, so a test reading the whole cell would pass on text
    the person ticking the box cannot see.
    """
    return "\n".join(line for line in cell.splitlines() if line.startswith("#@markdown"))


def test_the_notebook_carries_the_tool_s_own_name():
    """Colab shows a notebook by its file name alone -- the title inside it never reaches the tab.
    Two tools open at once are told apart by that name and nothing else, and Run all in the wrong
    tab clones the wrong repo and starts the wrong app. Read from the folder rather than written
    down, so renaming a tool carries the rule with it.
    """
    found = sorted(name for name in os.listdir(TOOL) if name.endswith(".ipynb"))

    assert found == [os.path.basename(TOOL).replace("-", "") + ".ipynb"], \
        f"Defterin adı aracının adı değil: {found}"


def test_every_file_the_panel_counts_is_fetched_by_the_notebook():
    """A row naming a kind rather than a file is skipped here and covered by
    test_the_notebook_offers_every_photo_model instead, which pins all three checkpoints by name and
    by version id -- a tighter guard than this one, not a looser one."""
    missing = [row["name"] for group in GROUPS.values() for row in group
               if "name" in row and row["name"] not in _source()]

    assert missing == [], f"Defter bu dosyaları indirmiyor: {missing}"


def test_the_notebook_installs_the_encoder_the_graph_asks_for():
    """ComfyUI validates every node it is sent, so a graph naming an encoder the notebook never
    installed does not degrade -- it fails every single render. The graph and the notebook are one
    thing, and this is the seam where that is checked before Colab charges an install for it."""
    assert "pamparamm/ComfyUI-ppm" in _source(), \
        "Grafiğin istediği kodlayıcıyı veren paket defterde kurulmuyor"


def test_the_notebook_says_how_many_custom_nodes_it_installs():
    """The count sits in two places -- the list itself and the heading above it -- and a copy is what
    goes stale. Read from the list rather than written down here, so adding a node fails this test
    until the sentence a reader sees agrees with what the cell actually clones."""
    listed = _cell("CUSTOM_NODES = [").count('.git"),')
    heading = _cell("## ComfyUI + Custom Node")

    assert listed, "CUSTOM_NODES listesi okunamadı"
    assert f"({listed})" in heading, f"Başlıktaki sayı listeyle uyuşmuyor: {listed} satır"


def test_the_intro_agrees_with_the_custom_node_list():
    """The count lives in three places -- the list, the heading over it, and the sentence that opens
    the notebook. The third went stale when the list grew to 20 (Madde 138) because the test above
    only ever read the heading."""
    listed = _cell("CUSTOM_NODES = [").count('.git"),')
    intro = _cell("# Queen Editor — Colab kurulumu")

    assert listed, "CUSTOM_NODES listesi okunamadı"
    assert f"({listed} custom node)" in intro, \
        f"Giriş hücresindeki sayı listeyle uyuşmuyor: {listed} satır"


def test_every_producer_has_a_checkbox_of_its_own():
    """Colab draws a `#@param {type:"boolean"}` line as a checkbox: that is how the user picks.
    Default False, so nothing heavy starts by accident."""
    source = _source()

    for kind in GROUPS:
        assert f'{SWITCH[kind]} = False  #@param {{type:"boolean"}}' in source, \
            f"{kind}: CONFIG'de kapalı gelen bir onay kutusu yok"


def test_the_form_names_the_producer_boxes_too():
    """Labelling one block of boxes and leaving the other bare would read as if the bare one
    belonged to the labelled one -- the same confusion, moved up a line."""
    config = _cell("# === CONFIG ===")
    heading = config.find("#@markdown ### Üreticiler")
    first_box = config.find("INSTALL_PHOTO = ")

    assert heading != -1, "Üreticiler başlığı yok"
    assert heading < first_box, "Başlık kutuların önünde değil"


def test_the_form_separates_the_two_groups_of_boxes():
    """Colab draws #@param lines into the form and #@markdown text along with them, while a plain
    # comment never reaches it. The two blocks of boxes ran together there with nothing saying
    where one ended.

    Pinned by position rather than by wording: the words stay free to change, the structure cannot
    quietly go away.
    """
    config = _cell("# === CONFIG ===")
    divider = config.find("#@markdown ---")
    heading = config.find("#@markdown ### Fotoğraf modelleri")
    first_box = re.search(r"^PHOTO_\w+ = (?:True|False)  #@param", config, re.M)

    assert divider != -1, "Formda iki grubu ayıran çizgi yok"
    assert heading != -1, "Fotoğraf modelleri başlığı yok"
    assert first_box, "CONFIG'de tek bir model kutusu yok"
    assert divider < heading < first_box.start(), "Ayraç ve başlık kutuların önünde değil"


def test_the_form_leaves_the_model_section_at_its_heading():
    """Every sentence that stood under this heading was a copy of something the run already says:
    the guard below prints the pick-at-least-one rule in Turkish, the boxes show for themselves
    that they come empty, and the download cell prints the disk cost computed from what was
    actually ticked. A copy is the thing that goes stale, so the form keeps the heading and the run
    keeps the sentences.

    Measured by what is left rather than by what is gone: a test naming the removed lines would
    stay green on a form that grew three different ones.
    """
    drawn = _drawn(_cell("# === CONFIG ===")).splitlines()

    assert "#@markdown ---" in drawn, "Formda iki grubu ayıran çizgi yok"
    tail = drawn[drawn.index("#@markdown ---"):]

    assert tail == ["#@markdown ---", "#@markdown ### Fotoğraf modelleri"], \
        f"Model bölümü başlıktan ibaret değil: {tail}"


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


def test_every_photo_model_has_a_checkbox_of_its_own():
    """The switch has to sit in CONFIG -- Colab draws #@param only where it is written -- and the row
    saying what to fetch sits in the model cell. Two lists, and a name in one but not the other is
    either a box that downloads nothing or a download nobody can turn off.

    Every checkpoint is here, the group's own included: which models come down is the user's pick.
    """
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", _cell("# === CONFIG ==="), re.M)
    rows = re.findall(r"^\s*\((PHOTO_\w+),", _cell("PHOTO_MODELS = ["), re.M)

    assert boxes, "CONFIG'de tek bir model kutusu yok"
    assert sorted(boxes) == sorted(rows), f"Kutular {sorted(boxes)}, satırlar {sorted(rows)}"


def test_every_photo_model_comes_switched_off():
    """Photo ticked draws the boxes empty and picks nothing heavy for anyone.

    The first assertion is not spare: with no PHOTO_* line at all the second one holds for free.
    """
    config = _cell("# === CONFIG ===")
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", config, re.M)
    on = re.findall(r"^(PHOTO_\w+) = True  #@param", config, re.M)

    assert boxes, "CONFIG'de tek bir model kutusu yok"
    assert on == [], f"Model açık geliyor: {on}"


def test_choosing_photo_without_a_model_stops_the_notebook():
    """Photo ticked and every model box empty means a renderer with nothing to render with. Asked in
    CONFIG like every other gate: a second here beats ten minutes after ComfyUI's install.

    The expected line is built from the boxes rather than written down, so a model added without
    being added to the guard fails here instead of silently reopening the hole.
    """
    config = _cell("# === CONFIG ===")
    boxes = re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", config, re.M)
    guard = "assert not INSTALL_PHOTO or " + " or ".join(boxes)

    assert boxes, "CONFIG'de tek bir model kutusu yok"
    assert guard in config, f"Beklenen kontrol yok:\n{guard}"


def test_an_unticked_photo_model_costs_no_bytes():
    """The rule the three producer boxes already follow, one level down: a row is reached only
    through its own switch."""
    assert "in PHOTO_MODELS if on" in _cell("PHOTO_MODELS = ["), \
        "PHOTO_MODELS satırları kendi anahtarıyla süzülmüyor"


def test_the_photo_estimate_counts_only_what_the_group_always_takes():
    """The base is the four files the graph's branches read -- the lora, the upscaler, the detector,
    the SAM. The checkpoints are the user's pick, so counting one of them into the base would warn a
    single-model run about disk it was never going to use."""
    assert "(INSTALL_PHOTO, PHOTO_GIB," in _cell("SIZES = ["), \
        "SIZES foto için hâlâ sabit bir sayı taşıyor"
    assert "PHOTO_GIB = 2 +" in _cell("PHOTO_GIB ="), \
        "Disk tabanı hâlâ bir checkpoint'in payını taşıyor"


def test_the_notebook_offers_every_photo_model():
    """Named rather than derived: this is the one place saying which models the notebook can fetch,
    so a silent edit cannot quietly change what a run is able to install. Reading the list itself
    would only say that the list contains what it contains."""
    cell = _cell("PHOTO_MODELS = [")

    for name in ("nova3DCGXL_ilV90.safetensors", "novaOrangeXL_rexV10.safetensors",
                 "novaAnimeXL_ilV190.safetensors"):
        assert name in cell, f"Defter bu modeli indirmiyor: {name}"
    for version in ("2744564", "2945776", "2940478"):
        assert version in cell, f"Civitai version id defterde yok: {version}"


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


def test_the_tunnel_is_opened_over_tcp_rather_than_quic():
    """cloudflared speaks QUIC by default, and QUIC rides on UDP. Colab's network throttles UDP and
    leaves TCP alone: on 2026-08-24 the same photo took 17.74 s over the default tunnel and 0.18 s
    over one started with this flag -- same machine, same minute, ninety times apart. Without it a
    gallery of 81 photos is unusable and nothing in the app explains why."""
    flask_cell = _cell("# === Start Flask")

    assert '"--protocol", "http2"' in flask_cell, \
        "cloudflared varsayılan QUIC ile açılıyor — Colab'ın ağı UDP'yi kısıyor"


def test_the_protocol_flag_says_what_it_is_standing_in_for():
    """One word in an argument list, and nothing about it says a default was overruled. A reader
    who cannot see what it replaced is a reader who deletes it as noise -- and the gallery goes
    ninety times slower with no error anywhere. The reason has to travel next to the flag."""
    flask_cell = _cell("# === Start Flask")

    assert "QUIC" in flask_cell, \
        "Bayrağın neyin yerine geçtiği yazılmamış — sebebi olmayan bayrak silinir"
