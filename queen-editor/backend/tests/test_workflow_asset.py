import json

from backend import config
from backend.features.producers.domain import model_groups
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


def test_video_workflow_is_api_format_with_the_nodes_we_patch():
    """The video graph is a copy of collab-toolbox's WAN 2.2 I2V export -- our own file, and the
    three nodes the adapter patches are asserted by name and by input, because a node that kept its
    id but renamed its input would swallow the patch and only surface as a bad render."""
    with open(config.VIDEO_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert "nodes" not in workflow, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
    assert workflow["287"]["class_type"] == "LoadImage"
    assert "image" in workflow["287"]["inputs"]
    assert workflow["233:240"]["class_type"] == "PromptGenerator"
    assert {"prompt", "seed"} <= set(workflow["233:240"]["inputs"])
    assert workflow["210"]["class_type"] == "Seed (rgthree)"
    assert "seed" in workflow["210"]["inputs"]


def test_the_first_last_video_workflow_is_api_format_with_the_nodes_we_patch():
    """The second video graph: the arbuzai workflow's FIRST2LASTFRAME group, exported as our own
    file. It carries two LoadImage nodes rather than one, and which of them is the ending frame is
    decided by the graph's wiring -- so both ids are asserted, and so is the node that reads them."""
    with open(config.VIDEO_FIRST_LAST_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert "nodes" not in workflow, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
    assert workflow["338"]["class_type"] == "LoadImage"
    assert "image" in workflow["338"]["inputs"]
    assert workflow["342"]["class_type"] == "LoadImage"
    assert "image" in workflow["342"]["inputs"]
    # The two pictures are only an ending frame because this node reads them as one.
    assert workflow["343"]["class_type"] == "WanFirstLastFrameToVideo"
    assert workflow["343"]["inputs"]["start_image"][0] == "338"
    assert workflow["343"]["inputs"]["end_image"][0] == "342"
    assert workflow["333:291"]["class_type"] == "PromptGenerator"
    assert {"prompt", "seed"} <= set(workflow["333:291"]["inputs"])
    assert workflow["327"]["class_type"] == "Seed (rgthree)"
    assert "seed" in workflow["327"]["inputs"]


def test_both_video_graphs_agree_on_how_long_a_render_runs():
    """How long a video runs is read from one graph and quoted for every video, export estimate
    included. Two graphs disagreeing would make that number a lie for half the gallery."""
    with open(config.VIDEO_WORKFLOW_PATH, encoding="utf-8") as f:
        standard = json.load(f)
    with open(config.VIDEO_FIRST_LAST_WORKFLOW_PATH, encoding="utf-8") as f:
        first_last = json.load(f)

    assert standard["178"]["inputs"]["value"] == first_last["335"]["inputs"]["value"]


def _graphs():
    """The three shipped graphs, read fresh. Every size question below needs all of them: the rule
    is about how they agree, not about any one of them."""
    graphs = []
    for path in (config.WORKFLOW_PATH, config.VIDEO_WORKFLOW_PATH,
                 config.VIDEO_FIRST_LAST_WORKFLOW_PATH):
        with open(path, encoding="utf-8") as f:
            graphs.append(json.load(f))
    return graphs


def _video_size(graph, node_id):
    """The mxSlider2D's width and height. It carries each as a pair -- the slider's own value and
    the one it displays -- and a render that read one while a test read the other would pass here
    and produce something else, so both are asserted equal."""
    inputs = graph[node_id]["inputs"]
    assert inputs["Xi"] == inputs["Xf"], f"{node_id}: X çifti ayrışmış"
    assert inputs["Yi"] == inputs["Yf"], f"{node_id}: Y çifti ayrışmış"
    return inputs["Xi"], inputs["Yi"]


def test_the_photo_graph_renders_the_portrait_size():
    """Madde 228: back to the size before 218 made it landscape. 1024x1536 is in the graph author's
    own table of supported sizes -- the High-Res column, which this graph feeds straight into
    EmptyLatentImage."""
    photo, _standard, _first_last = _graphs()

    assert photo["1"]["inputs"]["value"] == 1024
    assert photo["11"]["inputs"]["value"] == 1536


def test_both_video_graphs_render_the_same_portrait_size():
    """480 wide keeps the short side at the 480 WAN 2.2's I2V class was trained at, and 720 makes
    it exactly the photo's 2:3.

    The two graphs are asserted against each other as well as against the number -- a project mixes
    standard and first-last videos in one export, and two sizes there is a broken file.
    """
    _photo, standard, first_last = _graphs()

    assert _video_size(standard, "208") == (480, 720)
    assert _video_size(first_last, "328") == (480, 720)


def test_the_photo_and_the_video_agree_on_the_shape_of_the_frame():
    """The rule behind the numbers, and the one that outlives them: the video graph pulls the photo
    to its own size with keep_proportion "stretch", so two shapes that drift apart do not fail --
    they squash the picture, silently. One percent is well under what an eye catches.
    """
    photo, standard, _first_last = _graphs()
    photo_shape = photo["1"]["inputs"]["value"] / photo["11"]["inputs"]["value"]
    width, height = _video_size(standard, "208")

    assert abs(photo_shape - width / height) / photo_shape < 0.01


def test_every_graph_makes_a_portrait_frame():
    """The item itself, asked of the thing rather than of the numbers: an edit that keeps the ratio
    but swaps width and height in both graphs would pass the shape assertion above."""
    photo, standard, first_last = _graphs()

    assert photo["1"]["inputs"]["value"] < photo["11"]["inputs"]["value"]
    for graph, node_id in ((standard, "208"), (first_last, "328")):
        width, height = _video_size(graph, node_id)
        assert width < height


def _model_files(node):
    """Every .safetensors named anywhere in the graph, nested widgets included -- Power Lora Loader
    keeps its loras inside dicts, so a flat scan over node inputs would miss half of them.

    A loader whose widget is empty contributes nothing on its own: the graph carries two orphan GGUF
    loaders with a null name, and null is not a string.
    """
    if isinstance(node, str):
        return {node} if node.endswith(".safetensors") else set()
    if isinstance(node, dict):
        return set().union(set(), *(_model_files(value) for value in node.values()))
    if isinstance(node, list):
        return set().union(set(), *(_model_files(item) for item in node))
    return set()


def test_every_model_the_video_graph_loads_is_in_the_video_group():
    """The producers panel judges "installed" by this group, so a file the graph loads and the group
    does not name is a panel that says ready over a render that cannot start."""
    with open(config.VIDEO_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    listed = {row["name"] for row in GROUPS["video"]}
    missing = sorted(_model_files(workflow) - listed)
    assert not missing, f"Graf bu dosyaları yüklüyor ama grup saymıyor: {missing}"


def test_every_model_the_first_last_graph_loads_is_in_the_video_group():
    """The same guard for the second graph, and the reason it needs its own: FIRST2LASTFRAME reads a
    CLIP vision model that the I2V hat has no node for, so scanning only the first graph would leave
    the panel calling the video producer ready over a render that cannot start."""
    with open(config.VIDEO_FIRST_LAST_WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    listed = {row["name"] for row in GROUPS["video"]}
    missing = sorted(_model_files(workflow) - listed)
    assert not missing, f"Graf bu dosyaları yüklüyor ama grup saymıyor: {missing}"


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


def test_both_h3_graphs_render_four_seconds_at_512_by_768():
    """The user's settings from 213's trial. One number is quoted for every video, and one export
    joins both kinds -- two lengths or two sizes there would be a lie and a broken file."""
    for graph in _h3_graphs():
        director = graph["2730"]["inputs"]
        assert (director["duration"], director["width"], director["height"]) == (4, 512, 768)


def test_the_photo_and_the_h3_video_agree_on_the_shape_of_the_frame():
    photo = _graphs()[0]
    photo_shape = photo["1"]["inputs"]["value"] / photo["11"]["inputs"]["value"]

    for graph in _h3_graphs():
        director = graph["2730"]["inputs"]
        assert abs(photo_shape - director["width"] / director["height"]) / photo_shape < 0.01


def test_every_model_the_h3_graphs_load_is_in_the_h3_group():
    listed = {row["name"] for row in model_groups.H3_VIDEO}

    for graph in _h3_graphs():
        missing = sorted(_model_files(graph) - listed)
        assert not missing, f"Graf bu dosyaları yüklüyor ama grup saymıyor: {missing}"


def test_both_h3_graphs_load_eros_max_beta5():
    """Madde 329: the checkpoint the user's liked example was made with, tried after Mystic XXX over
    DaSiWa disappointed. Each graph has two model loaders -- the Director takes one as its FL2VA model
    and the other as its REF2VA model, and picks by mode -- so every loader is asked, found by its
    class rather than its id: what is asked is which model the graph loads, and a third loader would
    slip past a test naming two ids. Whether the group counts the file is the scan's question above:
    unet_name is a plain input it sees."""
    expected = {("MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors", "default")}

    for graph in _h3_graphs():
        loaded = {(node["inputs"]["unet_name"], node["inputs"]["weight_dtype"])
                  for node in graph.values() if node["class_type"] == "UNETLoader"}
        assert loaded == expected, f"Grafiğin model düğümleri bunları yüklüyor: {loaded}"


def test_the_h3_graphs_carry_motion_booster_at_seventy_and_mystic_xxx_at_half():
    """Motion Booster at 0.7 is the user's pick from 213's trial. Mystic XXX came with madde 328 and
    sits at half strength under Eros (madde 329): Eros's author folded Mystic into the checkpoint
    itself, so full strength would lay it on twice. One stack serves all three modes: it takes the
    model the Director picked for its mode (output 5), and REF2VA runs on the I2VA graph (madde 304)
    -- that wire is why the lora needed no new export. The stack keeps its loras inside a JSON string,
    which the model scan above cannot see into -- so it is read here, and its files held to the
    group. Sorted: what is asked is what the stack loads, not which slot holds it."""
    expected = [("H3_Motion_BoosterV2.safetensors", 0.7), ("MysticXXX_MMH3-V4.safetensors", 0.5)]

    for graph in _h3_graphs():
        stack = graph["2678"]["inputs"]
        assert stack["model"] == ["2730", 5], "Yığın Director'ın kipine göre seçtiği modeli almıyor"
        loaded = sorted((slot["lora"], slot["str"]) for slot in json.loads(stack["stack_data"])
                        if slot["on"] and slot["lora"] != "None")
        assert loaded == expected, f"Yığın bunları yüklüyor: {loaded}"

    listed = {row["name"] for row in model_groups.H3_VIDEO}
    missing = [name for name, _strength in expected if name not in listed]
    assert missing == [], f"Grup yığının bu LoRA'larını saymıyor: {missing}"


def test_both_h3_graphs_save_an_mp4():
    """Left on Auto the saver wrote WebM/AV1 in the user's trial (madde 245), which the producer never
    picks up -- and the rest of the app names, plays and joins videos as mp4."""
    for graph in _h3_graphs():
        saver = graph["2568"]
        assert saver["class_type"] == "DaSiWa_EnhancedVideoCombine"
        assert (saver["inputs"]["container"], saver["inputs"]["codec"]) == ("MP4", "H.264")


def test_the_app_knows_no_video_model_until_the_notebook_names_one():
    """Empty means video was not installed: the disk cannot say which model was picked, only the
    notebook can."""
    assert config.VIDEO_MODEL == ""
