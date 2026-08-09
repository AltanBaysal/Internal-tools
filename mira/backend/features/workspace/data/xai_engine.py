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

    def stream(self, messages, tools=None):
        return self._client.stream(self._for_xai(messages), tools=tools)

    @staticmethod
    def _for_xai(messages):
        return [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": ROLE_FOR_XAI[message["role"]], "content": message["content"]}
            for message in messages
        ]
