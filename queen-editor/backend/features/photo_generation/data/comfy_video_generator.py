"""The video producer over ComfyUI -- the only place that knows what the video graph looks like.

Node ids come from our own export (queen-editor/workflow_video_api.json). They are inherited
knowledge from collab-toolbox's photo_to_video notebook, which drives the same WAN 2.2 I2V graph:
  "287"     LoadImage        -> the frame's photo
  "233:240" PromptGenerator  -> the video prompt (and its own seed)
  "210"     Seed (rgthree)   -> the sampler's noise seed
  "178"     PrimitiveFloat   -> how many seconds one render runs

A new export can renumber these; then this file changes and nothing else does. The duration is read
rather than patched: the graph is where it is set (design v3, madde 28), and this file is the only
one that knows where in the graph that is -- so anybody who needs the number asks instead of
keeping a copy.
"""
import json

IMAGE_NODE = "287"
PROMPT_NODE = "233:240"
SEED_NODE = "210"
DURATION_NODE = "178"

# What counts as the render. A video graph often carries a preview image node too, so the file is
# chosen by its own extension rather than by which output key it landed in.
VIDEO_EXTENSIONS = (".mp4",)


class ComfyVideoGenerator:
    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", source=None):
        """`source` is the frame's photo as (name, bytes) -- an I2V render hangs on a picture.

        `negative` and `model` belong to the port rather than to this graph: both are baked into
        the export, and a video job carries neither.
        """
        if not source:
            raise RuntimeError("Video için kaynak foto verilmedi")
        workflow = self._load()
        name, data = source
        workflow[IMAGE_NODE]["inputs"]["image"] = self._client.upload_image(name, data)
        workflow[PROMPT_NODE]["inputs"]["prompt"] = prompt
        if seed is not None:
            # Both seeds: the sampler's noise and PromptGenerator's own, so the same seed
            # reproduces the video even when the prompt carries wildcard syntax. A job with no seed
            # leaves the graph's own value where it is.
            workflow[SEED_NODE]["inputs"]["seed"] = seed
            workflow[PROMPT_NODE]["inputs"]["seed"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history, extensions=VIDEO_EXTENSIONS)

    def seconds(self):
        """How long one render runs, as the graph has it. Float on purpose: the field is one, and
        rounding it here would be a second version of the truth as surely as a copy would be."""
        return float(self._load()[DURATION_NODE]["inputs"]["value"])

    def _load(self):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        try:
            with open(self._workflow_path, encoding="utf-8") as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"Video grafiği yok: {self._workflow_path} — ComfyUI'de "
                "'Workflow → Export (API)' ile kaydet ve repoya commit'le") from None
        if "nodes" in workflow:
            raise RuntimeError("workflow_video_api.json UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in (IMAGE_NODE, PROMPT_NODE, SEED_NODE, DURATION_NODE):
            if node_id not in workflow:
                raise RuntimeError(f"Video grafiğinde {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow
