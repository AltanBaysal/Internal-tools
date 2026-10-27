"""Qwen Image 2.1 Turbo's producer (madde 499): the official Turbo template, with the prompt, the
seed, the size and the lora box's pick written in, and nothing else."""
import json

import pytest

from backend import config
from backend.features.photo_generation.data.comfy_qwen_photo_generator import (
    ComfyQwenPhotoGenerator,
)
from backend.tests.test_comfy_photo_generator import FakeClient
from backend.tests.test_workflow_asset import _links


def generator_at(path=config.QWEN_WORKFLOW_PATH):
    """Over the shipped graph unless a test hands it another one."""
    client = FakeClient()
    return client, ComfyQwenPhotoGenerator(client, path, timeout=60)


def shipped():
    with open(config.QWEN_WORKFLOW_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_the_prompt_and_the_seed_are_written_into_the_graph():
    client, generator = generator_at()

    picture = generator.generate("kraliçe tahtta", "", 42, "qwen21turbo", "none")

    assert picture == b"PNG"
    assert client.submitted["452"]["inputs"]["prompt"] == "kraliçe tahtta"
    assert client.submitted["488"]["inputs"]["noise_seed"] == 42
    assert client.waited == ("p1", 60)


def test_translucent_penetration_is_laid_over_the_model_with_its_word_in_front():
    """Between the diffusion model and Qwen's cache, where 484's trial put a lora; its trigger in
    front of the prompt, as Nova's Slime does (the user's call)."""
    client, generator = generator_at()

    generator.generate("kraliçe tahtta", "", 42, "qwen21turbo", "translucent_penetration")

    sent = client.submitted
    assert sent["lora:1"]["inputs"] == {
        "lora_name": "translucent_penetration_v5_qwen_image_2_1.safetensors",
        "strength_model": 1.0, "model": ["451", 0]}
    assert sent["490"]["inputs"]["model"] == ["lora:1", 0]
    assert sent["452"]["inputs"]["prompt"] == "translucent penetration, kraliçe tahtta"
    assert all(link[0] in sent for node in sent.values() for link in _links(node))


def test_no_pick_is_translucent_penetration():
    """The box's first row, as on Krea."""
    client, generator = generator_at()

    generator.generate("p", "", 1, "qwen21turbo", "")

    assert client.submitted["490"]["inputs"]["model"] == ["lora:1", 0]


def test_bos_draws_with_the_model_alone_and_names_no_lora():
    client, generator = generator_at()

    generator.generate("kraliçe tahtta", "blurry", 42, "qwen21turbo", "none")

    sent, own = client.submitted, shipped()
    assert sent["452"]["inputs"]["prompt"] == "kraliçe tahtta"
    assert "blurry" not in json.dumps(sent)
    assert set(sent) == set(own)
    for node_id in set(own) - {"452", "488"}:
        assert sent[node_id] == own[node_id], f"{node_id} değişmiş"


@pytest.mark.parametrize("orientation, size", [("yatay", (1536, 864)), ("dikey", (1024, 1536))])
def test_a_picture_is_made_at_its_orientations_size(orientation, size):
    client, generator = generator_at()

    generator.generate("p", "", 1, "qwen21turbo", "none", orientation=orientation)

    latent = client.submitted["456"]["inputs"]
    assert (latent["width"], latent["height"]) == size
    assert latent["batch_size"] == 1


def test_no_orientation_leaves_the_graphs_own_size():
    client, generator = generator_at()

    generator.generate("p", "", 1, "qwen21turbo", "none")

    latent = client.submitted["456"]["inputs"]
    assert (latent["width"], latent["height"]) == (1024, 1024)


def test_qwen_takes_every_argument_the_queue_hands_a_producer():
    """One call shape for every producer (ports.PhotoGenerator): what a photo has no use for is
    taken and ignored."""
    _client, generator = generator_at()

    assert generator.generate("p", "", 1, "qwen21turbo", "usnr", source=("a.png", b""),
                              end=("b.png", b""), references=(), seconds=8,
                              happy_ending=True, orientation="yatay") == b"PNG"


def test_generate_does_not_mutate_the_file_on_disk():
    before = open(config.QWEN_WORKFLOW_PATH, "rb").read()
    _client, generator = generator_at()

    generator.generate("p", "", 1, "qwen21turbo", "translucent_penetration", orientation="dikey")

    assert open(config.QWEN_WORKFLOW_PATH, "rb").read() == before


def test_a_ui_format_export_is_rejected(tmp_path):
    path = tmp_path / "qwen.json"
    path.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")
    _client, generator = generator_at(str(path))

    with pytest.raises(RuntimeError, match="UI formatında"):
        generator.generate("p", "", 1)


@pytest.mark.parametrize("missing", ["452", "488", "456", "451", "490"])
def test_a_missing_node_is_named(tmp_path, missing):
    graph = shipped()
    del graph[missing]
    path = tmp_path / "qwen.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    _client, generator = generator_at(str(path))

    with pytest.raises(RuntimeError, match=missing):
        generator.generate("p", "", 1)
