import json

import pytest

from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator


class FakeClient:
    def __init__(self):
        self.submitted = None
        self.waited = None

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        self.waited = (prompt_id, timeout)
        return {"outputs": {}}

    def fetch_output(self, history):
        return b"PNG"


def write_graph(tmp_path, graph=None):
    path = tmp_path / "workflow_api.json"
    path.write_text(json.dumps(graph if graph is not None else {
        "3": {"inputs": {"wildcard_text": "eski", "populated_text": "eski"},
              "class_type": "ImpactWildcardProcessor"},
        "40": {"inputs": {"seed": -1}, "class_type": "Seed (rgthree)"},
    }), encoding="utf-8")
    return str(path)


def test_generate_patches_the_graph_and_returns_bytes(tmp_path):
    client = FakeClient()
    generator = ComfyPhotoGenerator(client, write_graph(tmp_path), timeout=60)

    assert generator.generate("kraliçe tahtta", 12345) == b"PNG"

    node3 = client.submitted["3"]["inputs"]
    assert node3["wildcard_text"] == "kraliçe tahtta"      # Impact Pack #483: both fields
    assert node3["populated_text"] == "kraliçe tahtta"
    assert client.submitted["40"]["inputs"]["seed"] == 12345   # never the export's -1
    assert client.waited == ("p1", 60)


def test_generate_does_not_mutate_the_file_on_disk(tmp_path):
    path = write_graph(tmp_path)
    generator = ComfyPhotoGenerator(FakeClient(), path, timeout=60)
    generator.generate("yeni", 1)
    with open(path, encoding="utf-8") as f:
        assert json.load(f)["3"]["inputs"]["wildcard_text"] == "eski"


def test_ui_format_export_is_rejected(tmp_path):
    path = write_graph(tmp_path, {"nodes": [], "links": []})
    with pytest.raises(RuntimeError) as exc:
        ComfyPhotoGenerator(FakeClient(), path, timeout=60).generate("x", 1)
    assert "Export (API)" in str(exc.value)


def test_missing_node_is_reported(tmp_path):
    path = write_graph(tmp_path, {"3": {"inputs": {"wildcard_text": "", "populated_text": ""}}})
    with pytest.raises(RuntimeError) as exc:
        ComfyPhotoGenerator(FakeClient(), path, timeout=60).generate("x", 1)
    assert "40" in str(exc.value)
