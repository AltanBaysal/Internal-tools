"""ModelEngine -- the Engine port, backed by the model service."""
from backend.features.workspace.domain.prompt import system_prompt

# Disk keeps the design's own word for the role; the model is told OpenAI's. The translation is a
# transport detail, so it lives here and nowhere else.
ROLE_FOR_MODEL = {"user": "user", "ai": "assistant"}


class ModelEngine:
    """One engine over a named set of transports, since Madde 146.

    A transport is bound to its address and its key at construction, so the map holds one per row
    of config.py's table. Two names pick from it: the default speaks every turn (Madde 358 -- one
    model, and nothing on the screen names it), and the prompt writer answers a tool's one question.
    """

    def __init__(self, clients, default, prompt_writer):
        self._clients = clients
        self._default = default
        # Which of them writes a prompt when a tool asks for one (Madde 175). A third name rather
        # than a third engine: the transports are already built here, and the writer is one of them.
        self._prompt_writer = prompt_writer

    def write_once(self, system, user):
        """One question to the prompt writer, with a system prompt that is not this app's.

        Which model runs the conversation and which one writes a prompt are two roles, so this
        reaches past the default for the one client the second role names.

        SYSTEM_PROMPT stays out of it, which is why _for_model is not used either: that prompt is a
        page about tools, files and chats, in front of a model whose whole job is one sentence.
        """
        return self._clients[self._prompt_writer].write_once(
            [{"role": "system", "content": system}, {"role": "user", "content": user}]
        )

    def stream(self, messages, tools=None, on_open=None):
        return self._clients[self._default].stream(
            self._for_model(messages),
            tools=tools,
            on_open=on_open,
        )

    @staticmethod
    def _for_model(messages):
        # Asked when the request is built rather than read at import (Madde 196): the second part of
        # that text is the owner's, and one written today belongs in the very next turn.
        prepared = [{"role": "system", "content": system_prompt()}]
        for message in messages:
            # Copied whole so tool_calls and tool_call_id ride along; only the role is translated,
            # and a role the model already understands (assistant, tool) passes through untouched.
            translated = dict(message)
            translated["role"] = ROLE_FOR_MODEL.get(message["role"], message["role"])
            prepared.append(translated)
        return prepared
