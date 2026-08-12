import json

import pytest

from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator


class FakeClient:
    def __init__(self, checkpoints=()):
        self.submitted = None
        self.waited = None
        self._checkpoints = list(checkpoints)

    def checkpoints(self):
        return list(self._checkpoints)

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
        "4": {"inputs": {"wildcard_text": "eski negatif", "populated_text": "eski negatif"},
              "class_type": "ImpactWildcardProcessor"},
        "40": {"inputs": {"seed": -1}, "class_type": "Seed (rgthree)"},
        "45": {"inputs": {"ckpt_name": "export.safetensors"},
               "class_type": "CheckpointLoaderSimple"},
    }), encoding="utf-8")
    return str(path)


def generator_at(tmp_path, graph=None):
    client = FakeClient()
    return client, ComfyPhotoGenerator(client, write_graph(tmp_path, graph), timeout=60)


def test_the_photo_producer_is_installed_when_the_renderer_lists_a_model(tmp_path):
    generator = ComfyPhotoGenerator(FakeClient(checkpoints=["nova.safetensors"]),
                                    write_graph(tmp_path), timeout=60)

    assert generator.installed() is True


def test_the_photo_producer_is_not_installed_when_the_renderer_lists_none(tmp_path):
    generator = ComfyPhotoGenerator(FakeClient(checkpoints=[]), write_graph(tmp_path), timeout=60)

    assert generator.installed() is False


def test_generate_patches_prompt_negative_and_seed(tmp_path):
    client, generator = generator_at(tmp_path)

    assert generator.generate("kraliçe tahtta", "blurry", 12345) == b"PNG"

    node3 = client.submitted["3"]["inputs"]
    node4 = client.submitted["4"]["inputs"]
    assert node3["wildcard_text"] == "kraliçe tahtta"       # Impact Pack #483: both fields
    assert node3["populated_text"] == "kraliçe tahtta"
    assert node4["wildcard_text"] == "blurry"
    assert node4["populated_text"] == "blurry"
    assert client.submitted["40"]["inputs"]["seed"] == 12345   # never the export's -1
    assert client.waited == ("p1", 60)


def test_empty_negative_clears_the_exports_own_text(tmp_path):
    # "no negative" must mean no negative, not "whatever the export shipped".
    client, generator = generator_at(tmp_path)
    generator.generate("kraliçe", "", 1)
    assert client.submitted["4"]["inputs"]["populated_text"] == ""


def test_generate_does_not_mutate_the_file_on_disk(tmp_path):
    client = FakeClient()
    path = write_graph(tmp_path)
    ComfyPhotoGenerator(client, path, timeout=60).generate("yeni", "yeni negatif", 1)
    with open(path, encoding="utf-8") as f:
        graph = json.load(f)
    assert graph["3"]["inputs"]["wildcard_text"] == "eski"
    assert graph["4"]["inputs"]["wildcard_text"] == "eski negatif"


def test_ui_format_export_is_rejected(tmp_path):
    _client, generator = generator_at(tmp_path, {"nodes": [], "links": []})
    with pytest.raises(RuntimeError) as exc:
        generator.generate("x", "", 1)
    assert "Export (API)" in str(exc.value)


def test_the_chosen_model_is_written_to_the_checkpoint_node(tmp_path):
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "başka.safetensors")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "başka.safetensors"


def test_no_model_leaves_the_graphs_own_checkpoint_alone(tmp_path):
    # Frames planned before models were a thing, and every frame when the list cannot be read:
    # the export's own default is what renders them, exactly as before.
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "export.safetensors"


def test_the_installed_models_come_from_the_server(tmp_path):
    client = FakeClient(checkpoints=["nova.safetensors", "başka.safetensors"])
    generator = ComfyPhotoGenerator(client, write_graph(tmp_path), timeout=60)

    assert generator.models() == ["nova.safetensors", "başka.safetensors"]


@pytest.mark.parametrize("missing", ["3", "4", "40", "45"])
def test_missing_node_is_reported(tmp_path, missing):
    graph = {
        "3": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "4": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "40": {"inputs": {"seed": -1}},
        "45": {"inputs": {"ckpt_name": "export.safetensors"}},
    }
    del graph[missing]
    _client, generator = generator_at(tmp_path, graph)
    with pytest.raises(RuntimeError) as exc:
        generator.generate("x", "", 1)
    assert missing in str(exc.value)
