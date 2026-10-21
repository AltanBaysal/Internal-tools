"""PhotoGenerator for Krea 2 Turbo over ComfyUI -- the only place that knows what its graph looks like.

The graph is the user's own export from ComfyUI (madde 482), shipped as it was given in
assets/workflow_photo_krea2_api.json. Three nodes are written per picture:
  "53:19" PrimitiveStringMultiline "Text String (User Prompt)" -> the prompt
  "53:3"  KSampler -> the seed
  "53:5"  EmptyLatentImage -> width and height, which then no longer read ResolutionSelector "57"

Everything else stays the user's: 8 steps at cfg 1, SNOFS at 0.8 behind its switch, the prompt
refiner off. A new export can renumber these; then this file changes and nothing else does.
"""
import json

from backend.features.photo_generation.domain.orientation import LANDSCAPE, PORTRAIT

PROMPT_NODE = "53:19"
SEED_NODE = "53:3"
LATENT_NODE = "53:5"

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

        The rest is taken because the queue has one call shape for every producer, and none of it
        reaches Krea. The negative has nowhere to go: the graph's is the prompt zeroed, and at cfg 1
        ComfyUI does not compute it. The lora box's loras are Illustrious ones that cannot load on
        Krea, which draws with the graph's own SNOFS -- so no lora's trigger goes in front of the
        prompt either, and the prompt reaches the graph exactly as the frame carries it.
        """
        workflow = self._load()
        workflow[PROMPT_NODE]["inputs"]["value"] = prompt
        workflow[SEED_NODE]["inputs"]["seed"] = seed
        if orientation is not None:
            latent = workflow[LATENT_NODE]["inputs"]
            latent["width"], latent["height"] = SIZES[orientation]
        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history)

    def _load(self):
        """Fresh copy per picture -- patching is never written back to the shipped file."""
        with open(self._workflow_path, encoding="utf-8") as f:
            workflow = json.load(f)
        if "nodes" in workflow:
            raise RuntimeError("Krea grafiği UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in (PROMPT_NODE, SEED_NODE, LATENT_NODE):
            if node_id not in workflow:
                raise RuntimeError(f"Krea grafiğinde {node_id} node yok — grafik yeniden export "
                                   "edilmiş olabilir, node id'lerini güncelle")
        return workflow
