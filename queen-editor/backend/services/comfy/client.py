"""ComfyUI HTTP transport -- submit a graph, wait for it, pull the produced file.

Media-agnostic on purpose: no node id, no prompt, no seed, no photo/video concept. Whoever calls
this decides what the graph means. `http`, `sleep` and `now` are injected so tests need no server.
"""
import json
import time
import uuid

import requests

from backend.services.comfy.errors import ComfyExecutionError, ComfyUnreachable, describe


class ComfyClient:
    def __init__(self, base_url, http=requests, poll_interval=5, sleep=time.sleep,
                 now=time.monotonic, log_path=""):
        self.base = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())
        self._http = http
        self._poll_interval = poll_interval
        self._sleep = sleep
        self._now = now
        # ComfyUI's own log, read only when it cannot be reached (madde 230).
        self._log_path = log_path

    def _send(self, method, url, **kwargs):
        """Every request goes through here, so none of them can forget what a refusal means."""
        try:
            return getattr(self._http, method)(url, **kwargs)
        except requests.ConnectionError as exc:
            raise ComfyUnreachable(self.base, exc, self._log_path) from exc

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
            raise RuntimeError(f"POST /upload/image -> HTTP {resp.status_code}\n{resp.text}")
        return resp.json()["name"]

    def submit(self, workflow):
        """Queue the graph; returns ComfyUI's prompt_id."""
        resp = self._send("post", f"{self.base}/prompt",
                               json={"prompt": workflow, "client_id": self.client_id}, timeout=30)
        if resp.status_code >= 400:
            # The server's own body, not a summary of it.
            raise RuntimeError(f"POST /prompt -> HTTP {resp.status_code}\n{resp.text}")
        data = resp.json()
        if data.get("node_errors"):
            raise RuntimeError("POST /prompt -> node_errors\n"
                               + json.dumps(data["node_errors"], indent=2, ensure_ascii=False))
        return data["prompt_id"]

    def wait(self, prompt_id, timeout):
        """Poll /history until the prompt appears. Raises ComfyExecutionError if it failed."""
        start = self._now()
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
            self._sleep(self._poll_interval)

    def fetch_output(self, history_entry, extensions=None):
        """Download THE produced file over /view and return its bytes.

        type=="output" drops temp previews (a preview node registers temp files). Exactly one real
        output is the contract: silently picking one of N would hide a graph whose batch size is
        not 1, so the raw outputs are printed and the render stops.

        `extensions` is how a caller says which medium it came for: a video graph often carries an
        image node as well, so the file is chosen by its own name rather than by which key it
        landed in -- which key that is (images, gifs, videos, audio) is the node's own business.
        No extensions means the images a photo graph makes.
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
        if len(outputs) > 1:
            raise RuntimeError(
                f"1 çıktı bekleniyordu, {len(outputs)} geldi — grafikte Batch Size 1 mi?\n{came}")
        item = outputs[0]
        resp = self._send("get", f"{self.base}/view", timeout=300, params={
            "filename": item["filename"],
            "subfolder": item.get("subfolder", ""),
            "type": "output",
        })
        resp.raise_for_status()
        return resp.content

    def interrupt(self):
        """Cut whatever ComfyUI is rendering right now; harmless when nothing runs."""
        resp = self._send("post", f"{self.base}/interrupt", timeout=30)
        resp.raise_for_status()
