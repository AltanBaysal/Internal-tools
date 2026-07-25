# Queen Editor — Bölüm 5: Çoklu foto · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prompt listesi + negatif + varyant yapıştır → **Üret** → her prompt × varyant sırayla üretilir, galeri (solda, 5 sütun) üretim sürerken dolar, **Durdur** çalışır.

**Architecture:** Batch döngüsü `usecases/start_batch.py`'nin kurduğu closure'da; `runner.py` yalnız thread + durum + durdurma bayrağı taşır (`report`/`request_stop` eklenir, işten **özet dict** alır). Hata kuralı saf `domain/policy.py`'de (atla / üst üste 3 / infra). Prompt listesi `domain/prompt_list.py`'de `ast.literal_eval` ile parse edilir. `services/*` ve `features/projects` **hiç değişmez**.

**Tech Stack:** Python 3 · Flask · pytest · React 18 · Vite 5 · Google Colab (T4 + Drive) · ComfyUI

**Spec:** [2026-07-25-queen-editor-b5-coklu-foto-design.md](../specs/2026-07-25-queen-editor-b5-coklu-foto-design.md) · **Bölüm 4:** [2026-07-25-queen-editor-b4-tek-foto-design.md](../specs/2026-07-25-queen-editor-b4-tek-foto-design.md) · **Şemsiye:** [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md)

## Global Constraints

- **Dil ayrımı:** kod yorumu/docstring ve commit mesajı **İngilizce**; UI metni ve notebook çıktısı **Türkçe**.
- **Katman yasakları:** `feature ↛ feature`, `servis ↛ feature`, `servis ↛ servis`. `domain/` `flask`/`requests`/dosya yolu bilmez; `ComfyExecutionError` tipini de bilmez — infra bayrağı `getattr(exc, "infra", False)` ile okunur. Grafik bilgisi yalnız `data/comfy_photo_generator.py`, dosya adı şeması yalnız `data/photo_store.py`. Bağlama yalnız `main.py`.
- **`services/comfy`, `services/drive`, `features/projects`, `web/`, `config.py` DEĞİŞMEZ.** Bu bölümün kanıtı bu: yeni özellik komşusuz tek feature klasörüne iniyor.
- **`start_generation.py` silinir** — tek yol `start_batch` (tek foto = 1 prompt × 1 varyant). Testleri yeni yola taşınır, iki yol tutulmaz.
- **Prompt girişi yalnız Python listesi:** `["a", "b"]` ya da `PROMPTS = ["a", "b"]`. Köşeli parantezsiz düz metin **hata** (mesaj örnekle yol gösterir) — spec kararı, tek prompt için de `["..."]` yazılır.
- **Numaralama:** batch başında `start = next_number`; prompt `j` → numara `start+j`, varyant `v` → harf `LETTERS[v]`. Prompt-major sıra (`0_a 0_b … 1_a`). Patlayan kare numarasını boş bırakır.
- **Negatif tek ortak metin**, boş olabilir (negatifsiz üretim). Node **4**'e de çift alan yazılır (`wildcard_text` + `populated_text`).
- **Hata politikası:** kare hatası → atla; **üst üste 3** ya da **infra** → batch `error` ile durur, ham hata metni durumda. Kırmızı kare kartı/devam **yok** (B7).
- **Durdurma nazik:** bayrak kareler *arasında* okunur; süren render biter. ComfyUI `/interrupt` kullanılmaz.
- **Vendor değişmez.** Kit'in `Segment`'i tıklanamaz (wireframe, `onClick` yok) — varyant seçici kendi bileşenimiz, yalnız `wf-segment`/`is-on` sınıflarını kullanır.
- **Test komutu:** `queen-editor/` içinden `python -m pytest -q`. ComfyUI/Drive/GPU/ağ isteyen test yok. Bölüm 1-4'ten kalan 90 testin **yalnız** tek-foto yoluna bağlı olanları taşınır (`test_photo_runner`, `test_photo_usecases`, `test_photo_routes`, `test_comfy_photo_generator`, `test_workflow_asset`); diğerleri bozulmaz.
- **Frontend derleme:** `queen-editor/frontend/` içinde `npm run build`, `dist/` commit'lenir.
- **Commit politikası:** Colab kodu repodan klonluyor → son task'ta önce commit+push (kullanıcı onayıyla), sonra doğrulama.

## Dosya yapısı

| Dosya | Sorumluluk |
|---|---|
| `domain/prompt_list.py` **(yeni)** | Yapıştırılan metin → `list[str]`. Tek iş: parse + doğrula. |
| `domain/policy.py` **(yeni)** | "Devam mı, dur mu?" — tek karar fonksiyonu, saf. |
| `domain/usecases/start_batch.py` **(yeni)** | Doğrula → kareleri planla → closure'ı runner'a ver. `start_generation.py`'nin yerini alır. |
| `domain/usecases/stop_generation.py` **(yeni)** | Bayrağı kaldır, güncel durumu dön. |
| `domain/usecases/list_photos.py` **(yeni)** | Galeri listesi; proje yoksa `ProjectMissing`. |
| `domain/ports.py` (değişir) | `PhotoGenerator.generate(prompt, negative, seed)`; `PhotoStore.list_photos`. |
| `runner.py` (değişir) | + `report(patch)`, `request_stop()`, `stop_requested()`; iş **özet dict** döner. |
| `data/comfy_photo_generator.py` (değişir) | + `NEGATIVE_NODE "4"`, negatif enjeksiyonu. |
| `data/photo_store.py` (değişir) | + `list_photos` (numara azalan, harf artan). |
| `presentation/routes.py` (değişir) | `generate` gövdesi · `POST /api/stop` · `GET …/photos`. |
| `main.py` (değişir) | Yeni use case'lerin bağlanması. |
| `frontend/.../Gallery.jsx` · `VariantPicker.jsx` · `ProgressPanel.jsx` **(yeni)** | Galeri · varyant seçici · üretim durumu. |
| `frontend/.../GeneratePanel.jsx` · `ProjectScreen.jsx` · `useGeneration.js` (değişir) | Form · yerleşim (solda galeri) · yoklama + foto tazeleme. |

Silinen: `domain/usecases/start_generation.py`.

---

### Task 1: `domain/prompt_list.py` — yapıştırılan listeyi oku

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/prompt_list.py`
- Test: `queen-editor/backend/tests/test_prompt_list.py`

**Interfaces:**
- Consumes: (yok)
- Produces: `parse_prompts(text) -> list[str]` · `InvalidPrompts(Exception)` (mesajı Türkçe, doğrudan kullanıcıya gider).

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_prompt_list.py`

```python
import pytest

from backend.features.photo_generation.domain.prompt_list import InvalidPrompts, parse_prompts


def test_parses_a_python_list():
    assert parse_prompts('["kraliçe tahtta", "kraliçe bahçede"]') == ["kraliçe tahtta", "kraliçe bahçede"]


def test_strips_a_leading_assignment():
    # The list is pasted straight out of a notebook cell.
    assert parse_prompts('PROMPTS = ["a", "b"]') == ["a", "b"]


def test_multiline_items_survive_and_are_stripped():
    assert parse_prompts('["""\n  kraliçe\n"""]') == ["kraliçe"]


def test_empty_items_are_dropped():
    # nova-3dcg's contract: an empty item is a deliberate "skip this line" switch.
    assert parse_prompts('["a", "", "  ", "b"]') == ["a", "b"]


def test_empty_text_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts("   ")
    assert str(exc.value) == "Prompt listesi boş."


def test_unreadable_text_reports_pythons_own_error():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["a", ')
    assert "Python listesi bekleniyor" in str(exc.value)
    assert "[\"ilk prompt\"" in str(exc.value)      # shows an example


def test_bare_string_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('"tek prompt"')
    assert "köşeli parantez" in str(exc.value)


def test_non_list_is_rejected_with_its_type():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts("42")
    assert "int" in str(exc.value)


def test_non_string_item_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["a", 3]')
    assert "metin" in str(exc.value)


def test_list_of_only_empty_items_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["", "   "]')
    assert str(exc.value) == "Listede dolu prompt yok."
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_prompt_list.py -q`
Expected: FAIL — `ModuleNotFoundError: ...domain.prompt_list`.

- [ ] **Step 3: `domain/prompt_list.py` yaz**

```python
"""The pasted prompt list -> list[str]. Pure, and it never executes what it reads.

The text comes straight out of a notebook cell, so a leading `PROMPTS =` is stripped before
parsing and `ast.literal_eval` does the rest: it accepts literals only -- no calls, no names,
nothing executable -- so a paste can be wrong but never dangerous.
"""
import ast
import re

_ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*\s*=\s*")
_EXAMPLE = '["ilk prompt", "ikinci prompt"]'


class InvalidPrompts(Exception):
    """The pasted text is not a usable prompt list (message is user-facing)."""


def parse_prompts(text):
    if not text or not text.strip():
        raise InvalidPrompts("Prompt listesi boş.")

    body = _ASSIGNMENT.sub("", text.strip(), count=1)
    try:
        value = ast.literal_eval(body)
    except (ValueError, SyntaxError, MemoryError, RecursionError) as exc:
        # Python's own message, not a guess about what the user meant.
        raise InvalidPrompts(f"Prompt listesi okunamadı — Python listesi bekleniyor, örnek: "
                             f"{_EXAMPLE}. Python hatası: {exc}") from None

    if isinstance(value, str):
        raise InvalidPrompts(f"Tek metin geldi — köşeli parantezli liste bekleniyor: {_EXAMPLE}")
    if not isinstance(value, (list, tuple)):
        raise InvalidPrompts(f"Liste bekleniyordu, {type(value).__name__} geldi. Örnek: {_EXAMPLE}")
    if not all(isinstance(item, str) for item in value):
        raise InvalidPrompts(f"Listenin her öğesi metin olmalı. Örnek: {_EXAMPLE}")

    prompts = [item.strip() for item in value if item.strip()]
    if not prompts:
        raise InvalidPrompts("Listede dolu prompt yok.")
    return prompts
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (90 + 10 = 100).

---

### Task 2: `domain/policy.py` — devam mı, dur mu

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/policy.py`
- Test: `queen-editor/backend/tests/test_policy.py`

**Interfaces:**
- Consumes: (yok)
- Produces: `MAX_CONSECUTIVE = 3` · `stop_reason(consecutive, infra) -> str | None` (metin Türkçe, kullanıcıya gider).

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_policy.py`

```python
from backend.features.photo_generation.domain import policy


def test_a_single_failure_keeps_the_batch_going():
    assert policy.stop_reason(1, infra=False) is None
    assert policy.stop_reason(2, infra=False) is None


def test_three_consecutive_failures_stop_the_batch():
    reason = policy.stop_reason(policy.MAX_CONSECUTIVE, infra=False)
    assert reason is not None and "3" in reason


def test_infra_failure_stops_on_the_first_one():
    reason = policy.stop_reason(1, infra=True)
    assert reason is not None and "Altyapı" in reason


def test_reasons_say_the_batch_stopped():
    # The text lands in the status line, so it must read as a sentence to the user.
    assert "durduruldu" in policy.stop_reason(1, infra=True)
    assert "durduruldu" in policy.stop_reason(3, infra=False)
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_policy.py -q`
Expected: FAIL — `ImportError: cannot import name 'policy'`.

- [ ] **Step 3: `domain/policy.py` yaz**

```python
"""When does a batch stop? One pure decision, so changing the rule touches one file.

Inherited from api.ipynb: a model loader failure means every remaining render would hit the
identical error, so it stops immediately; a render-specific failure only costs that frame, and a
run that keeps failing is broken rather than unlucky.
"""

MAX_CONSECUTIVE = 3


def stop_reason(consecutive, infra):
    """(consecutive failures, infra flag) -> user-facing reason, or None to keep going."""
    if infra:
        return "Altyapı hatası (model yükleyici) — üretim durduruldu"
    if consecutive >= MAX_CONSECUTIVE:
        return f"Üst üste {MAX_CONSECUTIVE} render başarısız — üretim durduruldu"
    return None
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (100 + 4 = 104).

---

### Task 3: `runner.py` — ilerleme bildirimi + nazik durdurma

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/runner.py`
- Test: `queen-editor/backend/tests/test_photo_runner.py` (**tamamı yeniden yazılır** — iş artık özet dict dönüyor)

**Interfaces:**
- Consumes: (yok)
- Produces: `PhotoRunner(spawn=None)` — `start(project, job) -> bool` (`job()` özet dict döner) · `status() -> dict` · `report(patch)` · `request_stop()` · `stop_requested() -> bool`.

- [ ] **Step 1: `test_photo_runner.py`'ı yeni sözleşmeyle baştan yaz** (dosyanın tamamını değiştir)

```python
from backend.features.photo_generation.runner import PhotoRunner


def sync_runner():
    """spawn=lambda fn: fn() runs the job inline -- the test needs no thread and no sleep."""
    return PhotoRunner(spawn=lambda fn: fn())


def test_starts_idle():
    assert PhotoRunner().status() == {"status": "idle"}


def test_the_jobs_summary_becomes_the_state():
    runner = sync_runner()
    assert runner.start("düğün", lambda: {"status": "done", "done": 6, "failed": 0, "total": 6}) is True
    assert runner.status() == {"status": "done", "project": "düğün",
                               "done": 6, "failed": 0, "total": 6}


def test_report_updates_progress_while_the_job_runs():
    runner = sync_runner()
    seen = []

    def job():
        runner.report({"done": 0, "total": 2, "current": {"number": 3, "letter": "a"}})
        seen.append(runner.status())
        return {"status": "done", "done": 2, "failed": 0, "total": 2}

    runner.start("düğün", job)
    assert seen[0] == {"status": "running", "project": "düğün", "done": 0, "total": 2,
                       "current": {"number": 3, "letter": "a"}}


def test_report_after_the_job_ended_is_ignored():
    # A late report from a dead thread must not resurrect "running".
    runner = sync_runner()
    runner.start("düğün", lambda: {"status": "done", "done": 1, "failed": 0, "total": 1})
    runner.report({"done": 99})
    assert runner.status()["status"] == "done" and runner.status()["done"] == 1


def test_unexpected_exception_becomes_error_with_the_real_message():
    runner = sync_runner()

    def boom():
        raise RuntimeError("ComfyUI öldü")

    runner.start("düğün", boom)
    state = runner.status()
    assert state["status"] == "error" and state["error"] == "ComfyUI öldü"


def test_second_start_is_refused_while_running():
    runner = PhotoRunner(spawn=lambda fn: None)   # never runs -> stays "running"
    assert runner.start("düğün", lambda: {"status": "done"}) is True
    assert runner.status()["status"] == "running"
    assert runner.start("düğün", lambda: {"status": "done"}) is False


def test_a_finished_job_does_not_block_the_next_one():
    runner = sync_runner()
    runner.start("düğün", lambda: {"status": "done", "done": 1, "failed": 0, "total": 1})
    assert runner.start("düğün", lambda: {"status": "done", "done": 2, "failed": 0, "total": 2}) is True
    assert runner.status()["done"] == 2


def test_the_job_sees_the_stop_request():
    runner = sync_runner()
    runner.request_stop()
    seen = []

    def job():
        seen.append(runner.stop_requested())
        return {"status": "stopped"}

    runner.start("düğün", job)
    assert seen == [False], "start must clear a stale stop flag"


def test_stop_requested_during_the_job_is_visible():
    runner = sync_runner()
    seen = []

    def job():
        runner.request_stop()
        seen.append(runner.stop_requested())
        return {"status": "stopped"}

    runner.start("düğün", job)
    assert seen == [True]
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_runner.py -q`
Expected: FAIL — `AttributeError: 'PhotoRunner' object has no attribute 'report'` (ve özet testleri).

- [ ] **Step 3: `runner.py`'ı güncelle** (dosyanın tamamı)

```python
"""One photo job at a time, in the background -- this feature's own worker.

Deliberately NOT a shared service: video generation will copy this file rather than depend on it,
so a change here can never break another pipeline (the maintenance rule for this project).

The worker knows nothing about photos, frames or policy: it starts one job, holds whatever progress
the job reports, and carries the stop flag the job reads between frames. `spawn` is injected:
production starts a daemon thread, tests run the job inline and stay deterministic.
"""
import threading


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class PhotoRunner:
    def __init__(self, spawn=None):
        self._spawn = spawn or _thread_spawn
        self._lock = threading.Lock()
        self._state = {"status": "idle"}
        self._stop = False

    def status(self):
        with self._lock:
            return dict(self._state)

    def start(self, project, job):
        """Claim the worker and run `job` in the background. False means one is already running.

        `job()` returns the summary dict it wants published ({"status": "done"|"stopped"|"error",
        ...}); the runner stamps the project onto it.
        """
        with self._lock:
            if self._state["status"] == "running":
                return False
            self._state = {"status": "running", "project": project}
            self._stop = False      # a stale request must not kill the run that just started
        self._spawn(lambda: self._run(project, job))
        return True

    def report(self, patch):
        """Progress from the running job. Ignored unless a job is running, so a late report from a
        thread that already finished cannot resurrect "running"."""
        with self._lock:
            if self._state.get("status") == "running":
                self._state = {**self._state, **patch}

    def request_stop(self):
        with self._lock:
            self._stop = True

    def stop_requested(self):
        with self._lock:
            return self._stop

    def _run(self, project, job):
        try:
            summary = job()
        except Exception as exc:   # the message is user-facing: whatever really failed, verbatim
            self._set({"status": "error", "project": project, "error": str(exc)})
            return
        self._set({**summary, "project": project})

    def _set(self, state):
        with self._lock:
            self._state = state
```

- [ ] **Step 4: Testi çalıştır** — `test_photo_runner` geçer, `test_photo_usecases`/`test_photo_routes` **kırılır** (beklenen: eski `start_generation` işi dict dönmüyor; Task 6-7 onları taşıyor)

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_runner.py -q`
Expected: PASS (9 test — dosya 5'ten 9'a çıktı, toplam 104 + 4 = 108).

---

### Task 4: `data/photo_store.py` — galeri listesi

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/photo_store.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Test: `queen-editor/backend/tests/test_photo_store.py` (mevcut dosyaya ekleme)

**Interfaces:**
- Consumes: `DriveStorage.list_files` (Bölüm 4)
- Produces: `DrivePhotoStore.list_photos(project) -> list[str]` — numara azalan, aynı numarada harf artan.

- [ ] **Step 1: Failing testleri mevcut dosyanın sonuna ekle**

```python
def test_list_photos_newest_number_first(tmp_path):
    project = tmp_path / "düğün"
    project.mkdir()
    for name in ("0_a.png", "10_a.png", "2_a.png"):
        (project / name).write_bytes(b"x")
    assert store_at(tmp_path).list_photos("düğün") == ["10_a.png", "2_a.png", "0_a.png"]


def test_list_photos_letters_ascend_within_a_number(tmp_path):
    project = tmp_path / "düğün"
    project.mkdir()
    for name in ("3_c.png", "3_a.png", "3_b.png"):
        (project / name).write_bytes(b"x")
    assert store_at(tmp_path).list_photos("düğün") == ["3_a.png", "3_b.png", "3_c.png"]


def test_list_photos_ignores_files_outside_the_scheme(tmp_path):
    project = tmp_path / "düğün"
    project.mkdir()
    for name in ("0_a.png", "notlar.txt", "prompts.json", "_bozuk.png"):
        (project / name).write_bytes(b"x")
    assert store_at(tmp_path).list_photos("düğün") == ["0_a.png"]


def test_list_photos_is_empty_for_a_project_without_photos(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).list_photos("düğün") == []
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_store.py -q`
Expected: FAIL — `AttributeError: 'DrivePhotoStore' object has no attribute 'list_photos'`.

- [ ] **Step 3: `photo_store.py`'ye `list_photos` ekle** (`next_number`'ın altına)

```python
    def list_photos(self, project):
        """Photo file names, newest number first, letters ascending inside a number.

        Sorted here rather than in the UI: the order is part of what the file names mean, and this
        is the only place that understands them.
        """
        numbered = [(number, name)
                    for number, name in ((_number_of(name), name)
                                         for name in self._storage.list_files(project))
                    if number is not None]
        numbered.sort(key=lambda item: (-item[0], item[1]))
        return [name for _number, name in numbered]
```

- [ ] **Step 4: `ports.py`'nin `PhotoStore`'una imzayı ekle** (`photo_dir`'in üstüne)

```python
    def list_photos(self, project: str) -> list:
        """Photo file names for the gallery, newest first."""
        ...
```

- [ ] **Step 5: Testi çalıştır, geçsin**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_store.py -q`
Expected: PASS (9 test: 5 eski + 4 yeni).

---

### Task 5: `data/comfy_photo_generator.py` — negatif node 4

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Test: `queen-editor/backend/tests/test_comfy_photo_generator.py` (**tamamı yeniden yazılır** — imza değişti)
- Test: `queen-editor/backend/tests/test_workflow_asset.py` (node 4 doğrulaması eklenir)

**Interfaces:**
- Consumes: `ComfyClient` (Bölüm 4)
- Produces: `ComfyPhotoGenerator(client, workflow_path, timeout).generate(prompt, negative, seed) -> bytes`; `PROMPT_NODE "3"` · `NEGATIVE_NODE "4"` · `SEED_NODE "40"`.

- [ ] **Step 1: `test_comfy_photo_generator.py`'ı baştan yaz** (dosyanın tamamı)

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
        "4": {"inputs": {"wildcard_text": "eski negatif", "populated_text": "eski negatif"},
              "class_type": "ImpactWildcardProcessor"},
        "40": {"inputs": {"seed": -1}, "class_type": "Seed (rgthree)"},
    }), encoding="utf-8")
    return str(path)


def generator_at(tmp_path, graph=None):
    client = FakeClient()
    return client, ComfyPhotoGenerator(client, write_graph(tmp_path, graph), timeout=60)


def test_generate_patches_prompt_negative_and_seed(tmp_path):
    client, generator = generator_at(tmp_path)

    assert generator.generate("kraliçe tahtta", "blurry", 12345) == b"PNG"

    node3 = client.submitted["3"]["inputs"]
    node4 = client.submitted["4"]["inputs"]
    assert node3["wildcard_text"] == "kraliçe tahtta"       # Impact Pack #483: both fields
    assert node3["populated_text"] == "kraliçe tahtta"
    assert node4["wildcard_text"] == "blurry"
    assert node4["populated_text"] == "blurry"
    assert client.submitted["40"]["inputs"]["seed"] == 12345   # never the export's -1
    assert client.waited == ("p1", 60)


def test_empty_negative_clears_the_exports_own_text(tmp_path):
    # "no negative" must mean no negative, not "whatever the export shipped".
    client, generator = generator_at(tmp_path)
    generator.generate("kraliçe", "", 1)
    assert client.submitted["4"]["inputs"]["populated_text"] == ""


def test_generate_does_not_mutate_the_file_on_disk(tmp_path):
    client = FakeClient()
    path = write_graph(tmp_path)
    ComfyPhotoGenerator(client, path, timeout=60).generate("yeni", "yeni negatif", 1)
    with open(path, encoding="utf-8") as f:
        graph = json.load(f)
    assert graph["3"]["inputs"]["wildcard_text"] == "eski"
    assert graph["4"]["inputs"]["wildcard_text"] == "eski negatif"


def test_ui_format_export_is_rejected(tmp_path):
    _client, generator = generator_at(tmp_path, {"nodes": [], "links": []})
    with pytest.raises(RuntimeError) as exc:
        generator.generate("x", "", 1)
    assert "Export (API)" in str(exc.value)


@pytest.mark.parametrize("missing", ["3", "4", "40"])
def test_missing_node_is_reported(tmp_path, missing):
    graph = {
        "3": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "4": {"inputs": {"wildcard_text": "", "populated_text": ""}},
        "40": {"inputs": {"seed": -1}},
    }
    del graph[missing]
    _client, generator = generator_at(tmp_path, graph)
    with pytest.raises(RuntimeError) as exc:
        generator.generate("x", "", 1)
    assert missing in str(exc.value)
```

- [ ] **Step 2: `test_workflow_asset.py`'a node 4 doğrulamasını ekle** (mevcut testin sonuna)

```python
    assert workflow["4"]["class_type"] == "ImpactWildcardProcessor"
    assert {"wildcard_text", "populated_text"} <= set(workflow["4"]["inputs"])
```

- [ ] **Step 3: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_comfy_photo_generator.py -q`
Expected: FAIL — `TypeError: generate() takes 3 positional arguments but 4 were given`.

- [ ] **Step 4: `comfy_photo_generator.py`'ı güncelle** (dosyanın tamamı)

```python
"""PhotoGenerator over ComfyUI -- the only place that knows what the graph looks like.

Node ids come from our own export (queen-editor/workflow_api.json):
  "3"  ImpactWildcardProcessor, _meta.title "POSITIVE"
  "4"  ImpactWildcardProcessor, _meta.title "NEGATIVE"
  "40" Seed (rgthree) -> KSampler, FaceDetailer and both wildcard processors read it

A new export can renumber these; then this file changes and nothing else does.
"""
import json

PROMPT_NODE = "3"
NEGATIVE_NODE = "4"
SEED_NODE = "40"


class ComfyPhotoGenerator:
    def __init__(self, client, workflow_path, timeout):
        self._client = client
        self._workflow_path = workflow_path
        self._timeout = timeout

    def generate(self, prompt, negative, seed):
        workflow = self._load()
        self._set_text(workflow, PROMPT_NODE, prompt)
        # An empty negative is written through as empty: leaving the export's own text in place
        # would mean "no negative" silently kept a negative.
        self._set_text(workflow, NEGATIVE_NODE, negative or "")
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
        for node_id in (PROMPT_NODE, NEGATIVE_NODE, SEED_NODE):
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

- [ ] **Step 5: `ports.py`'de `PhotoGenerator` imzasını güncelle**

```python
class PhotoGenerator(Protocol):
    def generate(self, prompt: str, negative: str, seed: int) -> bytes:
        """Render one photo and return its bytes."""
        ...
```

- [ ] **Step 6: Testleri çalıştır**

Run: `cd queen-editor && python -m pytest backend/tests/test_comfy_photo_generator.py backend/tests/test_workflow_asset.py -q`
Expected: PASS (8 test: 4 + parametrize 3 + 1 asset). Asset testi fail ederse grafikte node 4 yok — grafiği yeniden export etmek gerekir (Bölüm 4'ün kopyasında var).

---

### Task 6: `usecases/start_batch.py` — batch döngüsü

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/stop_generation.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/list_photos.py`
- Delete: `queen-editor/backend/features/photo_generation/domain/usecases/start_generation.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py` (**tamamı yeniden yazılır**)

**Interfaces:**
- Consumes: `parse_prompts`/`InvalidPrompts` (Task 1) · `policy.stop_reason` (Task 2) · runner sözleşmesi (Task 3) · `PhotoStore`/`PhotoGenerator` portları (Task 4-5)
- Produces:
  - `start_batch(runner, store, generator, new_seed, project, text, negative, variants) -> None`; `InvalidVariants` / `ProjectMissing` / `Busy` (+ `InvalidPrompts` yukarıdan geçer)
  - `LETTERS` · `plan_frames(start, prompts, variants) -> list[(number, letter, prompt)]`
  - `stop_generation(runner) -> dict` · `list_photos(store, project) -> list[str]` (`ProjectMissing`)

- [ ] **Step 1: `test_photo_usecases.py`'ı baştan yaz** (dosyanın tamamı)

```python
import pytest

from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_photos import list_photos
from backend.features.photo_generation.domain.usecases.start_batch import (
    Busy,
    InvalidVariants,
    ProjectMissing,
    plan_frames,
    start_batch,
)
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.runner import PhotoRunner


class FakeStore:
    def __init__(self, projects=("düğün",), next_no=0, photos=()):
        self.projects = list(projects)
        self.next_no = next_no
        self.photos = list(photos)
        self.saved = []

    def project_exists(self, project):
        return project in self.projects

    def next_number(self, project):
        return self.next_no

    def save(self, project, number, letter, data):
        self.saved.append((number, letter, data))
        return f"{number}_{letter}.png"

    def list_photos(self, project):
        return list(self.photos)

    def photo_dir(self, project):
        return f"/fake/{project}"


class FakeGenerator:
    """Records what each frame asked for. Failure cases use their own purpose-built fakes."""

    def __init__(self):
        self.calls = []

    def generate(self, prompt, negative, seed):
        self.calls.append((prompt, negative, seed))
        return b"PNG"


class Infra(RuntimeError):
    infra = True


def sync_runner():
    return PhotoRunner(spawn=lambda fn: fn())


def run_batch(runner, store, generator, project="düğün", text='["a", "b"]', negative="neg",
              variants=2, seed=42):
    return start_batch(runner, store, generator, lambda: seed, project, text, negative, variants)


def test_plan_frames_is_prompt_major():
    assert plan_frames(3, ["ilk", "ikinci"], 2) == [
        (3, "a", "ilk"), (3, "b", "ilk"), (4, "a", "ikinci"), (4, "b", "ikinci")]


def test_numbering_continues_from_the_store():
    store, generator, runner = FakeStore(next_no=7), FakeGenerator(), sync_runner()
    run_batch(runner, store, generator, text='["a"]', variants=3)
    assert [(n, letter) for n, letter, _d in store.saved] == [(7, "a"), (7, "b"), (7, "c")]


def test_every_frame_gets_prompt_negative_and_a_fresh_seed():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seeds = iter([11, 22, 33, 44])
    start_batch(runner, store, generator, lambda: next(seeds), "düğün", '["a", "b"]', "neg", 2)
    assert generator.calls == [("a", "neg", 11), ("a", "neg", 22),
                               ("b", "neg", 33), ("b", "neg", 44)]


def test_finished_batch_reports_its_counts():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    run_batch(runner, store, generator)
    assert runner.status() == {"status": "done", "project": "düğün",
                               "done": 4, "failed": 0, "total": 4}


def test_progress_is_reported_before_each_frame():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seen = []
    original = generator.generate

    def spy(prompt, negative, seed):
        seen.append(runner.status())
        return original(prompt, negative, seed)

    generator.generate = spy
    run_batch(runner, store, generator, text='["a"]', variants=2)
    assert seen[0]["current"] == {"number": 0, "letter": "a", "prompt": "a"}
    assert (seen[0]["done"], seen[0]["total"]) == (0, 2)
    assert (seen[1]["done"], seen[1]["total"]) == (1, 2)


def test_a_failed_frame_is_skipped_and_the_batch_continues():
    class FailsFirstFrame:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("node 41: OOM")
            return b"PNG"

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, FailsFirstFrame(), text='["a"]', variants=2)
    state = runner.status()
    assert (state["status"], state["done"], state["failed"]) == ("done", 1, 1)
    assert [(n, letter) for n, letter, _d in store.saved] == [(0, "b")]


def test_three_consecutive_failures_stop_the_batch():
    class AlwaysBroken:
        def generate(self, prompt, negative, seed):
            raise RuntimeError("node 41: OOM")

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, AlwaysBroken(), text='["a", "b"]', variants=2)
    state = runner.status()
    assert state["status"] == "error"
    assert "Üst üste 3" in state["error"] and "OOM" in state["error"]
    assert (state["done"], state["failed"], state["total"]) == (0, 3, 4)


def test_infra_failure_stops_on_the_first_frame():
    class Broken:
        def generate(self, prompt, negative, seed):
            raise Infra("node 9 (CheckpointLoaderSimple): dosya yok")

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, Broken(), text='["a", "b"]', variants=2)
    state = runner.status()
    assert state["status"] == "error" and "Altyapı" in state["error"]
    assert (state["failed"], state["total"]) == (1, 4)


def test_stop_request_ends_the_batch_between_frames():
    store, runner = FakeStore(), sync_runner()

    class StopsAfterFirst:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed):
            self.calls += 1
            runner.request_stop()
            return b"PNG"

    generator = StopsAfterFirst()
    run_batch(runner, store, generator, text='["a", "b"]', variants=2)
    state = runner.status()
    assert (state["status"], state["done"], state["total"]) == ("stopped", 1, 4)
    assert generator.calls == 1


def test_bad_prompt_text_is_rejected_before_anything_runs():
    store, generator = FakeStore(), FakeGenerator()
    with pytest.raises(InvalidPrompts):
        run_batch(sync_runner(), store, generator, text="42")
    assert generator.calls == [] and store.saved == []


@pytest.mark.parametrize("variants", [0, 27, "3", None, True])
def test_invalid_variants_are_rejected(variants):
    with pytest.raises(InvalidVariants) as exc:
        run_batch(sync_runner(), FakeStore(), FakeGenerator(), variants=variants)
    assert "1-26" in str(exc.value)


def test_missing_project_is_rejected():
    with pytest.raises(ProjectMissing) as exc:
        run_batch(sync_runner(), FakeStore(), FakeGenerator(), project="yok")
    assert str(exc.value) == "Proje yok: yok"


def test_busy_runner_is_rejected():
    runner = PhotoRunner(spawn=lambda fn: None)   # stays "running"
    run_batch(runner, FakeStore(), FakeGenerator())
    with pytest.raises(Busy) as exc:
        run_batch(runner, FakeStore(), FakeGenerator())
    assert str(exc.value) == "Zaten bir üretim sürüyor."


def test_stop_generation_sets_the_flag_and_returns_the_state():
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("düğün", lambda: {"status": "done"})
    state = stop_generation(runner)
    assert state["status"] == "running" and runner.stop_requested() is True


def test_stop_generation_when_idle_is_a_no_op():
    assert stop_generation(PhotoRunner()) == {"status": "idle"}


def test_list_photos_passes_the_store_through():
    assert list_photos(FakeStore(photos=["1_a.png", "0_a.png"]), "düğün") == ["1_a.png", "0_a.png"]


def test_list_photos_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        list_photos(FakeStore(), "yok")


def test_get_status_passes_the_runner_state_through():
    assert get_status(PhotoRunner()) == {"status": "idle"}
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_usecases.py -q`
Expected: FAIL — `ModuleNotFoundError: ...usecases.start_batch`.

- [ ] **Step 3: `usecases/start_batch.py` yaz**

```python
"""Start a batch: validate, plan the frames, hand ONE job to the runner.

The loop lives here rather than in the runner: it is business behaviour (order, numbering, what a
failure costs), and here it is testable with a synchronous spawn -- no threads in a test.

Pure: the seed comes from an injected `new_seed`, and runner/store/generator are ports. The
exception messages are the user-facing Turkish text; presentation maps them to status codes and
forwards them untouched.
"""
from backend.features.photo_generation.domain import policy
from backend.features.photo_generation.domain.prompt_list import parse_prompts

LETTERS = "abcdefghijklmnopqrstuvwxyz"


class InvalidVariants(Exception):
    """Variant count outside 1..len(LETTERS) (message is user-facing)."""


class ProjectMissing(Exception):
    """No such project folder."""


class Busy(Exception):
    """A generation is already running."""


def plan_frames(start, prompts, variants):
    """[(number, letter, prompt)] in prompt-major order: 0_a 0_b … 1_a.

    Number = prompt, letter = variant -- nova-3dcg's meaning, kept so a photo's name still says
    which prompt produced it.
    """
    return [(start + index, LETTERS[variant], prompt)
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]


def start_batch(runner, store, generator, new_seed, project, text, negative, variants):
    prompts = parse_prompts(text)          # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= len(LETTERS):
        raise InvalidVariants(f"Varyant sayısı 1-{len(LETTERS)} arası bir tam sayı olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    frames = plan_frames(store.next_number(project), prompts, variants)
    total = len(frames)

    def job():
        done = failed = consecutive = 0
        for number, letter, prompt in frames:
            if runner.stop_requested():
                return {"status": "stopped", "done": done, "failed": failed, "total": total}
            runner.report({"done": done, "failed": failed, "total": total,
                           "current": {"number": number, "letter": letter, "prompt": prompt}})
            try:
                data = generator.generate(prompt, negative, new_seed())
            except Exception as exc:
                failed += 1
                consecutive += 1
                # getattr, not isinstance: domain must not import the ComfyUI service.
                reason = policy.stop_reason(consecutive, getattr(exc, "infra", False))
                if reason:
                    return {"status": "error", "error": f"{reason}\n{exc}",
                            "done": done, "failed": failed, "total": total}
                continue
            store.save(project, number, letter, data)
            done += 1
            consecutive = 0
        return {"status": "done", "done": done, "failed": failed, "total": total}

    if not runner.start(project, job):
        raise Busy("Zaten bir üretim sürüyor.")
```

- [ ] **Step 4: `usecases/stop_generation.py` yaz**

```python
"""Ask the running batch to stop after the frame it is on."""


def stop_generation(runner):
    """Raise the flag and return the current state (idle is a no-op)."""
    runner.request_stop()
    return runner.status()
```

- [ ] **Step 5: `usecases/list_photos.py` yaz**

```python
"""The gallery's list: what is on disk, newest first."""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_photos(store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return store.list_photos(project)
```

- [ ] **Step 6: `usecases/start_generation.py`'ı sil**

```bash
git rm queen-editor/backend/features/photo_generation/domain/usecases/start_generation.py
```

- [ ] **Step 7: Testi çalıştır**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_usecases.py -q`
Expected: PASS (22 test: 18 fonksiyon, varyant testi 5 parametreli). Dosya 7'den 22'ye çıktı → toplam 115 + 15 = 130. `test_photo_routes` hâlâ kırık (Task 7).

---

### Task 7: Route'lar + composition root

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`
- Modify: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_photo_routes.py` (**tamamı yeniden yazılır**)

**Interfaces:**
- Consumes: Task 6'nın use case'leri · `DrivePhotoStore` · `ComfyPhotoGenerator` · `create_app`
- Produces: `make_photo_generation_blueprint(start_batch, get_status, stop_generation, list_photos, photo_dir) -> Blueprint`; uçlar `POST /api/projects/<p>/generate` · `GET /api/status` · `POST /api/stop` · `GET /api/projects/<p>/photos` · `GET /photos/<p>/<file>`.

- [ ] **Step 1: `test_photo_routes.py`'ı baştan yaz** (dosyanın tamamı)

```python
from functools import partial

from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_photos import list_photos
from backend.features.photo_generation.domain.usecases.start_batch import start_batch
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


class FakeGenerator:
    def generate(self, prompt, negative, seed):
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
        start_batch=partial(start_batch, runner, store, generator or FakeGenerator(), lambda: 42),
        get_status=partial(get_status, runner),
        stop_generation=partial(stop_generation, runner),
        list_photos=partial(list_photos, store),
        photo_dir=store.photo_dir,
    )
    app = create_app(dist_dir=str(dist), blueprints=[blueprint])
    return app.test_client(), drive


def generate(client, project="düğün", **body):
    payload = {"prompts": '["kraliçe tahtta"]', "negative": "blurry", "variants": 1, **body}
    return client.post(f"/api/projects/{project}/generate", json=payload)


def test_generate_returns_202_and_writes_every_frame(tmp_path):
    client, drive = make_client(tmp_path)
    resp = generate(client, prompts='["a", "b"]', variants=2)
    assert resp.status_code == 202
    assert sorted(p.name for p in (drive / "düğün").iterdir()) == [
        "0_a.png", "0_b.png", "1_a.png", "1_b.png"]


def test_status_reports_the_counts(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=2)
    assert client.get("/api/status").get_json() == {
        "status": "done", "project": "düğün", "done": 4, "failed": 0, "total": 4}


def test_status_is_idle_before_anything_runs(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/status").get_json() == {"status": "idle"}


def test_unreadable_prompt_list_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = generate(client, prompts="tek prompt")
    assert resp.status_code == 400
    assert "liste" in resp.get_json()["error"].lower()


def test_bad_variants_return_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = generate(client, variants=0)
    assert resp.status_code == 400
    assert "Varyant" in resp.get_json()["error"]


def test_missing_variants_return_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate", json={"prompts": '["a"]'})
    assert resp.status_code == 400


def test_missing_negative_generates_without_one(tmp_path):
    client, drive = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate",
                       json={"prompts": '["a"]', "variants": 1})
    assert resp.status_code == 202
    assert (drive / "düğün" / "0_a.png").exists()


def test_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    resp = generate(client, project="yok")
    assert resp.status_code == 404
    assert "yok" in resp.get_json()["error"]


def test_busy_runner_returns_409(tmp_path):
    client, _ = make_client(tmp_path, runner=PhotoRunner(spawn=lambda fn: None))
    generate(client)
    resp = generate(client)
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Zaten bir üretim sürüyor."


def test_failed_batch_shows_the_real_error_in_status(tmp_path):
    class Broken:
        def generate(self, prompt, negative, seed):
            raise RuntimeError("node 9 (CheckpointLoaderSimple): dosya yok")

    client, _ = make_client(tmp_path, generator=Broken())
    generate(client, prompts='["a", "b", "c"]', variants=1)
    state = client.get("/api/status").get_json()
    assert state["status"] == "error" and "CheckpointLoaderSimple" in state["error"]


def test_stop_returns_the_current_status(tmp_path):
    client, _ = make_client(tmp_path, runner=PhotoRunner(spawn=lambda fn: None))
    generate(client)
    resp = client.post("/api/stop")
    assert resp.status_code == 200 and resp.get_json()["status"] == "running"


def test_photos_are_listed_newest_first(tmp_path):
    client, drive = make_client(tmp_path)
    for name in ("0_a.png", "2_a.png", "notlar.txt"):
        (drive / "düğün" / name).write_bytes(b"x")
    assert client.get("/api/projects/düğün/photos").get_json() == {
        "photos": ["2_a.png", "0_a.png"]}


def test_photos_of_an_unknown_project_return_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/photos").status_code == 404


def test_photo_is_served_from_the_project_folder(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "0_a.png").write_bytes(b"PNGDATA")
    assert client.get("/photos/düğün/0_a.png").data == b"PNGDATA"
    assert client.get("/photos/düğün/yok.png").status_code == 404
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && python -m pytest backend/tests/test_photo_routes.py -q`
Expected: FAIL — `TypeError: make_photo_generation_blueprint() got an unexpected keyword argument 'stop_generation'`.

- [ ] **Step 3: `presentation/routes.py`'ı güncelle** (dosyanın tamamı)

```python
"""/api/projects/<project>/generate · /api/status · /api/stop
/api/projects/<project>/photos · /photos/<project>/<file>

Translation only: no rules here. The use case's exception messages go out verbatim, so the wording
lives in exactly one place (the domain).
"""
from flask import Blueprint, jsonify, request, send_from_directory

from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.usecases.start_batch import (
    Busy,
    InvalidVariants,
    ProjectMissing,
)


def make_photo_generation_blueprint(start_batch, get_status, stop_generation, list_photos,
                                    photo_dir):
    """The callables are already bound to a runner/store/generator (see main.py)."""
    bp = Blueprint("photo_generation", __name__)

    @bp.post("/api/projects/<project>/generate")
    def post_generate(project):
        body = request.get_json(silent=True) or {}
        prompts = body.get("prompts")
        # A non-string body field is treated as empty text -> "Prompt listesi boş."
        prompts = prompts if isinstance(prompts, str) else ""
        negative = body.get("negative")
        # No negative is legitimate (the batch renders without one); a non-string counts as none.
        negative = negative if isinstance(negative, str) else ""
        try:
            start_batch(project, prompts, negative, body.get("variants"))
        except (InvalidPrompts, InvalidVariants) as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # 202: a batch runs for minutes, so the request only reports that the job was accepted.
        return jsonify({"job": "running"}), 202

    @bp.get("/api/status")
    def status():
        return jsonify(get_status())

    @bp.post("/api/stop")
    def stop():
        return jsonify(stop_generation())

    @bp.get("/api/projects/<project>/photos")
    def photos(project):
        try:
            return jsonify({"photos": list_photos(project)})
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.get("/photos/<project>/<filename>")
    def serve_photo(project, filename):
        # send_from_directory rejects paths that escape the folder.
        return send_from_directory(photo_dir(project), filename)

    return bp
```

- [ ] **Step 4: `main.py`'ı güncelle** — import'lar ve blueprint bağlaması

`start_generation` import'u `start_batch` + `stop_generation` + `list_photos` ile değişir:

```python
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_photos import list_photos
from backend.features.photo_generation.domain.usecases.start_batch import start_batch
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
```

ve blueprint kurulumu:

```python
_photo_bp = make_photo_generation_blueprint(
    start_batch=partial(start_batch, _photo_runner, _photo_store, _photo_generator,
                        lambda: random.randint(0, 2**31 - 1)),
    get_status=partial(get_status, _photo_runner),
    stop_generation=partial(stop_generation, _photo_runner),
    list_photos=partial(list_photos, _photo_store),
    photo_dir=_photo_store.photo_dir,
)
```

Dosyanın kalanı (storage, project store, comfy client, generator, runner, `create_app`) aynı.

- [ ] **Step 5: Bütün testleri çalıştır**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (136). Zincir: 90 (B4 sonu) → +10 parse → +4 policy → +4 runner → +4 store → +3 generator → +15 use case → +6 route.

- [ ] **Step 6: Sunucunun ayağa kalktığını doğrula**

Run: `cd queen-editor && python -c "from backend.main import app; print(sorted(r.rule for r in app.url_map.iter_rules()))"`
Expected: liste `/api/stop` ve `/api/projects/<project>/photos` kurallarını da içerir.

---

### Task 8: Frontend — api + yoklama kancası

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`

**Interfaces:**
- Consumes: Task 7'nin uçları
- Produces: `generateBatch(project, {prompts, negative, variants})` · `stopGeneration()` · `listPhotos(project)` · `useGeneration(project) -> {job, photos, error, generate, stop}`.

- [ ] **Step 1: `api.js`'de B4'ün `generatePhoto`'sunu değiştir ve iki fonksiyon ekle**

`generatePhoto` silinir (tek foto yolu kalktı), yerine:

```javascript
export async function generateBatch(project, { prompts, negative, variants }) {
  return request(`/api/projects/${encodeURIComponent(project)}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, negative, variants }),
  });
}

export async function stopGeneration() {
  return request("/api/stop", { method: "POST" });
}

export async function listPhotos(project) {
  const body = await request(`/api/projects/${encodeURIComponent(project)}/photos`);
  return body.photos;
}
```

`getStatus` ve `photoUrl` aynı kalır.

- [ ] **Step 2: `useGeneration.js`'i baştan yaz** (dosyanın tamamı)

```javascript
import { useCallback, useEffect, useRef, useState } from "react";

import { generateBatch, getStatus, listPhotos, stopGeneration } from "../../shared/api.js";

const POLL_MS = 2000;

// A batch runs for minutes, so the server answers 202 and we ask /api/status until it settles.
// The gallery is refreshed alongside every poll: Drive is the truth about what exists, so the
// grid fills while the batch runs and survives a reload.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  const [photos, setPhotos] = useState([]);
  const [error, setError] = useState(null);   // rejected request (400/404/409), not a failed render
  const timer = useRef(null);

  const refreshPhotos = useCallback(() => {
    listPhotos(project)
      .then(setPhotos)
      .catch((err) => setError(err.message));
  }, [project]);

  const poll = useCallback(() => {
    getStatus()
      .then((state) => {
        setJob(state);
        refreshPhotos();
        if (state.status === "running") {
          timer.current = setTimeout(poll, POLL_MS);
        }
      })
      .catch((err) => setError(err.message));
  }, [refreshPhotos]);

  useEffect(() => {
    poll();
    return () => clearTimeout(timer.current);
  }, [poll]);

  const generate = useCallback(
    (form) => {
      setError(null);
      return generateBatch(project, form)
        .then(() => {
          setJob({ status: "running", project, done: 0, failed: 0, total: 0 });
          timer.current = setTimeout(poll, POLL_MS);
        })
        .catch((err) => setError(err.message));
    },
    [project, poll],
  );

  const stop = useCallback(
    () => stopGeneration().then(setJob).catch((err) => setError(err.message)),
    [],
  );

  return { job, photos, error, generate, stop };
}
```

- [ ] **Step 3: Derleme bu adımda kırılır — beklenen**

Run: `cd queen-editor/frontend && npm run build`
Expected: FAIL — `"generatePhoto" is not exported` (`GeneratePanel`/`ProjectScreen` hâlâ B4 hâlinde). Task 9 onları yazıyor; derleme orada yeşile döner.

---

### Task 9: Frontend — galeri, varyant seçici, paneller, yerleşim

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`
- Create: `queen-editor/frontend/src/features/photo_generation/VariantPicker.jsx`
- Create: `queen-editor/frontend/src/features/photo_generation/ProgressPanel.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Regenerate: `queen-editor/frontend/dist/`

**Interfaces:**
- Consumes: `useGeneration` (Task 8) · `photoUrl` · kit (`Btn`, `Hand`, `Mono`, `Note`, `Icon`, `Status`)
- Produces: `<ProjectScreen project={ad} />` — solda galeri, sağda panel.

- [ ] **Step 1: `Gallery.jsx` yaz**

```jsx
import { photoUrl } from "../../shared/api.js";
import { Mono, Note } from "../../vendor/kit.jsx";

const GRID = {
  display: "grid",
  gridTemplateColumns: "repeat(5, 1fr)",
  gap: 10,
};

// Five columns, newest number first (the server sorts). New tab on click.
export default function Gallery({ project, photos }) {
  if (!photos.length) {
    return (
      <Note size={13} style={{ color: "var(--ink-3)" }}>
        Henüz foto yok — sağdaki listeyi doldur, Üret'e bas.
      </Note>
    );
  }
  return (
    <div style={GRID}>
      {photos.map((file) => (
        <a key={file} href={photoUrl(project, file)} target="_blank" rel="noreferrer"
           style={{ display: "flex", flexDirection: "column", gap: 4, textDecoration: "none" }}>
          <img src={photoUrl(project, file)} alt={file}
               style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                        border: "1px solid var(--border)", borderRadius: 3 }} />
          <Mono size={10} style={{ color: "var(--ink-3)" }}>{file}</Mono>
        </a>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: `VariantPicker.jsx` yaz**

```jsx
import { Mono } from "../../vendor/kit.jsx";

const OPTIONS = [1, 2, 3, 4];

// The design's segmented control is a wireframe (its buttons have no onClick), so this is our own
// component wearing its CSS. Changing the offered range is a one-line change here.
export default function VariantPicker({ value, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <Mono size={11} style={{ color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" }}>
        Varyant
      </Mono>
      <div className="wf-segment">
        {OPTIONS.map((option) => (
          <button
            key={option}
            className={option === value ? "is-on" : ""}
            onClick={() => onChange(option)}
          >{option}</button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: `ProgressPanel.jsx` yaz**

```jsx
import { Btn, Mono, Note } from "../../vendor/kit.jsx";

const BAR = {
  height: 6,
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 3,
  overflow: "hidden",
};

// Artboard 04: counter, progress bar, the frame being rendered, Stop.
export default function ProgressPanel({ job, onStop }) {
  const { done = 0, failed = 0, total = 0, current } = job;
  // total is 0 for the first poll after 202 (the server has not planned the frames yet).
  const percent = total ? Math.round(((done + failed) / total) * 100) : 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <Mono size={12} style={{ color: "var(--accent)" }}>
        üretiliyor — {done + failed}/{total || "…"}
      </Mono>
      <div style={BAR}>
        <div style={{ width: `${percent}%`, height: "100%", background: "var(--accent)" }} />
      </div>
      {current && (
        <Mono size={11} style={{ color: "var(--ink-3)", whiteSpace: "nowrap",
                                 overflow: "hidden", textOverflow: "ellipsis" }}>
          {current.number}_{current.letter} · {current.prompt}
        </Mono>
      )}
      {failed > 0 && (
        <Note size={12} style={{ color: "var(--danger)" }}>{failed} kare başarısız — atlandı</Note>
      )}
      <Btn onClick={onStop} style={{ justifyContent: "center", padding: "8px 12px" }}>Durdur</Btn>
      <Note size={11} style={{ color: "var(--ink-3)" }}>
        Durdurunca süren kare tamamlanır, sıradaki başlamaz.
      </Note>
    </div>
  );
}
```

- [ ] **Step 4: `GeneratePanel.jsx`'i baştan yaz** (dosyanın tamamı)

```jsx
import { useState } from "react";

import { Btn, Icon, Mono, Note } from "../../vendor/kit.jsx";
import VariantPicker from "./VariantPicker.jsx";

const LABEL = {
  color: "var(--ink-2)",
  letterSpacing: ".08em",
  textTransform: "uppercase",
};

const RAW_ERROR = {
  color: "var(--ink-3)",
  background: "var(--bg)",
  border: "1px solid var(--border)",
  borderRadius: 3,
  padding: "6px 8px",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

const PLACEHOLDER = '["ilk prompt", "ikinci prompt"]';

// Artboard 03: the prompt LIST (pasted as a Python list), one shared negative, variants, Üret.
export default function GeneratePanel({ job, error, busyElsewhere, onGenerate }) {
  const [prompts, setPrompts] = useState("");
  const [negative, setNegative] = useState("");
  const [variants, setVariants] = useState(4);

  const summary = {
    done: `bitti — ${job.done}/${job.total}`,
    stopped: `durduruldu — ${job.done}/${job.total}`,
  }[job.status];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {summary && <Mono size={11} style={{ color: "var(--ink-2)" }}>{summary}</Mono>}

      <Mono size={11} style={LABEL}>Prompt listesi</Mono>
      <textarea
        className="wf-input"
        rows={10}
        value={prompts}
        placeholder={PLACEHOLDER}
        onChange={(e) => setPrompts(e.target.value)}
        style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 12.5 }}
      />

      <Mono size={11} style={LABEL}>Negatif (hepsine)</Mono>
      <textarea
        className="wf-input"
        rows={3}
        value={negative}
        onChange={(e) => setNegative(e.target.value)}
        style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 12.5 }}
      />

      <VariantPicker value={variants} onChange={setVariants} />

      <Btn hl disabled={!prompts.trim() || busyElsewhere}
           onClick={() => onGenerate({ prompts, negative, variants })}
           style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
        <Icon.Sparkle /> Üret
      </Btn>

      {busyElsewhere && (
        <Note size={12} style={{ color: "var(--ink-3)" }}>
          Üretim sürüyor: {job.project} — bitmesini bekle.
        </Note>
      )}
      {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
      {job.status === "error" && (
        <>
          <span style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
            <Icon.Warn />
            <Note size={13} style={{ color: "var(--danger)", fontWeight: 500 }}>Üretim durdu</Note>
          </span>
          {/* The server's own error text -- we never guess the cause. */}
          <Mono size={11} style={RAW_ERROR}>{job.error}</Mono>
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 5: `ProjectScreen.jsx`'i baştan yaz** (dosyanın tamamı)

```jsx
import { navigate } from "../../shared/router.js";
import { Btn, Hand } from "../../vendor/kit.jsx";
import Gallery from "./Gallery.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import ProgressPanel from "./ProgressPanel.jsx";
import { useGeneration } from "./useGeneration.js";

const HEADER = {
  display: "grid",
  gridTemplateColumns: "1fr auto 1fr",
  alignItems: "center",
  padding: "14px 32px",
  background: "var(--bg-2)",
  borderBottom: "1px solid var(--border)",
};

// Artboard 03/04: gallery on the LEFT (the content), panel on the RIGHT (the controls).
export default function ProjectScreen({ project }) {
  const { job, photos, error, generate, stop } = useGeneration(project);
  const running = job.status === "running";
  // The worker is global: a batch started from another project blocks this one (the server 409s).
  const busyElsewhere = running && job.project !== project;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <div style={HEADER}>
        <Btn ghost onClick={() => navigate("/")}>← Projeler</Btn>
        <Hand size={20}>{project}</Hand>
        <span />
      </div>

      <div style={{ flex: 1, display: "flex", gap: 32, padding: "24px 32px", alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <Gallery project={project} photos={photos} />
        </div>
        <div style={{ width: 380, flexShrink: 0 }}>
          {running && !busyElsewhere
            ? <ProgressPanel job={job} onStop={stop} />
            : <GeneratePanel job={job} error={error} busyElsewhere={busyElsewhere}
                             onGenerate={generate} />}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Derle**

Run: `cd queen-editor/frontend && npm run build`
Expected: PASS — `dist/index.html` + `dist/assets/*` yeniden üretilir, uyarı yok.

- [ ] **Step 7: Backend testleri hâlâ geçiyor mu**

Run: `cd queen-editor && python -m pytest -q`
Expected: PASS (136).

---

### Task 10: Colab doğrulaması + commit (kullanıcı kapısı)

**Files:** (yok — doğrulama + commit)

Notebook değişmiyor: Bölüm 4'ün kurulum hücreleri ve `QE_COMFY_URL` aynen geçerli.

- [ ] **Step 1: Yerel tam tur**

Run: `cd queen-editor && python -m pytest -q` → PASS (123)
Run: `cd queen-editor/frontend && npm run build` → hata yok, `dist/` güncel

- [ ] **Step 2: Commit + push (kullanıcı onayıyla, doğrulamadan önce)**

Notebook repodan klonluyor; push edilmeyen kod Colab'da yok.

**Çok satırlı mesajı komut satırından geçirmeye çalışma** — PowerShell here-string'i argümanlara
bölüyor (Bölüm 4'te yaşandı). Mesaj önce scratchpad'e yazılır, sonra `-F` ile verilir.

Mesaj dosyası (`<scratchpad>/b5-commit-msg.txt`):

```
feat(queen-editor): Bölüm 5 — çoklu foto, galeri ve Durdur

Paste a prompt list, pick a variant count, hit Üret: every prompt x variant is
rendered in order into <project>/<n>_<letter>.png and the gallery fills while the
batch runs.

The batch loop lives in the use case, not the runner: order, numbering and what a
failure costs are business rules, and a synchronous spawn makes them testable
without threads. The runner only carries the thread, the reported progress and the
stop flag. Stopping is cooperative -- the frame in flight finishes, the next one
never starts.

Failure policy is one pure function (domain/policy.py): a frame failure is skipped,
three in a row or a loader failure stops the batch with the server's own error text.
Red per-frame cards and resume stay in Part 7.

start_generation is gone: one photo is one prompt x one variant, so keeping a second
path would have been dead code.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

```bash
# docs (yol haritasının sol/sağ düzeltmesi + durum satırı dahil)
git add -- docs/superpowers/specs/2026-07-25-queen-editor-b5-coklu-foto-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b5-coklu-foto.md \
  docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md
git commit -m "docs(queen-editor): Bölüm 5 — çoklu foto spec + plan, yol haritası düzeltmesi" -m \
  "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- \
  docs/superpowers/specs/2026-07-25-queen-editor-b5-coklu-foto-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b5-coklu-foto.md \
  docs/superpowers/plans/2026-07-24-queen-editor-roadmap.md
# feat
git add -- queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist
git commit -F "<scratchpad>/b5-commit-msg.txt" -- \
  queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist
git push origin feat/queen-editor-v1
```

Silinen dosya (`start_generation.py`) `git add -- queen-editor/backend` ile silinmiş olarak kaydedilir — commit sonrası `git status` temiz olmalı.

- [ ] **Step 3: Kullanıcı Colab doğrulaması (T4)**

**Runtime → T4 GPU** → Run all → linke gir → projeye tıkla. Beklenen:

1. Ekran: **solda** galeri (varsa Bölüm 4'ün fotoları, en yeni üstte), **sağda** prompt listesi + negatif + varyant + Üret.
2. 3 prompt'luk `PROMPTS = [...]` yapıştır, varyant **2** → **Üret** → sağ panel ilerlemeye döner: `n/6`, çubuk, `numara_harf · prompt`. Galeri canlı dolar.
3. Bitince `bitti — 6/6`, form geri gelir; Drive'da 6 yeni dosya, numaralar eskilerin devamı; sıra `N_a N_b (N+1)_a …`.
4. Tekrar Üret (1 prompt × 1 varyant) → yeni numara sona eklenir, üstüne yazma yok.
5. Üretim sürerken **Durdur** → süren kare biter, `durduruldu — n/6`, form geri gelir; galeride o ana kadarkiler var.
6. Üretim sürerken sayfayı yenile → ilerleme bloğu geri gelir, galeri dolu; form boş (bilinçli bedel).
7. Fotoya tıkla → yeni sekmede açılır.
8. Köşeli parantezsiz metin yaz → **Üret** → kırmızı satırda örnekli Türkçe hata (400).
9. (Negatif) ComfyUI'yi öldür (`!pkill -f 'python main.py'`) → Üret → üst üste 3 hatada `Üretim durdu` + ham hata metni.

---

## Doğrulama özeti

| Ne | Nasıl |
|---|---|
| Prompt listesi parse | `pytest backend/tests/test_prompt_list.py` → 10 |
| Hata politikası | `pytest backend/tests/test_policy.py` → 4 |
| Runner (rapor + durdurma) | `pytest backend/tests/test_photo_runner.py` → 9 |
| Galeri sırası | `pytest backend/tests/test_photo_store.py` → 9 |
| Negatif node 4 | `pytest backend/tests/test_comfy_photo_generator.py` → 7 |
| Grafikte node 3/4/40 var | `pytest backend/tests/test_workflow_asset.py` → 1 |
| Batch döngüsü (sıra, atla, dur, stop) | `pytest backend/tests/test_photo_usecases.py` → 22 |
| Uçlar | `pytest backend/tests/test_photo_routes.py` → 14 |
| Bölüm 1-4 bozulmadı | `python -m pytest -q` → 136 |
| Sunucu ayağa kalkıyor | `python -c "from backend.main import app; …"` → `/api/stop` + `…/photos` listede |
| Arayüz derleniyor | `cd frontend && npm run build` |
| Uçtan uca | Colab (T4): 3 prompt × 2 varyant → 6 foto, galeri canlı dolar, Durdur çalışır |
| Bölüm 5 kapanır | Kullanıcı doğrular → docs + feat commit'leri + push |
