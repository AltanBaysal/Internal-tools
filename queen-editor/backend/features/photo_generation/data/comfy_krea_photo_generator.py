"""PhotoGenerator for Krea 2 Turbo over ComfyUI -- the only place that knows what its graph looks like.

The graph is the user's own export from ComfyUI (madde 482), shipped as it was given in
assets/workflow_photo_krea2_api.json. Written per picture:
  "53:19" PrimitiveStringMultiline "Text String (User Prompt)" -> the prompt
  "53:3"  KSampler -> the seed
  "53:5"  EmptyLatentImage -> width and height, which then no longer read ResolutionSelector "57"
and the lora box's pick (madde 499):
  "53:15" LoraLoaderModelOnly -> the pick's first file, SNOFS; any further file is laid over it
  "53:22" ComfySwitchNode "Switch (Model)" -> its on_true reads the last of them
  "53:23" PrimitiveBoolean "Enable LoRA?" -> off for Boş: the model then comes straight from the
          DiT, and the prompt past the graph's trigger node

The graph's own trigger slot, "53:27"'s string_b, stays empty: it would put the word after the
prompt, and the user asked for it in front, as on Nova (catalog.with_trigger). While the switch is
on that node still appends its ", " to the prompt -- harmless, and the user's graph as it was given.

Everything else stays the user's: 8 steps at cfg 1, the prompt refiner off. A new export can
renumber these; then this file changes and nothing else does.
"""
from backend.features.photo_generation.data.comfy_graph import load_graph
from backend.features.photo_generation.data.lora_chain import chain_loras
from backend.features.photo_generation.domain import catalog
from backend.features.photo_generation.domain.orientation import LANDSCAPE, PORTRAIT

PROMPT_NODE = "53:19"
SEED_NODE = "53:3"
LATENT_NODE = "53:5"
LORA_NODE = "53:15"
MODEL_SWITCH_NODE = "53:22"
LORA_SWITCH_NODE = "53:23"
NODES = (PROMPT_NODE, SEED_NODE, LATENT_NODE, LORA_NODE, MODEL_SWITCH_NODE, LORA_SWITCH_NODE)

# About 1 MP, the user's workflow's own setting, at exactly the ratio of H3's video of the same
# orientation (madde 475), both sides on 16 -- Qwen Image's VAE times the DiT's patch.
# test_workflow_asset holds the three.
SIZES = {LANDSCAPE: (1280, 720), PORTRAIT: (832, 1248)}


class ComfyKreaPhotoGenerator:
    """No generate_batch and no fits_batch: Krea makes a prompt's variants one by one. Its memory
    factor is not something this repo can read, and a 12.9B DiT fills the card at 1 MP anyway."""

    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=(), seconds=None, happy_ending=False, orientation=None):
        """The picture of `prompt` from `seed`, at `orientation`'s size; None leaves the graph's own.
        Drawn with the pick of Krea's own lora box that the frame's line records (catalog.own_pick).

        The rest is taken because the queue has one call shape for every producer, and none of it
        reaches Krea. The negative has nowhere to go: the graph's is the prompt zeroed, and at cfg 1
        ComfyUI does not compute it.
        """
        workflow = load_graph(self._workflow_path, NODES)
        pick = catalog.own_pick(catalog.KREA2, lora)
        workflow[PROMPT_NODE]["inputs"]["value"] = catalog.with_trigger(prompt, pick)
        workflow[SEED_NODE]["inputs"]["seed"] = seed
        if orientation is not None:
            latent = workflow[LATENT_NODE]["inputs"]
            latent["width"], latent["height"] = SIZES[orientation]
        self._set_loras(workflow, pick["files"] if pick else [])
        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history)

    @staticmethod
    def _set_loras(workflow, files):
        """The graph's own loader takes the first file and its switch stays on; the rest are laid
        over it. No file is Boş, which the graph's switch already knows how to draw."""
        workflow[LORA_SWITCH_NODE]["inputs"]["value"] = bool(files)
        if not files:
            return
        first, rest = files[0], files[1:]
        loader = workflow[LORA_NODE]["inputs"]
        loader["lora_name"], loader["strength_model"] = first["lora"], first["strength"]
        workflow[MODEL_SWITCH_NODE]["inputs"]["on_true"] = chain_loras(
            workflow, [LORA_NODE, 0], rest)
