"""DeepSeek chat transport -- an instruction, words and pictures, or a conversation and its tools,
in; the answer's words and the tool calls it makes, back.

One request, and a failure raised in the server's own words; sending it again is box.py's. Knows
nothing about video, prompts, frames or agents: what to ask is the caller's business (see
features/photo_generation/data/prompt_writer.py). `http` is injected so tests need no network.
"""
import base64
import mimetypes

import requests


class NotConfigured(RuntimeError):
    """No API key on this machine (message is user-facing)."""


def _picture(name, data):
    """One picture as a message part: a data URL, because the file is on this machine and no link
    could point at it. Its type is read off its name."""
    media_type = mimetypes.guess_type(name)[0]
    return {"type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{base64.b64encode(data).decode()}"}}


class DeepSeekClient:
    def __init__(self, api_key, model, url, http=requests, timeout=120):
        # Trimmed here because this is what builds the header: a key pasted with a trailing
        # newline would otherwise travel as `Bearer sk-...\n`. It also turns a key of nothing but
        # spaces into no key at all, so the sentence written for a missing key is the one the user
        # gets.
        self._api_key = (api_key or "").strip()
        self._model = model
        self._url = url
        self._http = http
        self._timeout = timeout

    def complete(self, system, text="", images=()):
        """One system message + one user message of pictures and words -> the answer's text.

        `images` is [(name, bytes)]. They ride in the user message alone: DeepSeek answers 400 to a
        picture in the system message. No words means no text part at all, rather than an empty one.
        """
        said = [_picture(name, data) for name, data in images]
        if text:
            said.append({"type": "text", "text": text})
        answer, _ = self.send([{"role": "system", "content": system},
                               {"role": "user", "content": said}])
        return answer

    def send(self, messages, tools=()):
        """A conversation and the tools the model may call -> (the answer's words, its tool calls).

        Both go as they are: what they say is the caller's business. The words come back trimmed, ""
        when there are none, and the tool calls as DeepSeek sent them, [] when there are none. An
        answer with neither is an empty answer.
        """
        if not self._api_key:
            raise NotConfigured(
                "DEEPSEEK_API_KEY yok — Colab Secrets'a ekle ve notebook erişimini aç")
        body = {"model": self._model, "messages": messages}
        # Only when there are some: a question offered nothing to call -- every prompt writer's --
        # goes as it always did.
        if tools:
            body["tools"] = tools
        response = self._http.post(
            self._url,
            headers={"Authorization": f"Bearer {self._api_key}",
                     "Content-Type": "application/json"},
            json=body,
            timeout=self._timeout,
        )
        if response.status_code >= 400:
            # The server's own body, never a guessed cause: a refusal can be the picture, the model
            # name, the key or the balance, and only the body knows which.
            raise RuntimeError(f"DeepSeek HTTP {response.status_code}\n{response.text}")
        try:
            message = response.json()["choices"][0]["message"]
            # An answer that calls a tool comes with its content null.
            words = (message.get("content") or "").strip()
            calls = message.get("tool_calls") or []
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"DeepSeek cevabı beklenen biçimde değil ({type(exc).__name__})\n"
                               f"{response.text}") from None
        if not words and not calls:
            raise RuntimeError(f"DeepSeek boş cevap döndü:\n{response.text}")
        return words, calls
