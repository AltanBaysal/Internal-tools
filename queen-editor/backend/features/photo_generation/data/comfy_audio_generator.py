"""The sound producer over ComfyUI -- the only place that knows what the audio graph looks like.

Node ids come from our own export (queen-editor/workflow_audio_api.json), which drives ComfyUI's
MMAudio node -- the same engine collab-toolbox's mmaudio notebook uses, reached through ComfyUI
rather than in-process, so this app keeps one engine and installs nothing:
  "1"  VHS_LoadVideoPath -> the frame's video
  "2"  MMAudioSampler    -> the sound prompt (and its seed)

A new export can renumber these; then this file changes and nothing else does. How long the sound
is never appears here: it follows the video the graph was given.
"""
import json

VIDEO_NODE = "1"
PROMPT_NODE = "2"

# What counts as the render. The graph may publish a preview of the video as well, so the file is
# chosen by its own extension rather than by which output key it landed in.
AUDIO_EXTENSIONS = (".wav",)


class ComfyAudioGenerator:
    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", source=None):
        """`source` is the frame's video as (name, bytes) -- a sound is laid over one video.

        `negative` and `model` belong to the port rather than to this graph: both are baked into
        the export, and a sound job carries neither.
        """
        if not source:
            raise RuntimeError("Ses için kaynak video verilmedi")
        workflow = self._load()
        name, data = source
        # /upload/image is ComfyUI's own way in for any file the graph loads by name, video too.
        workflow[VIDEO_NODE]["inputs"]["video"] = self._client.upload_image(name, data)
        workflow[PROMPT_NODE]["inputs"]["prompt"] = prompt
        if seed is not None and "seed" in workflow[PROMPT_NODE]["inputs"]:
            # A job with no seed leaves the graph's own value where it is.
            workflow[PROMPT_NODE]["inputs"]["seed"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history, extensions=AUDIO_EXTENSIONS)

    def _load(self):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        try:
            with open(self._workflow_path, encoding="utf-8") as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"Ses grafiği yok: {self._workflow_path} — ComfyUI'de "
                "'Workflow → Export (API)' ile kaydet ve repoya commit'le") from None
        if "nodes" in workflow:
            raise RuntimeError("workflow_audio_api.json UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in (VIDEO_NODE, PROMPT_NODE):
            if node_id not in workflow:
                raise RuntimeError(f"Ses grafiğinde {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow
