# Queen Editor v5 · Görev 16 — Video prompt'unu dil modeli yazar · Uygulama planı

> **Uygulayıcıya:** her adım önce kırmızı test, sonra en küçük kod. Tasarım:
> [Görev 16 spec](../specs/2026-08-12-queen-editor-v5-gorev-16-video-prompt-design.md).

**Hedef:** sırası gelen video işinin prompt'u boşsa, motor onu xAI Grok'a fotonun prompt'undan
yazdırsın, o metinle üretsin ve metni videonun kayıt satırına yazsın.

**Mimari:** taşıma katmanı yeni bir servis (`services/xai/client.py`); ne sorulacağı üretim
özelliğinin data katmanında (`data/xai_prompt_writer.py`); motor yazıcıyı `{iş türü: yazıcı}`
haritasından bulur — üreticilerdeki kalıbın aynısı.

**Yığın:** Python (pytest) · `requests` (comfy istemcisindeki gibi enjekte edilir).

## Genel kısıtlar

- Kod, yorum, test adı ve commit **İngilizce**; kullanıcıya görünen metin **Türkçe**.
- Hata mesajı **asla sebep uydurmaz**: sunucunun kendi gövdesi basılır.
- Katman kuralı: `presentation → domain ← data → services`; domain saf kalır, port alır.
- Somut bağlama yalnız `backend/main.py`'de.
- Test komutları (birebir):
  - `python -m pytest queen-editor -q`
  - `npm test --prefix queen-editor/frontend -- --run`
  - `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — xAI istemcisi

**Dosyalar:**
- Yeni: `queen-editor/backend/services/xai/__init__.py` (boş)
- Yeni: `queen-editor/backend/services/xai/client.py`
- Test: `queen-editor/backend/tests/test_xai_client.py`

**Arayüz:**
- Üretir: `XaiClient(api_key, model, url, http=requests, timeout=120)` · `.complete(system, user) -> str`

- [ ] **Adım 1 — kırmızı test:**

```python
import pytest

from backend.services.xai.client import NotConfigured, XaiClient


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text or ""

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeHttp:
    """Records the one request the client makes and answers with what the test set up."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "body": json, "timeout": timeout})
        return self.response


def answering(text):
    return FakeResponse({"choices": [{"message": {"content": text}}]})


def client(http, api_key="k-1"):
    return XaiClient(api_key, "grok-4.3", "https://api.x.ai/v1/chat/completions", http=http,
                     timeout=120)


def test_the_request_carries_the_model_the_instruction_and_the_prompt():
    http = FakeHttp(answering(" she turns her head slowly "))

    answer = client(http).complete("talimat", "kırmızı elbiseli kadın")

    assert answer == "she turns her head slowly"          # trimmed: the model pads its answers
    call = http.calls[0]
    assert call["url"] == "https://api.x.ai/v1/chat/completions"
    assert call["headers"]["Authorization"] == "Bearer k-1"
    assert call["timeout"] == 120
    assert call["body"] == {
        "model": "grok-4.3",
        "messages": [{"role": "system", "content": "talimat"},
                     {"role": "user", "content": "kırmızı elbiseli kadın"}],
    }


def test_an_http_error_is_raised_with_the_servers_own_body():
    http = FakeHttp(FakeResponse(status_code=401, text='{"error": "invalid key"}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "prompt")

    assert "401" in str(blew_up.value)
    assert '{"error": "invalid key"}' in str(blew_up.value)


def test_an_answer_that_is_not_the_expected_shape_shows_what_came():
    http = FakeHttp(FakeResponse({"choices": []}, text='{"choices": []}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "prompt")

    assert '{"choices": []}' in str(blew_up.value)


def test_an_empty_answer_is_a_failure_rather_than_an_empty_prompt():
    http = FakeHttp(answering("   "))

    with pytest.raises(RuntimeError):
        client(http).complete("talimat", "prompt")


def test_without_a_key_it_says_so_before_it_asks_anything():
    http = FakeHttp(answering("x"))

    with pytest.raises(NotConfigured):
        client(http, api_key="").complete("talimat", "prompt")

    assert http.calls == []
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → ImportError.

- [ ] **Adım 3 — `services/xai/client.py`:**

```python
"""xAI chat transport -- send two messages, get the answer's text back.

Knows nothing about video, prompts or frames: what to ask is the caller's business (see
features/photo_generation/data/xai_prompt_writer.py). `http` is injected so tests need no network.
"""
import json

import requests


class NotConfigured(RuntimeError):
    """No API key on this machine (message is user-facing)."""


class XaiClient:
    def __init__(self, api_key, model, url, http=requests, timeout=120):
        self._api_key = api_key
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
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Video prompt yazıcısı

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Yeni: `queen-editor/backend/features/photo_generation/data/xai_prompt_writer.py`
- Test: `queen-editor/backend/tests/test_video_prompt_writer.py`

**Arayüz:**
- Tüketir: `XaiClient.complete`.
- Üretir: `VideoPromptWriter(client).write(prompts) -> str`; port `PromptWriter.write(prompts)`.

- [ ] **Adım 1 — kırmızı test:**

```python
from backend.features.photo_generation.data.xai_prompt_writer import (
    INSTRUCTION,
    VideoPromptWriter,
)


class FakeClient:
    def __init__(self, answer="she turns her head"):
        self.answer = answer
        self.calls = []

    def complete(self, system, user):
        self.calls.append((system, user))
        return self.answer


def test_the_photo_prompt_is_what_the_model_is_asked_to_convert():
    client = FakeClient()

    written = VideoPromptWriter(client).write({"photo": "kırmızı elbiseli kadın"})

    assert written == "she turns her head"
    assert client.calls == [(INSTRUCTION, "kırmızı elbiseli kadın")]


def test_the_instruction_says_what_wan_needs_and_what_to_leave_out():
    # The rules are the whole value of this file: a drifted instruction is a wrong prompt.
    assert "image-to-video" in INSTRUCTION
    assert "Keep the camera static" in INSTRUCTION
    assert "Output only the motion prompt itself" in INSTRUCTION
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → ImportError.

- [ ] **Adım 3 — `data/xai_prompt_writer.py`:**

```python
"""What the language model is asked when a video job needs a prompt.

The instruction is inherited knowledge, not code: collab-toolbox's prompt_converter notebook does
this same conversion, and its rules are what a Wan I2V prompt needs. Nothing is read from that file
at runtime -- the tools share knowledge, never imports.

The transport is services/xai/client.py; this file only decides what to say.
"""

# English, and it stays English: it is written for the model, not for a reader of the screen. Wan's
# own prompts are English too.
INSTRUCTION = """
You are an expert prompt engineer specializing in image-to-video generation with the Wan model.
I will give you one SDXL prompt that was used to generate a still image. Convert it into an
optimized Wan image-to-video (I2V) positive prompt.

Follow these rules:

Don't re-describe the static scene in detail — Wan already receives the actual image as input. The
image defines the appearance; your job is to define motion.
Keep the camera static — no camera movement, no zoom, no pan.
Focus primarily on the action in the image — bring the subject's main activity to life as natural,
continuous movement. Build the motion around what the subject is actively doing.
Add subtle secondary motion to support the main action (hair, clothing, breathing, environmental
details like wind or water).
Keep it natural and physically plausible — realistic motion looks better than exaggerated movement
that breaks the image.
Specify pacing and mood.

Output only the motion prompt itself, as one concise paragraph of plain text. No list, no
surrounding quotes, no numbering, no explanations, no markdown code fences, no extra text.
"""


class VideoPromptWriter:
    def __init__(self, client):
        self._client = client

    def write(self, prompts):
        """`prompts` is what the frame already says, layer by layer. A video is made from the photo,
        so that is the one this writer reads."""
        return self._client.complete(INSTRUCTION, prompts.get("photo", ""))
```

- [ ] **Adım 4 — `ports.py`'ye portu ekle:**

```python
class PromptWriter(Protocol):
    def write(self, prompts: dict) -> str:
        """The prompt a job of this type should be produced with.

        `prompts` is what the frame already says: {"photo": …} today, plus the video's own when
        audio joins. Raising is a failure like any other -- the loop's three attempts and its
        frame-fault rule apply to it unchanged.
        """
        ...
```

- [ ] **Adım 5:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — Motor prompt'u yazdırır

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/run_loop.py`
- Değişecek: `queen-editor/backend/features/photo_generation/domain/usecases/run_queue.py`,
  `start_batch.py`, `resume_batch.py`, `retry_frame.py`, `retry_failed.py`, `queue_videos.py`
  (yalnız `writers` parametresini taşımak için)
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Arayüz:**
- `make_job(..., writers=None)` · `run_queue(..., writers=None)` · use case'ler `writers=None`
  taşır (adlandırılmış parametre, en sonda — çağıranların hiçbiri kırılmaz).

- [ ] **Adım 1 — kırmızı testler (`test_photo_usecases.py`, video testlerinin yanına):**

```python
class FakeWriter:
    """The language model, without one: answers the same sentence and counts the asks."""

    def __init__(self, answer="kadın başını yavaşça çeviriyor", blows_up=None):
        self.answer = answer
        self.blows_up = blows_up
        self.calls = []

    def write(self, prompts):
        self.calls.append(prompts)
        if self.blows_up:
            raise self.blows_up
        return self.answer


def video_job_project(prompt="p", job_prompt=""):
    """A produced photo and one video job owed on it."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[
        frame(0, prompt=prompt),
        {"id": "0_a", "type": "video", "number": 0, "variant": 0, "prompt": job_prompt,
         "negative": "", "seed": None, "model": ""},
    ])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                            "prompt": prompt})
    return store, record, plan_store


def test_a_video_job_with_no_prompt_has_one_written_from_the_photos():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    generator, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.calls == [{"photo": "kırmızı elbiseli kadın"}]
    # Produced with the written text, and the record says the layer was made with it.
    assert generator.calls == [("kadın başını yavaşça çeviriyor", "", None, "")]
    video = [row for row in record.rows if row.get("layer") == "video"][0]
    assert video["prompt"] == "kadın başını yavaşça çeviriyor"


def test_a_job_that_carries_its_own_prompt_never_reaches_the_model():
    # An edited prompt is the user's own words: asking the model again would overwrite them.
    store, record, plan_store = video_job_project(job_prompt="elini kaldırıyor")
    generator, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.calls == []
    assert generator.calls == [("elini kaldırıyor", "", None, "")]


def test_a_frame_with_no_photo_prompt_is_not_worth_an_ask():
    store, record, plan_store = video_job_project(prompt="")
    generator, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.calls == []
    assert generator.calls == [("", "", None, "")]


def test_the_three_attempts_of_one_job_spend_a_single_ask():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    # Fails on the written prompt twice, then renders it.
    generator = FailsTwice("kadın başını yavaşça çeviriyor")
    writer = FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert len(writer.calls) == 1


def test_a_model_that_will_not_answer_stops_the_run():
    # No answer is not this frame's fault: the next job would fall exactly the same way.
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    runner = sync_runner()
    writer = FakeWriter(blows_up=RuntimeError("xAI HTTP 401\ninvalid key"))

    resume_batch(runner, store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    state = runner.status()
    assert state["status"] == "error"
    assert "401" in state["error"]
    # Nothing written: the job is still owed once the key is fixed.
    assert [row for row in record.rows if row.get("layer") == "video"] == []
```

`FailsTwice` yardımcısını testlerin yanına yaz:

```python
class FailsTwice:
    """Drops the first two attempts at the same job, then renders whatever is offered."""

    def __init__(self, expect):
        self.expect = expect
        self.calls = []

    def generate(self, prompt, negative, seed, model=""):
        self.calls.append((prompt, negative, seed, model))
        if len(self.calls) < 3:
            raise FrameFault(f"node 41: {prompt}")
        return b"MP4"
```

> `frame(0, prompt=...)` yardımcısının imzasını dosyadan doğrula (`frame(number, letter, prompt,
> seed)`).

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı (`writers` bilinmiyor).

- [ ] **Adım 3 — `run_loop.py`:** döngü yazıcıyı da tür haritasından bulur.

Modül başlığına ekle:

```
Some jobs are produced with a prompt nobody typed: a video's own is written by a language model when
its turn comes. Which model that is the loop does not know either -- it looks the job's type up in a
second map, exactly the way it finds the producer.
```

`make_job` imzası: `..., clock=time.monotonic, log=None, order_store=None, writers=None`.
Docstring'e bir paragraf:

```
`writers` maps a job type to the thing that writes its prompt when the job carries none (see
ports.PromptWriter). A type with no writer is produced with the prompt it has, which is what a photo
job -- whose prompt is the user's own -- always does.
```

Döngü gövdesinde, `attempts, holding = 0, None` satırını genişlet:

```python
        # Attempts spent on the job in hand, which job they belong to, and the prompt written for
        # it. Memory only: a dead process must leave no count behind, and a restarted run deserves
        # three fresh tries.
        attempts, holding, written = 0, None, None
```

`if name != holding:` bloğu:

```python
            if name != holding:
                # A different job: its predecessor's attempts and its written prompt are not its.
                holding, attempts, written = name, 0, None
```

`try:` bloğunun başına, `producer.generate` çağrısından önce:

```python
            try:
                writer = (writers or {}).get(kind)
                if writer and not current["prompt"] and written is None:
                    # Asked here rather than when the job was queued: a job that waits hours would
                    # otherwise be produced from a prompt written for a gallery that has changed,
                    # and queueing 40 jobs would spend 40 requests before a single frame is made.
                    # Inside the try on purpose -- a model that will not answer is a failure like
                    # any other, and the three attempts and the frame-fault rule already say what
                    # happens next.
                    source = _prompts_of(record, project, fid)
                    # Nothing to convert: asking would buy an invented prompt. I2V sees the picture
                    # itself, so producing with an empty prompt is a real answer here.
                    if any(source.values()):
                        written = writer.write(source)
                prompt = current["prompt"] or written or ""
                data = producer.generate(prompt, current["negative"], current["seed"],
                                         current["model"])
```

Kayıt satırı yazılan metni taşır:

```python
            record.append(project, {"file": filename, "frame": fid, "layer": kind,
                                    "status": queue.DONE,
                                    "prompt": prompt, "negative": current["negative"],
                                    "seed": current["seed"], "createdAt": now()})
```

Modül sonuna yardımcı:

```python
def _prompts_of(record, project, fid):
    """What the frame already says, layer by layer -- the material a prompt writer works from.

    Read from the record rather than the plan: a copy frame has no photo job of its own, and its
    photo row is where its prompt lives.
    """
    photo = next((row for row in record.list(project) if row["frame"] == fid), None)
    return {"photo": (photo or {}).get("prompt", "")}
```

- [ ] **Adım 4 — `run_queue.py`:** `writers=None` parametresi ekle ve `make_job`'a geçir.

```python
def run_queue(runner, store, record, plan_store, producers, now, project, log=None,
              order_store=None, writers=None):
```

```python
    job = make_job(runner, store, record, plan_store, producers, now, project, log=log,
                   order_store=order_store, writers=writers)
```

- [ ] **Adım 5 — kullanan use case'ler:** `start_batch`, `resume_batch`, `retry_frame`,
`retry_failed`, `queue_videos` imzalarının sonuna `writers=None` ekle ve `run_queue`'ya geçir.
Her birinde tek satır; başka bir şey değişmez.

- [ ] **Adım 6:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 4 — Bağlama: config, main, notebook

**Dosyalar:**
- Değişecek: `queen-editor/backend/config.py`, `queen-editor/backend/main.py`
- Değişecek: `queen-editor/app.ipynb` (CONFIG hücresi + Flask'ı başlatan hücre)
- Test: yok (bağlama noktası; davranış testleri Görev 1-3'te)

- [ ] **Adım 1 — `config.py`:**

```python
# The language model that writes a video's prompt (design v3, madde 27). The key comes from Colab
# Secrets through the notebook; without one the app still starts and photos still render -- only a
# video job's turn stops the run, with the client's own sentence.
XAI_API_KEY = os.environ.get("QE_XAI_API_KEY", "")
XAI_MODEL = os.environ.get("QE_XAI_MODEL", "grok-4.3")
XAI_URL = os.environ.get("QE_XAI_URL", "https://api.x.ai/v1/chat/completions")
XAI_TIMEOUT = 120          # seconds per request; one prompt is a short answer
```

- [ ] **Adım 2 — `main.py`:**

```python
from backend.features.photo_generation.data.xai_prompt_writer import VideoPromptWriter
from backend.services.xai.client import XaiClient
```

```python
# Who writes a job's prompt when it carries none. Photo has no writer: its prompt is the user's own.
_xai = XaiClient(config.XAI_API_KEY, config.XAI_MODEL, config.XAI_URL, timeout=config.XAI_TIMEOUT)
_writers = {layers.VIDEO: VideoPromptWriter(_xai)}
```

`start_batch`, `resume_batch`, `retry_frame`, `retry_failed`, `queue_videos` partial'larına
`writers=_writers` ekle.

- [ ] **Adım 3 — `app.ipynb` CONFIG hücresi:** `CIVITAI_COOKIE`'nin okunduğu yerin altına:

```python
# The video prompt is written by xAI; the key comes from Secrets like the two above. No assert:
# a photo-only run needs no language model, and stopping the notebook for it would be wrong.
try:
    XAI_API_KEY = userdata.get("XAI_API_KEY")
except Exception:
    XAI_API_KEY = ""
```

ve hücrenin sonundaki print'lerin yanına:

```python
print(f"✓ xAI anahtarı: {'okundu' if XAI_API_KEY else 'yok — video prompt yazılamaz'}")
```

- [ ] **Adım 4 — `app.ipynb` Flask hücresi:** `flask_env` sözlüğüne `"QE_XAI_API_KEY": XAI_API_KEY`
ekle (yorumu da güncelle: ortamdan okunanlar Drive kökü, ComfyUI adresi ve xAI anahtarı).

- [ ] **Adım 5:** `python -m pytest queen-editor -q` → yeşil (defter testsiz; import kırılmadığını
tam takım söyler).

---

## Görev 5 — Tam takım ve commit

- [ ] **Adım 1:** `python -m pytest queen-editor -q`
- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run`
- [ ] **Adım 3:** commit (ön yüz değişmedi, `dist/` yeniden kurulmaz):

```
feat(queen-editor): a video's prompt is written when its turn comes
```
