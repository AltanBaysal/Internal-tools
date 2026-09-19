"""The MiniMax H3 video producer over ComfyUI -- the only place that knows what the H3 graphs look
like.

Two graphs, the same seam as WAN's producer: with an ending frame the FL2VA graph runs, without one
the I2VA graph. Both are our own exports (madde 242):
  "2730"  MiniMaxH3Director   -> the pictures and the prompt
  "2739"  DaSiWa_SeedControl  -> the sampler's noise seed

The Director keeps its pictures and its prompt inside its own JSON rather than in wired inputs. The
pictures are items of `timeline_data`, written in by position; the prompt sits in four places --
`prompt`, the timeline's `simple_prompt` and `resolved_prompt`, and `builder_state`'s
`simple_prompt`. Which of them the node reads cannot be told without running it, so all four carry
the same text.

Which picture sits where is the graph's fact, not the scene's, so this file opens the prompt with it
rather than the writer. The sentences are the graph's own examples ("Example: FL2VA First Frame" and
"First+Last Frame", collab-toolbox's minimax-h3/workflow.json) -- inherited knowledge, not a
dependency.
"""
import json
import os

DIRECTOR_NODE = "2730"
SEED_NODE = "2739"
NODES = (DIRECTOR_NODE, SEED_NODE)

I2VA_SENTENCE = ("For the target video, at 0.00 seconds into the target video, Picture 1 (from "
                 "Shot 1) is fully referenced.")
FL2VA_SENTENCE = ("How the reference pictures align with the target video — Picture 1 (from Shot 1) "
                  "aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) "
                  "aligns with the {seconds:.2f}-second mark of the target video.")

# Motion Booster's word; the writer decides whether a scene gets it (madde 246).
TRIGGER = "dynv2"

# The graph previews through a tiny VAE as it samples; only the mp4 is the render.
VIDEO_EXTENSIONS = (".mp4",)


class ComfyH3VideoGenerator:
    def __init__(self, client, workflow_path, first_last_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._first_last_path = first_last_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None):
        """`source` is the frame's photo as (name, bytes); `end`, when given, is the picture the video
        arrives at, and giving one is the whole of the choice between the two graphs.

        `negative`, `model` and `lora` belong to the port rather than to these graphs: the lora and
        its strength are baked into the exports (madde 213), and a video job carries none of them.
        """
        if not source:
            # The ending frame is where the video arrives, not what it is built on.
            raise RuntimeError("Video için kaynak foto verilmedi")
        path = self._first_last_path if end else self._workflow_path
        workflow = self._load(path)
        director = workflow[DIRECTOR_NODE]["inputs"]

        names = [self._client.upload_image(*source)]
        if end:
            names.append(self._client.upload_image(*end))
        timeline = json.loads(director["timeline_data"])
        if len(timeline["items"]) != len(names):
            raise RuntimeError(
                f"{os.path.basename(path)} grafiğinin timeline'ında {len(timeline['items'])} resim "
                f"var, bu video {len(names)} resimle üretiliyor — grafik değişmiş, yeniden export et")
        for item, name in zip(timeline["items"], names):
            item["value"] = name

        if end:
            opening = FL2VA_SENTENCE.format(seconds=float(director["duration"]))
        else:
            opening = I2VA_SENTENCE
        if prompt.startswith(TRIGGER):
            # The lora only wakes when its word is the first thing H3 reads (user, madde 246), and
            # the picture sentence is ours -- so the word is lifted out and put in front of it.
            rest = prompt[len(TRIGGER):].lstrip(". \n")
            written = f"{TRIGGER}. {opening}\n\n{rest}"
        else:
            written = f"{opening}\n\n{prompt}"
        director["prompt"] = written
        timeline["builder_state"]["simple_prompt"] = written
        timeline["resolved_prompt"] = written
        director["timeline_data"] = json.dumps(timeline, ensure_ascii=False)
        state = json.loads(director["builder_state"])
        state["simple_prompt"] = written
        director["builder_state"] = json.dumps(state, ensure_ascii=False)

        if seed is not None:
            # A job with no seed leaves the graph's own value where it is.
            workflow[SEED_NODE]["inputs"]["seed_value"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history, extensions=VIDEO_EXTENSIONS)

    def seconds(self):
        """How long one render runs, as the I2VA graph's Director has it. One number is quoted for
        every video; that the two graphs agree is held by test_workflow_asset."""
        standard = self._load(self._workflow_path)
        return float(standard[DIRECTOR_NODE]["inputs"]["duration"])

    def _load(self, path):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        try:
            with open(path, encoding="utf-8") as f:
                workflow = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"Video grafiği yok: {path} — ComfyUI'de "
                "'Workflow → Export (API)' ile kaydet ve repoya commit'le") from None
        name = os.path.basename(path)
        if "nodes" in workflow:
            raise RuntimeError(f"{name} UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in NODES:
            if node_id not in workflow:
                raise RuntimeError(f"{name} grafiğinde {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow
