"""ComfyUI error shapes -- classify, never invent a cause.

The classifier answers one question: did a model loader fail? A loader failure means the model is
broken or missing, so every following render would hit the identical error; anything else is
specific to this render. Everything else in the message is passed through verbatim.
"""
import json


class ComfyExecutionError(RuntimeError):
    """A prompt failed inside ComfyUI. Carries the raw error plus the infra flag."""

    def __init__(self, text, traceback_text, infra):
        super().__init__(text)
        self.text = text
        self.traceback_text = traceback_text
        self.infra = infra


def describe(status):
    """ComfyUI history status -> (text, traceback_text, infra).

    Falls back to dumping the raw status: an unrecognised shape must stay visible, not be
    summarised into a guess.
    """
    for entry in status.get("messages", []):
        if not (isinstance(entry, (list, tuple)) and len(entry) == 2):
            continue
        kind, data = entry
        if kind != "execution_error" or not isinstance(data, dict):
            continue
        node_type = str(data.get("node_type", "?"))
        text = (f"node {data.get('node_id')} ({node_type})\n"
                f"{data.get('exception_type')}: {str(data.get('exception_message', '')).strip()}\n"
                f"inputs: {data.get('current_inputs')}")
        tb = "".join(data.get("traceback", []) or [])
        # Substring, not suffix: our graph's loaders include CheckpointLoaderSimple and
        # "Power Lora Loader (rgthree)". Matching only the end would let the checkpoint -- the
        # model likeliest to be missing, since it is the gated Civitai one -- pass as a
        # render-specific error, so every following render would repeat the same failure.
        return text, tb, "loader" in node_type.lower()
    return f"status: {json.dumps(status, ensure_ascii=False)}", "", False
