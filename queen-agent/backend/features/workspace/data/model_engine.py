"""ModelEngine -- the Engine port, backed by the model service."""
from backend.features.workspace.domain.prompt import SDXL_DOCUMENT, system_prompt

# Disk keeps the design's own word for the role; the model is told OpenAI's. The translation is a
# transport detail, so it lives here and nowhere else.
ROLE_FOR_MODEL = {"user": "user", "ai": "assistant"}


class ModelEngine:
    """One engine over a named set of transports, since Madde 146.

    A transport is bound to its address and its key at construction, so the map holds one per row
    of config.py's table. The default picks from it and speaks every turn (Madde 358 -- one model,
    and nothing on the screen names it).
    """

    def __init__(self, clients, default):
        self._clients = clients
        self._default = default

    def stream(self, messages, tools=None, on_open=None):
        return self._clients[self._default].stream(
            self._for_model(messages),
            tools=tools,
            on_open=on_open,
        )

    def stream_alone(self, system, text, on_open=None):
        # Past _for_model on purpose: see the port (Engine.stream_alone).
        return self._clients[self._default].stream(
            [{"role": "system", "content": system}, {"role": "user", "content": text}],
            on_open=on_open,
        )

    @staticmethod
    def _for_model(messages):
        # Asked when the request is built rather than read at import (Madde 196): the second part of
        # that text is the owner's, and one written today belongs in the very next turn.
        #
        # The SDXL document follows it as a message of its own (Madde 453): kept out of the system
        # prompt, and here rather than in the turn's own messages so the fixed head of a request is
        # built in one place, ahead of everything that changes.
        prepared = [
            {"role": "system", "content": system_prompt()},
            {"role": "system", "content": SDXL_DOCUMENT},
        ]
        for message in messages:
            # Copied whole so tool_calls and tool_call_id ride along; only the role is translated,
            # and a role the model already understands (assistant, tool) passes through untouched.
            translated = dict(message)
            translated["role"] = ROLE_FOR_MODEL.get(message["role"], message["role"])
            prepared.append(translated)
        return prepared
