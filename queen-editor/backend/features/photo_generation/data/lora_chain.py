"""Laying loras over a model in a ComfyUI graph -- the one way Krea's and Qwen's producers put their
lora box's files in (madde 499). Which model output the chain starts from, and what reads its end,
stays with each producer: that is the part of the graph only it knows."""

# The ids the added loaders take. Neither graph uses this prefix: Krea's ids are "53:<n>", Qwen's
# plain numbers.
PREFIX = "lora:"


def chain_loras(graph, model, files):
    """One LoraLoaderModelOnly per file, added to `graph` in order, each over the model of the one
    before it, the first over `model` (a ComfyUI link, [node id, output]). The link to the last
    one's model, or `model` itself when there are no files."""
    for index, file in enumerate(files, start=1):
        node_id = f"{PREFIX}{index}"
        graph[node_id] = {"class_type": "LoraLoaderModelOnly",
                          "inputs": {"lora_name": file["lora"], "strength_model": file["strength"],
                                     "model": model},
                          "_meta": {"title": "Load LoRA"}}
        model = [node_id, 0]
    return model
