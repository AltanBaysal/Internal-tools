import json
import os

from backend import config
from backend.features.producers.domain.model_groups import GROUPS

# The shipped graph is an asset, so its shape is verified here: a UI-format export or a renamed
# node would only surface as a failed render on Colab otherwise.

# The encoder that reads BREAK as a break rather than as a word. Written once because the name came
# from reading the node's source rather than running it: if Colab says otherwise, one line moves and
# the assertions keep their shape.
BREAK_ENCODER = "CLIPTextEncodeBREAK"


def test_workflow_is_api_format_with_the_nodes_we_patch():
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert "nodes" not in workflow, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
    assert workflow["3"]["class_type"] == "ImpactWildcardProcessor"
    assert {"wildcard_text", "populated_text"} <= set(workflow["3"]["inputs"])
    assert workflow["4"]["class_type"] == "ImpactWildcardProcessor"
    assert {"wildcard_text", "populated_text"} <= set(workflow["4"]["inputs"])
    assert "seed" in workflow["40"]["inputs"]
    # The model the user picks lands here; a renamed input would drop the choice in silence.
    assert "ckpt_name" in workflow["45"]["inputs"]


def test_the_positive_encoder_understands_break():
    """Two characters in one frame bleed into each other, and half of that happens while the prompt
    is read: tags inside one chunk are read in each other's context. BREAK closes the chunk where it
    is written -- but only for an encoder that knows the word. A plain CLIPTextEncode encodes it as
    a word instead, which does not separate anything, it pollutes.

    Only this node changes. Both KSampler and ToDetailerPipe read the positive from its output, so
    one swap covers the detailer too.
    """
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)

    assert workflow["36"]["class_type"] == BREAK_ENCODER


def test_the_negative_path_keeps_the_plain_encoder():
    """A decision, not an accident: BREAK has no work to do in a negative, and a node nobody touched
    is a node nobody broke. Without this the next export could swap both encoders and the graph would
    still look right to every other test here."""
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)

    assert workflow["38"]["class_type"] == "CLIPTextEncode"


def test_the_prompt_reaches_the_encoder_through_the_chain():
    """The whole positive path, pinned by its wiring rather than by its node names: the adapter
    writes the prompt into 3, 39 strips the stray commas, and 36 encodes what comes out. Swapping
    36's class must not drop the wires, and 39 must not be cut out of the middle -- either would
    surface as a render that silently ignores the prompt."""
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)

    assert workflow["39"]["inputs"]["string"][0] == "3"
    assert workflow["36"]["inputs"]["text"][0] == "39"
    assert "clip" in workflow["36"]["inputs"]


def _photo():
    """The photo graph, read fresh."""
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_the_photo_graph_renders_the_portrait_size():
    """Madde 228: back to the size before 218 made it landscape. 1024x1536 is in the graph author's
    own table of supported sizes -- the High-Res column, which this graph feeds straight into
    EmptyLatentImage."""
    photo = _photo()

    assert photo["1"]["inputs"]["value"] == 1024
    assert photo["11"]["inputs"]["value"] == 1536


def test_every_graph_makes_a_portrait_frame():
    """The item itself, asked of the thing rather than of the numbers: an edit that keeps the ratio
    but swaps width and height in every graph would pass the shape assertions. The photo's and both
    H3 Directors' -- the three graphs that ship (madde 435)."""
    photo = _photo()

    assert photo["1"]["inputs"]["value"] < photo["11"]["inputs"]["value"]
    for graph in _h3_graphs():
        director = graph["2730"]["inputs"]
        assert director["width"] < director["height"]


def test_the_photo_graph_runs_the_face_detailer():
    """Madde 469 reverses 430, the user's words: "Yüz detailer'ını geri aç ... 430'u geri alırım"
    (12 Ekim). The face detector finds the face, SAM ViT-B masks it, FaceDetailer redraws it. Asked
    by class rather than by id, so a new export that renumbers the nodes still passes."""
    photo = _photo()
    classes = [node["class_type"] for node in photo.values()]

    assert classes.count("FaceDetailerPipe") == 1, "Fotoğraf grafiğinde tek bir FaceDetailer yok"
    sams = [node["inputs"]["model_name"] for node in photo.values()
            if node["class_type"] == "SAMLoader"]
    assert sams == ["sam_vit_b_01ec64.pth"], f"Grafiğin SAM'leri: {sams}"
    detectors = {node["inputs"]["model_name"] for node in photo.values()
                 if node["class_type"] == "UltralyticsDetectorProvider"}
    assert detectors == {"bbox/face_yolov9c.pt"}, f"Grafiğin dedektörleri: {detectors}"


def test_the_photo_graph_saves_the_detailed_picture():
    """The picture is saved once FaceDetailer has redrawn the face, as in the user's export."""
    photo = _photo()
    savers = [node for node in photo.values() if node["class_type"] == "SaveImage"]

    assert len(savers) == 1, f"Grafikte {len(savers)} Save Image var"
    source = savers[0]["inputs"]["images"][0]
    assert photo[source]["class_type"] == "FaceDetailerPipe", \
        f"Save Image resmi FaceDetailer'dan değil {photo[source]['class_type']}'dan alıyor"


# The nodes that end the photo graph: the saved picture, and the panel comparing the detailer's
# before and after.
OUTPUT_CLASSES = {"SaveImage", "Image Comparer (rgthree)"}


def test_every_node_of_the_photo_graph_feeds_an_output():
    """A node no output reads is left over from a removed branch: a setting nothing uses, or a
    model patch only a gone node read. Walking back from every output has to reach every node."""
    photo = _photo()
    waiting = [node_id for node_id, node in photo.items() if node["class_type"] in OUTPUT_CLASSES]

    reached = set()
    while waiting:
        node_id = waiting.pop()
        if node_id in reached:
            continue
        reached.add(node_id)
        waiting += [value[0] for value in photo[node_id]["inputs"].values()
                    if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str)]

    hanging = sorted(set(photo) - reached)
    assert not hanging, f"Hiçbir çıkışa ulaşmayan düğümler: {hanging}"


def _model_files(node):
    """Every .safetensors named anywhere in the graph, nested widgets included -- Power Lora Loader
    keeps its loras inside dicts, so a flat scan over node inputs would miss half of them.

    A loader whose widget is empty contributes nothing on its own: null is not a string.
    """
    if isinstance(node, str):
        return {node} if node.endswith(".safetensors") else set()
    if isinstance(node, dict):
        return set().union(set(), *(_model_files(value) for value in node.values()))
    if isinstance(node, list):
        return set().union(set(), *(_model_files(item) for item in node))
    return set()


def test_the_only_graphs_shipped_are_the_two_photo_ones_and_h3_s():
    """Madde 435, the user's words: "wan modelini kaldıralım queen editorden direkt kullanımıyor
    zaten". Queen Editor makes H3 videos alone, so WAN's two graphs no longer ship -- a graph left
    behind would be one nobody renders and somebody edits. Krea 2 Turbo's is the second photo graph
    (madde 482)."""
    shipped = sorted(name for name in os.listdir(os.path.dirname(config.WORKFLOW_PATH))
                     if name.endswith(".json"))

    assert shipped == ["workflow_api.json", "workflow_photo_krea2_api.json",
                       "workflow_video_h3_api.json", "workflow_video_h3_first_last_api.json"], \
        f"Gönderilen grafikler: {shipped}"


# MiniMax H3 (madde 243): two graphs exported by the user in 213's trial and made sterile in 242.


def _h3_graphs():
    """I2VA first, FL2VA second -- the order the producer reads them in."""
    graphs = []
    for path in (config.H3_VIDEO_WORKFLOW_PATH, config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH):
        with open(path, encoding="utf-8") as f:
            graphs.append(json.load(f))
    return graphs


def test_both_h3_graphs_are_api_format_with_the_nodes_we_patch():
    """The Director keeps the pictures and the prompt; SeedControl keeps the noise seed. A node that
    kept its id but renamed an input would swallow the patch and only surface as a bad render."""
    for graph in _h3_graphs():
        assert "nodes" not in graph, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
        assert graph["2730"]["class_type"] == "MiniMaxH3Director"
        assert {"prompt", "timeline_data", "builder_state", "duration"} <= set(
            graph["2730"]["inputs"])
        assert graph["2739"]["class_type"] == "DaSiWa_SeedControl"
        assert "seed_value" in graph["2739"]["inputs"]


def test_the_h3_graphs_are_one_per_mode_with_room_for_their_pictures():
    """The producer writes the pictures in by position, so the room each graph has is part of its
    contract: one for a video that hangs on a photo, two for one that arrives at another."""
    i2va, fl2va = _h3_graphs()

    assert i2va["2730"]["inputs"]["mode"] == "I2VA"
    assert fl2va["2730"]["inputs"]["mode"] == "FL2VA"
    assert len(json.loads(i2va["2730"]["inputs"]["timeline_data"])["items"]) == 1
    assert len(json.loads(fl2va["2730"]["inputs"]["timeline_data"])["items"]) == 2


def test_both_h3_graphs_render_four_seconds_at_576_by_864():
    """Madde 434: 540p, up from 480p's 512 x 768. 576 x 864 is not the Director panel's 540p size --
    the panel rounds each side to its 32px grid on its own and gets 576 x 896 for 2:3, 3.6% off the
    photo -- but exact 2:3 with both sides on that grid, the user's pick over the panel's ("bu
    olsun"). The aspect stays auto, so the video follows the photo: a photo of another shape came
    out stretched in an earlier trial.

    One number is quoted for every video, and one export joins both kinds -- two lengths or two
    sizes there would be a lie and a broken file."""
    for graph in _h3_graphs():
        director = graph["2730"]["inputs"]
        assert (director["duration"], director["width"], director["height"]) == (4, 576, 864)
        resolution = json.loads(director["timeline_data"])["resolution"]
        assert (resolution["aspect"], resolution["resolution"]) == ("auto", "540p")


# Madde 476: every generation is landscape or portrait. The graphs ship as exported -- portrait --
# and each producer writes its orientation's size from its own table on every job.


def _sizes():
    """{orientation: ((photo w, h), (video w, h, the Director panel's preset))}"""
    from backend.features.photo_generation.data import comfy_h3_video_generator as video
    from backend.features.photo_generation.data import comfy_photo_generator as photo
    from backend.features.photo_generation.domain import orientation

    assert set(photo.SIZES) == set(video.SIZES) == set(orientation.ALL)
    return {name: (photo.SIZES[name], video.SIZES[name]) for name in orientation.ALL}


def test_the_photo_and_the_h3_video_have_exactly_one_shape_in_each_orientation():
    """The rule behind the numbers, and the one that outlives them: H3 pulls the photo to its own
    size, so a drift between the two shapes does not fail -- it stretches the picture, silently.
    Exact rather than close, because exact costs nothing here (madde 475): 1536 x 864 is 1024 x 576
    times 1.5, and 1024 x 1536 is 576 x 864 times 16/9."""
    for name, ((pw, ph), (vw, vh, _preset)) in _sizes().items():
        assert pw * vh == ph * vw, f"{name}: fotoğraf {pw}x{ph}, video {vw}x{vh} aynı oranda değil"


def test_every_h3_video_size_is_on_its_32_pixel_grid():
    """The user's rule (20 Ekim): sizes H3 really works at, not arbitrary numbers. Its VAE and its
    patches shrink each side 32 times, and ComfyUI's own H3 nodes step width and height by 32."""
    for name, (_photo_size, (vw, vh, _preset)) in _sizes().items():
        assert vw % 32 == 0 and vh % 32 == 0, f"{name}: {vw}x{vh} 32'nin katı değil"


def test_each_orientation_is_the_shape_it_is_named():
    """A swap of width and height keeps every ratio above and turns the picture the wrong way."""
    sizes = _sizes()
    (pw, ph), (vw, vh, _preset) = sizes["yatay"]
    assert pw > ph and vw > vh
    (pw, ph), (vw, vh, _preset) = sizes["dikey"]
    assert pw < ph and vw < vh


def test_the_sizes_are_the_ones_the_user_approved():
    """Madde 475: landscape is exact 16:9 -- the video 1024 x 576 at the panel's 576p, the photo
    1536 x 864 ("tamam videoyu böyle yapıcaz", "tamam böyle olsun"); portrait stays what it was."""
    assert _sizes() == {"yatay": ((1536, 864), (1024, 576, "576p")),
                        "dikey": ((1024, 1536), (576, 864, "540p"))}


def test_portrait_is_what_the_shipped_graphs_carry():
    """The graphs ship as exported, and a render asked for no orientation keeps their own size -- so
    the portrait row and the graphs cannot drift apart unseen."""
    (pw, ph), (vw, vh, preset) = _sizes()["dikey"]
    photo = _photo()

    assert (photo["1"]["inputs"]["value"], photo["11"]["inputs"]["value"]) == (pw, ph)
    for graph in _h3_graphs():
        director = graph["2730"]["inputs"]
        assert (director["width"], director["height"]) == (vw, vh)
        assert json.loads(director["timeline_data"])["resolution"]["resolution"] == preset


def test_every_model_the_h3_graphs_load_is_in_the_video_group():
    """The producers panel judges "installed" by this group, so a file the graph loads and the group
    does not name is a panel that says ready over a render that cannot start."""
    listed = {row["name"] for row in GROUPS["video"]}

    for graph in _h3_graphs():
        missing = sorted(_model_files(graph) - listed)
        assert not missing, f"Graf bu dosyaları yüklüyor ama grup saymıyor: {missing}"


def test_both_h3_graphs_load_eros_max_beta5():
    """Madde 333: Eros, the user's pick after trying it (329) and DaSiWa again (332). Each graph has
    two model loaders -- the Director takes one as its FL2VA model and the other as its REF2VA model,
    and picks by mode -- so every loader is asked, found by its class rather than its id: what is
    asked is which model the graph loads, and a third loader would slip past a test naming two ids.
    Whether the group counts the file is the scan's question above: unet_name is a plain input it
    sees."""
    expected = {("MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", "default")}

    for graph in _h3_graphs():
        loaded = {(node["inputs"]["unet_name"], node["inputs"]["weight_dtype"])
                  for node in graph.values() if node["class_type"] == "UNETLoader"}
        assert loaded == expected, f"Grafiğin model düğümleri bunları yüklüyor: {loaded}"


def test_the_h3_graphs_carry_motion_booster_alone_at_seventy():
    """Motion Booster at 0.7 is the user's pick from 213's trial, and since madde 330 the stack's only
    lora: Mystic XXX came off there. One stack serves all three modes: it takes the model the Director picked for its mode (output 5), and
    REF2VA runs on the I2VA graph (madde 304). A slot is read by its name, not filtered by `on`:
    whether the loader honours `on` is unknown, and "None" is how every empty slot has loaded nothing
    since 213 -- so a lora switched off but still named stays red here. The stack keeps its loras
    inside a JSON string, which the model scan above cannot see into -- so it is read here, and its
    file held to the group."""
    for graph in _h3_graphs():
        stack = graph["2678"]["inputs"]
        assert stack["model"] == ["2730", 5], "Yığın Director'ın kipine göre seçtiği modeli almıyor"
        named = [(slot["lora"], slot["str"], slot["on"]) for slot in json.loads(stack["stack_data"])
                 if slot["lora"] != "None"]
        assert named == [("H3_Motion_BoosterV2.safetensors", 0.7, True)], \
            f"Yığının adı olan yuvaları: {named}"

    assert "H3_Motion_BoosterV2.safetensors" in {row["name"] for row in GROUPS["video"]}, \
        "Grup yığının LoRA'sını saymıyor"


def test_both_h3_graphs_save_an_mp4():
    """Left on Auto the saver wrote WebM/AV1 in the user's trial (madde 245), which the producer never
    picks up -- and the rest of the app names, plays and joins videos as mp4."""
    for graph in _h3_graphs():
        saver = graph["2568"]
        assert saver["class_type"] == "DaSiWa_EnhancedVideoCombine"
        assert (saver["inputs"]["container"], saver["inputs"]["codec"]) == ("MP4", "H.264")


# Krea 2 Turbo (madde 482): the user's own ComfyUI export, shipped as it was given. The producer
# writes three nodes and leaves everything else the user's.


def _krea():
    """Krea's graph, read fresh."""
    with open(config.KREA2_WORKFLOW_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_the_krea_graph_is_api_format_with_the_nodes_we_patch():
    """The prompt, the seed and the size: a node that kept its id but renamed an input would swallow
    the patch and only surface as a picture of the wrong thing."""
    krea = _krea()

    assert "nodes" not in krea, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
    assert krea["53:19"]["class_type"] == "PrimitiveStringMultiline"
    assert "value" in krea["53:19"]["inputs"]
    assert krea["53:3"]["class_type"] == "KSampler"
    assert "seed" in krea["53:3"]["inputs"]
    assert krea["53:5"]["class_type"] == "EmptyLatentImage"
    assert {"width", "height", "batch_size"} <= set(krea["53:5"]["inputs"])


def test_the_krea_graph_has_no_negative_to_write():
    """Why the panel's negative never reaches Krea: the sampler's negative is the positive zeroed,
    and at cfg 1 ComfyUI does not compute it at all."""
    sampler = _krea()["53:3"]["inputs"]

    assert sampler["cfg"] == 1
    assert _krea()[sampler["negative"][0]]["class_type"] == "ConditioningZeroOut"


def test_the_krea_graph_renders_with_snofs_switched_on():
    """The user's workflow draws with SNOFS at 0.8, and the lora box's Illustrious loras cannot load
    on Krea -- so this is the lora every Krea picture has."""
    krea = _krea()

    assert (krea["53:15"]["inputs"]["lora_name"], krea["53:15"]["inputs"]["strength_model"]) == \
        ("snofs_krea_v1_5.safetensors", 0.8)
    assert krea["53:22"]["inputs"]["switch"] == ["53:23", 0]
    assert krea["53:23"]["inputs"]["value"] is True


def test_every_model_the_krea_graph_loads_is_krea_s_row_in_the_photo_group():
    """The panel counts Krea as a photo model by these files, so a file the graph loads and the row
    does not name is a panel that says ready over a render that cannot start -- and one the row names
    and the graph does not is a download nobody uses."""
    from backend.features.producers.domain.model_groups import KREA2_FILES

    assert _model_files(_krea()) == {row["name"] for row in KREA2_FILES}


def test_krea_s_sizes_keep_the_video_s_shape():
    """Madde 475's rule for Krea too: H3 pulls the photo to its own size, so the ratio has to be
    exact. Both sides on 16, Qwen Image's VAE times the DiT's patch. About 1 MP, the user's
    workflow's own setting: 1280 x 720 and 832 x 1248."""
    from backend.features.photo_generation.data import comfy_h3_video_generator as video
    from backend.features.photo_generation.data import comfy_krea_photo_generator as krea

    assert krea.SIZES == {"yatay": (1280, 720), "dikey": (832, 1248)}
    for name, (pw, ph) in krea.SIZES.items():
        vw, vh, _preset = video.SIZES[name]
        assert pw * vh == ph * vw, f"{name}: Krea {pw}x{ph}, video {vw}x{vh} aynı oranda değil"
        assert pw % 16 == 0 and ph % 16 == 0, f"{name}: {pw}x{ph} 16'nın katı değil"
        assert (pw > ph) == (vw > vh), f"{name}: Krea'nın şekli videonunkine ters"
