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

    def __init__(self, clients, default):
        self._clients = clients
        self._default = default

    def write_once(self, system, user, model=""):
        """One question with its own system prompt, and no tools (Madde 155).

        _for_xai is deliberately not used: what it puts in front of every conversation is the app's
        own system prompt, and this call wants a model that knows one job and nothing about a chat.
        """
        return self._chosen(model).complete_once(
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
