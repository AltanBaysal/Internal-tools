"""ComfyUI HTTP transport -- submit a graph, wait for it, pull the produced file.

Media-agnostic on purpose: no node id, no prompt, no seed, no photo/video concept. Whoever calls
this decides what the graph means. `http`, `sleep` and `now` are injected so tests need no server.
"""
import json
import time
import uuid

import requests

from backend.services.comfy.errors import ComfyExecutionError, describe


class ComfyClient:
    def __init__(self, base_url, http=requests, poll_interval=5, sleep=time.sleep,
                 now=time.monotonic):
        self.base = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())
        self._http = http
        self._poll_interval = poll_interval
        self._sleep = sleep
        self._now = now

    def submit(self, workflow):
        """Queue the graph; returns ComfyUI's prompt_id."""
        resp = self._http.post(f"{self.base}/prompt",
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
            history = self._http.get(f"{self.base}/history/{prompt_id}", timeout=30).json()
            if prompt_id in history:
                entry = history[prompt_id]
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise ComfyExecutionError(*describe(status))
                return entry
            self._sleep(self._poll_interval)

    def fetch_output(self, history_entry):
        """Download THE produced file over /view and return its bytes.

        type=="output" drops temp previews (a preview node registers temp files). Exactly one real
        output is the contract: silently picking one of N would hide a graph whose batch size is
        not 1, so the raw outputs are printed and the render stops.
        """
        outputs = [item
                   for node_output in history_entry.get("outputs", {}).values()
                   for item in node_output.get("images", [])
                   if item.get("type", "output") == "output"]
        if len(outputs) != 1:
            raise RuntimeError(
                f"1 çıktı görseli bekleniyordu, {len(outputs)} geldi — grafikte Batch Size 1 mi?\n"
                + json.dumps(history_entry.get("outputs", {}), indent=2, ensure_ascii=False))
        item = outputs[0]
        resp = self._http.get(f"{self.base}/view", timeout=300, params={
            "filename": item["filename"],
            "subfolder": item.get("subfolder", ""),
            "type": "output",
        })
        resp.raise_for_status()
        return resp.content

    def interrupt(self):
        """Cut whatever ComfyUI is rendering right now; harmless when nothing runs."""
        resp = self._http.post(f"{self.base}/interrupt", timeout=30)
        resp.raise_for_status()
