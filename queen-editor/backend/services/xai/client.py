"""xAI chat transport -- send two messages, get the answer's text back.

Knows nothing about video, prompts or frames: what to ask is the caller's business (see
features/photo_generation/data/xai_prompt_writer.py). `http` is injected so tests need no network.
"""
import requests


class NotConfigured(RuntimeError):
    """No API key on this machine (message is user-facing)."""


class XaiClient:
    def __init__(self, api_key, model, url, http=requests, timeout=120):
        # Trimmed here because this is what builds the header: a key pasted with a trailing
        # newline would otherwise travel as `Bearer sk-...\n`, which xAI answers 400 to. It also
        # turns a key of nothing but spaces into no key at all, so the sentence written for a
        # missing key is the one the user gets.
        self._api_key = (api_key or "").strip()
        self._model = model
        self._url = url
        self._http = http
        self._timeout = timeout

    def complete(self, system, user):
        """One system message + one user message -> the answer's text.

        One request per call rather than a batch: an answer carrying a whole list would be cut off
        by the model's output limit, and a list-shaped answer would add a format to parse.
        """
        if not self._api_key:
            raise NotConfigured("XAI_API_KEY yok — Colab Secrets'a ekle ve notebook erişimini aç")
        response = self._http.post(
            self._url,
            headers={"Authorization": f"Bearer {self._api_key}",
                     "Content-Type": "application/json"},
            json={"model": self._model,
                  "messages": [{"role": "system", "content": system},
                               {"role": "user", "content": user}]},
            timeout=self._timeout,
        )
        if response.status_code >= 400:
            # The server's own body, never a guessed cause: a 401 can be a missing key, a spent
            # quota or a wrong model name, and only the body knows which.
            raise RuntimeError(f"xAI HTTP {response.status_code}\n{response.text}")
        try:
            text = response.json()["choices"][0]["message"]["content"].strip()
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"xAI cevabı beklenen biçimde değil ({type(exc).__name__})\n"
                               f"{response.text}") from None
        if not text:
            raise RuntimeError(f"xAI boş cevap döndü:\n{response.text}")
        return text
