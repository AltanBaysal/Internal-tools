"""Reading a ComfyUI graph off disk (madde 488): the one place the photo, Krea and H3 producers load
their graphs, and the sentences it stops with."""
import json

import pytest

from backend.features.photo_generation.data.comfy_graph import load_graph

GRAPH = {"3": {"inputs": {"text": "eski"}, "class_type": "CLIPTextEncode"},
         "40": {"inputs": {"seed": -1}, "class_type": "Seed (rgthree)"}}


def write(tmp_path, graph, name="graf_api.json"):
    path = tmp_path / name
    path.write_text(json.dumps(graph), encoding="utf-8")
    return str(path)


def test_the_graph_comes_back_as_it_is_on_disk(tmp_path):
    assert load_graph(write(tmp_path, GRAPH), ("3", "40")) == GRAPH


def test_every_call_hands_back_its_own_copy(tmp_path):
    """A producer patches what it is given; the next render must not see that patch."""
    path = write(tmp_path, GRAPH)

    load_graph(path, ("3",))["3"]["inputs"]["text"] = "yamalı"

    assert load_graph(path, ("3",))["3"]["inputs"]["text"] == "eski"


def test_a_missing_file_says_where_it_was_looked_for_and_how_to_make_it(tmp_path):
    path = str(tmp_path / "yok_api.json")

    with pytest.raises(RuntimeError) as blew_up:
        load_graph(path, ("3",))

    said = str(blew_up.value)
    assert path in said
    assert "Export (API)" in said and "commit" in said
    assert blew_up.value.__suppress_context__


def test_a_ui_format_export_is_named_by_its_file(tmp_path):
    path = write(tmp_path, {"nodes": [], "links": []}, name="workflow_photo_krea2_api.json")

    with pytest.raises(RuntimeError) as blew_up:
        load_graph(path, ("3",))

    said = str(blew_up.value)
    assert said.startswith("workflow_photo_krea2_api.json UI formatında")
    assert "Export (API)" in said


def test_every_missing_node_is_named_at_once(tmp_path):
    path = write(tmp_path, GRAPH)

    with pytest.raises(RuntimeError) as blew_up:
        load_graph(path, ("3", "53:19", "40", "53:5"))

    assert str(blew_up.value).startswith("graf_api.json grafiğinde 53:19, 53:5 node yok")
