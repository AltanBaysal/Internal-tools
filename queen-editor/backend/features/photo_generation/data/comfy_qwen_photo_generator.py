"""PhotoGenerator for Qwen Image 2.1 Turbo over ComfyUI -- the only place that knows what its graph
looks like.

The graph is Comfy-Org's official Turbo text-to-image template (madde 499), flattened out of its
subgraph into API format by hand in assets/workflow_photo_qwen_api.json, with the template's own
node ids. Written per picture:
  "452" TextEncodeQwenImage21 -> the prompt
  "488" RandomNoise -> the seed
  "456" EmptyLatentImage -> width and height
  "490" QwenImage21Cache -> its model is the last lora of the pick, laid over "451" UNETLoader

Everything else stays the template's: the 8-step ManualSigmas schedule, euler, cfg 1. The template's
prompt enhancer, off there, is not in the graph: ComfyUI checks the file of every loader it is sent,
and the enhancer's is 9.47 GB nobody draws with (spec, karar 5).
"""
from backend.features.photo_generation.data.comfy_graph import load_graph
from backend.features.photo_generation.data.lora_chain import chain_loras
from backend.features.photo_generation.domain import catalog
from backend.features.photo_generation.domain.orientation import LANDSCAPE, PORTRAIT

PROMPT_NODE = "452"
NOISE_NODE = "488"
LATENT_NODE = "456"
MODEL_NODE = "451"
CACHE_NODE = "490"
NODES = (PROMPT_NODE, NOISE_NODE, LATENT_NODE, MODEL_NODE, CACHE_NODE)

# Exactly the ratio of H3's video of the same orientation (madde 475), on multiples of 32 as the
# template's note asks, and inside the 1.0 - 2.5 MP Translucent Penetration's Qwen version was
# trained for: 1.33 and 1.57 MP. The photo graph's own sizes. test_workflow_asset holds them.
SIZES = {LANDSCAPE: (1536, 864), PORTRAIT: (1024, 1536)}


class ComfyQwenPhotoGenerator:
    """No generate_batch and no fits_batch: Qwen makes a prompt's variants one by one, as Krea does
    -- its memory factor is not something this repo can read."""

    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=(), seconds=None, happy_ending=False, orientation=None):
        """The picture of `prompt` from `seed`, at `orientation`'s size; None leaves the graph's own.
        Drawn with the pick of Qwen's own lora box that the frame's line records
        (catalog.own_pick).

        The rest is taken because the queue has one call shape for every producer, and none of it
        reaches Qwen. The negative has nowhere to go: at cfg 1 ComfyUI does not compute it.
        """
        workflow = load_graph(self._workflow_path, NODES)
        pick = catalog.own_pick(catalog.QWEN, lora)
        workflow[PROMPT_NODE]["inputs"]["prompt"] = catalog.with_trigger(prompt, pick)
        workflow[NOISE_NODE]["inputs"]["noise_seed"] = seed
        if orientation is not None:
            latent = workflow[LATENT_NODE]["inputs"]
            latent["width"], latent["height"] = SIZES[orientation]
        workflow[CACHE_NODE]["inputs"]["model"] = chain_loras(
            workflow, [MODEL_NODE, 0], pick["files"] if pick else [])
        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history)
