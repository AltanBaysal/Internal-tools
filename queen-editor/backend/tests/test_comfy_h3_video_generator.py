"""The MiniMax H3 video producer: two graphs, a Director that keeps its pictures and its prompt inside
its own JSON, and a SeedControl that takes the noise seed.

Imported inside each test rather than at the top: a module that is not there yet would fail
collection and take every other question in this file down with it.
"""
import json

import pytest

from backend import config

I2VA_SENTENCE = ("For the target video, at 0.00 seconds into the target video, Picture 1 (from "
                 "Shot 1) is fully referenced.")


def fl2va_sentence(seconds):
    return ("How the reference pictures align with the target video — Picture 1 (from Shot 1) "
            "aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns "
            f"with the {seconds}-second mark of the target video.")


def director(mode, pictures, duration=4):
    """The Director as the export carries it: the pictures and the prompt live inside two JSON
    strings, and the prompt a third and a fourth time besides."""
    state = {"version": 2, "mode": mode, "prompt_mode": "simple", "simple_prompt": ""}
    timeline = {"version": 1,
                "items": [{"id": f"image-{slot}", "slot": slot, "start": slot, "type": "image",
                           "value": "example.png"} for slot in range(pictures)],
                "builder_state": state, "resolved_prompt": ""}
    return {"class_type": "MiniMaxH3Director",
            "inputs": {"mode": mode, "prompt": "", "duration": duration, "width": 512,
                       "height": 768, "timeline_data": json.dumps(timeline),
                       "builder_state": json.dumps(state)}}


def seed_control(value=7):
    return {"class_type": "DaSiWa_SeedControl", "inputs": {"seed_value": value}}


I2VA_GRAPH = {"2730": director("I2VA", 1), "2739": seed_control()}
FL2VA_GRAPH = {"2730": director("FL2VA", 2), "2739": seed_control()}


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


def graphs_at(tmp_path, i2va=None, fl2va=None):
    standard = tmp_path / "workflow_video_h3_api.json"
    standard.write_text(json.dumps(i2va if i2va is not None else I2VA_GRAPH), encoding="utf-8")
    ends = tmp_path / "workflow_video_h3_first_last_api.json"
    ends.write_text(json.dumps(fl2va if fl2va is not None else FL2VA_GRAPH), encoding="utf-8")
    return str(standard), str(ends)


def generator(tmp_path, client, i2va=None, fl2va=None, standard_path=None):
    from backend.features.photo_generation.data.comfy_h3_video_generator import (
        ComfyH3VideoGenerator,
    )
    standard, ends = graphs_at(tmp_path, i2va, fl2va)
    return ComfyH3VideoGenerator(client, standard_path or standard, ends, timeout=60)


def sent_director(client):
    return client.submitted["2730"]["inputs"]


def sent_pictures(client):
    return [item["value"] for item in json.loads(sent_director(client)["timeline_data"])["items"]]


def test_a_video_with_no_end_frame_is_rendered_by_the_i2va_graph(tmp_path):
    client = FakeClient()

    data = generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    assert data == b"MP4DATA"
    assert client.uploads == [("P0_0.png", b"PNG")]
    assert sent_director(client)["mode"] == "I2VA"
    assert sent_pictures(client) == ["server-P0_0.png"]


def test_a_video_with_an_end_frame_is_rendered_by_the_fl2va_graph(tmp_path):
    """The producer is told an ending picture, never a mode -- the same seam WAN's producer has, so
    loop and linked videos reach both engines in one shape."""
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"),
                                         end=("P1_0.png", b"END"))

    assert client.uploads == [("P0_0.png", b"PNG"), ("P1_0.png", b"END")]
    assert sent_director(client)["mode"] == "FL2VA"
    # In order: the first picture is where the video starts, the second where it arrives.
    assert sent_pictures(client) == ["server-P0_0.png", "server-P1_0.png"]


def test_an_i2va_prompt_opens_with_the_first_frame_sentence(tmp_path):
    """Which picture sits where is the graph's fact, not the scene's -- so the code says it, in the
    words of the graph's own example, and the writer only writes what happens."""
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    assert sent_director(client)["prompt"] == f"{I2VA_SENTENCE}\n\nmotion"


def test_an_fl2va_prompt_says_where_the_video_arrives_in_the_graph_s_own_seconds(tmp_path):
    client = FakeClient()
    longer = {"2730": director("FL2VA", 2, duration=6), "2739": seed_control()}

    generator(tmp_path, client, fl2va=longer).generate(
        "motion", "", 42, source=("P0_0.png", b"PNG"), end=("P1_0.png", b"END"))

    assert sent_director(client)["prompt"] == f"{fl2va_sentence('6.00')}\n\nmotion"


WRITTEN = "dynv2.\n\nintegrated_multimodal_description: [Shot 1] she turns"
SECTIONS = "integrated_multimodal_description: [Shot 1] she turns"


def test_dynv2_goes_before_the_i2va_picture_sentence(tmp_path):
    """The Motion Booster lora only wakes when dynv2 is the very first word H3 reads (user, madde
    246) -- and the picture sentence is the producer's, so the producer is what can put it there."""
    client = FakeClient()

    generator(tmp_path, client).generate(WRITTEN, "", 42, source=("P0_0.png", b"PNG"))

    assert sent_director(client)["prompt"] == f"dynv2. {I2VA_SENTENCE}\n\n{SECTIONS}"


def test_dynv2_goes_before_the_fl2va_picture_sentence(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate(WRITTEN, "", 42, source=("P0_0.png", b"PNG"),
                                         end=("P1_0.png", b"END"))

    assert sent_director(client)["prompt"] == f"dynv2. {fl2va_sentence('4.00')}\n\n{SECTIONS}"


def test_the_prompt_lands_in_all_four_places_the_director_keeps_one(tmp_path):
    """Which of the four the node reads cannot be told without running it; all four the same makes
    the question go away."""
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    said = sent_director(client)
    timeline = json.loads(said["timeline_data"])
    written = f"{I2VA_SENTENCE}\n\nmotion"
    assert said["prompt"] == written
    assert timeline["builder_state"]["simple_prompt"] == written
    assert timeline["resolved_prompt"] == written
    assert json.loads(said["builder_state"])["simple_prompt"] == written


def test_the_seed_goes_to_the_seed_control(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    assert client.submitted["2739"]["inputs"]["seed_value"] == 42


def test_a_seed_the_job_never_carried_leaves_the_graphs_own(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", None, source=("P0_0.png", b"PNG"))

    assert client.submitted["2739"]["inputs"]["seed_value"] == 7


def test_only_an_mp4_counts_as_the_render(tmp_path):
    # The graph previews through a tiny VAE as it samples; that must not be mistaken for the video.
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    assert client.fetched == ({"outputs": "history"}, (".mp4",))


def test_how_long_a_video_runs_is_the_director_s_duration(tmp_path):
    """Read from the I2VA graph alone, like WAN's standard graph: one number is quoted for every
    video, and the two graphs are held to it by test_workflow_asset."""
    longer = {"2730": director("FL2VA", 2, duration=6), "2739": seed_control()}

    assert generator(tmp_path, FakeClient(), fl2va=longer).seconds() == 4.0


def test_the_shipped_graph_is_never_written_back(tmp_path):
    """Fresh copy per render: a patched prompt left in the file would be the next frame's prompt."""
    client = FakeClient()
    gen = generator(tmp_path, client)

    gen.generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    with open(tmp_path / "workflow_video_h3_api.json", encoding="utf-8") as f:
        assert json.load(f)["2730"]["inputs"]["prompt"] == ""


def test_a_video_without_a_photo_to_hang_on_says_so(tmp_path):
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("motion", "", 42)

    assert "foto" in str(blew_up.value).lower()


def test_an_end_frame_does_not_stand_in_for_the_photo(tmp_path):
    with pytest.raises(RuntimeError) as blew_up:
        generator(tmp_path, FakeClient()).generate("motion", "", 42, end=("P1_0.png", b"END"))

    assert "foto" in str(blew_up.value).lower()


def test_a_missing_graph_names_the_file_it_wants(tmp_path):
    gen = generator(tmp_path, FakeClient(), standard_path=str(tmp_path / "yok.json"))

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    assert "yok.json" in str(blew_up.value)


def test_a_graph_exported_in_ui_format_says_which_export_to_use(tmp_path):
    gen = generator(tmp_path, FakeClient(), i2va={"nodes": [], "links": []})

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    assert "Export (API)" in str(blew_up.value)


@pytest.mark.parametrize("gone", ["2730", "2739"])
def test_a_graph_whose_nodes_moved_names_the_missing_one(tmp_path, gone):
    moved = {k: v for k, v in I2VA_GRAPH.items() if k != gone}
    gen = generator(tmp_path, FakeClient(), i2va=moved)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    assert gone in str(blew_up.value)


def test_a_timeline_holding_a_different_number_of_pictures_says_both(tmp_path):
    """The pictures are written in by position. A graph with room for two, handed one, would render
    with the export's placeholder in the second place and say nothing."""
    wrong = {"2730": director("I2VA", 2), "2739": seed_control()}
    gen = generator(tmp_path, FakeClient(), i2va=wrong)

    with pytest.raises(RuntimeError) as blew_up:
        gen.generate("motion", "", 42, source=("P0_0.png", b"PNG"))

    said = str(blew_up.value)
    assert "2" in said and "1" in said


POOL = [("kedi.png", b"ONE", "picture"), ("kuş.png", b"TWO", "picture")]


def test_a_video_made_from_references_is_rendered_in_ref2va(tmp_path):
    """The mode is a plain string on the Director and ref2va_model is already filled, so no new
    export was needed (madde 304)."""
    client = FakeClient()

    data = generator(tmp_path, client).generate("altı bölüm", "", 42, references=POOL)

    assert data == b"MP4DATA"
    assert sent_director(client)["mode"] == "REF2VA"


def test_every_reference_picture_is_uploaded_and_written_in_order(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate("altı bölüm", "", 42, references=POOL)

    assert client.uploads == [("kedi.png", b"ONE"), ("kuş.png", b"TWO")]
    assert sent_pictures(client) == ["server-kedi.png", "server-kuş.png"]
    items = json.loads(sent_director(client)["timeline_data"])["items"]
    # H3 numbers references by their order, so the row carries where each one stands.
    assert [(item["slot"], item["order"], item["type"]) for item in items] == [
        (0, 0, "image"), (1, 1, "image")]
    assert all(item["enabled"] for item in items)


def test_a_reference_video_needs_no_source_picture(tmp_path):
    # The card is born from the video itself: there is no picture under it (madde 303).
    client = FakeClient()

    generator(tmp_path, client).generate("altı bölüm", "", 42, references=POOL)

    assert client.uploads == [("kedi.png", b"ONE"), ("kuş.png", b"TWO")]


def test_a_reference_prompt_goes_in_as_the_user_wrote_it(tmp_path):
    """The picture sentence belongs to I2VA and FL2VA, where the producer knows which picture sits
    where. A REF2VA prompt is the user's own six sections, and nothing is put in front of it."""
    client = FakeClient()

    generator(tmp_path, client).generate("altı bölüm", "", 42, references=POOL)

    director_inputs = sent_director(client)
    assert director_inputs["prompt"] == "altı bölüm"
    assert json.loads(director_inputs["timeline_data"])["resolved_prompt"] == "altı bölüm"


def test_a_video_with_no_references_is_made_the_way_it_always_was(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"),
                                         references=())

    assert sent_director(client)["mode"] == "I2VA"
    assert sent_director(client)["prompt"].startswith(I2VA_SENTENCE)


MIXED_POOL = [("kedi.png", b"PIC", "picture"),
              ("dans.mp4", b"VID", "video"),
              ("ruzgar.wav", b"SND", "audio")]


def sent_items(client):
    return json.loads(sent_director(client)["timeline_data"])["items"]


def test_every_kind_of_reference_is_written_with_its_own_type(tmp_path):
    """The fields are the node's own, read off its source (21 Eylul): a row says what it is."""
    client = FakeClient()

    generator(tmp_path, client).generate("alti bolum", "", 42, references=MIXED_POOL)

    assert [item["type"] for item in sent_items(client)] == ["image", "video", "audio"]


def test_every_kind_of_reference_is_uploaded(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate("alti bolum", "", 42, references=MIXED_POOL)

    assert client.uploads == [("kedi.png", b"PIC"), ("dans.mp4", b"VID"), ("ruzgar.wav", b"SND")]
    assert [item["value"] for item in sent_items(client)] == [
        "server-kedi.png", "server-dans.mp4", "server-ruzgar.wav"]


def test_only_a_video_row_says_which_half_of_it_is_used(tmp_path):
    """media_mode is the V / A / V+A buttons of the node's own panel, and it belongs to a video row
    alone. Both halves go: the user put that clip in the pool to be followed, and throwing away
    half of it would be a choice nobody asked for."""
    client = FakeClient()

    generator(tmp_path, client).generate("alti bolum", "", 42, references=MIXED_POOL)

    modes = [item.get("media_mode") for item in sent_items(client)]
    assert modes == [None, "video_audio", None]


def test_the_rows_keep_the_pools_own_order(tmp_path):
    # One counter for the whole timeline: the row's order is its place there, whatever kind it is.
    client = FakeClient()

    generator(tmp_path, client).generate("alti bolum", "", 42, references=MIXED_POOL)

    assert [(item["slot"], item["order"], item["start"]) for item in sent_items(client)] == [
        (0, 0, 0), (1, 1, 1), (2, 2, 2)]


def test_no_row_asks_for_a_trim(tmp_path):
    """The node's own defaults are no trim at all, and a clip in the pool has already been through
    the limits (madde 298). Trimming would be the user's to ask for, in an item of its own."""
    client = FakeClient()

    generator(tmp_path, client).generate("alti bolum", "", 42, references=MIXED_POOL)

    assert all("trim_start" not in item and "trim_end" not in item for item in sent_items(client))


# The graph's own lora stack; the producer never touches it -- loras are baked into the exports.
STACK_NODE = "2678"


def shipped_generator(client):
    """The producer over the graphs that ship rather than the test's own: the stack is theirs."""
    from backend.features.photo_generation.data.comfy_h3_video_generator import (
        ComfyH3VideoGenerator,
    )
    return ComfyH3VideoGenerator(client, config.H3_VIDEO_WORKFLOW_PATH,
                                 config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH, timeout=60)


# Kareden's two graphs and Referanstan: every H3 video of the session.
every_mode = pytest.mark.parametrize("asked", [
    {"source": ("P0_0.png", b"PNG")},
    {"source": ("P0_0.png", b"PNG"), "end": ("P1_0.png", b"END")},
    {"references": POOL},
], ids=["i2va", "fl2va", "ref2va"])


@every_mode
def test_every_h3_video_is_rendered_with_eros_max_beta5(asked):
    """Madde 333, the user's pick after both were tried. The Director picks one of the graph's two
    model loaders by its mode, so what reaches ComfyUI is asked of every loader it is sent -- and
    REF2VA has no graph of its own and runs on the I2VA export with its mode changed (madde 304), so
    only the producer can say which model its render loads."""
    client = FakeClient()

    shipped_generator(client).generate("motion", "", 42, **asked)

    loaded = {node["inputs"]["unet_name"] for node in client.submitted.values()
              if node["class_type"] == "UNETLoader"}
    assert loaded == {"MiniMaxH3/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors"}, \
        f"ComfyUI'ye giden model düğümleri bunları yüklüyor: {loaded}"


@every_mode
def test_no_h3_video_is_rendered_with_mystic_xxx(asked):
    """Madde 330: the stack carries Motion Booster alone, in every mode. Mystic's file still comes down -- its notebook row
    stays, so turning it back on is a graph edit -- which is why the stack is what is asked: by name,
    on or off, because whether the loader honours `on` is unknown. Only the producer can say what
    REF2VA's render carries: it has no graph of its own (madde 304)."""
    client = FakeClient()

    shipped_generator(client).generate("motion", "", 42, **asked)

    stack = json.loads(client.submitted[STACK_NODE]["inputs"]["stack_data"])
    named = [slot["lora"] for slot in stack if slot["lora"] != "None"]
    assert "MysticXXX_MMH3-V4.safetensors" not in named, f"Yığının adı olan yuvaları: {named}"
