"""Laying loras over a model in a ComfyUI graph (madde 499): the one way Krea's and Qwen's producers
put their box's files in."""
from backend.features.photo_generation.data.lora_chain import chain_loras

FILES = [{"lora": "a.safetensors", "strength": 0.8}, {"lora": "b.safetensors", "strength": 1.0}]


def test_no_files_hand_the_model_back_and_add_nothing():
    graph = {"1": {"class_type": "UNETLoader", "inputs": {}}}

    assert chain_loras(graph, ["1", 0], []) == ["1", 0]
    assert list(graph) == ["1"]


def test_each_file_is_a_loader_over_the_one_before_it():
    """In the box's order, each at its own strength: the second takes the first's model."""
    graph = {"1": {"class_type": "UNETLoader", "inputs": {}}}

    end = chain_loras(graph, ["1", 0], FILES)

    assert end == ["lora:2", 0]
    assert graph["lora:1"] == {"class_type": "LoraLoaderModelOnly",
                               "inputs": {"lora_name": "a.safetensors", "strength_model": 0.8,
                                          "model": ["1", 0]},
                               "_meta": {"title": "Load LoRA"}}
    assert graph["lora:2"]["inputs"] == {"lora_name": "b.safetensors", "strength_model": 1.0,
                                         "model": ["lora:1", 0]}
