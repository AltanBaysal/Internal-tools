"""What the notebook's text has to say.

The notebook is the only thing that installs, configures and serves this app, and none of that
can run here -- a Colab cell does not execute in pytest. What text can still answer is whether
the notebook still says the things it must: every file the panel counts is named (FOUNDATION 9),
each producer sits behind its own switch, the outside world is probed before the heavy work,
and the tunnel is opened the way that measured fast.

The notebook is read, never run.

The download machinery left the notebook for colab/ in madde 310, and the custom node install in
madde 314; both are run in test_colab_*.py. What stays here is the seam: the notebook imports names
the modules give, finds them in its clone, and defines none of them again.
"""
import importlib
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


def _catalog():
    """The app's models and loras. Imported where it is used rather than at the top: a module that
    is not there yet would fail collection and take every other question in this file down with
    it."""
    from backend.features.photo_generation.domain.catalog import LORAS, MODELS
    return MODELS, LORAS


def _boxes():
    """Every PHOTO_* checkbox CONFIG draws -- models and loras alike."""
    return re.findall(r"^(PHOTO_\w+) = (?:True|False)  #@param", _cell("# === CONFIG ==="), re.M)


def _rows(listing):
    """The switches the rows of one list are filed under, e.g. PHOTO_MODELS."""
    return re.findall(r"^\s*\((PHOTO_\w+),", _cell(f"{listing} = ["), re.M)


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


def _imports_from_code():
    """(module, names) for every line the notebook imports its own code with."""
    return [(module, [name.strip() for name in names.split(",")])
            for module, names in re.findall(r"^from (colab\.\w+) import ([\w, ]+)$", _source(), re.M)]


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
    test_the_notebook_offers_every_checkpoint_a_model_asks_for instead, which pins the checkpoint by
    name and by version id -- a tighter guard than this one, not a looser one.

    Asked by the file's own name: the video group names H3's files the way the graph loads them,
    MiniMaxH3/ included, and the notebook names the file itself and puts it in that folder."""
    source = _source()
    missing = [row["name"] for group in GROUPS.values() for row in group
               if "name" in row and os.path.basename(row["name"]) not in source]

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


def test_the_notebook_installs_its_nodes_through_install_node():
    """The loop left the ComfyUI cell for colab/ in madde 314, where it runs under test. The list
    stays in the notebook, like the download lists."""
    imported = [name for module, names in _imports_from_code() if module == "colab.nodes"
                for name in names]

    assert re.search(r"for name, url in CUSTOM_NODES:\n\s+install_node\(name, url, ",
                     _cell("CUSTOM_NODES = [")), "Defter node'ları install_node ile kurmuyor"
    assert "install_node" in imported, "Defter install_node'u klondan import etmiyor"


def test_the_notebook_starts_comfyui_through_start_comfy():
    """The start left the ComfyUI cell for colab/ in madde 433, where it runs under test: the old one
    gone before the new one starts, and hazır only for the process the cell started."""
    imported = [name for module, names in _imports_from_code() if module == "colab.comfy"
                for name in names]

    assert "start_comfy(COMFY_ROOT, COMFY_PORT, COMFY_LOG)" in _cell("# === Start ComfyUI ==="), \
        "ComfyUI hücresi ComfyUI'yi start_comfy ile başlatmıyor"
    assert "start_comfy" in imported, "Defter start_comfy'yi klondan import etmiyor"


def test_every_producer_has_a_checkbox_of_its_own():
    """Colab draws a `#@param {type:"boolean"}` line as a checkbox: that is how the user picks.
    Default False, so nothing heavy starts by accident. Video's box installs H3, the one video model
    since madde 435."""
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
        f"Model bölümleri başlıklarından ibaret değil: {tail}"


def test_choosing_nothing_stops_the_notebook():
    """With no producer chosen the app opens and renders nothing -- a queued job waits forever.
    Hearing that in CONFIG costs a second; hearing it in the UI costs the whole setup run."""
    assert "assert INSTALL_PHOTO or INSTALL_VIDEO or INSTALL_AUDIO" in _source()


def test_civitai_files_come_down_through_the_mirror():
    """Each gated file is looked up in the user's own Hugging Face repo first (madde 311), and its row
    is kept for the table (madde 312)."""
    assert re.search(r"for [^\n]+ in civitai_jobs:\n\s+landed\.append\(civitai_fetch\(HF_MIRROR, ",
                     _cell("# === Target folders ===")), \
        "Civitai dosyaları aynadan geçmiyor ya da satırları tutulmuyor"


def test_the_mirror_is_named_once_in_config():
    """A repo is named where the Drive folder is: in CONFIG, once."""
    assert re.search(r'^HF_MIRROR\s*=\s*"[\w.-]+/[\w.-]+"', _cell("# === CONFIG ==="), re.M), \
        "Ayna CONFIG'de adlanmıyor"
    assert len(re.findall(r"^HF_MIRROR\s*=", _source(), re.M)) == 1, \
        "Ayna birden çok yerde adlanıyor"


def test_config_does_not_demand_the_cookie():
    """Only a file that falls back to Civitai needs the cookie (madde 311). Demanded in CONFIG, it
    would stop a run whose files are all mirrored, for nothing."""
    assert "len(COOKIE_VALUE" not in _cell("# === CONFIG ==="), "CONFIG çerezi hâlâ baştan istiyor"


def test_an_unticked_group_costs_no_bytes():
    """The whole point of the checkboxes: a group's list is only reached through its own switch."""
    source = _source()

    for names, switch in ((("CIVITAI_PHOTO", "HF_PHOTO"), SWITCH["photo"]),
                          (("CIVITAI_H3", "HF_H3"), SWITCH["video"]),
                          (("HF_AUDIO",), SWITCH["audio"])):
        for name in names:
            assert f"{name} if {switch} else []" in source, \
                f"{name} kendi anahtarının arkasında değil"


def test_every_model_the_app_knows_has_a_checkbox_of_its_own():
    """A model is written down twice on purpose: its name and its checkpoint in the app, because
    that is the side that patches the graph, and its version id and size in the notebook,
    because addresses live there (FOUNDATION 9). This is the seam that keeps the two halves naming
    the same models (madde 237).

    The switch has to sit in CONFIG -- Colab draws #@param only where it is written.
    """
    models, _loras = _catalog()
    known = sorted("PHOTO_" + model["id"].upper() for model in models)

    assert sorted(_rows("PHOTO_MODELS")) == known, \
        f"Model satırları {sorted(_rows('PHOTO_MODELS'))}, uygulamanın modelleri {known}"


def test_every_photo_box_is_a_model():
    """A box with no row downloads nothing; a row with no box cannot be turned off. And every box is
    a model: the lora files come with the photo group whatever was ticked, so a lora box would
    decide nothing about the disk -- Slime's old box went with the recipes (madde 237)."""
    rows = _rows("PHOTO_MODELS")

    assert rows, "Model satırı yok"
    assert sorted(_boxes()) == sorted(rows), f"Kutular {sorted(_boxes())}, satırlar {sorted(rows)}"


def test_the_disk_estimate_reads_the_chosen_checkpoints():
    """Pinned as the one name both the download list and the size sum read: two expressions
    deriving the same thing separately is how they come to disagree."""
    assert "CHOSEN_CHECKPOINTS" in _cell("PHOTO_MODELS = ["), \
        "Seçilen checkpoint'ler model satırlarından çıkarılmıyor"
    assert "CHOSEN_CHECKPOINTS" in _cell("PHOTO_GIB ="), \
        "Disk hesabı seçilen checkpoint'leri okumuyor"


def test_the_app_is_told_which_models_the_notebook_chose():
    """The disk cannot answer this: a checkpoint left from another run would be listed as if it had
    been ticked. Only the notebook knows what was ticked."""
    source = _source()

    assert '"QE_PHOTO_MODELS"' in source, "Defter seçilen modelleri uygulamaya geçirmiyor"
    assert '"QE_PHOTO_RECIPES"' not in source, "Defter hâlâ tarif kimlikleri geçiriyor"


def test_the_app_is_told_where_comfyui_writes_its_log():
    """When ComfyUI stops answering, its log is the only thing that knows why -- and it dies with
    the session. The app reads its tail into the error, so it has to know where the notebook
    sends it (madde 230)."""
    assert '"QE_COMFY_LOG"' in _source(), \
        "Defter ComfyUI log'unun yolunu uygulamaya geçirmiyor"


def test_every_photo_box_comes_switched_off():
    """Photo ticked draws the boxes empty and picks nothing heavy for anyone.

    The first assertion is not spare: with no PHOTO_* line at all the second one holds for free.
    """
    on = re.findall(r"^(PHOTO_\w+) = True  #@param", _cell("# === CONFIG ==="), re.M)

    assert _boxes(), "CONFIG'de tek bir fotoğraf kutusu yok"
    assert on == [], f"Kutu açık geliyor: {on}"


def test_choosing_photo_without_a_model_stops_the_notebook():
    """Photo ticked and every model box empty means a renderer with nothing to render with. A lora
    is not enough: it rides on a checkpoint. Asked in CONFIG like every other gate: a second here
    beats ten minutes after ComfyUI's install.

    The expected line is built from the model rows rather than written down, so a model added
    without being added to the guard fails here instead of silently reopening the hole.
    """
    models = _rows("PHOTO_MODELS")
    guard = "assert not INSTALL_PHOTO or " + " or ".join(models)

    assert models, "Model satırı yok"
    assert guard in _cell("# === CONFIG ==="), f"Beklenen kontrol yok:\n{guard}"


def test_an_unticked_model_costs_no_bytes():
    """The rule the three producer boxes already follow, one level down: a row is reached only
    through its own switch."""
    assert "in PHOTO_MODELS if on" in _cell("PHOTO_MODELS = ["), \
        "PHOTO_MODELS satırları kendi anahtarıyla süzülmüyor"


def test_the_photo_estimate_counts_only_what_the_group_always_takes():
    """The base is the files every photo run takes whatever was ticked -- both loras and the
    upscaler. The checkpoints come from the model boxes, so counting one of them into
    the base would warn a single-model run about disk it was never going to use."""
    assert "(INSTALL_PHOTO, PHOTO_GIB," in _cell("SIZES = ["), \
        "SIZES foto için hâlâ sabit bir sayı taşıyor"
    assert "PHOTO_GIB = 2 +" in _cell("PHOTO_GIB ="), \
        "Disk tabanı hâlâ bir checkpoint'in payını taşıyor"


def test_the_notebook_offers_every_checkpoint_a_model_asks_for():
    """Named rather than derived: this is the one place saying which files the notebook can fetch,
    so a silent edit cannot quietly change what a run is able to install. Reading the list itself
    would only say that the list contains what it contains."""
    cell = _cell("PHOTO_CHECKPOINTS = [")

    for filename, version in (("nova3DCGXL_ilV90.safetensors", "2744564"),
                              # madde 237: read from Civitai's own API in madde 222's trial.
                              ("DasiwaIllustriousAnime_epitaphecstasy.safetensors", "3012006")):
        assert filename in cell, f"Defter bu checkpoint'i indirmiyor: {filename}"
        assert version in cell, f"Civitai version id defterde yok: {version}"


def test_the_retired_nova_checkpoints_are_gone_from_the_notebook():
    """Nova Orange and Nova Anime left the recipe list (madde 226). A row left behind here would
    still be a box somebody could tick for 7 GiB that renders nothing the app offers."""
    source = _source()

    for leftover in ("novaOrangeXL_rexV10.safetensors", "novaAnimeXL_ilV190.safetensors",
                     "2945776", "2940478"):
        assert leftover not in source, f"Defterde kaldırılan Nova'dan iz kaldı: {leftover}"


def test_every_file_the_app_renders_with_is_one_the_notebook_can_fetch():
    """A model or a lora pointing at a file the notebook never downloads is a row that renders
    nothing -- and it would say so only after the install, as a missing-model error from ComfyUI.
    USNR is among the loras now, and it is the default: every frame that names none renders with
    it (madde 238)."""
    models, loras = _catalog()
    checkpoints = _cell("PHOTO_CHECKPOINTS = [")
    source = _source()

    for model in models:
        assert model["checkpoint"] in checkpoints, \
            f"{model['id']}: modelin checkpoint'i defterde yok — {model['checkpoint']}"
    for lora in loras:
        assert lora["lora"] in source, f"{lora['id']}: LoRA defterde yok — {lora['lora']}"


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


def test_the_app_is_told_where_the_notebook_installed():
    """The notebook owns the model tree now, so it is the side that names the path -- rather than
    both sides writing /content/ComfyUI and hoping they stay equal."""
    assert '"QE_COMFY_ROOT": COMFY_ROOT' in _source()


def test_the_deepseek_key_is_read_from_secrets_and_trimmed():
    """Madde 400: Queen AI writes H3's prompt. The secret is QueenAgent's own name, so the owner
    keeps one secret for both tools -- trimmed where it is pasted, because the paste is what carries
    the newline."""
    assert 'DEEPSEEK_API_KEY = (userdata.get("DEEPSEEK_API_KEY") or "").strip()' in _source(), \
        "DeepSeek anahtarı Secrets'tan kırpılarak okunmuyor"


def test_the_deepseek_key_travels_to_the_app():
    assert '"QE_DEEPSEEK_API_KEY": DEEPSEEK_API_KEY' in _cell("# === Start Flask"), \
        "Defter DeepSeek anahtarını uygulamaya geçirmiyor"


def test_the_setup_names_the_deepseek_secret():
    """Colab hands a secret only to the notebooks it was opened to, so the person setting up has to
    know its name."""
    assert "DEEPSEEK_API_KEY" in _cell("🔑 Secrets"), \
        "Kurulum anlatımı DeepSeek secret'ını saymıyor"


def test_the_notebook_fetches_motion_booster_by_its_version():
    """Named rather than derived, like the photo checkpoints: the one lora the user kept from 213's
    trial."""
    assert "3228867" in _cell("CIVITAI_H3 = ["), "Civitai version id defterde yok: 3228867"


def test_the_notebook_fetches_eros_max_from_its_author_s_repo_into_the_h3_diffusion_models():
    """Madde 333, the user's pick after trying both (329, 332): the file the author says to use by
    default (TURBO-hybrid int8), from the Hugging Face repo the Civitai page points at -- Civitai's
    own version link hands out a different, w4a8 file. A row of HF_H3: only a video run reaches it
    (test_an_unticked_group_costs_no_bytes), and hf_fetch uploads nothing, so the file never touches
    the mirror. H3DIFF is where the graph's MiniMaxH3/ prefix looks."""
    cell = _cell("HF_H3 = [")
    listing = cell[cell.find("HF_H3 = ["):]
    listing = listing[:listing.find("\n]")]

    assert re.search(r'\(\s*"TenStrip/10Eros-Max",'
                     r'\s*"10Eros_Max_h3_TURBO-hybrid_beta5_int8\.safetensors",'
                     r'\s*H3DIFF,\s*"10Eros_Max_h3_TURBO-hybrid_beta5_int8\.safetensors",',
                     listing), f"HF_H3'te Eros satırı yok:\n{listing}"


def test_the_retired_dasiwa_h3_checkpoint_is_gone_from_the_notebook():
    """Eros took its place (madde 333). A row left behind would still bring ~21 GB down on every H3
    run, for a file no graph loads. The file itself stays in the mirror (the user's call, "dasiwa
    silinmesin, dursun"): the notebook only stops fetching it."""
    source = _source()

    for leftover in ("dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_"
                     "row-wise_convrot_runtime_mixed.safetensors", "3314686"):
        assert leftover not in source, f"Defterde DaSiWa H3'ten iz kaldı: {leftover}"


def test_the_face_detailer_s_files_are_gone_from_the_notebook():
    """The photo graph runs no detailer since madde 430. A row left behind would still bring the
    detector and SAM down on every photo run, and the Subpack's install with them -- the package
    gives the graph nothing but the detector node. The folders go too: a cell making them and a
    summary listing them would be the same leftover. SAM was the one file fetched by a plain
    address, so the list of those and its loop go with it."""
    source = _source()

    for leftover in ("face_yolov9c.pt", "sam_vit_b_01ec64.pth", "Bingsu/adetailer",
                     "ComfyUI-Impact-Subpack", "ultralytics", "models/sams", "OPEN_PHOTO",
                     "open_jobs"):
        assert leftover not in source, f"Defterde yüz detailer'ından iz kaldı: {leftover}"


# What only WAN's graphs used (madde 435): the nodes of none of the three graphs left come from these
# packages -- they came with WAN's own notebook, wan22-arbuzai, and the photo's and H3's do not have
# them.
WAN_PACKAGES = ("melMass/comfy_mtb", "Kosinkadink/ComfyUI-VideoHelperSuite",
                "kijai/ComfyUI-WanVideoWrapper", "city96/ComfyUI-GGUF", "evanspearman/ComfyMath",
                "Fannovel16/ComfyUI-Frame-Interpolation", "GACLove/ComfyUI-VFI",
                "Suzie1/ComfyUI_Comfyroll_CustomNodes", "Smirnov75/ComfyUI-mxToolkit",
                "scottmudge/ComfyUI-NAG", "Alectriciti/comfyui-adaptiveprompts")


def test_wan_is_gone_from_the_notebook():
    """Madde 435, the user's words: "wan modelini kaldıralım queen editorden direkt kullanımıyor
    zaten". Its box, the pick it made and the name it handed the app; its files, the folder only its
    CLIP vision used, and its two graphs; and the packages only its graphs read. A row left behind
    would still bring ~39 GiB or a clone down for a producer the app no longer has."""
    source = _source()

    for leftover in ("VIDEO_WAN", "VIDEO_H3", "VIDEO_MODEL", "Wan2_1_VAE_fp32", "umt5_xxl",
                     "lightx2v", "SmoothMix", "clip_vision", "Comfy-Org/Wan_2",
                     "workflow_video_api.json", "workflow_video_first_last_api.json",
                     *WAN_PACKAGES):
        assert leftover not in source, f"Defterde WAN'dan iz kaldı: {leftover}"


def test_the_notebook_keeps_the_packages_the_photo_and_h3_graphs_read():
    """The other half of the same cut: the nine that stay. Photo's graph reads Impact-Pack, ppm,
    rgthree and Easy-Use; H3's reads DaSiWa and KJNodes; Manager, Custom-Scripts and Ultimate SD
    Upscale came with the photo's own notebook."""
    nodes = _cell("CUSTOM_NODES = [")

    for kept in ("ltdrdata/ComfyUI-Manager", "rgthree/rgthree-comfy", "ltdrdata/ComfyUI-Impact-Pack",
                 "yolain/ComfyUI-Easy-Use", "pythongosssss/ComfyUI-Custom-Scripts",
                 "ssitu/ComfyUI_UltimateSDUpscale", "kijai/ComfyUI-KJNodes",
                 "pamparamm/ComfyUI-ppm", "darksidewalker/ComfyUI-DaSiWa-Nodes"):
        assert kept in nodes, f"Defter bu paketi kurmuyor: {kept}"
    assert nodes.count('.git"),') == 9, "Defter dokuz paketten fazlasını kuruyor"


def test_the_notebook_fetches_mystic_xxx_by_its_version_into_the_loras():
    """Madde 328: the address is the user's -- Civitai version 3266628, "v4.0 (FL2VA & REF2VA)" -- and
    the file lands in loras/ under the name the lora stack would load it by. Madde 330 took it out of
    the stack and kept this row: the file stays on the disk, so turning it back on is a graph edit
    and no notebook change. A row of CIVITAI_H3, which only a video run reaches
    (test_an_unticked_group_costs_no_bytes)."""
    cell = _cell("CIVITAI_H3 = [")
    listing = cell[cell.find("CIVITAI_H3 = ["):]
    listing = listing[:listing.find("\n]")]

    assert re.search(r'\(3266628,\s*LORA,\s*"MysticXXX_MMH3-V4\.safetensors",', listing), \
        f"CIVITAI_H3'te Mystic XXX satırı yok:\n{listing}"


def test_the_notebook_fetches_hmcumshot_by_its_version_into_the_loras():
    """Madde 426: Mutlu son's lora, v1.0 -- Civitai version 3329529 -- landing in loras/ under the name
    the producer puts in the stack. A row of CIVITAI_H3, so it comes down with H3's other files and
    only on a video run (test_an_unticked_group_costs_no_bytes)."""
    cell = _cell("CIVITAI_H3 = [")
    listing = cell[cell.find("CIVITAI_H3 = ["):]
    listing = listing[:listing.find("\n]")]

    assert re.search(r'\(3329529,\s*LORA,\s*"HMCumshot_V1\.0\.safetensors",', listing), \
        f"CIVITAI_H3'te HMCumshot satırı yok:\n{listing}"


def test_hmcumshot_comes_through_the_mirror():
    """Through civitai_fetch's ordinary road: the HF mirror first, Civitai when it is not there."""
    from colab.downloads import MIRRORLESS

    assert "HMCumshot_V1.0.safetensors" not in MIRRORLESS


def test_no_huggingface_file_is_fetched_by_its_address():
    """An address sends the file through HF's bridge, which cuts a plain download to 8.7 MB/s on most
    of its servers (xet-core #821) -- the user timed H3's install at about a hundred minutes (madde
    310). Named by repo and path, a file can only come down through HF's own downloader."""
    cell = _cell("# === Target folders ===")

    assert cell, "İndirme hücresi bulunamadı"
    assert "huggingface.co" not in cell, "İndirme hücresinde hâlâ HF adresi var"


def test_huggingface_files_come_down_through_hf_fetch():
    """hf_fetch is the path around HF's bridge. Without hf_xet installed, huggingface_hub goes back to
    the bridge with nothing but a log line, so installing it is half of the rule. Each download's row
    is kept for the table the cell ends with (madde 312)."""
    assert re.search(r"for [^\n]+ in hf_jobs:\n\s+landed\.append\(hf_fetch\(",
                     _cell("# === Target folders ===")), \
        "HF dosyaları hf_fetch ile inmiyor ya da satırları tutulmuyor"
    assert re.search(r"pip install[^\n]*hf_xet", _source()), "Defter hf_xet'i kurmuyor"


def test_the_models_cell_ends_with_the_download_summary():
    """The rows the downloads hand back are collected in one list and printed as a table once
    everything is down (madde 312)."""
    cell = _cell("# === Target folders ===")
    imported = [name for module, names in _imports_from_code() if module == "colab.downloads"
                for name in names]

    assert -1 < cell.find("landed = []") < cell.find("in hf_jobs:"), \
        "Satır listesi döngülerden önce açılmıyor"
    assert cell.find("download_summary(landed)") > cell.find("in civitai_jobs:") > -1, \
        "Özet tablosu indirmelerden sonra basılmıyor"
    assert "download_summary" in imported, "Defter özet tablosunu klondan import etmiyor"


def test_every_name_the_notebook_imports_from_its_code_exists():
    """The notebook cannot run here, but its import lines can: a name the module does not give is an
    ImportError on the machine, after the clone and before a single model comes down."""
    imports = _imports_from_code()

    assert imports, "Defter kendi kodunu import etmiyor"
    for module, names in imports:
        found = importlib.import_module(module)
        missing = [name for name in names if not hasattr(found, name)]
        assert missing == [], f"{module} bu adları vermiyor: {missing}"


def test_the_notebook_reaches_its_code_through_the_clone():
    """The module lives in the clone, which is not on the kernel's path until the notebook puts it
    there -- and it has to be there before the first import."""
    helpers = _cell("# === Shared helpers ===")
    path, first = helpers.find("sys.path.insert(0, APP_DIR)"), helpers.find("from colab.")

    assert -1 < path < first, "Yardımcılar hücresi klonu yola import'tan önce koymuyor"


def test_a_rerun_imports_the_code_it_just_cloned():
    """The clone cell deletes and clones the repo on every run, so a re-run picks up a push without a
    new runtime. Python keeps a module it imported for as long as the kernel lives: unless the cell
    drops it, a re-run clones the new code and keeps running the old."""
    assert "del sys.modules[" in _cell("# === Shared helpers ==="), \
        "Yardımcılar hücresi önceki koşunun modülünü bırakmıyor"


def test_the_notebook_defines_none_of_the_code_it_imports():
    """One home per function: a copy left in a cell would run instead of the tested one."""
    source = _source()
    names = [name for _module, names in _imports_from_code() for name in names]

    assert names, "Defter kendi kodunu import etmiyor"
    assert [name for name in names if f"def {name}(" in source] == [], \
        "Defter import ettiği kodu kendisi tanımlıyor"


def test_the_notebook_installs_the_nodes_the_h3_graph_asks_for():
    """SeedControl, EnhancedVideoCombine and the lora stack come from this package. ComfyUI
    validates every node it is sent, so a missing one fails every H3 render."""
    assert "darksidewalker/ComfyUI-DaSiWa-Nodes" in _cell("CUSTOM_NODES = [")


def test_the_disk_estimate_counts_h3_when_video_is_ticked():
    assert '(INSTALL_VIDEO, 37, "video (H3)")' in _cell("SIZES = ["), "Disk hesabı H3'ü saymıyor"


def test_the_clone_checks_for_the_h3_graphs_too():
    clone = _cell("# === Clone ===")

    for name in ("workflow_video_h3_api.json", "workflow_video_h3_first_last_api.json"):
        assert name in clone, f"Klon {name} dosyasını aramıyor"


def test_the_clone_looks_for_the_graphs_under_assets():
    """The graphs moved in madde 251, and the notebook is the only reader Colab can break: the app
    asks config, so a wrong path here is invisible to the suite and stops the run with "Grafik yok"
    on the machine instead."""
    clone = _cell("# === Clone ===")

    assert 'os.path.join(CLONE_DIR, "queen-editor", "assets", _name)' in clone, \
        "Klon grafikleri assets/ altında aramıyor"


def test_the_tunnel_is_opened_over_tcp_rather_than_quic():
    """cloudflared speaks QUIC by default, and QUIC rides on UDP. Colab's network throttles UDP and
    leaves TCP alone: on 2026-08-24 the same photo took 17.74 s over the default tunnel and 0.18 s
    over one started with this flag -- same machine, same minute, ninety times apart. Without it a
    gallery of 81 photos is unusable and nothing in the app explains why."""
    flask_cell = _cell("# === Start Flask")

    assert '"--protocol", "http2"' in flask_cell, \
        "cloudflared varsayılan QUIC ile açılıyor — Colab'ın ağı UDP'yi kısıyor"
