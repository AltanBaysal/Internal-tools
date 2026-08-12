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
