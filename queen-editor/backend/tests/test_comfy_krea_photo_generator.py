"""Krea 2 Turbo's producer (madde 482): the user's graph, with the prompt, the seed and the size
written in, and nothing else."""
import json

import pytest

from backend import config
from backend.features.photo_generation.data.comfy_krea_photo_generator import (
    ComfyKreaPhotoGenerator,
)
from backend.tests.test_comfy_photo_generator import FakeClient


def generator_at(path=config.KREA2_WORKFLOW_PATH):
    """Over the shipped graph unless a test hands it another one."""
    client = FakeClient()
    return client, ComfyKreaPhotoGenerator(client, path, timeout=60)


def shipped():
    with open(config.KREA2_WORKFLOW_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_the_prompt_and_the_seed_are_written_into_the_graph():
    client, generator = generator_at()

    picture = generator.generate("kraliçe tahtta", "", 42)

    assert picture == b"PNG"
    assert client.submitted["53:19"]["inputs"]["value"] == "kraliçe tahtta"
    assert client.submitted["53:3"]["inputs"]["seed"] == 42
    assert client.waited == ("p1", 60)


def test_the_negative_the_lora_and_its_trigger_never_reach_krea():
    """cfg 1 computes no negative, and the lora box's loras are Illustrious ones that cannot load on
    Krea -- so Slime's word is not put in front of the prompt either. The graph goes as the user
    made it, but for the three nodes."""
    client, generator = generator_at()

    generator.generate("kraliçe tahtta", "blurry", 42, "krea2", "slime")

    sent, own = client.submitted, shipped()
    assert sent["53:19"]["inputs"]["value"] == "kraliçe tahtta"
    assert "blurry" not in json.dumps(sent)
    for node_id in set(own) - {"53:19", "53:3"}:
        assert sent[node_id] == own[node_id], f"{node_id} değişmiş"


@pytest.mark.parametrize("orientation, size", [("yatay", (1280, 720)), ("dikey", (832, 1248))])
def test_a_picture_is_made_at_its_orientations_size(orientation, size):
    """Written into the latent as numbers, so it no longer reads the Resolution Selector."""
    client, generator = generator_at()

    generator.generate("p", "", 1, orientation=orientation)

    latent = client.submitted["53:5"]["inputs"]
    assert (latent["width"], latent["height"]) == size
    assert latent["batch_size"] == 1


def test_no_orientation_leaves_the_graphs_own_size():
    client, generator = generator_at()

    generator.generate("p", "", 1)

    assert client.submitted["53:5"]["inputs"]["width"] == ["57", 0]


def test_krea_takes_every_argument_the_queue_hands_a_producer():
    """One call shape for every producer (ports.PhotoGenerator): what a photo has no use for is
    taken and ignored."""
    _client, generator = generator_at()

    assert generator.generate("p", "", 1, "krea2", "usnr", source=("a.png", b""),
                              end=("b.png", b""), references=(), seconds=8,
                              happy_ending=True, orientation="yatay") == b"PNG"


def test_generate_does_not_mutate_the_file_on_disk():
    before = open(config.KREA2_WORKFLOW_PATH, "rb").read()
    _client, generator = generator_at()

    generator.generate("p", "", 1, orientation="dikey")

    assert open(config.KREA2_WORKFLOW_PATH, "rb").read() == before


def test_a_ui_format_export_is_rejected(tmp_path):
    path = tmp_path / "krea.json"
    path.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")
    _client, generator = generator_at(str(path))

    with pytest.raises(RuntimeError, match="UI formatında"):
        generator.generate("p", "", 1)


@pytest.mark.parametrize("missing", ["53:19", "53:3", "53:5"])
def test_a_missing_node_is_named(tmp_path, missing):
    graph = shipped()
    del graph[missing]
    path = tmp_path / "krea.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    _client, generator = generator_at(str(path))

    with pytest.raises(RuntimeError, match=missing):
        generator.generate("p", "", 1)
