"""XaiEngine -- the Engine port, backed by the xAI service."""
from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

# Disk keeps the design's own word for the role; xAI is told OpenAI's. The translation is a
# transport detail, so it lives here and nowhere else.
ROLE_FOR_XAI = {"user": "user", "ai": "assistant"}


class XaiEngine:
    def __init__(self, client):
        self._client = client

    def complete(self, messages, tools=None):
        return self._client.complete(self._for_xai(messages), tools=tools)

    def stream(self, messages, tools=None, on_open=None, conversation_id=""):
        return self._client.stream(
            self._for_xai(messages),
            tools=tools,
            on_open=on_open,
            conversation_id=conversation_id,
        )

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
