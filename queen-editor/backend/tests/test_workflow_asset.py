import json

from backend import config

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
