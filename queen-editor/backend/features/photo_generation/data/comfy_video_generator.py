"""The video producer over ComfyUI -- the only place that knows what the video graphs look like.

Two graphs, because a video that ends on a picture is a different pipeline rather than the same one
with a node swapped: the FIRST2LASTFRAME hat carries its own checkpoints, its own CLIP vision and
its own sampling. Moving standard production onto it would change how every video already made
would look, so both ship and the job decides which one runs.

Node ids come from our own exports. workflow_video_api.json (WAN 2.2 I2V, inherited knowledge from
collab-toolbox's photo_to_video notebook):
  "287"     LoadImage        -> the frame's photo
  "233:240" PromptGenerator  -> the video prompt (and its own seed)
  "210"     Seed (rgthree)   -> the sampler's noise seed
  "178"     PrimitiveFloat   -> how many seconds one render runs

workflow_video_first_last_api.json (the arbuzai workflow's FIRST2LASTFRAME group):
  "338"     LoadImage        -> the frame the video starts on
  "342"     LoadImage        -> the frame it ends on
  "333:291" PromptGenerator  -> the video prompt (and its own seed)
  "327"     Seed (rgthree)   -> the sampler's noise seed

A new export can renumber these; then this file changes and nothing else does. The duration is read
rather than patched: the graph is where it is set (design v3, madde 28), and this file is the only
one that knows where in the graph that is -- so anybody who needs the number asks instead of
keeping a copy. It is read from the standard graph alone, because one number is quoted for every
video whatever graph made it; that the two graphs agree is held by test_workflow_asset.
"""
import json
import os

IMAGE_NODE = "287"
PROMPT_NODE = "233:240"
SEED_NODE = "210"
DURATION_NODE = "178"
STANDARD_NODES = (IMAGE_NODE, PROMPT_NODE, SEED_NODE, DURATION_NODE)

FIRST_LAST_START_NODE = "338"
FIRST_LAST_END_NODE = "342"
FIRST_LAST_PROMPT_NODE = "333:291"
FIRST_LAST_SEED_NODE = "327"
# No duration node: the length is read from the standard graph alone, so demanding one here would
# fail a first-last render over a number it never looks at.
FIRST_LAST_NODES = (FIRST_LAST_START_NODE, FIRST_LAST_END_NODE, FIRST_LAST_PROMPT_NODE,
                    FIRST_LAST_SEED_NODE)

# What counts as the render. A video graph often carries a preview image node too, so the file is
# chosen by its own extension rather than by which output key it landed in.
VIDEO_EXTENSIONS = (".mp4",)


class ComfyVideoGenerator:
    def __init__(self, client, workflow_path, first_last_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._first_last_path = first_last_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        """`source` is the frame's photo as (name, bytes) -- an I2V render hangs on a picture.

        `end` is the picture the video arrives at, same shape, and giving one is the whole of the
        decision made here: with an ending frame the render runs on the first-last graph, without
        one it runs exactly as it always has. Which frame that picture belongs to -- the frame's own
        for a loop, the next one's for a linked video -- is the queue's answer, so the word "mode"
        never reaches this layer.

        `negative` and `model` belong to the port rather than to these graphs: both are baked into
        the exports, and a video job carries neither.
        """
        if not source:
            # The ending frame is where the video arrives, not what it is built on.
            raise RuntimeError("Video için kaynak foto verilmedi")
        if end:
            workflow = self._load(self._first_last_path, FIRST_LAST_NODES)
            image_node, prompt_node, seed_node = (FIRST_LAST_START_NODE, FIRST_LAST_PROMPT_NODE,
                                                  FIRST_LAST_SEED_NODE)
        else:
            workflow = self._load(self._workflow_path, STANDARD_NODES)
            image_node, prompt_node, seed_node = IMAGE_NODE, PROMPT_NODE, SEED_NODE

        workflow[image_node]["inputs"]["image"] = self._client.upload_image(*source)
        if end:
            # Uploaded after the first one and never before it: an ending frame is a picture the
            # server has to hold, exactly like the photo the video hangs on.
            workflow[FIRST_LAST_END_NODE]["inputs"]["image"] = self._client.upload_image(*end)
        workflow[prompt_node]["inputs"]["prompt"] = prompt
        if seed is not None:
            # Both seeds: the sampler's noise and PromptGenerator's own, so the same seed
            # reproduces the video even when the prompt carries wildcard syntax. A job with no seed
            # leaves the graph's own value where it is.
            workflow[seed_node]["inputs"]["seed"] = seed
            workflow[prompt_node]["inputs"]["seed"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history, extensions=VIDEO_EXTENSIONS)

    def seconds(self):
        """How long one render runs, as the graph has it. Float on purpose: the field is one, and
        rounding it here would be a second version of the truth as surely as a copy would be."""
        standard = self._load(self._workflow_path, STANDARD_NODES)
        return float(standard[DURATION_NODE]["inputs"]["value"])

    def _load(self, path, required):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        try:
            with open(path, encoding="utf-8") as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"Video grafiği yok: {path} — ComfyUI'de "
                "'Workflow → Export (API)' ile kaydet ve repoya commit'le") from None
        # The file's own name, not a written one: two graphs share this loader and a hardcoded name
        # would send whoever reads the error to the wrong file.
        name = os.path.basename(path)
        if "nodes" in workflow:
            raise RuntimeError(f"{name} UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in required:
            if node_id not in workflow:
                raise RuntimeError(f"{name} grafiğinde {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow
