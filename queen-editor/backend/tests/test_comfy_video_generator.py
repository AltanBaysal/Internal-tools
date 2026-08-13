import json

import pytest

from backend.features.photo_generation.data.comfy_video_generator import ComfyVideoGenerator

GRAPH = {
    "287": {"class_type": "LoadImage", "inputs": {"image": "example.png"}},
    "233:240": {"class_type": "PromptGenerator", "inputs": {"prompt": "", "seed": -1}},
    "210": {"class_type": "Seed", "inputs": {"seed": -1}},
    "178": {"class_type": "PrimitiveFloat", "inputs": {"value": 5}},
}


class FakeClient:
    def __init__(self):
        self.uploaded = None
        self.submitted = None
        self.fetched = None

    def upload_image(self, name, data):
        self.uploaded = (name, data)
        return f"server-{name}"

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        return {"outputs": "history"}

    def fetch_output(self, history_entry, extensions=None):
        self.fetched = (history_entry, extensions)
        return b"MP4DATA"


def graph_at(tmp_path, graph=None):
    path = tmp_path / "workflow_video_api.json"
    path.write_text(json.dumps(graph if graph is not None else GRAPH), encoding="utf-8")
    return str(path)


def generator(tmp_path, client, graph=None):
    return ComfyVideoGenerator(client, graph_at(tmp_path, graph), timeout=60)


def test_how_long_a_video_runs_is_read_from_the_graph(tmp_path):
    # The graph is where the length is set. Anybody else holding a copy of the number -- the export
    # summary did -- goes on quoting it after the graph moves.
    assert generator(tmp_path, FakeClient()).seconds() == 5


def test_a_fractional_length_is_not_rounded_away(tmp_path):
    graph = {**GRAPH, "178": {"class_type": "PrimitiveFloat", "inputs": {"value": 7.5}}}

    assert generator(tmp_path, FakeClient(), graph).seconds() == 7.5


def test_the_frames_photo_is_uploaded_and_the_graph_points_at_it(tmp_path):
    client = FakeClient()

    data = generator(tmp_path, client).generate("kadın dönüyor", "", 42,
                                                source=("P0_0.png", b"PNGDATA"))

    assert data == b"MP4DATA"
    assert client.uploaded == ("P0_0.png", b"PNGDATA")
    assert client.submitted["287"]["inputs"]["image"] == "server-P0_0.png"
    assert client.submitted["233:240"]["inputs"]["prompt"] == "kadın dönüyor"
    # Both seeds: the sampler's noise and the prompt node's own, so one seed reproduces the video.
    assert client.submitted["210"]["inputs"]["seed"] == 42
    assert client.submitted["233:240"]["inputs"]["seed"] == 42
    # Only an mp4 counts as the render: a preview image node must not be mistaken for it.
    assert client.fetched == ({"outputs": "history"}, (".mp4",))


def test_a_video_without_a_photo_to_hang_on_says_so(tmp_path):
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("prompt", "", 42)

    assert "foto" in str(blew_up.value).lower()


def test_a_missing_graph_names_the_file_it_wants(tmp_path):
    gen = ComfyVideoGenerator(FakeClient(), str(tmp_path / "yok.json"), timeout=60)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "yok.json" in str(blew_up.value)


def test_a_graph_exported_in_ui_format_says_which_export_to_use(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={"nodes": [], "links": []})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "Export (API)" in str(blew_up.value)


def test_a_graph_whose_nodes_moved_names_the_missing_one(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={k: v for k, v in GRAPH.items() if k != "210"})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "210" in str(blew_up.value)


def test_a_seed_the_job_never_carried_leaves_the_graphs_own(tmp_path):
    # A video job plans no seed of its own: the graph's randomisation stands.
    client = FakeClient()

    generator(tmp_path, client).generate("prompt", "", None, source=("P0_0.png", b"PNG"))

    assert client.submitted["210"]["inputs"]["seed"] == -1
