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


# The lora loader as the real export ships it: one slot, switched on, carrying the style lora the
# graph has always rendered with. A model's frame replaces this with the lora box's pick.
SHIPPED_LORAS = {"lora_1": {"on": True, "lora": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors",
                            "strength": 0.8}}


def write_graph(tmp_path, graph=None):
    path = tmp_path / "workflow_api.json"
    path.write_text(json.dumps(graph if graph is not None else {
        "3": {"inputs": {"wildcard_text": "eski", "populated_text": "eski"},
              "class_type": "ImpactWildcardProcessor"},
        "4": {"inputs": {"wildcard_text": "eski negatif", "populated_text": "eski negatif"},
              "class_type": "ImpactWildcardProcessor"},
        "27": {"inputs": dict(SHIPPED_LORAS), "class_type": "Power Lora Loader (rgthree)"},
        "40": {"inputs": {"seed": -1}, "class_type": "Seed (rgthree)"},
        "45": {"inputs": {"ckpt_name": "export.safetensors"},
               "class_type": "CheckpointLoaderSimple"},
    }), encoding="utf-8")
    return str(path)


def lora_slots(inputs):
    """The loader's lora rows only -- the node also carries its header widget, the model and the
    clip, and none of those say which lora is switched on."""
    return {key: value for key, value in inputs.items() if key.startswith("lora_")}


def generator_at(tmp_path, graph=None):
    client = FakeClient()
    return client, ComfyPhotoGenerator(client, write_graph(tmp_path, graph), timeout=60)


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
    assert lora_slots(client.submitted["27"]["inputs"]) == SHIPPED_LORAS


def test_a_bare_file_name_still_leaves_the_loras_alone(tmp_path):
    """Picking a checkpoint has never meant picking a lora arrangement, and a frame planned that way
    has to keep rendering the way it did."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "başka.safetensors")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "başka.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == SHIPPED_LORAS


USNR = {"lora_1": {"on": True, "lora": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors",
                   "strength": 0.8}}
SLIME = {"lora_1": {"on": True, "lora": "translucent_penetration_v5.safetensors", "strength": 0.9}}


def test_a_nova_frame_that_names_no_lora_renders_with_usnr(tmp_path):
    """The value is the model's id, not its file -- written into the loader as-is it would ask
    ComfyUI for a checkpoint called `nova3dcg`. And a frame that names no lora renders with the
    default, USNR at 0.8 (madde 238): what Standart meant on Nova, so a frame sent under it renders
    as it did."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "nova3dcg")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "nova3DCGXL_ilV90.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == USNR


def test_a_dasiwa_frame_that_names_no_lora_renders_with_usnr(tmp_path):
    """The default is the lora box's, not the model's: there is no arrangement of a model's own any
    more, and the user asked for USNR on every model (madde 238)."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "dasiwa")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == \
        "DasiwaIllustriousAnime_epitaphecstasy.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == USNR


@pytest.mark.parametrize("model", ["nova3dcg", "dasiwa"])
def test_usnr_chosen_loads_usnr_alone_and_leaves_the_prompt(tmp_path, model):
    """USNR is a row of the lora box now, over any model. It needs no word in the prompt."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, model, "usnr")

    assert lora_slots(client.submitted["27"]["inputs"]) == USNR
    assert client.submitted["3"]["inputs"]["populated_text"] == "kraliçe"


@pytest.mark.parametrize("model", ["nova3dcg", "dasiwa"])
def test_none_chosen_loads_no_lora_and_leaves_the_prompt(tmp_path, model):
    """Boş means no lora at all -- the export's USNR goes too, or Boş would still render with it."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, model, "none")

    assert lora_slots(client.submitted["27"]["inputs"]) == {}
    assert client.submitted["3"]["inputs"]["populated_text"] == "kraliçe"


def test_a_chosen_lora_replaces_whatever_the_loader_shipped(tmp_path):
    """The export ships USNR switched on, and the user picked Slime because USNR was off when they
    liked what they saw (madde 214). A pick fills the slots alone, never beside what was there."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "nova3dcg", "slime")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "nova3DCGXL_ilV90.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == SLIME


def test_a_chosen_loras_trigger_opens_the_prompt(tmp_path):
    """A lora that is loaded but never named in the prompt changes nothing -- the render comes back
    ordinary and no error is raised anywhere. The lora carries the word, so picking it is enough."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe tahtta", "", 1, "nova3dcg", "slime")

    node3 = client.submitted["3"]["inputs"]
    assert node3["wildcard_text"] == "translucent penetration, kraliçe tahtta"
    assert node3["populated_text"] == "translucent penetration, kraliçe tahtta"


def test_the_default_leaves_the_prompt_and_the_negative_alone(tmp_path):
    """Only a lora that needs a word carries one, and the negative is nobody's lora."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "blurry", 1, "nova3dcg")

    assert client.submitted["3"]["inputs"]["populated_text"] == "kraliçe"
    assert client.submitted["4"]["inputs"]["populated_text"] == "blurry"


def test_a_lora_goes_onto_any_model_it_is_chosen_with(tmp_path):
    """The two boxes are independent: Slime over DaSiWa is a pick the panel allows, and it is what
    madde 222's trial is about."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "dasiwa", "slime")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == \
        "DasiwaIllustriousAnime_epitaphecstasy.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == SLIME


def test_an_old_slime_recipe_renders_as_nova_with_slime(tmp_path):
    """Frames planned before the split carry `recipe:slime` in the plan. No migration is written
    (the user's call), but they render as they were picked."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe tahtta", "", 1, "recipe:slime")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "nova3DCGXL_ilV90.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == SLIME
    assert client.submitted["3"]["inputs"]["populated_text"] == \
        "translucent penetration, kraliçe tahtta"


def test_an_old_nova_recipe_renders_as_nova_with_usnr(tmp_path):
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, "recipe:nova3dcg")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "nova3DCGXL_ilV90.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == USNR


def test_an_unknown_lora_stops_the_render(tmp_path):
    """Rendering without it would hand back a photo that is not what was asked for, with nothing
    anywhere saying the lora was never applied."""
    _client, generator = generator_at(tmp_path)

    with pytest.raises(RuntimeError) as exc:
        generator.generate("kraliçe", "", 1, "nova3dcg", "yok")

    assert "yok" in str(exc.value)


@pytest.mark.parametrize("retired", ["novaorange", "novaanime"])
def test_a_retired_nova_recipe_renders_as_nova_3dcg(tmp_path, retired):
    """A frame planned with one of the two removed Novas still carries its name, in the plan and in
    the project's settings. The user's call (madde 226): it renders as Nova 3DCG, quietly, rather
    than stopping the queue over a model nobody used."""
    client, generator = generator_at(tmp_path)

    generator.generate("kraliçe", "", 1, f"recipe:{retired}")

    assert client.submitted["45"]["inputs"]["ckpt_name"] == "nova3DCGXL_ilV90.safetensors"
    assert lora_slots(client.submitted["27"]["inputs"]) == USNR


def test_an_unknown_recipe_stops_the_render(tmp_path):
    """Falling back to a plain render would hand back a photo that is not what was asked for, with
    nothing anywhere saying the recipe was never applied."""
    _client, generator = generator_at(tmp_path)

    with pytest.raises(RuntimeError) as exc:
        generator.generate("kraliçe", "", 1, "recipe:yok")

    assert "yok" in str(exc.value)


def test_a_model_on_a_graph_with_no_lora_loader_says_which_node_is_missing(tmp_path):
    """A re-export can renumber the graph. Asked for only when a model needs it: demanding the
    loader on every render would break a graph that never had one."""
    graph = {
        "3": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "4": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "40": {"inputs": {"seed": -1}},
        "45": {"inputs": {"ckpt_name": "export.safetensors"}},
    }
    _client, generator = generator_at(tmp_path, graph)

    with pytest.raises(RuntimeError) as exc:
        generator.generate("kraliçe", "", 1, "nova3dcg", "slime")

    assert "27" in str(exc.value)


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
