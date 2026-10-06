"""The MiniMax H3 video producer over ComfyUI -- the only place that knows what the H3 graphs look
like.

Two graphs, the same seam as WAN's producer: with an ending frame the FL2VA graph runs, without one
the I2VA graph. Both are our own exports (madde 242):
  "2730"  MiniMaxH3Director   -> the pictures, the prompt and the length
  "2739"  DaSiWa_SeedControl  -> the sampler's noise seed

The Director keeps its pictures and its prompt inside its own JSON rather than in wired inputs. The
pictures are items of `timeline_data`, written in by position; the prompt sits in four places --
`prompt`, the timeline's `simple_prompt` and `resolved_prompt`, and `builder_state`'s
`simple_prompt`. Which of them the node reads cannot be told without running it, so all four carry
the same text.

The length is the Director's `duration`, in seconds (madde 422): the graph's own note says to set it
there, and nothing else in the graph counts frames -- the latent comes out of the Director's guide,
and the Combine takes its frame rate from the Director. It sits in three places for the same reason
the prompt sits in four: the input, and the `duration` of both builder states.

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

# Motion Booster's word, added by hand to the prompts that want it (madde 331).
TRIGGER = "dynv2"

# The mode the Director runs a pool-made video in. A plain string on the node, which is why no new
# export was needed: the ref2va_model slot of the shipped graph is already filled (madde 304).
REF2VA = "REF2VA"
# What a reference row of the timeline carries, read off the shipped export rather than guessed at.
# source_width and source_height are deliberately absent: the producer does not know the size of a
# file it was handed, and the node has a ref_image_size input of its own. So are trim_start and
# trim_end -- the node's own defaults are no trim, and a clip in the pool has already been through
# the app's limits (madde 298).
REFERENCE_ITEM = {"enabled": True, "duration": 1, "thumbnail": None}

# The pool's words are H3's labels (<Picture N>); a timeline row's are the node's own field values.
# They meet here, because this file is the only one that knows the node's vocabulary (madde 305).
ROW_TYPE = {"picture": "image", "video": "video", "audio": "audio"}
# Which half of a video reference is used -- the V / A / V+A buttons of the node's own panel. Both,
# because the user put that clip in the pool to be followed and dropping half of it would be a
# choice nobody asked for. Only a video row carries the field at all.
BOTH_HALVES = "video_audio"

# The graph previews through a tiny VAE as it samples; only the mp4 is the render.
VIDEO_EXTENSIONS = (".mp4",)


def _director(workflow, seconds):
    """The Director's inputs, set to run `seconds`. A job with no length leaves the graph's own --
    every one queued before madde 422."""
    director = workflow[DIRECTOR_NODE]["inputs"]
    if seconds is not None:
        director["duration"] = seconds
    return director


class ComfyH3VideoGenerator:
    def __init__(self, client, workflow_path, first_last_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._first_last_path = first_last_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=(), seconds=None):
        """`source` is the frame's photo as (name, bytes); `end`, when given, is the picture the video
        arrives at, and giving one is the whole of the choice between the two graphs.

        `references` is the project's pool as (name, bytes, kind). Given any, the video is made of
        THEM and of no frame at all: the mode becomes REF2VA and no source picture is asked for
        (madde 304).

        `negative`, `model` and `lora` belong to the port rather than to these graphs: the lora and
        its strength are baked into the exports (madde 213), and a video job carries none of them.

        `seconds` is how long the video runs, from its job (madde 422), in every mode; None leaves
        the graph's own.
        """
        if references:
            return self._from_pool(prompt, seed, references, seconds)
        if not source:
            # The ending frame is where the video arrives, not what it is built on.
            raise RuntimeError("Video için kaynak foto verilmedi")
        path = self._first_last_path if end else self._workflow_path
        workflow = self._load(path)
        # Set before the FL2VA sentence reads it: the second picture sits at the video's end.
        director = _director(workflow, seconds)

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
        return self._render(workflow, director, timeline, written, seed)

    def _from_pool(self, prompt, seed, references, seconds):
        """The same graph, run in REF2VA: the timeline is the pool rather than the frame.

        The I2VA export is what is loaded, because the mode is a string and the node's ref2va_model
        slot is already filled -- there is no second graph to keep in step.

        The prompt goes in as the user wrote it. The opening sentence the other two modes carry is
        the producer telling H3 which picture sits where; here the prompt is the user's own six
        sections and nothing is put in front of it.
        """
        workflow = self._load(self._workflow_path)
        director = _director(workflow, seconds)
        director["mode"] = REF2VA
        timeline = json.loads(director["timeline_data"])
        # Ordered rows, because H3 numbers references by their order and a prompt's <Picture 2>
        # counts from there (madde 300).
        timeline["items"] = [self._row(index, name, data, kind)
                             for index, (name, data, kind) in enumerate(references)]
        return self._render(workflow, director, timeline, prompt, seed)

    def _row(self, index, name, data, kind):
        """One reference as a timeline row: what it is, where it sits, and the name it went up under.

        Uploaded the way a picture is -- the node looks its files up by name, whatever they hold.
        """
        row_type = ROW_TYPE[kind]
        return {**REFERENCE_ITEM, "id": f"{row_type}-{index}", "order": index, "slot": index,
                "start": index, "type": row_type,
                "value": self._client.upload_image(name, data),
                **({"media_mode": BOTH_HALVES} if row_type == "video" else {})}

    def _render(self, workflow, director, timeline, written, seed):
        """Write the prompt in all four places the node may read it, the length in all three, and
        run the graph."""
        director["prompt"] = written
        timeline["builder_state"]["simple_prompt"] = written
        timeline["builder_state"]["duration"] = director["duration"]
        timeline["resolved_prompt"] = written
        director["timeline_data"] = json.dumps(timeline, ensure_ascii=False)
        state = json.loads(director["builder_state"])
        state["simple_prompt"] = written
        state["duration"] = director["duration"]
        director["builder_state"] = json.dumps(state, ensure_ascii=False)

        if seed is not None:
            # A job with no seed leaves the graph's own value where it is.
            workflow[SEED_NODE]["inputs"]["seed_value"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history, extensions=VIDEO_EXTENSIONS)

    def seconds(self, asked=None):
        """How long a video asked to run `asked` seconds comes out: what it is asked, since that is
        what the Director is told (madde 422); asked none, the graph's own, as the I2VA graph's
        Director has it. The loop writes the answer on the video's row (madde 423), and the export
        summary counts a row that says no length at the graph's own. That the two graphs agree is
        held by test_workflow_asset."""
        if asked is not None:
            return asked
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
