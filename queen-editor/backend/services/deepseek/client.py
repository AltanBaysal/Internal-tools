"""DeepSeek chat transport -- an instruction, words and pictures in, the answer's text back.

Knows nothing about video, prompts or frames: what to ask is the caller's business (see
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
        if not self._api_key:
            raise NotConfigured(
                "DEEPSEEK_API_KEY yok — Colab Secrets'a ekle ve notebook erişimini aç")
        said = [_picture(name, data) for name, data in images]
        if text:
            said.append({"type": "text", "text": text})
        response = self._http.post(
            self._url,
            headers={"Authorization": f"Bearer {self._api_key}",
                     "Content-Type": "application/json"},
            json={"model": self._model,
                  "messages": [{"role": "system", "content": system},
                               {"role": "user", "content": said}]},
            timeout=self._timeout,
        )
        if response.status_code >= 400:
            # The server's own body, never a guessed cause: a refusal can be the picture, the model
            # name, the key or the balance, and only the body knows which.
            raise RuntimeError(f"DeepSeek HTTP {response.status_code}\n{response.text}")
        try:
            answer = response.json()["choices"][0]["message"]["content"].strip()
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"DeepSeek cevabı beklenen biçimde değil ({type(exc).__name__})\n"
                               f"{response.text}") from None
        if not answer:
            raise RuntimeError(f"DeepSeek boş cevap döndü:\n{response.text}")
        return answer
