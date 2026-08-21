import json

from backend import config
from backend.features.producers.domain.model_groups import GROUPS

# The shipped graph is an asset, so its shape is verified here: a UI-format export or a renamed
# node would only surface as a failed render on Colab otherwise.


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
