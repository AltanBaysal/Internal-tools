"""ComfyUI transport -- submit a graph, wait for it, pull the files it produced, say how much memory
the card it renders on has.

Media-agnostic on purpose: no node id, no prompt, no seed, no photo/video concept. Whoever calls
this decides what the graph means. `http`, `websocket`, `sleep` and `now` are injected so tests need
no server.
"""
import json
import time
import uuid

import requests

from backend.services.comfy.errors import (
    ComfyExecutionError,
    ComfyHttpError,
    ComfyTimeout,
    ComfyUnreachable,
    describe,
)


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


def _ok(resp):
    """requests' own raise_for_status, its error raised as ComfyHttpError in requests' own words: the
    type is what carries the queue's mark for a 5xx (madde 433)."""
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise ComfyHttpError(str(exc), resp.status_code) from exc


class ComfyClient:
    def __init__(self, base_url, http=requests, poll_interval=5, sleep=time.sleep,
                 now=time.monotonic, log_path="", websocket=None):
        self.base = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())
        self._http = http
        self._poll_interval = poll_interval
        self._sleep = sleep
        self._now = now
        # ComfyUI's own log, read only when it cannot be reached (madde 230).
        self._log_path = log_path
        # The websocket-client module or a stand-in; None is the library itself, at the first wait.
        self._websocket = websocket

    def _send(self, method, url, **kwargs):
        """Every request goes through here, so none of them can forget what a refusal means -- or a
        reply that never came. A connection that could not be made in time is a ConnectionError too,
        and reads as unreachable."""
        try:
            return getattr(self._http, method)(url, **kwargs)
        except requests.ConnectionError as exc:
            raise ComfyUnreachable(self.base, exc, self._log_path) from exc
        except requests.Timeout as exc:
            raise ComfyTimeout(str(exc)) from exc

    def upload_image(self, name, data):
        """Put an image in ComfyUI's input folder and return the name the server kept it under.

        The graph runs on the server's own disk while the picture lives on Drive, so the bytes
        travel over HTTP. overwrite=true because the name is the frame's own: uploading the same
        frame again has to replace it, not become "P0_0 (1).png" that LoadImage never looks at.
        """
        resp = self._send("post", f"{self.base}/upload/image",
                               files={"image": (name, data)},
                               data={"overwrite": "true"}, timeout=120)
        if resp.status_code >= 400:
            raise ComfyHttpError(f"POST /upload/image -> HTTP {resp.status_code}\n{resp.text}",
                                 resp.status_code)
        return resp.json()["name"]

    def submit(self, workflow):
        """Queue the graph; returns ComfyUI's prompt_id."""
        resp = self._send("post", f"{self.base}/prompt",
                               json={"prompt": workflow, "client_id": self.client_id}, timeout=30)
        if resp.status_code >= 400:
            # The server's own body, not a summary of it.
            raise ComfyHttpError(f"POST /prompt -> HTTP {resp.status_code}\n{resp.text}",
                                 resp.status_code)
        data = resp.json()
        if data.get("node_errors"):
            raise RuntimeError("POST /prompt -> node_errors\n"
                               + json.dumps(data["node_errors"], indent=2, ensure_ascii=False))
        return data["prompt_id"]

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

    def fetch_output(self, history_entry, extensions=None):
        """Download THE produced file over /view and return its bytes.

        Exactly one real output is the contract: silently picking one of N would hide a graph whose
        batch size is not 1, so the raw outputs are printed and the render stops.

        `extensions` is how a caller says which medium it came for: a video graph often carries an
        image node as well, so the file is chosen by its own name rather than by which key it
        landed in -- which key that is (images, gifs, videos, audio) is the node's own business.
        No extensions means the images a photo graph makes.
        """
        return self.fetch_outputs(history_entry, 1, extensions)[0]

    def fetch_outputs(self, history_entry, count, extensions=None):
        """Download the `count` produced files over /view, in the order the graph listed them -- a
        batch's pictures in the batch's order (madde 411).

        type=="output" drops temp previews (a preview node registers temp files). Any other number
        of real outputs stops the render with the raw outputs printed: taking what came would hand
        a frame a picture that is not its own, or none.
        """
        outputs = []
        for node_output in history_entry.get("outputs", {}).values():
            groups = node_output.values() if extensions else [node_output.get("images", [])]
            for group in groups:
                if not isinstance(group, list):
                    continue
                for item in group:
                    if not isinstance(item, dict) or item.get("type", "output") != "output":
                        continue
                    if extensions and not item.get("filename", "").lower().endswith(
                            tuple(extensions)):
                        continue
                    outputs.append(item)
        came = json.dumps(history_entry.get("outputs", {}), indent=2, ensure_ascii=False)
        if not outputs:
            wanted = ", ".join(extensions) if extensions else "görsel"
            raise RuntimeError(f"{wanted} çıktısı gelmedi — gelenler:\n{came}")
        if len(outputs) != count:
            raise RuntimeError(f"{count} çıktı bekleniyordu, {len(outputs)} geldi — grafikte "
                               f"Batch Size {count} mi?\n{came}")
        return [self._view(item) for item in outputs]

    def _view(self, item):
        """One produced file's bytes."""
        resp = self._send("get", f"{self.base}/view", timeout=300, params={
            "filename": item["filename"],
            "subfolder": item.get("subfolder", ""),
            "type": "output",
        })
        _ok(resp)
        return resp.content

    def vram_total(self):
        """The memory of the card ComfyUI renders on, in bytes, as /system_stats reports it -- it
        lists that device first. What decides whether a prompt's variants fit in one batch
        (madde 411)."""
        resp = self._send("get", f"{self.base}/system_stats", timeout=30)
        _ok(resp)
        return resp.json()["devices"][0]["vram_total"]

    def interrupt(self):
        """Cut whatever ComfyUI is rendering right now; harmless when nothing runs."""
        resp = self._send("post", f"{self.base}/interrupt", timeout=30)
        _ok(resp)
