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

from backend.features.photo_generation.domain import catalog

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

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=()):
        """`source` and `end` are nobody's business here: a picture is made from its words alone and
        arrives nowhere. Both are taken because the queue has one call shape for every producer --
        see ports.PhotoGenerator.
        """
        workflow = self._load()
        model, lora = catalog.LEGACY.get(model, (model, lora))
        chosen = self._model(model)
        extra = self._lora(lora)
        if extra and extra["trigger"]:
            # A lora that is loaded but never named in the prompt renders an ordinary photo and
            # raises nothing anywhere -- so its word goes in front of the user's own.
            prompt = f"{extra['trigger']}, {prompt}"
        self._set_text(workflow, PROMPT_NODE, prompt)
        # An empty negative is written through as empty: leaving the export's own text in place
        # would mean "no negative" silently kept a negative.
        self._set_text(workflow, NEGATIVE_NODE, negative or "")
        # The export ships seed -1: rgthree randomises that in the frontend widget, which does not
        # exist in API mode, so sending it through would pin every render to the same noise.
        workflow[SEED_NODE]["inputs"]["seed"] = seed
        # No model means the export's own checkpoint: frames planned before models could be chosen
        # render exactly as they used to, and so does every frame when the list cannot be read.
        if chosen:
            workflow[MODEL_NODE]["inputs"]["ckpt_name"] = chosen["checkpoint"]
            # The pick fills the loader alone rather than joining the lora the export ships with:
            # Slime was liked with USNR off (madde 214). Boş empties it.
            self._set_loras(workflow, [extra] if extra else [])
        elif model:
            # A bare file name is a checkpoint and nothing more: picking one has never meant picking
            # a lora, and a frame planned that way keeps rendering the way it did -- with the
            # export's own USNR, which is the default anyway.
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
    def _model(model):
        """The catalog model this value names, or None when it names a file or nothing at all.

        An old `recipe:` value that catalog.LEGACY does not know stops the render. Falling back to a
        plain one would hand back a picture that is not what was asked for, with nothing anywhere
        saying the pick went unapplied.
        """
        if model.startswith(catalog.LEGACY_PREFIX):
            raise RuntimeError(f"Tanınmayan tarif: {model[len(catalog.LEGACY_PREFIX):]} — "
                               "uygulama bu tarifi bilmiyor, defter bu depodan yeni olabilir")
        return catalog.find_model(model)

    @staticmethod
    def _lora(lora):
        """The catalog lora this value names, or None for Boş. A frame that names none renders with
        the default (madde 238). An id nobody knows stops the render, for the same reason an unknown
        model does."""
        if lora == catalog.NO_LORA:
            return None
        lora = lora or catalog.DEFAULT_LORA
        found = catalog.find_lora(lora)
        if found is None:
            raise RuntimeError(f"Tanınmayan LoRA: {lora} — uygulama bu LoRA'yı bilmiyor, "
                               "defter bu depodan yeni olabilir")
        return found

    @staticmethod
    def _set_loras(workflow, loras):
        """Hand the loader these loras and nothing else.

        A replacement rather than an addition: the graph ships with its own lora switched on, and
        the whole of madde 214 is that Slime was liked with that one OFF. Every lora_* slot goes,
        then these are written from lora_1 -- the loader reads them in that order.
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
