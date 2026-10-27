"""Krea 2 Turbo's producer (madde 482): the user's graph, with the prompt, the seed and the size
written in, and nothing else."""
import json

import pytest

from backend import config
from backend.features.photo_generation.data.comfy_krea_photo_generator import (
    ComfyKreaPhotoGenerator,
)
from backend.tests.test_comfy_photo_generator import FakeClient
from backend.tests.test_workflow_asset import _links


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


@pytest.mark.parametrize("lora", ["snofs", "", "slime"])
def test_snofs_draws_with_the_graph_as_the_user_made_it(lora):
    """SNOFS is the user's own workflow: at 0.8 in 53:15, switched on. No pick draws it too, and so
    does Nova's Slime, which is no Krea lora (madde 486, 499). cfg 1 computes no negative, so the
    one typed goes nowhere. The graph goes as it was given, but for the prompt and the seed."""
    client, generator = generator_at()

    generator.generate("kraliçe tahtta", "blurry", 42, "krea2", lora)

    sent, own = client.submitted, shipped()
    assert sent["53:19"]["inputs"]["value"] == "kraliçe tahtta"
    assert "blurry" not in json.dumps(sent)
    assert set(sent) == set(own)
    for node_id in set(own) - {"53:19", "53:3"}:
        assert sent[node_id] == own[node_id], f"{node_id} değişmiş"


def test_snofs_and_slime_are_laid_one_over_the_other_with_slime_s_word_in_front():
    """The user's words: "İkisi aynı anda yüklenir. Slime fotoğrafında SNOFS da etkisini sürdürür."
    Slime's Krea version over SNOFS, at 1.0, and the model switch reading the second; its trigger in
    front of the prompt, as Nova's Slime does (madde 499)."""
    client, generator = generator_at()

    generator.generate("kraliçe tahtta", "", 42, "krea2", "snofs_slime")

    sent = client.submitted
    assert (sent["53:15"]["inputs"]["lora_name"], sent["53:15"]["inputs"]["strength_model"]) == \
        ("snofs_krea_v1_5.safetensors", 0.8)
    assert sent["lora:1"]["inputs"] == {"lora_name": "translucent_penetration_v5_krea2.safetensors",
                                        "strength_model": 1.0, "model": ["53:15", 0]}
    assert sent["53:22"]["inputs"]["on_true"] == ["lora:1", 0]
    assert sent["53:23"]["inputs"]["value"] is True
    assert sent["53:19"]["inputs"]["value"] == "translucent penetration, kraliçe tahtta"
    assert all(link[0] in sent for node in sent.values() for link in _links(node))


def test_bos_switches_the_graph_s_lora_off_and_names_none():
    """Boş: the graph's own switch takes the model straight from the DiT and the prompt past the
    trigger node."""
    client, generator = generator_at()

    generator.generate("kraliçe tahtta", "", 42, "krea2", "none")

    sent = client.submitted
    assert sent["53:23"]["inputs"]["value"] is False
    assert sent["53:19"]["inputs"]["value"] == "kraliçe tahtta"
    assert set(sent) == set(shipped())


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


@pytest.mark.parametrize("missing", ["53:19", "53:3", "53:5", "53:15", "53:22", "53:23"])
def test_a_missing_node_is_named(tmp_path, missing):
    graph = shipped()
    del graph[missing]
    path = tmp_path / "krea.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    _client, generator = generator_at(str(path))

    with pytest.raises(RuntimeError, match=missing):
        generator.generate("p", "", 1)
