"""XaiEngine -- the Engine port, backed by the xAI service."""
from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

# Disk keeps the design's own word for the role; xAI is told OpenAI's. The translation is a
# transport detail, so it lives here and nowhere else.
ROLE_FOR_XAI = {"user": "user", "ai": "assistant"}


class XaiEngine:
    """One engine over a named set of transports, since Madde 146.

    Which model answers is an input again rather than a line in config.py, and the map is here
    because a transport is bound to its address and its key at construction -- picking one is
    therefore picking a client, not passing a string down.
    """

    def __init__(self, clients, default, prompt_writer):
        self._clients = clients
        self._default = default
        # Which of them writes a prompt when a tool asks for one (Madde 175). A third name rather
        # than a third engine: the transports are already built here, and the writer is one of them.
        self._prompt_writer = prompt_writer

    def write_once(self, system, user):
        """One question to the prompt writer, with a system prompt that is not this app's.

        Nothing is chosen here. Which model runs the conversation is the user's, and which one
        writes a prompt is a role -- so this reaches past _chosen for the one client the role names.

        SYSTEM_PROMPT stays out of it, which is why _for_xai is not used either: that prompt is a
        page about tools, files and chats, in front of a model whose whole job is one sentence.
        """
        return self._clients[self._prompt_writer].write_once(
            [{"role": "system", "content": system}, {"role": "user", "content": user}]
        )

    def stream(self, messages, tools=None, on_open=None, conversation_id="", model=""):
        return self._chosen(model).stream(
            self._for_xai(messages),
            tools=tools,
            on_open=on_open,
            conversation_id=conversation_id,
        )

    def _chosen(self, model):
        """The transport the turn named, or the default.

        The same fallback config.engine_for keeps, held again here because this is the layer a
        record actually reaches: a message written before Madde 146 names no model at all, and one
        written before Madde 82 names a model that is gone.
        """
        return self._clients.get(model) or self._clients[self._default]

    @staticmethod
    def _for_xai(messages):
        prepared = [{"role": "system", "content": SYSTEM_PROMPT}]
        for message in messages:
            # Copied whole so tool_calls and tool_call_id ride along; only the role is translated,
            # and a role xAI already understands (assistant, tool) passes through untouched.
            translated = dict(message)
            translated["role"] = ROLE_FOR_XAI.get(message["role"], message["role"])
            prepared.append(translated)
        return prepared
