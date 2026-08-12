import json

import pytest

from backend.features.photo_generation.data.comfy_audio_generator import ComfyAudioGenerator

GRAPH = {
    "1": {"class_type": "VHS_LoadVideoPath", "inputs": {"video": "example.mp4"}},
    "2": {"class_type": "MMAudioSampler", "inputs": {"prompt": "", "seed": -1}},
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
        return b"WAVDATA"


def graph_at(tmp_path, graph=None):
    path = tmp_path / "workflow_audio_api.json"
    path.write_text(json.dumps(graph if graph is not None else GRAPH), encoding="utf-8")
    return str(path)


def generator(tmp_path, client, graph=None):
    return ComfyAudioGenerator(client, graph_at(tmp_path, graph), timeout=60)


def test_the_frames_video_is_uploaded_and_the_graph_points_at_it(tmp_path):
    client = FakeClient()

    data = generator(tmp_path, client).generate("fabric rustling", "", 7,
                                                source=("0_a_V1_0.mp4", b"MP4DATA"))

    assert data == b"WAVDATA"
    assert client.uploaded == ("0_a_V1_0.mp4", b"MP4DATA")
    assert client.submitted["1"]["inputs"]["video"] == "server-0_a_V1_0.mp4"
    assert client.submitted["2"]["inputs"]["prompt"] == "fabric rustling"
    assert client.submitted["2"]["inputs"]["seed"] == 7
    # Only a wav counts as the render: the graph may publish a preview of the video too.
    assert client.fetched == ({"outputs": "history"}, (".wav",))


def test_a_sound_without_a_video_to_lay_it_over_says_so(tmp_path):
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("prompt", "", 7)

    assert "video" in str(blew_up.value).lower()


def test_a_missing_graph_names_the_file_it_wants(tmp_path):
    gen = ComfyAudioGenerator(FakeClient(), str(tmp_path / "yok.json"), timeout=60)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 7, source=("0_a_V1_0.mp4", b"MP4"))

    assert "yok.json" in str(blew_up.value)


def test_a_graph_exported_in_ui_format_says_which_export_to_use(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={"nodes": [], "links": []})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 7, source=("0_a_V1_0.mp4", b"MP4"))

    assert "Export (API)" in str(blew_up.value)


def test_a_graph_whose_nodes_moved_names_the_missing_one(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={k: v for k, v in GRAPH.items() if k != "2"})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 7, source=("0_a_V1_0.mp4", b"MP4"))

    assert "2" in str(blew_up.value)


def test_a_seed_the_job_never_carried_leaves_the_graphs_own(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate("prompt", "", None, source=("0_a_V1_0.mp4", b"MP4"))

    assert client.submitted["2"]["inputs"]["seed"] == -1
