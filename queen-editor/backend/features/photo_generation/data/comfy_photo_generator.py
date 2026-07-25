"""PhotoGenerator over ComfyUI -- the only place that knows what the graph looks like.

Node ids come from our own export (queen-editor/workflow_api.json):
  "3"  ImpactWildcardProcessor, _meta.title "POSITIVE"
  "4"  ImpactWildcardProcessor, _meta.title "NEGATIVE"
  "40" Seed (rgthree) -> KSampler, FaceDetailer and both wildcard processors read it

A new export can renumber these; then this file changes and nothing else does.
"""
import json

PROMPT_NODE = "3"
NEGATIVE_NODE = "4"
SEED_NODE = "40"


class ComfyPhotoGenerator:
    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed):
        workflow = self._load()
        self._set_text(workflow, PROMPT_NODE, prompt)
        # An empty negative is written through as empty: leaving the export's own text in place
        # would mean "no negative" silently kept a negative.
        self._set_text(workflow, NEGATIVE_NODE, negative or "")
        # The export ships seed -1: rgthree randomises that in the frontend widget, which does not
        # exist in API mode, so sending it through would pin every render to the same noise.
        workflow[SEED_NODE]["inputs"]["seed"] = seed

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
        for node_id in (PROMPT_NODE, NEGATIVE_NODE, SEED_NODE):
            if node_id not in workflow:
                raise RuntimeError(f"Workflow'da {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow

    @staticmethod
    def _set_text(workflow, node_id, text):
        """Write BOTH text fields.

        Which one the server reads in API mode varies by build (Impact Pack #483: some never
        process wildcard_text), so writing both means this text is used either way.
        """
        workflow[node_id]["inputs"]["wildcard_text"] = text
        workflow[node_id]["inputs"]["populated_text"] = text
