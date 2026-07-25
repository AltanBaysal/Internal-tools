# Queen Editor — Bölüm 4: Tek foto · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Karta tıkla → proje ekranı → prompt yaz → **Üret** → ComfyUI bir foto üretsin, `queenEditor/<proje>/0_a.png` olarak Drive'a düşsün ve ekranda görünsün.

**Architecture:** `services/comfy` yalnız taşıma (HTTP + hata sınıflandırma), `services/drive` genel dosya I/O'suyla büyür. Foto'ya özgü her şey `features/photo_generation` içinde: grafiği bilen `data/comfy_photo_generator.py`, adları bilen `data/photo_store.py`, thread'i taşıyan `runner.py`, saf `domain/`. Üretim arka planda çalışır, UI `GET /api/status` ile sorar. Notebook'un kurulum hücreleri `nova-3dcg/api.ipynb`'den birebir kopya.

**Tech Stack:** Python 3 · Flask · pytest · React 18 · Vite 5 · Google Colab (T4 GPU + Drive) · ComfyUI (headless, port 8188) · cloudflared

**Spec:** [2026-07-25-queen-editor-b4-tek-foto-design.md](../specs/2026-07-25-queen-editor-b4-tek-foto-design.md) · **Şemsiye:** [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md) · **Bağımsızlık:** [2026-07-25-queen-editor-bagimsizlik-design.md](../specs/2026-07-25-queen-editor-bagimsizlik-design.md)

## Global Constraints

- **Dil ayrımı:** kod yorumları/docstring ve commit mesajları **İngilizce**; UI metni ve notebook markdown/`print`/`assert` **Türkçe**.
- **Katman yasakları:** `feature ↛ feature`, `servis ↛ feature`, `servis ↛ servis`. `domain/` `flask`/`requests`/dosya yolu bilmez. Grafik bilgisi (node id'leri) **yalnız** `data/comfy_photo_generator.py`'de; dosya adı şeması (`N_a.png`) **yalnız** `data/photo_store.py`'de. Bağlama yalnız `main.py`.
- **Feature adı `photo_generation`** (backend + frontend) — `generation` değil; video kendi feature'ı olacak.
- **`services/comfy` medya bilmez:** node id'si, prompt, seed, foto kavramı yok — yalnız ComfyUI protokolü.
- **Merkezi iş servisi yok:** `runner.py` feature'ın malı. Video kendi kopyasını yazacak (kullanıcı kararı: bağımlılık yerine tekrar).
- **Devralınan davranış (kod kopyalanmadan):** POSITIVE node `3` ve NEGATIVE node `4` için **çift alan** (`wildcard_text` + `populated_text`, Impact Pack #483) · Seed node `40`, değeri **biz** üretiriz (export'taki `-1` asla gönderilmez) · history'de `type=="output"` filtresi + **tam 1 çıktı** sözleşmesi · `node_type` içinde `loader` **geçiyorsa** hata **infra** — nova-3dcg burada `endswith` kullanıyor, ama grafiğin `CheckpointLoaderSimple` ve `Power Lora Loader (rgthree)` node'ları o testten kaçıyor; bu fonksiyon kopyalanmadığı (kendi katmanımıza yazıldığı) için bilinçli sapma.
- **Bölüm 4'te node `4`'e yazılmaz** (negatif kutusu yok — export'un negatifi geçerli); yükleyici yalnız yazdığı node'ları doğrular (`3`, `40`). Node `4` Bölüm 5'te eklenir.
- **Notebook kurulum hücreleri birebir kopya** (`nova-3dcg/api.ipynb`): helpers · custom node'lar · modeller · ComfyUI başlatma. İki bilinçli sapma: (1) cookie değeri Colab Secrets'tan (`CIVITAI_COOKIE`), (2) `describe_comfy_error` notebook'a kopyalanmaz — backend'e taşındı. Markdown hücreleri queen-editor bağlamına uyarlanır (kod verbatim).
- **Modeller her oturum yeniden iner** — Drive cache yok (nova-3dcg deseni).
- **Test komutu:** `queen-editor/` içinden `python -m pytest -q`. Hiçbir test ComfyUI, Drive, GPU veya ağ istemez. Bölüm 3'ün **42 testi** bozulmaz.
- **Frontend derleme:** `queen-editor/frontend/` içinde `npm run build`, `dist/` commit'lenir (CLAUDE.md kuralı).
- **Commit politikası:** Colab'da doğrulanmadan commit yok; **ama** Colab kodu repodan klonluyor — son task'ta önce commit+push, sonra doğrulama (kullanıcı onayıyla).

---

### Task 1: `services/comfy/errors.py` — hata sınıflandırma

**Files:**
- Create: `queen-editor/backend/services/comfy/__init__.py` (boş)
- Create: `queen-editor/backend/services/comfy/errors.py`
- Test: `queen-editor/backend/tests/test_comfy_errors.py`

**Interfaces:**
- Consumes: (yok)
- Produces: `ComfyExecutionError(text, traceback_text, infra)` — `.text`, `.traceback_text`, `.infra` alanlarıyla; `describe(status) -> (text, traceback_text, infra)`.

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_comfy_errors.py`

```python
from backend.services.comfy.errors import ComfyExecutionError, describe


def _status(node_type, message="boom"):
    return {
        "status_str": "error",
        "messages": [
            ["execution_start", {}],
            ["execution_error", {
                "node_id": "41",
                "node_type": node_type,
                "exception_type": "RuntimeError",
                "exception_message": message,
                "current_inputs": {"seed": 7},
                "traceback": ["line 1\n", "line 2\n"],
            }],
        ],
    }


def test_describe_reports_node_and_message():
    text, tb, infra = describe(_status("KSampler"))
    assert "node 41 (KSampler)" in text
    assert "RuntimeError: boom" in text
    assert tb == "line 1\nline 2\n"
    assert infra is False


def test_loader_node_is_infra():
    _text, _tb, infra = describe(_status("CheckpointLoaderSimple"))
    assert infra is True


def test_loader_is_recognised_mid_name():
    # A real node in our graph: the name ends in "(rgthree)", not in "loader".
    _text, _tb, infra = describe(_status("Power Lora Loader (rgthree)"))
    assert infra is True


def test_status_without_execution_error_is_dumped_raw():
    text, tb, infra = describe({"status_str": "error", "messages": [["execution_cached", {}]]})
    assert "execution_cached" in text          # the raw status, not an invented cause
    assert (tb, infra) == ("", False)


def test_error_carries_its_parts():
    err = ComfyExecutionError("t", "tb", True)
    assert (str(err), err.text, err.traceback_text, err.infra) == ("t", "t", "tb", True)
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_comfy_errors.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.services.comfy'`.

- [ ] **Step 3: `services/comfy/__init__.py` (boş) ve `errors.py` yaz**

```python
"""ComfyUI error shapes -- classify, never invent a cause.

The classifier answers one question: did a model loader fail? A loader failure means the model is
broken or missing, so every following render would hit the identical error; anything else is
specific to this render. Everything else in the message is passed through verbatim.
"""
import json


class ComfyExecutionError(RuntimeError):
    """A prompt failed inside ComfyUI. Carries the raw error plus the infra flag."""

    def __init__(self, text, traceback_text, infra):
        super().__init__(text)
        self.text = text
        self.traceback_text = traceback_text
        self.infra = infra


def describe(status):
    """ComfyUI history status -> (text, traceback_text, infra).

    Falls back to dumping the raw status: an unrecognised shape must stay visible, not be
    summarised into a guess.
    """
    for entry in status.get("messages", []):
        if not (isinstance(entry, (list, tuple)) and len(entry) == 2):
            continue
        kind, data = entry
        if kind != "execution_error" or not isinstance(data, dict):
            continue
        node_type = str(data.get("node_type", "?"))
        text = (f"node {data.get('node_id')} ({node_type})\n"
                f"{data.get('exception_type')}: {str(data.get('exception_message', '')).strip()}\n"
                f"inputs: {data.get('current_inputs')}")
        tb = "".join(data.get("traceback", []) or [])
        # Substring, not suffix: our graph's loaders include CheckpointLoaderSimple and
        # "Power Lora Loader (rgthree)". Matching only the end would let the checkpoint -- the
        # model likeliest to be missing, since it is the gated Civitai one -- pass as a
        # render-specific error, so every following render would repeat the same failure.
        return text, tb, "loader" in node_type.lower()
    return f"status: {json.dumps(status, ensure_ascii=False)}", "", False
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (42 + 5 = 47).

---

### Task 2: `services/comfy/client.py` — HTTP taşıma

**Files:**
- Create: `queen-editor/backend/services/comfy/client.py`
- Test: `queen-editor/backend/tests/test_comfy_client.py`

**Interfaces:**
- Consumes: `describe`, `ComfyExecutionError` (Task 1)
- Produces: `ComfyClient(base_url, http=requests, poll_interval=5, sleep=time.sleep, now=time.monotonic)` — `submit(workflow) -> prompt_id` · `wait(prompt_id, timeout) -> history_entry` · `fetch_output(history_entry) -> bytes`.

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_comfy_client.py`

```python
import pytest

from backend.services.comfy.client import ComfyClient
from backend.services.comfy.errors import ComfyExecutionError


class FakeResponse:
    def __init__(self, payload=None, status_code=200, content=b""):
        self._payload = payload if payload is not None else {}
        self.status_code = status_code
        self.text = "raw body"
        self.content = content

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeHttp:
    """Stands in for the requests module: records calls, replays queued responses."""

    def __init__(self, post=None, gets=()):
        self._post = post or FakeResponse({"prompt_id": "p1"})
        self._gets = list(gets)
        self.posted = None
        self.get_calls = []

    def post(self, url, json=None, timeout=None):
        self.posted = (url, json)
        return self._post

    def get(self, url, timeout=None, params=None):
        self.get_calls.append((url, params))
        return self._gets.pop(0) if self._gets else FakeResponse({})


def client_with(http, **kw):
    return ComfyClient("http://comfy:8188", http=http, poll_interval=0, sleep=lambda s: None, **kw)


def test_submit_returns_prompt_id_and_sends_workflow():
    http = FakeHttp()
    assert client_with(http).submit({"3": {}}) == "p1"
    url, body = http.posted
    assert url == "http://comfy:8188/prompt"
    assert body["prompt"] == {"3": {}} and body["client_id"]


def test_submit_raises_with_raw_body_on_http_error():
    http = FakeHttp(post=FakeResponse(status_code=400))
    with pytest.raises(RuntimeError) as exc:
        client_with(http).submit({})
    assert "400" in str(exc.value) and "raw body" in str(exc.value)


def test_submit_raises_on_node_errors():
    http = FakeHttp(post=FakeResponse({"prompt_id": "p1", "node_errors": {"3": "bad"}}))
    with pytest.raises(RuntimeError) as exc:
        client_with(http).submit({})
    assert "node_errors" in str(exc.value)


def test_wait_returns_entry_when_history_appears():
    entry = {"outputs": {}, "status": {"status_str": "success"}}
    http = FakeHttp(gets=[FakeResponse({}), FakeResponse({"p1": entry})])
    assert client_with(http).wait("p1", timeout=100) == entry


def test_wait_raises_comfy_error_on_failed_status():
    entry = {"status": {"status_str": "error", "messages": [
        ["execution_error", {"node_id": "9", "node_type": "CheckpointLoaderSimple",
                             "exception_type": "OSError", "exception_message": "no file"}]]}}
    http = FakeHttp(gets=[FakeResponse({"p1": entry})])
    with pytest.raises(ComfyExecutionError) as exc:
        client_with(http).wait("p1", timeout=100)
    assert exc.value.infra is True


def test_wait_times_out():
    ticks = iter([0, 10, 20, 30])
    http = FakeHttp()
    with pytest.raises(TimeoutError):
        client_with(http, now=lambda: next(ticks)).wait("p1", timeout=15)


def test_fetch_output_downloads_the_single_output_image():
    entry = {"outputs": {"55": {"images": [
        {"filename": "a.png", "subfolder": "", "type": "output"},
        {"filename": "preview.png", "subfolder": "", "type": "temp"},
    ]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"PNGDATA")])
    assert client_with(http).fetch_output(entry) == b"PNGDATA"
    _url, params = http.get_calls[0]
    assert params["filename"] == "a.png" and params["type"] == "output"


def test_fetch_output_refuses_when_not_exactly_one_output():
    entry = {"outputs": {"55": {"images": [
        {"filename": "a.png", "type": "output"}, {"filename": "b.png", "type": "output"}]}}}
    with pytest.raises(RuntimeError) as exc:
        client_with(FakeHttp()).fetch_output(entry)
    assert "Batch Size" in str(exc.value)
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_comfy_client.py -q`
Expected: FAIL — `ModuleNotFoundError: ...comfy.client`.

- [ ] **Step 3: `services/comfy/client.py` yaz**

```python
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
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (47 + 8 = 55).

---

### Task 3: `services/drive/storage.py` — dosya I/O ile büyür

**Files:**
- Modify: `queen-editor/backend/services/drive/storage.py`
- Test: `queen-editor/backend/tests/test_drive_storage.py` (mevcut dosyaya ekleme)

**Interfaces:**
- Consumes: `DriveStorage(root)` (Bölüm 3)
- Produces: `dir_exists(subdir) -> bool` · `list_files(subdir) -> list[str]` · `write_bytes(subdir, name, data) -> None` · `dir_path(subdir) -> str`. Mevcut `list_dirs()` / `make_dir(name)` değişmez.

- [ ] **Step 1: Failing testleri mevcut dosyanın sonuna ekle**

```python
def test_dir_exists(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    assert storage.dir_exists("düğün") is True
    assert storage.dir_exists("yok") is False


def test_write_bytes_then_list_files(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"
    assert storage.list_files("düğün") == ["0_a.png"]


def test_list_files_skips_directories(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("düğün/altklasör")
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    assert storage.list_files("düğün") == ["0_a.png"]


def test_list_files_returns_empty_for_missing_dir(tmp_path):
    assert DriveStorage(str(tmp_path)).list_files("yok") == []


def test_dir_path_joins_root_and_subdir(tmp_path):
    storage = DriveStorage(str(tmp_path))
    assert storage.dir_path("düğün") == str(tmp_path / "düğün")
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_drive_storage.py -q`
Expected: FAIL — `AttributeError: 'DriveStorage' object has no attribute 'dir_exists'`.

- [ ] **Step 3: `storage.py`'ye dört metodu ekle** (`make_dir`'in altına, sınıf içinde)

```python
    def dir_exists(self, subdir):
        return os.path.isdir(os.path.join(self.root, subdir))

    def dir_path(self, subdir):
        """Absolute path of root/subdir -- for callers that hand a directory to someone else
        (Flask serves files straight from disk)."""
        return os.path.join(self.root, subdir)

    def list_files(self, subdir):
        """File names directly under root/subdir. A missing folder lists as empty: 'no files yet'
        and 'no folder yet' are the same answer to the caller, and the folder is created on write."""
        path = os.path.join(self.root, subdir)
        if not os.path.isdir(path):
            return []
        with os.scandir(path) as entries:
            return [e.name for e in entries if e.is_file()]

    def write_bytes(self, subdir, name, data):
        """Write root/subdir/name, creating the folder if needed."""
        path = os.path.join(self.root, subdir)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "wb") as f:
            f.write(data)
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (55 + 5 = 60).

---

### Task 4: Grafiğin repo kopyası + koruma testi

**Files:**
- Create: `queen-editor/workflow_api.json` (kopya)
- Modify: `queen-editor/backend/config.py`
- Test: `queen-editor/backend/tests/test_workflow_asset.py`

**Interfaces:**
- Consumes: (yok)
- Produces: `config.WORKFLOW_PATH` · `config.COMFY_URL` · `config.RENDER_TIMEOUT` · `config.POLL_INTERVAL`; repoda API formatında, node `3`/`40` içeren `workflow_api.json`.

- [ ] **Step 1: Grafiği kopyala**

`collab-toolbox/photo_generator/nova-3dcg/workflow_api.json` dosyasını **birebir** `queen-editor/workflow_api.json` olarak yaz (Read ile oku, Write ile yaz — içeriğe dokunma). Bu bizim kopyamız; nova-3dcg'nin dosyası okunmaz (bağımsızlık kuralı).

- [ ] **Step 2: `config.py`'ye ComfyUI ayarlarını ekle** (`DRIVE_ROOT`'un altına)

```python
# ComfyUI runs on the same Colab machine; the notebook can point us elsewhere (tests do too).
COMFY_URL = os.environ.get("QE_COMFY_URL", "http://127.0.0.1:8188")

# The graph ships in the repo (our own copy -- never read collab-toolbox's file).
WORKFLOW_PATH = os.path.join(os.path.dirname(_BACKEND_DIR), "workflow_api.json")

RENDER_TIMEOUT = 15 * 60   # seconds for one photo; a T4 render is ~1 min, so this is a stall guard
POLL_INTERVAL = 5          # seconds between /history polls
```

- [ ] **Step 3: Koruma testi yaz** — `queen-editor/backend/tests/test_workflow_asset.py`

```python
import json

from backend import config

# The shipped graph is an asset, so its shape is verified here: a UI-format export or a renamed
# node would only surface as a failed render on Colab otherwise.


def test_workflow_is_api_format_with_the_nodes_we_patch():
    with open(config.WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)
    assert "nodes" not in workflow, "UI formatında export — 'Workflow → Export (API)' gerekiyor"
    assert workflow["3"]["class_type"] == "ImpactWildcardProcessor"
    assert {"wildcard_text", "populated_text"} <= set(workflow["3"]["inputs"])
    assert "seed" in workflow["40"]["inputs"]
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (60 + 1 = 61). Fail ederse kopyalanan dosya yanlış export'tur — Step 1'i tekrarla.

---

### Task 5: `photo_generation/runner.py` — arka plan işçisi

**Files:**
- Create: `queen-editor/backend/features/photo_generation/__init__.py` (boş)
- Create: `queen-editor/backend/features/photo_generation/runner.py`
- Test: `queen-editor/backend/tests/test_photo_runner.py`

**Interfaces:**
- Consumes: (yok)
- Produces: `PhotoRunner(spawn=None)` — `start(project, step) -> bool` (`False` = meşgul) · `status() -> dict` (`{"status": "idle"}` · `{"status": "running", "project": …}` · `{"status": "done", "project": …, "file": …}` · `{"status": "error", "project": …, "error": …}`). `step` argümansız çağrılır, kaydedilen dosya adını döner.

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_photo_runner.py`

```python
from backend.features.photo_generation.runner import PhotoRunner


def sync_runner():
    """spawn=lambda fn: fn() runs the job inline -- the test needs no thread and no sleep."""
    return PhotoRunner(spawn=lambda fn: fn())


def test_starts_idle():
    assert PhotoRunner().status() == {"status": "idle"}


def test_done_carries_the_saved_file_name():
    runner = sync_runner()
    assert runner.start("düğün", lambda: "0_a.png") is True
    assert runner.status() == {"status": "done", "project": "düğün", "file": "0_a.png"}


def test_failure_becomes_error_with_the_real_message():
    runner = sync_runner()

    def boom():
        raise RuntimeError("ComfyUI öldü")

    runner.start("düğün", boom)
    state = runner.status()
    assert state["status"] == "error" and state["error"] == "ComfyUI öldü"


def test_second_start_is_refused_while_running():
    runner = PhotoRunner(spawn=lambda fn: None)   # never runs -> stays "running"
    assert runner.start("düğün", lambda: "0_a.png") is True
    assert runner.status()["status"] == "running"
    assert runner.start("düğün", lambda: "1_a.png") is False


def test_a_finished_job_does_not_block_the_next_one():
    runner = sync_runner()
    runner.start("düğün", lambda: "0_a.png")
    assert runner.start("düğün", lambda: "1_a.png") is True
    assert runner.status()["file"] == "1_a.png"
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_runner.py -q`
Expected: FAIL — `ModuleNotFoundError: ...photo_generation.runner`.

- [ ] **Step 3: `features/photo_generation/__init__.py` (boş) ve `runner.py` yaz**

```python
"""One photo job at a time, in the background -- this feature's own worker.

Deliberately NOT a shared service: video generation will copy this file rather than depend on it,
so a change here can never break another pipeline (the maintenance rule for this project).

A photo takes 30-90s, far longer than a request should stay open, so `start` returns immediately
and the UI asks `status()`. `spawn` is injected: production starts a daemon thread, tests run the
job inline and stay deterministic.
"""
import threading


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class PhotoRunner:
    def __init__(self, spawn=None):
        self._spawn = spawn or _thread_spawn
        self._lock = threading.Lock()
        self._state = {"status": "idle"}

    def status(self):
        with self._lock:
            return dict(self._state)

    def start(self, project, step):
        """Claim the worker and run `step` in the background. False means one is already running."""
        with self._lock:
            if self._state["status"] == "running":
                return False
            self._state = {"status": "running", "project": project}
        self._spawn(lambda: self._run(project, step))
        return True

    def _run(self, project, step):
        try:
            filename = step()
        except Exception as exc:   # the message is user-facing: whatever really failed, verbatim
            self._set({"status": "error", "project": project, "error": str(exc)})
            return
        self._set({"status": "done", "project": project, "file": filename})

    def _set(self, state):
        with self._lock:
            self._state = state
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (61 + 5 = 66).

---

### Task 6: `photo_generation/domain` — portlar + use case'ler

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/__init__.py` (boş)
- Create: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/__init__.py` (boş)
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/start_generation.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/get_status.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `PhotoRunner.start/status` (Task 5)
- Produces:
  - `PhotoGenerator` Protocol: `generate(prompt: str, seed: int) -> bytes`
  - `PhotoStore` Protocol: `project_exists(project) -> bool` · `next_number(project) -> int` · `save(project, number, letter, data) -> str` · `photo_dir(project) -> str`
  - `start_generation(runner, store, generator, new_seed, project, prompt) -> None`; `InvalidPrompt` / `ProjectMissing` / `Busy` istisnaları (mesajları Türkçe, doğrudan kullanıcıya gider)
  - `get_status(runner) -> dict`

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_photo_usecases.py`

```python
import pytest

from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.start_generation import (
    Busy,
    InvalidPrompt,
    ProjectMissing,
    start_generation,
)
from backend.features.photo_generation.runner import PhotoRunner


class FakeStore:
    def __init__(self, projects=("düğün",), next_no=0):
        self.projects = list(projects)
        self.next_no = next_no
        self.saved = []

    def project_exists(self, project):
        return project in self.projects

    def next_number(self, project):
        return self.next_no

    def save(self, project, number, letter, data):
        self.saved.append((project, number, letter, data))
        return f"{number}_{letter}.png"

    def photo_dir(self, project):
        return f"/fake/{project}"


class FakeGenerator:
    def __init__(self):
        self.calls = []

    def generate(self, prompt, seed):
        self.calls.append((prompt, seed))
        return b"PNG"


def sync_runner():
    return PhotoRunner(spawn=lambda fn: fn())


def start(runner, store, generator, project="düğün", prompt="kraliçe tahtta", seed=99):
    return start_generation(runner, store, generator, lambda: seed, project, prompt)


def test_generates_and_saves_with_the_next_number():
    store, generator, runner = FakeStore(next_no=3), FakeGenerator(), sync_runner()
    start(runner, store, generator)
    assert generator.calls == [("kraliçe tahtta", 99)]
    assert store.saved == [("düğün", 3, "a", b"PNG")]
    assert runner.status() == {"status": "done", "project": "düğün", "file": "3_a.png"}


@pytest.mark.parametrize("prompt", ["", "   "])
def test_empty_prompt_is_rejected(prompt):
    store, generator = FakeStore(), FakeGenerator()
    with pytest.raises(InvalidPrompt) as exc:
        start(sync_runner(), store, generator, prompt=prompt)
    assert str(exc.value) == "Prompt boş olamaz."
    assert generator.calls == []


def test_missing_project_is_rejected():
    with pytest.raises(ProjectMissing) as exc:
        start(sync_runner(), FakeStore(), FakeGenerator(), project="yok")
    assert str(exc.value) == "Proje yok: yok"


def test_busy_runner_is_rejected():
    runner = PhotoRunner(spawn=lambda fn: None)   # stays "running"
    start(runner, FakeStore(), FakeGenerator())
    with pytest.raises(Busy) as exc:
        start(runner, FakeStore(), FakeGenerator())
    assert str(exc.value) == "Zaten bir üretim sürüyor."


def test_generator_failure_lands_in_the_status():
    class Broken:
        def generate(self, prompt, seed):
            raise RuntimeError("node 41: OOM")

    runner = sync_runner()
    start(runner, FakeStore(), Broken())
    assert runner.status()["error"] == "node 41: OOM"


def test_get_status_passes_the_runner_state_through():
    assert get_status(PhotoRunner()) == {"status": "idle"}
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_usecases.py -q`
Expected: FAIL — `ModuleNotFoundError: ...photo_generation.domain`.

- [ ] **Step 3: `domain/__init__.py` (boş) ve `domain/ports.py` yaz**

```python
"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol


class PhotoGenerator(Protocol):
    def generate(self, prompt: str, seed: int) -> bytes:
        """Render one photo and return its bytes."""
        ...


class PhotoStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def next_number(self, project: str) -> int:
        """Highest existing number + 1, so nothing is ever overwritten."""
        ...

    def save(self, project: str, number: int, letter: str, data: bytes) -> str:
        """Persist the photo; returns the file name it was stored under."""
        ...

    def photo_dir(self, project: str) -> str:
        """Absolute folder the photos live in -- presentation serves files from it."""
        ...
```

- [ ] **Step 4: `domain/usecases/__init__.py` (boş) ve `usecases/start_generation.py` yaz**

```python
"""Start one photo: validate, reserve a number, hand a single step to the runner.

Pure: the seed comes from an injected `new_seed` callable (randomness would make this untestable),
and the runner/store/generator are ports. The exception messages are the user-facing Turkish text --
presentation maps them to status codes and forwards them untouched.
"""


class InvalidPrompt(Exception):
    """Empty prompt (message is user-facing)."""


class ProjectMissing(Exception):
    """No such project folder."""


class Busy(Exception):
    """A generation is already running."""


def start_generation(runner, store, generator, new_seed, project, prompt):
    if not prompt or not prompt.strip():
        raise InvalidPrompt("Prompt boş olamaz.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    number = store.next_number(project)
    seed = new_seed()

    def step():
        # One photo per job in Part 4; Part 5 hands the runner a list of these.
        data = generator.generate(prompt, seed)
        return store.save(project, number, "a", data)

    if not runner.start(project, step):
        raise Busy("Zaten bir üretim sürüyor.")
```

- [ ] **Step 5: `usecases/get_status.py` yaz**

```python
"""What the UI polls: the runner's current state, unchanged."""


def get_status(runner):
    return runner.status()
```

- [ ] **Step 6: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (66 + 7 = 73).

---

### Task 7: `data/comfy_photo_generator.py` — grafiği bilen tek yer

**Files:**
- Create: `queen-editor/backend/features/photo_generation/data/__init__.py` (boş)
- Create: `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`
- Test: `queen-editor/backend/tests/test_comfy_photo_generator.py`

**Interfaces:**
- Consumes: `ComfyClient.submit/wait/fetch_output` (Task 2)
- Produces: `ComfyPhotoGenerator(client, workflow_path, timeout)` — `PhotoGenerator` portunu gerçekler (`generate(prompt, seed) -> bytes`).

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_comfy_photo_generator.py`

```python
import json

import pytest

from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator


class FakeClient:
    def __init__(self):
        self.submitted = None
        self.waited = None

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        self.waited = (prompt_id, timeout)
        return {"outputs": {}}

    def fetch_output(self, history):
        return b"PNG"


def write_graph(tmp_path, graph=None):
    path = tmp_path / "workflow_api.json"
    path.write_text(json.dumps(graph if graph is not None else {
        "3": {"inputs": {"wildcard_text": "eski", "populated_text": "eski"},
              "class_type": "ImpactWildcardProcessor"},
        "40": {"inputs": {"seed": -1}, "class_type": "Seed (rgthree)"},
    }), encoding="utf-8")
    return str(path)


def test_generate_patches_the_graph_and_returns_bytes(tmp_path):
    client = FakeClient()
    generator = ComfyPhotoGenerator(client, write_graph(tmp_path), timeout=60)

    assert generator.generate("kraliçe tahtta", 12345) == b"PNG"

    node3 = client.submitted["3"]["inputs"]
    assert node3["wildcard_text"] == "kraliçe tahtta"      # Impact Pack #483: both fields
    assert node3["populated_text"] == "kraliçe tahtta"
    assert client.submitted["40"]["inputs"]["seed"] == 12345   # never the export's -1
    assert client.waited == ("p1", 60)


def test_generate_does_not_mutate_the_file_on_disk(tmp_path):
    path = write_graph(tmp_path)
    generator = ComfyPhotoGenerator(FakeClient(), path, timeout=60)
    generator.generate("yeni", 1)
    with open(path, encoding="utf-8") as f:
        assert json.load(f)["3"]["inputs"]["wildcard_text"] == "eski"


def test_ui_format_export_is_rejected(tmp_path):
    path = write_graph(tmp_path, {"nodes": [], "links": []})
    with pytest.raises(RuntimeError) as exc:
        ComfyPhotoGenerator(FakeClient(), path, timeout=60).generate("x", 1)
    assert "Export (API)" in str(exc.value)


def test_missing_node_is_reported(tmp_path):
    path = write_graph(tmp_path, {"3": {"inputs": {"wildcard_text": "", "populated_text": ""}}})
    with pytest.raises(RuntimeError) as exc:
        ComfyPhotoGenerator(FakeClient(), path, timeout=60).generate("x", 1)
    assert "40" in str(exc.value)
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_comfy_photo_generator.py -q`
Expected: FAIL — `ModuleNotFoundError: ...data.comfy_photo_generator`.

- [ ] **Step 3: `data/__init__.py` (boş) ve `data/comfy_photo_generator.py` yaz**

```python
"""PhotoGenerator over ComfyUI -- the only place that knows what the graph looks like.

Node ids come from our own export (queen-editor/workflow_api.json):
  "3"  ImpactWildcardProcessor, _meta.title "POSITIVE"
  "40" Seed (rgthree) -> KSampler, FaceDetailer and both wildcard processors read it

A new export can renumber these; then this file changes and nothing else does. Node "4" (NEGATIVE)
is deliberately untouched in Part 4 -- the export's own negative applies until Part 5 adds the box.
"""
import json

PROMPT_NODE = "3"
SEED_NODE = "40"


class ComfyPhotoGenerator:
    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, seed):
        workflow = self._load()
        self._set_text(workflow, PROMPT_NODE, prompt)
        # The export ships seed -1: rgthree randomises that in the frontend widget, which does not
        # exist in API mode, so sending it through would pin every render to the same noise.
        workflow[SEED_NODE]["inputs"]["seed"] = seed

        prompt_id = self._client.submit(workflow)
        history = self._client.wait(prompt_id, self._timeout)
        return self._client.fetch_output(history)

    def _load(self):
        """Fresh copy per render -- patching is never written back to the shipped file."""
        with open(self._workflow_path, encoding="utf-8") as f:
            workflow = json.load(f)
        if "nodes" in workflow:
            raise RuntimeError("workflow_api.json UI formatında — ComfyUI'de "
                               "'Workflow → Export (API)' ile kaydet")
        for node_id in (PROMPT_NODE, SEED_NODE):
            if node_id not in workflow:
                raise RuntimeError(f"Workflow'da {node_id} node yok — graf değişmiş, "
                                   "node id'lerini güncelle")
        return workflow

    @staticmethod
    def _set_text(workflow, node_id, text):
        """Write BOTH text fields.

        Which one the server reads in API mode varies by build (Impact Pack #483: some never
        process wildcard_text), so writing both means this text is used either way.
        """
        workflow[node_id]["inputs"]["wildcard_text"] = text
        workflow[node_id]["inputs"]["populated_text"] = text
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (73 + 4 = 77).

---

### Task 8: `data/photo_store.py` — adları bilen tek yer

**Files:**
- Create: `queen-editor/backend/features/photo_generation/data/photo_store.py`
- Test: `queen-editor/backend/tests/test_photo_store.py`

**Interfaces:**
- Consumes: `DriveStorage.dir_exists/list_files/write_bytes/dir_path` (Task 3)
- Produces: `DrivePhotoStore(storage)` — `PhotoStore` portunu gerçekler.

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_photo_store.py`

```python
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.services.drive.storage import DriveStorage


def store_at(path):
    return DrivePhotoStore(DriveStorage(str(path)))


def test_project_exists_follows_the_folder(tmp_path):
    store = store_at(tmp_path)
    (tmp_path / "düğün").mkdir()
    assert store.project_exists("düğün") is True
    assert store.project_exists("yok") is False


def test_next_number_starts_at_zero(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).next_number("düğün") == 0


def test_next_number_is_highest_plus_one(tmp_path):
    project = tmp_path / "düğün"
    project.mkdir()
    for name in ("0_a.png", "7_c.png", "3_b.png", "notlar.txt", "_bozuk.png"):
        (project / name).write_bytes(b"x")
    assert store_at(tmp_path).next_number("düğün") == 8


def test_save_writes_the_file_and_returns_its_name(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).save("düğün", 4, "a", b"PNG") == "4_a.png"
    assert (tmp_path / "düğün" / "4_a.png").read_bytes() == b"PNG"


def test_photo_dir_is_the_project_folder(tmp_path):
    assert store_at(tmp_path).photo_dir("düğün") == str(tmp_path / "düğün")
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_store.py -q`
Expected: FAIL — `ModuleNotFoundError: ...data.photo_store`.

- [ ] **Step 3: `data/photo_store.py` yaz**

```python
"""PhotoStore over DriveStorage -- the only place that knows photos are named "<n>_<letter>.png"
inside the project folder.

Numbering never reuses a number: the next one is the highest on disk plus one, so a second run
appends instead of overwriting. Files that do not match the scheme (notes, half-written names) are
ignored rather than guessed at.
"""


def _number_of(filename):
    """"12_a.png" -> 12; anything that does not fit the scheme -> None."""
    if not filename.endswith(".png"):
        return None
    number, _, letter = filename[: -len(".png")].partition("_")
    if not number.isdigit() or len(letter) != 1 or not letter.isalpha():
        return None
    return int(number)


class DrivePhotoStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def next_number(self, project):
        numbers = [n for n in (_number_of(name) for name in self._storage.list_files(project))
                   if n is not None]
        return max(numbers) + 1 if numbers else 0

    def save(self, project, number, letter, data):
        filename = f"{number}_{letter}.png"
        self._storage.write_bytes(project, filename, data)
        return filename

    def photo_dir(self, project):
        return self._storage.dir_path(project)
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (77 + 5 = 82).

---

### Task 9: Route'lar + composition root

**Files:**
- Create: `queen-editor/backend/features/photo_generation/presentation/__init__.py` (boş)
- Create: `queen-editor/backend/features/photo_generation/presentation/routes.py`
- Modify: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_photo_routes.py`

**Interfaces:**
- Consumes: use case'ler (Task 6) · `DrivePhotoStore` (Task 8) · `ComfyPhotoGenerator` (Task 7) · `ComfyClient` (Task 2) · `create_app(dist_dir, blueprints)` (Bölüm 3)
- Produces: `make_photo_generation_blueprint(start_generation, get_status, photo_dir) -> Blueprint`; uçlar `POST /api/projects/<project>/generate`, `GET /api/status`, `GET /photos/<project>/<filename>`.

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_photo_routes.py`

```python
from functools import partial

from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.start_generation import start_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


class FakeGenerator:
    def generate(self, prompt, seed):
        return b"PNGDATA"


def make_client(tmp_path, generator=None, runner=None):
    drive = tmp_path / "drive"
    (drive / "düğün").mkdir(parents=True)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")

    store = DrivePhotoStore(DriveStorage(str(drive)))
    runner = runner or PhotoRunner(spawn=lambda fn: fn())
    blueprint = make_photo_generation_blueprint(
        start_generation=partial(start_generation, runner, store,
                                 generator or FakeGenerator(), lambda: 42),
        get_status=partial(get_status, runner),
        photo_dir=store.photo_dir,
    )
    app = create_app(dist_dir=str(dist), blueprints=[blueprint])
    return app.test_client(), drive


def test_generate_returns_202_and_writes_the_photo(tmp_path):
    client, drive = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe tahtta"})
    assert resp.status_code == 202
    assert (drive / "düğün" / "0_a.png").read_bytes() == b"PNGDATA"


def test_status_reports_done_with_the_file(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    assert client.get("/api/status").get_json() == {
        "status": "done", "project": "düğün", "file": "0_a.png"}


def test_status_is_idle_before_anything_runs(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/status").get_json() == {"status": "idle"}


def test_empty_prompt_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate", json={"prompt": "  "})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Prompt boş olamaz."


def test_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects/yok/generate", json={"prompt": "kraliçe"})
    assert resp.status_code == 404
    assert "yok" in resp.get_json()["error"]


def test_busy_runner_returns_409(tmp_path):
    client, _ = make_client(tmp_path, runner=PhotoRunner(spawn=lambda fn: None))
    client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    resp = client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Zaten bir üretim sürüyor."


def test_failed_generation_shows_the_real_error_in_status(tmp_path):
    class Broken:
        def generate(self, prompt, seed):
            raise RuntimeError("node 9 (CheckpointLoaderSimple): dosya yok")

    client, _ = make_client(tmp_path, generator=Broken())
    client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    state = client.get("/api/status").get_json()
    assert state["status"] == "error" and "CheckpointLoaderSimple" in state["error"]


def test_photo_is_served_from_the_project_folder(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "0_a.png").write_bytes(b"PNGDATA")
    assert client.get("/photos/düğün/0_a.png").data == b"PNGDATA"
    assert client.get("/photos/düğün/yok.png").status_code == 404
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_routes.py -q`
Expected: FAIL — `ModuleNotFoundError: ...presentation.routes`.

- [ ] **Step 3: `presentation/__init__.py` (boş) ve `presentation/routes.py` yaz**

```python
"""/api/projects/<project>/generate · /api/status · /photos/<project>/<file>

Translation only: no rules here. The use case's exception messages go out verbatim, so the wording
lives in exactly one place (the domain).
"""
from flask import Blueprint, jsonify, request, send_from_directory

from backend.features.photo_generation.domain.usecases.start_generation import (
    Busy,
    InvalidPrompt,
    ProjectMissing,
)


def make_photo_generation_blueprint(start_generation, get_status, photo_dir):
    """The callables are already bound to a runner/store/generator (see main.py)."""
    bp = Blueprint("photo_generation", __name__)

    @bp.post("/api/projects/<project>/generate")
    def post_generate(project):
        prompt = (request.get_json(silent=True) or {}).get("prompt", "")
        if not isinstance(prompt, str):
            prompt = ""   # anything but a string is treated as empty -> "Prompt boş olamaz."
        try:
            start_generation(project, prompt)
        except InvalidPrompt as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # 202: the photo takes 30-90s, so the request only reports that the job was accepted.
        return jsonify({"job": "running"}), 202

    @bp.get("/api/status")
    def status():
        return jsonify(get_status())

    @bp.get("/photos/<project>/<filename>")
    def serve_photo(project, filename):
        # send_from_directory rejects paths that escape the folder.
        return send_from_directory(photo_dir(project), filename)

    return bp
```

- [ ] **Step 4: `main.py`'yi genişlet** (mevcut projects bağlamasının altına, `create_app` çağrısından önce)

```python
import random

from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.start_generation import start_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.comfy.client import ComfyClient

_photo_store = DrivePhotoStore(_storage)
_comfy_client = ComfyClient(config.COMFY_URL, poll_interval=config.POLL_INTERVAL)
_photo_generator = ComfyPhotoGenerator(_comfy_client, config.WORKFLOW_PATH, config.RENDER_TIMEOUT)
_photo_runner = PhotoRunner()

_photo_bp = make_photo_generation_blueprint(
    start_generation=partial(start_generation, _photo_runner, _photo_store, _photo_generator,
                             lambda: random.randint(0, 2**31 - 1)),
    get_status=partial(get_status, _photo_runner),
    photo_dir=_photo_store.photo_dir,
)

app = create_app(blueprints=[_projects_bp, _photo_bp])
```

Dikkat: Bölüm 3'te `DriveStorage(config.DRIVE_ROOT)` doğrudan `DriveProjectStore(...)` çağrısının içinde kuruluyor. Bu task'ta o satır iki satıra ayrılır (aynı nesne iki store'a verilsin diye):

```python
_storage = DriveStorage(config.DRIVE_ROOT)
_project_store = DriveProjectStore(_storage)
```

Eski `app = create_app(blueprints=[_projects_bp])` satırı silinir (yukarıdaki iki blueprint'li hâli geçerli).

- [ ] **Step 5: Bütün testleri çalıştır**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (82 + 8 = 90).

- [ ] **Step 6: Sunucunun gerçekten ayağa kalktığını doğrula** (import hatası/yazım hatası kalmasın)

Run: `cd queen-editor && python -c "from backend.main import app; print(sorted(r.rule for r in app.url_map.iter_rules()))"`
Expected: liste `/api/health`, `/api/projects`, `/api/projects/<project>/generate`, `/api/status`, `/photos/<project>/<filename>`, `/`, `/<path:path>` kurallarını içerir.

---

### Task 10: Frontend — yol yönlendirmesi + kart tıklaması

**Files:**
- Create: `queen-editor/frontend/src/shared/router.js`
- Modify: `queen-editor/frontend/src/App.jsx`
- Modify: `queen-editor/frontend/src/features/projects/ProjectCard.jsx`

**Interfaces:**
- Consumes: (yok)
- Produces: `navigate(path)` · `useRoute() -> path` · `projectFromPath(path) -> string | null`. `ProjectCard` artık `/projects/<ad>`'a gider.

- [ ] **Step 1: `shared/router.js` yaz**

```js
import { useEffect, useState } from "react";

// Two screens, so two paths -- a router library would be more code than this file.
// Flask already serves index.html for any path (SPA fallback), so a reload keeps the screen.
export function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export function useRoute() {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  return path;
}

// Project names carry spaces and Turkish letters, so the path segment is encoded.
export function projectFromPath(path) {
  const match = path.match(/^\/projects\/(.+)$/);
  return match ? decodeURIComponent(match[1]) : null;
}
```

- [ ] **Step 2: `App.jsx`'i iki ekrana çevir**

```jsx
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import { projectFromPath, useRoute } from "./shared/router.js";

export default function App() {
  const project = projectFromPath(useRoute());
  return project ? <ProjectScreen project={project} /> : <ProjectsScreen />;
}
```

- [ ] **Step 3: `ProjectCard.jsx`'i tıklanır yap**

Yorumu ve `div`'i değiştir (dosyanın kalanı aynı):

```jsx
import { formatModified } from "../../shared/date.js";
import { navigate } from "../../shared/router.js";
import { Hand, Mono } from "../../vendor/kit.jsx";

// Part 4 wired the click: the card opens the project screen.
export default function ProjectCard({ name, modifiedAt }) {
  return (
    <div
      className="wf-card"
      onClick={() => navigate(`/projects/${encodeURIComponent(name)}`)}
      style={{
        aspectRatio: "4/3",
        padding: 14,
        cursor: "pointer",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
      }}
    >
```

- [ ] **Step 4: Derleme bu adımda kırılır — beklenen**

Run: `cd queen-editor/frontend && npm run build`
Expected: FAIL — `Could not resolve "./features/photo_generation/ProjectScreen.jsx"`. Task 11 o dosyayı yazıyor; derleme oradaki adımda yeşile döner.

---

### Task 11: Frontend — proje ekranı + üretim paneli

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Create: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Create: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx`
- Create: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Regenerate: `queen-editor/frontend/dist/`

**Interfaces:**
- Consumes: `POST /api/projects/<ad>/generate` · `GET /api/status` · `GET /photos/...` (Task 9) · `navigate` (Task 10) · kit primitifleri (Bölüm 3)
- Produces: `<ProjectScreen project={ad} />`.

- [ ] **Step 1: `shared/api.js`'ye üç fonksiyon ekle** (dosyanın sonuna)

```js
export async function generatePhoto(project, prompt) {
  return request(`/api/projects/${encodeURIComponent(project)}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
}

export async function getStatus() {
  return request("/api/status");
}

// Plain URL, not a fetch: the browser loads it into an <img>.
export function photoUrl(project, file) {
  return `/photos/${encodeURIComponent(project)}/${encodeURIComponent(file)}`;
}
```

- [ ] **Step 2: `features/photo_generation/useGeneration.js` yaz**

```js
import { useCallback, useEffect, useRef, useState } from "react";

import { generatePhoto, getStatus } from "../../shared/api.js";

const POLL_MS = 2000;

// The photo takes 30-90s, so the server answers 202 and we ask /api/status until it settles.
// Polling also runs once on mount: a reload during or after a job picks the state back up.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  const [error, setError] = useState(null);   // rejected request (400/404/409), not a failed render
  const timer = useRef(null);

  const poll = useCallback(() => {
    getStatus()
      .then((state) => {
        setJob(state);
        if (state.status === "running") {
          timer.current = setTimeout(poll, POLL_MS);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    poll();
    return () => clearTimeout(timer.current);
  }, [poll]);

  const generate = useCallback(
    (prompt) => {
      setError(null);
      return generatePhoto(project, prompt)
        .then(() => {
          setJob({ status: "running", project });
          timer.current = setTimeout(poll, POLL_MS);
        })
        .catch((err) => setError(err.message));
    },
    [project, poll],
  );

  return { job, error, generate };
}
```

- [ ] **Step 3: `features/photo_generation/GeneratePanel.jsx` yaz**

```jsx
import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";

const RAW_ERROR = {
  color: "var(--ink-3)",
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 3,
  padding: "6px 8px",
  maxWidth: 520,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

// Part 4 is one prompt and one photo: no negative box, no variants, no Stop (Part 5).
export default function GeneratePanel({ job, error, onGenerate }) {
  const [prompt, setPrompt] = useState("");
  const running = job.status === "running";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 520 }}>
      <Mono size={11} style={{ color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" }}>
        Prompt
      </Mono>
      <textarea
        className="wf-input"
        rows={4}
        value={prompt}
        disabled={running}
        onChange={(e) => setPrompt(e.target.value)}
        style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 12.5 }}
      />
      <Btn hl disabled={!prompt.trim() || running} onClick={() => onGenerate(prompt)}
           style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
        <Icon.Sparkle /> {running ? "üretiliyor…" : "Üret"}
      </Btn>

      {running && <Mono size={11} style={{ color: "var(--accent)" }}>ComfyUI çalışıyor — 1-2 dakika sürebilir</Mono>}
      {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
      {job.status === "error" && (
        <>
          <span style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
            <Icon.Warn />
            <Note size={13} style={{ color: "var(--danger)", fontWeight: 500 }}>Üretim başarısız</Note>
          </span>
          {/* The server's own error text -- we never guess the cause. */}
          <Mono size={11} style={RAW_ERROR}>{job.error}</Mono>
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 4: `features/photo_generation/ProjectScreen.jsx` yaz**

```jsx
import { photoUrl } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import { Btn, Hand, Mono, Note } from "../../vendor/kit.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import { useGeneration } from "./useGeneration.js";

// Part 4 skeleton: header + one prompt + the produced photo. Part 5 replaces the body with
// artboard 03 (prompt list, negative, variants, 5-column gallery).
export default function ProjectScreen({ project }) {
  const { job, error, generate } = useGeneration(project);
  const photo = job.status === "done" && job.project === project ? job.file : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr auto 1fr",
        alignItems: "center",
        padding: "14px 32px",
        background: "var(--bg-2)",
        borderBottom: "1px solid var(--border)",
      }}>
        <Btn ghost onClick={() => navigate("/")}>← Projeler</Btn>
        <Hand size={20}>{project}</Hand>
        <span />
      </div>

      <div style={{ flex: 1, display: "flex", gap: 32, padding: "24px 32px", alignItems: "flex-start" }}>
        <GeneratePanel job={job} error={error} onGenerate={generate} />

        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
          {photo ? (
            <>
              {/* New tab on click -- the same gesture the gallery will use in Part 5. */}
              <a href={photoUrl(project, photo)} target="_blank" rel="noreferrer">
                <img src={photoUrl(project, photo)} alt={photo}
                     style={{ maxWidth: "100%", border: "1px solid var(--border)", borderRadius: 4 }} />
              </a>
              <Mono size={11} style={{ color: "var(--ink-3)" }}>{photo}</Mono>
            </>
          ) : (
            <Note size={13} style={{ color: "var(--ink-3)" }}>
              Prompt yaz, Üret'e bas — fotoğraf burada belirecek
            </Note>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Derle**

Run: `cd queen-editor/frontend && npm run build`
Expected: PASS — `dist/index.html` + `dist/assets/*` yeniden üretilir, uyarı yok.

- [ ] **Step 6: Backend testleri hâlâ geçiyor mu**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (89).

---

### Task 12: Notebook — ComfyUI kurulumu (birebir kopya) + T4 + cookie

**Files:**
- Modify: `queen-editor/app.ipynb` (NotebookEdit)
- Modify: `queen-editor/README.md`

**Interfaces:**
- Consumes: `config.COMFY_URL`'ün `QE_COMFY_URL` ile ezilebilmesi (Task 4) · `python -m backend.main` (Task 9)
- Produces: Colab'da (T4) ayakta ComfyUI + doğru adresi bilen Flask.

Kaynak: `collab-toolbox/photo_generator/nova-3dcg/api.ipynb`. Hücreler Read ile okunup NotebookEdit ile yapıştırılır; **kod birebir**, markdown queen-editor bağlamına uyarlanır.

- [ ] **Step 1: Başlık markdown'ını (ilk hücre) güncelle**

```markdown
# Queen Editor — Tek foto (Bölüm 4)

Drive'ı bağlar → repoyu klonlar → **ComfyUI'yi kurar** (8 custom node + ~7.5 GiB model) → **Flask**
arayüzü servis eder → **cloudflared** linki basar. Projeye girip prompt yazınca ComfyUI bir foto
üretir, `MyDrive/queenEditor/<proje>/0_a.png` olarak Drive'a düşer ve ekranda görünür.

> **Runtime → Change runtime type → T4 GPU** gerekiyor (SDXL). CPU runtime'da kurulum hücresi durur.

## Kullanım
1. Bu `app.ipynb`'yi Colab'a yükle (**File → Upload notebook**).
2. **🔑 Secrets** panelinde iki secret olmalı: `GITHUB_TOKEN` (fine-grained, yalnız bu repo,
   `Contents: read`) ve `CIVITAI_COOKIE` (civitai.red → giriş yap → F12 → Application → Cookies →
   `__Secure-civ-token` değeri; ~30 günde bir yenilenir).
3. **Runtime → Run all** → Drive izni ver → ilk kurulum ~10-15 dk → en alttaki linke gir.
```

- [ ] **Step 2: CONFIG hücresine ComfyUI ayarlarını, cookie'yi ve GPU kapısını ekle**

`DRIVE_FOLDER` satırının altına:

```python
# === ComfyUI (kurulum + üretim; backend QE_COMFY_URL ile bu adrese konuşur) ===
COMFY_PORT  = 8188
COMFY_ROOT  = "/content/ComfyUI"
COMFY_LOG   = "/content/comfyui.log"
COMFYUI_URL = f"http://127.0.0.1:{COMFY_PORT}"

# Civitai's gated models need the session cookie. Like GITHUB_TOKEN it comes from Colab Secrets --
# this notebook is committed, so a pasted session JWT would land in git.
try:
    COOKIE_VALUE = userdata.get("CIVITAI_COOKIE")
except Exception:
    COOKIE_VALUE = ""
```

`print` satırlarının üstüne (assert'lerin yanına):

```python
assert len(COOKIE_VALUE or "") > 200, (
    "❌ CIVITAI_COOKIE yok/çok kısa — Colab 🔑 Secrets'a 'CIVITAI_COOKIE' adıyla ekle: "
    "civitai.red → giriş → F12 → Application → Cookies → __Secure-civ-token değeri (ES256 JWT)"
)

# SDXL needs a GPU; on a CPU runtime the model download would finish and ComfyUI would then fail.
import subprocess as _sp
_gpu = _sp.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
               capture_output=True, text=True)
assert _gpu.returncode == 0 and _gpu.stdout.strip(), (
    "❌ GPU yok — Runtime → Change runtime type → T4 GPU seç ve Run all'ı yeniden çalıştır"
)
print(f"✓ GPU: {_gpu.stdout.strip()}")
```

- [ ] **Step 3: Klon hücresinin doğrulamasına grafiği ekle**

`DIST` assert'inin altına:

```python
# The graph ships with the repo too (our own copy) -- a forgotten commit shows up here.
WORKFLOW = os.path.join(CLONE_DIR, "queen-editor", "workflow_api.json")
assert os.path.exists(WORKFLOW), f"❌ Grafik yok: {WORKFLOW} — workflow_api.json commit'lenmiş mi?"
```

- [ ] **Step 4: Yardımcılar hücresini ekle** (klon hücresinden sonra)

`nova-3dcg/api.ipynb`'nin `cell-5`'i (`# === Shared helpers — log + fail-loud run + model validation ===`) **birebir**, iki değişiklikle:
- `describe_comfy_error` fonksiyonu **çıkarılır** (backend'de `services/comfy/errors.py` olarak yaşıyor).
- son `print` satırı: `print("✓ Ortak yardımcılar hazır (log, run, human, head_text, check_safetensors)")`

(`assert "COMFY_ROOT" in globals()` kapısı kalır — CONFIG çalışmadan kurulum başlamasın.)

- [ ] **Step 5: Custom node hücrelerini ekle**

`api.ipynb`'nin `cell-6` (markdown) ve `cell-7` (kod) hücreleri. Kod **birebir** (8 paketlik `CUSTOM_NODES`, `--recurse-submodules`, boş klasör kontrolü). Markdown şu metinle yazılır:

```markdown
## ComfyUI + Custom Node'lar (8)

Grafiğin ihtiyacı olan 7 paket + Manager. Liste grafiğin node künyelerinden çıkarıldı; kalan node'lar
comfy-core, kurulum istemez. Biri başarısız olursa hücre `RuntimeError` ile durur (fail-loud).
```

- [ ] **Step 6: Model hücrelerini ekle**

`api.ipynb`'nin `cell-8` (markdown) ve `cell-9` (kod) hücreleri. Kod **birebir** (`check_binary`, `fetch`, `civitai_url`/`cookie_header`/`civitai_probe`, 2 Civitai + 3 açık model, probe → indir → özet; `COMFY = COMFY_ROOT` satırı dahil). Markdown:

```markdown
## Modeller — önce gated probe, sonra indir (~7.5 GiB)

Gated erişim **ağır indirmeden önce** doğrulanır (ilk 1 KB): cookie ölmüşse 6.5 GiB'lık checkpoint'e
başlamadan, Civitai'nin **gerçek yanıtıyla** durur. Bozuk/eksik dosyada hücre durur; bozuk dosya
silinmez, inceleme için diskte kalır. Dosyalar grafiğin beklediği adlarla iner.
```

- [ ] **Step 7: ComfyUI başlatma hücrelerini ekle**

`api.ipynb`'nin `cell-10` (markdown) ve `cell-11` (kod) hücreleri. Kod **birebir** (pkill, `Popen`, 90 sn `/system_stats` bekleme, log kuyruğu). Markdown:

```markdown
## ComfyUI'yi başlat (arka planda)

ComfyUI subprocess olarak kalkar; arayüzün backend'i `QE_COMFY_URL` ile bu adrese konuşur. **90 sn
içinde hazır olmazsa** hücre log'un son 30 satırını basıp durur — sonraki hücre ölü sunucuya
çalışmasın. Tünel yok: ComfyUI'ın kendi arayüzü açılmıyor.
```

- [ ] **Step 8: Serve hücresine ComfyUI adresini geçir**

`flask_env` satırını değiştir:

```python
flask_env = {**os.environ, "QE_DRIVE_ROOT": DRIVE_ROOT, "QE_COMFY_URL": COMFYUI_URL}
```

Link mesajını da güncelle:

```python
print("⬆️  Linke gir → projeye tıkla → prompt yaz → Üret.\n")
```

- [ ] **Step 9: `README.md`'yi güncelle**

`So far:` paragrafını değiştir:

```markdown
So far: **Part 1** proved the private repo clones on Colab; **Part 2** serves the pre-built frontend
with Flask and opens a tunnel; **Part 3** adds the projects screen; **Part 4** brings ComfyUI up and
generates one photo per prompt into the project folder. Needs a **T4 GPU** runtime and a
`CIVITAI_COOKIE` secret from Part 4 on.
```

`### 3. Run` bölümünün ilk cümlesine kurulum süresini ekle:

```markdown
**Runtime → Change runtime type → T4 GPU**, then **Runtime → Run all.** The notebook mounts Drive
(**grant access in the popup**), clones the repo, installs ComfyUI and downloads ~7.5 GiB of models
(~10-15 min on the first run of a session), starts Flask and prints a cloudflared link.
```

- [ ] **Step 10: Notebook'un yapısını doğrula**

Read ile `queen-editor/app.ipynb` açılır. Hücre sırası: **başlık md → CONFIG → mount → klon →
yardımcılar → custom node md+kod → model md+kod → ComfyUI md+kod → serve**. `describe_comfy_error`
notebook'ta **geçmemeli** (Grep ile kontrol: 0 sonuç).

---

### Task 13: Colab doğrulaması + commit (kullanıcı kapısı)

**Files:** (yok — doğrulama + commit)

- [ ] **Step 1: Yerel tam tur**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (90 test).
Run: `cd queen-editor/frontend && npm run build`
Expected: hata yok, `dist/` güncel.

- [ ] **Step 2: Commit + push (kullanıcı onayıyla, doğrulamadan önce)**

Notebook repodan klonluyor; push edilmeyen kod Colab'da yok. Pathspec ile iki commit:

```bash
# docs
git add -- docs/superpowers/specs/2026-07-25-queen-editor-b4-tek-foto-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b4-tek-foto.md
git commit -m "docs(queen-editor): Bölüm 4 — tek foto spec + plan" -- \
  docs/superpowers/specs/2026-07-25-queen-editor-b4-tek-foto-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b4-tek-foto.md
# feat (backend + frontend kaynağı + derlenmiş dist + grafik + notebook/README)
git add -- queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist \
  queen-editor/workflow_api.json queen-editor/app.ipynb queen-editor/README.md
git commit -m "feat(queen-editor): Bölüm 4 — ComfyUI ile tek foto üretimi" -- \
  queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist \
  queen-editor/workflow_api.json queen-editor/app.ipynb queen-editor/README.md
git push origin feat/queen-editor-v1
```

- [ ] **Step 3: Kullanıcı Colab doğrulaması (T4)**

**Runtime → T4 GPU** → Run all. Beklenen:
1. `✓ GPU: Tesla T4, …` · Drive izni · klon · 8 custom node · gated probe OK · ~7.5 GiB model ·
   `✓ ComfyUI hazır (…s)` · Flask + link.
2. Linke gir → Projeler → **karta tıkla** → proje ekranı açılır, URL `/projects/<ad>`; yenile →
   aynı ekran.
3. Prompt yaz → **Üret** → "üretiliyor…" → ~1-2 dk → foto ekranda; Drive'da
   `queenEditor/<ad>/0_a.png`. Fotoya tıkla → yeni sekmede açılır.
4. Üretim sürerken sekmeyi kapat/aç → durum "üretiliyor" olarak sürer, bitince foto görünür.
5. İkinci **Üret** → `1_a.png` (üstüne yazma yok).
6. Boş prompt'ta Üret pasif; üretim sürerken buton pasif.
7. (Negatif) ComfyUI'yi öldür (`!pkill -f 'python main.py'`) → Üret → kırmızı **Üretim başarısız** +
   sunucunun ham hata metni.
8. **← Projeler** → liste geri gelir.

---

## Doğrulama özeti

| Ne | Nasıl |
|---|---|
| Hata sınıflandırma | `pytest backend/tests/test_comfy_errors.py` → 5 |
| ComfyUI taşıma | `pytest backend/tests/test_comfy_client.py` → 8 |
| Drive dosya I/O | `pytest backend/tests/test_drive_storage.py` → 10 (5 eski + 5 yeni) |
| Grafik kopyası sağlam | `pytest backend/tests/test_workflow_asset.py` → 1 |
| Arka plan işçisi | `pytest backend/tests/test_photo_runner.py` → 5 |
| Use case'ler | `pytest backend/tests/test_photo_usecases.py` → 7 |
| Grafik enjeksiyonu | `pytest backend/tests/test_comfy_photo_generator.py` → 4 |
| Numaralandırma + kayıt | `pytest backend/tests/test_photo_store.py` → 5 |
| Uçlar | `pytest backend/tests/test_photo_routes.py` → 8 |
| Bölüm 1-3 bozulmadı | `python -m pytest -q` → 90 test |
| Sunucu ayağa kalkıyor | `python -c "from backend.main import app; …"` → route listesi |
| Arayüz derleniyor | `cd frontend && npm run build` |
| Uçtan uca | Colab (T4) Run all → prompt → foto ekranda + Drive'da |
| Bölüm 4 kapanır | Kullanıcı doğrular → docs + feat commit'leri + push |
