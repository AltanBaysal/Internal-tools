import json

import pytest

from backend.features.photo_generation.data.comfy_video_generator import ComfyVideoGenerator

GRAPH = {
    "287": {"class_type": "LoadImage", "inputs": {"image": "example.png"}},
    "233:240": {"class_type": "PromptGenerator", "inputs": {"prompt": "", "seed": -1}},
    "210": {"class_type": "Seed", "inputs": {"seed": -1}},
    "178": {"class_type": "PrimitiveFloat", "inputs": {"value": 5}},
}

# The second graph -- the arbuzai workflow's FIRST2LASTFRAME hat. Its duration deliberately differs
# from the standard graph's here, so a test can prove which of the two the length is read from.
FIRST_LAST_GRAPH = {
    "338": {"class_type": "LoadImage", "inputs": {"image": "example.png"}},
    "342": {"class_type": "LoadImage", "inputs": {"image": "example.png"}},
    "343": {"class_type": "WanFirstLastFrameToVideo",
            "inputs": {"start_image": ["338", 0], "end_image": ["342", 0]}},
    "333:291": {"class_type": "PromptGenerator", "inputs": {"prompt": "", "seed": -1}},
    "327": {"class_type": "Seed", "inputs": {"seed": -1}},
    "335": {"class_type": "PrimitiveFloat", "inputs": {"value": 9}},
}


class FakeClient:
    def __init__(self):
        self.uploads = []
        self.submitted = None
        self.fetched = None

    def upload_image(self, name, data):
        self.uploads.append((name, data))
        return f"server-{name}"

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        return {"outputs": "history"}

    def fetch_output(self, history_entry, extensions=None):
        self.fetched = (history_entry, extensions)
        return b"MP4DATA"


def graphs_at(tmp_path, graph=None, first_last=None):
    standard = tmp_path / "workflow_video_api.json"
    standard.write_text(json.dumps(graph if graph is not None else GRAPH), encoding="utf-8")
    ends = tmp_path / "workflow_video_first_last_api.json"
    ends.write_text(json.dumps(first_last if first_last is not None else FIRST_LAST_GRAPH),
                    encoding="utf-8")
    return str(standard), str(ends)


def generator(tmp_path, client, graph=None, first_last=None, first_last_path=None):
    standard, ends = graphs_at(tmp_path, graph, first_last)
    return ComfyVideoGenerator(client, standard, first_last_path or ends, timeout=60)


def test_how_long_a_video_runs_is_read_from_the_graph(tmp_path):
    # The graph is where the length is set. Anybody else holding a copy of the number -- the export
    # summary did -- goes on quoting it after the graph moves.
    assert generator(tmp_path, FakeClient()).seconds() == 5


def test_a_fractional_length_is_not_rounded_away(tmp_path):
    graph = {**GRAPH, "178": {"class_type": "PrimitiveFloat", "inputs": {"value": 7.5}}}

    assert generator(tmp_path, FakeClient(), graph).seconds() == 7.5


def test_the_length_is_still_read_from_the_standard_graph(tmp_path):
    """One number is quoted for every video whatever graph made it, so it comes from one place. The
    two graphs are held to the same duration by test_workflow_asset, not by asking both here."""
    assert generator(tmp_path, FakeClient()).seconds() == 5


def test_a_video_with_no_end_frame_is_rendered_by_the_standard_graph(tmp_path):
    client = FakeClient()

    data = generator(tmp_path, client).generate("kadın dönüyor", "", 42,
                                                source=("P0_0.png", b"PNGDATA"))

    assert data == b"MP4DATA"
    assert client.uploads == [("P0_0.png", b"PNGDATA")]
    assert client.submitted["287"]["inputs"]["image"] == "server-P0_0.png"
    assert client.submitted["233:240"]["inputs"]["prompt"] == "kadın dönüyor"
    # Both seeds: the sampler's noise and the prompt node's own, so one seed reproduces the video.
    assert client.submitted["210"]["inputs"]["seed"] == 42
    assert client.submitted["233:240"]["inputs"]["seed"] == 42
    # The graph that ends on a picture is not even opened.
    assert "343" not in client.submitted
    # Only an mp4 counts as the render: a preview image node must not be mistaken for it.
    assert client.fetched == ({"outputs": "history"}, (".mp4",))


def test_a_video_with_an_end_frame_is_rendered_by_the_first_last_graph(tmp_path):
    """The producer is told an ending picture, never a mode: loop and linked differ only in which
    photo arrives here, and both are this one graph."""
    client = FakeClient()

    data = generator(tmp_path, client).generate("kadın dönüyor", "", 42,
                                                source=("P0_0.png", b"PNGDATA"),
                                                end=("P1_0.png", b"ENDDATA"))

    assert data == b"MP4DATA"
    assert client.submitted["338"]["inputs"]["image"] == "server-P0_0.png"
    assert client.submitted["342"]["inputs"]["image"] == "server-P1_0.png"
    assert client.submitted["333:291"]["inputs"]["prompt"] == "kadın dönüyor"
    assert client.submitted["327"]["inputs"]["seed"] == 42
    assert client.submitted["333:291"]["inputs"]["seed"] == 42
    # The standard graph's nodes are nowhere in what was sent.
    assert "287" not in client.submitted


def test_both_frames_reach_the_server_as_uploads(tmp_path):
    # An ending frame is a picture like the first one: ComfyUI renders what it has been given, so a
    # path or a name that never travelled would be a file the server cannot find.
    client = FakeClient()

    generator(tmp_path, client).generate("p", "", 42, source=("P0_0.png", b"PNGDATA"),
                                         end=("P1_0.png", b"ENDDATA"))

    assert client.uploads == [("P0_0.png", b"PNGDATA"), ("P1_0.png", b"ENDDATA")]


def test_an_end_frame_does_not_stand_in_for_the_photo(tmp_path):
    # A video is built on a picture; the ending frame is where it arrives, not what it is made of.
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("p", "", 42, end=("P1_0.png", b"ENDDATA"))

    assert "foto" in str(blew_up.value).lower()


def test_a_video_without_a_photo_to_hang_on_says_so(tmp_path):
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("prompt", "", 42)

    assert "foto" in str(blew_up.value).lower()


def test_a_missing_graph_names_the_file_it_wants(tmp_path):
    _standard, ends = graphs_at(tmp_path)
    gen = ComfyVideoGenerator(FakeClient(), str(tmp_path / "yok.json"), ends, timeout=60)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "yok.json" in str(blew_up.value)


def test_a_missing_first_last_graph_names_the_file_it_wants(tmp_path):
    gen = generator(tmp_path, FakeClient(), first_last_path=str(tmp_path / "sonyok.json"))

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"), end=("P1_0.png", b"END"))

    assert "sonyok.json" in str(blew_up.value)


def test_a_graph_exported_in_ui_format_says_which_export_to_use(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={"nodes": [], "links": []})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "Export (API)" in str(blew_up.value)


def test_a_first_last_graph_exported_in_ui_format_says_which_export_to_use(tmp_path):
    gen = generator(tmp_path, FakeClient(), first_last={"nodes": [], "links": []})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"), end=("P1_0.png", b"END"))

    assert "Export (API)" in str(blew_up.value)


def test_a_graph_whose_nodes_moved_names_the_missing_one(tmp_path):
    gen = generator(tmp_path, FakeClient(), graph={k: v for k, v in GRAPH.items() if k != "210"})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"))

    assert "210" in str(blew_up.value)


def test_a_first_last_graph_whose_nodes_moved_names_the_missing_one(tmp_path):
    moved = {k: v for k, v in FIRST_LAST_GRAPH.items() if k != "342"}
    gen = generator(tmp_path, FakeClient(), first_last=moved)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("prompt", "", 42, source=("P0_0.png", b"PNG"), end=("P1_0.png", b"END"))

    assert "342" in str(blew_up.value)


def test_a_seed_the_job_never_carried_leaves_the_graphs_own(tmp_path):
    # A video job plans no seed of its own: the graph's randomisation stands.
    client = FakeClient()

    generator(tmp_path, client).generate("prompt", "", None, source=("P0_0.png", b"PNG"))

    assert client.submitted["210"]["inputs"]["seed"] == -1
