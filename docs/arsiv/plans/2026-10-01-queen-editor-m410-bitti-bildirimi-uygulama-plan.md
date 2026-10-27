# Madde 410 — ComfyUI'nin bitti bildirimi, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `ComfyClient.wait` bakışlar arasında uyumak yerine ComfyUI'nin soketini dinlesin, ve bu
prompt'un bitti bildirimi gelince hemen `/history`'ye baksın; `9faf41ab`'deki 34 test yeşile dönsün.

**Yaklaşım:** Kütüphane `websocket=` ile enjekte edilir, verilmezse ilk `wait`'te içe aktarılır. Soket
ilk bakıştan önce açılır, en çok bir aralık dinlenir, kopunca bırakılır, her durumda kapanır.

**Araçlar:** websocket-client (Colab'da kurulu; burada yalnız sahtesi), stdlib `json`.

**Spec:** [m410 uygulama turu](../specs/2026-10-01-queen-editor-m410-bitti-bildirimi-uygulama-design.md)
· [test turu](../specs/2026-10-01-queen-editor-m410-bitti-bildirimi-testler-design.md)

## Her yere geçerli kurallar

- Testlere dokunulmaz; suite kodla yeşile döner. `skip` / `xfail` yok.
- `websocket` modülün başında içe aktarılmaz — `test_requirements.py` ve bu makinedeki toplama düşer.
- Hata mesajları aynen kalır; yorumlar yalnız neden'i ve bugün doğru olanı söyler.
- Defter, ekran, `dist`, `main.py`, yol haritası değişmez.

---

## Görev 1: `client.py`

**Dosya:** Değiştir: `queen-editor/backend/services/comfy/client.py`

- [ ] **Adım 1: Modülün docstring'i ve iki modül fonksiyonu.**

```python
"""ComfyUI transport -- submit a graph, wait for it, pull the produced file.

Media-agnostic on purpose: no node id, no prompt, no seed, no photo/video concept. Whoever calls
this decides what the graph means. `http`, `websocket`, `sleep` and `now` are injected so tests need
no server.
"""
import json
import time
import uuid

import requests

from backend.services.comfy.errors import ComfyExecutionError, ComfyUnreachable, describe


def _websocket_client():
    """websocket-client, the library ComfyUI's own socket example uses. Colab's runtime ships it and
    a developer's machine may not, so it is imported at the first wait rather than at the top: the
    app and its suite start without it, and the suite hands the client its own."""
    import websocket
    return websocket


def _is_done(message, prompt_id):
    """Whether a socket message is ComfyUI saying prompt_id is done.

    That is `executing` with no node: sent once the prompt's /history entry is written, after a
    success, a failure and an interrupt alike. `execution_success` comes before the entry, so it is
    not the one. Bytes are previews, and an empty string is how a close frame comes back. Only an
    `executing` message's data is read -- ComfyUI's own, always a dict -- never a custom node's.
    """
    if not isinstance(message, str) or not message:
        return False
    notice = json.loads(message)
    return (notice.get("type") == "executing" and notice["data"].get("node") is None
            and notice["data"].get("prompt_id") == prompt_id)
```

- [ ] **Adım 2: `__init__` `websocket=` alır.**

```python
    def __init__(self, base_url, http=requests, poll_interval=5, sleep=time.sleep,
                 now=time.monotonic, log_path="", websocket=None):
        ...
        # The websocket-client module or a stand-in; None is the library itself, at the first wait.
        self._websocket = websocket
```

- [ ] **Adım 3: `wait` ve iki yardımcı.**

```python
    def wait(self, prompt_id, timeout):
        """Look in /history until the prompt is there. Raises ComfyExecutionError if it failed.

        Between looks it listens on ComfyUI's socket instead of sleeping, and looks again the moment
        ComfyUI says the prompt is done (madde 410). The socket only says when to look; /history
        alone says what happened. Never listened to for longer than the poll interval, a notice that
        does not come or a socket that breaks or never opens costs that interval, as before, and
        never the prompt.
        """
        websocket = self._websocket or _websocket_client()
        start = self._now()
        # Opened before the first look: ComfyUI drops a notice for an id with no socket open, so a
        # prompt that ends before this is found by the look, and one that ends after it is heard.
        socket = self._listen(websocket)
        try:
            while True:
                if self._now() - start > timeout:
                    raise TimeoutError(f"prompt {prompt_id}: {timeout}s içinde bitmedi")
                history = self._send("get", f"{self.base}/history/{prompt_id}", timeout=30).json()
                if prompt_id in history:
                    entry = history[prompt_id]
                    status = entry.get("status", {})
                    if status.get("status_str") == "error":
                        raise ComfyExecutionError(*describe(status))
                    return entry
                if socket is None:
                    self._sleep(self._poll_interval)
                elif not self._hear_done(websocket, socket, prompt_id):
                    socket.close()
                    socket = None
        finally:
            if socket is not None:
                # close() waits for ComfyUI's reply. ComfyUI forgets an id when a socket under it
                # goes, whichever socket holds the id by then: the old one has to be gone before the
                # next wait opens its own.
                socket.close()

    def _listen(self, websocket):
        """ComfyUI's socket for this client's prompts, or None when it does not open."""
        url = "ws" + self.base[len("http"):] + f"/ws?clientId={self.client_id}"
        try:
            return websocket.create_connection(url, timeout=self._poll_interval)
        except (websocket.WebSocketException, OSError):
            return None

    def _hear_done(self, websocket, socket, prompt_id):
        """Listen until ComfyUI says prompt_id is done, one poll interval at most: messages never
        stop while a prompt runs, and the interval is what keeps the looks -- and the stall guard
        between them -- coming. False when the socket broke on the way."""
        deadline = self._now() + self._poll_interval
        while (left := deadline - self._now()) > 0:
            socket.settimeout(left)
            try:
                message = socket.recv()
            except websocket.WebSocketTimeoutException:
                return True
            except (websocket.WebSocketException, OSError):
                return False
            if _is_done(message, prompt_id):
                return True
        return True
```

## Görev 2: `config.py` ve `requirements.txt`

**Dosyalar:** Değiştir: `queen-editor/backend/config.py`, `queen-editor/backend/requirements.txt`

- [ ] **Adım 1: `POLL_INTERVAL`'ın yorumu.**

```python
POLL_INTERVAL = 5          # longest gap between /history looks; ComfyUI's done notice cuts it short
```

- [ ] **Adım 2: `requirements.txt`'e `websocket-client>=1.8`** — `requests>=2.32`'nin altına.

## Görev 3: Koşu ve commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; `test_comfy_client.py`'nin 34 testi geçer, `test_composition_root.py` ve
`test_requirements.py` yeşil kalır.

- [ ] **Adım 2: Commit** — kod, uygulama spec'i ve bu plan:

```powershell
git add queen-editor/backend/services/comfy/client.py queen-editor/backend/config.py queen-editor/backend/requirements.txt docs/specs/2026-10-01-queen-editor-m410-bitti-bildirimi-uygulama-design.md docs/plans/2026-10-01-queen-editor-m410-bitti-bildirimi-uygulama-plan.md
git commit -m @'
feat(queen-editor): 410 -- ComfyClient.wait listens on ComfyUI's socket between looks at /history and looks again the moment executing with no node comes for its prompt, instead of sleeping five seconds; /history still says what happened, the socket is listened to for one interval at most, a dropped or refused socket leaves the five second looks as they were, and it is closed however the wait ends; websocket-client, which Colab ships, is imported at the first wait and declared in requirements.txt; the notebook, the graphs and what is submitted are unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
