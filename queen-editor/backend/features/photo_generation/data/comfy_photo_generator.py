"""PhotoGenerator over ComfyUI -- the only place that knows what the graph looks like.

Node ids come from our own export (queen-editor/workflow_api.json):
  "3"  ImpactWildcardProcessor, _meta.title "POSITIVE"
  "4"  ImpactWildcardProcessor, _meta.title "NEGATIVE"
  "27" Power Lora Loader (rgthree) -> which loras are switched on, and how strongly
  "40" Seed (rgthree) -> KSampler, FaceDetailer and both wildcard processors read it
  "45" CheckpointLoaderSimple -> which model renders the frame

A new export can renumber these; then this file changes and nothing else does.
"""
import json

from backend.features.photo_generation.domain import recipes

PROMPT_NODE = "3"
NEGATIVE_NODE = "4"
LORA_NODE = "27"
SEED_NODE = "40"
MODEL_NODE = "45"


class ComfyPhotoGenerator:
    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def models(self):
        """Which checkpoints are installed -- asked of the server, never listed here."""
        return self._client.checkpoints()

    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        """`source` and `end` are nobody's business here: a picture is made from its words alone and
        arrives nowhere. Both are taken because the queue has one call shape for every producer --
        see ports.PhotoGenerator.
        """
        workflow = self._load()
        recipe = self._recipe(model)
        if recipe:
            # A lora that is loaded but never named in the prompt renders an ordinary photo and
            # raises nothing anywhere -- so the recipe's word goes in front of the user's own.
            prompt = f"{recipe['trigger']}, {prompt}" if recipe["trigger"] else prompt
        self._set_text(workflow, PROMPT_NODE, prompt)
        # An empty negative is written through as empty: leaving the export's own text in place
        # would mean "no negative" silently kept a negative.
        self._set_text(workflow, NEGATIVE_NODE, negative or "")
        # The export ships seed -1: rgthree randomises that in the frontend widget, which does not
        # exist in API mode, so sending it through would pin every render to the same noise.
        workflow[SEED_NODE]["inputs"]["seed"] = seed
        # No model means the export's own checkpoint: frames planned before models could be chosen
        # render exactly as they used to, and so does every frame when the list cannot be read.
        if recipe:
            workflow[MODEL_NODE]["inputs"]["ckpt_name"] = recipe["checkpoint"]
            self._set_loras(workflow, recipe["loras"])
        elif model:
            # A bare file name is a checkpoint and nothing more: picking one has never meant picking
            # a lora arrangement, and a frame planned that way keeps rendering the way it did.
            workflow[MODEL_NODE]["inputs"]["ckpt_name"] = model

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history)

    def _load(self):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        with open(self._workflow_path, encoding="utf-8") as f:
            workflow = json.load(f)
        if "nodes" in workflow:
            raise RuntimeError("workflow_api.json UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in (PROMPT_NODE, NEGATIVE_NODE, SEED_NODE, MODEL_NODE):
            if node_id not in workflow:
                raise RuntimeError(f"Workflow'da {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow

    @staticmethod
    def _recipe(model):
        """The recipe this value names, or None when it names a file or nothing at all.

        An id nobody knows stops the render. Falling back to a plain one would hand back a picture
        that is not what was asked for, with nothing anywhere saying the recipe went unapplied.
        """
        if not model.startswith(recipes.PREFIX):
            return None
        recipe_id = model[len(recipes.PREFIX):]
        recipe = recipes.find(recipe_id)
        if recipe is None:
            raise RuntimeError(f"Tanınmayan tarif: {recipe_id} — uygulama bu tarifi bilmiyor, "
                               "defter bu depodan yeni olabilir")
        return recipe

    @staticmethod
    def _set_loras(workflow, loras):
        """Hand the loader the recipe's loras and nothing else.

        A replacement rather than an addition: the graph ships with its own lora switched on, and
        the whole of madde 214 is that Slime was liked with that one OFF. Every lora_* slot goes,
        then the recipe's are written from lora_1 -- the loader reads them in that order.
        """
        node = workflow.get(LORA_NODE)
        if node is None:
            raise RuntimeError(f"Workflow'da {LORA_NODE} node yok — grafik yeniden export edilmiş "
                               "olabilir, LoRA yükleyicisinin id'sini güncelle")
        inputs = node["inputs"]
        for key in [key for key in inputs if key.startswith("lora_")]:
            del inputs[key]
        for index, lora in enumerate(loras, start=1):
            inputs[f"lora_{index}"] = {"on": True, "lora": lora["lora"],
                                       "strength": lora["strength"]}

    @staticmethod
    def _set_text(workflow, node_id, text):
        """Write BOTH text fields.

        Which one the server reads in API mode varies by build (Impact Pack #483: some never
        process wildcard_text), so writing both means this text is used either way.
        """
        workflow[node_id]["inputs"]["wildcard_text"] = text
        workflow[node_id]["inputs"]["populated_text"] = text
