"""ComfyUI error shapes -- report, never invent a cause.

There is one thing this module says beyond passing the server's words through verbatim: reaching
this exception at all means ComfyUI ran the graph and answered that the render failed. That makes it
the frame's failure rather than the run's, which is the only split the queue's stop rule needs
(backend/features/photo_generation/domain/policy.py). Everything else -- an unreachable server, an
HTTP error, a timeout -- leaves this exception unraised and travels up as itself.
"""
import json


class ComfyExecutionError(RuntimeError):
    """A prompt failed inside ComfyUI. Carries the raw error the server reported."""

    # Read by the domain through getattr, so it never has to import this service.
    frame_level = True

    def __init__(self, text, traceback_text):
        super().__init__(text)
        self.text = text
        self.traceback_text = traceback_text


def describe(status):
    """ComfyUI history status -> (text, traceback_text).

    Falls back to dumping the raw status: an unrecognised shape must stay visible, not be
    summarised into a guess.
    """
    for entry in status.get("messages", []):
        if not (isinstance(entry, (list, tuple)) and len(entry) == 2):
            continue
        kind, data = entry
        if kind != "execution_error" or not isinstance(data, dict):
            continue
        text = (f"node {data.get('node_id')} ({data.get('node_type', '?')})\n"
                f"{data.get('exception_type')}: {str(data.get('exception_message', '')).strip()}\n"
                f"inputs: {data.get('current_inputs')}")
        return text, "".join(data.get("traceback", []) or [])
    return f"status: {json.dumps(status, ensure_ascii=False)}", ""
