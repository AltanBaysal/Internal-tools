# Görev 12 — Kurulum akışı · Uygulama Planı

> **Çalıştıran ajan için:** GEREKLİ ALT BECERİ: superpowers:executing-plans.

**Amaç:** Bir üreticinin model grubu uygulamanın içinden iner; ilerlemesi görünür, iptal edilebilir,
bitince ilgili panel kendiliğinden açılır.

**Mimari:** İndirmenin kendisi bir **servis** (`services/download/`), hangi dosyaların gerektiği
`producers` feature'ının **verisi**, nereye ineceği onun **data** katmanı, arka planda koşması ise
kendi **runner**'ı — foto koşucusunun kopyası, bağımlısı değil.

**Spec:** [Görev 12 tasarımı](../specs/2026-08-12-queen-editor-v5-gorev-12-kurulum-akisi-design.md)

## Global kısıtlar

- **Full TDD:** önce kırmızı test. İndirme testleri **sahte fetcher** ile koşar; ağ yok, disk
  `tmp_path`.
- `services/` hiçbir feature'ı bilmez; somut bağlama yalnız `main.py`'de.
- Dil ayrımı: yorum/test adı/commit **İngilizce**, kullanıcı metni **Türkçe**.
- Test komutları: `npm test --prefix queen-editor/frontend -- --run` ·
  `python -m pytest queen-editor -q` · derleme `npm run build --prefix queen-editor/frontend`.
- **Tek commit**, görevin sonunda, `dist/` ile birlikte.

---

### Görev 1: Model grubu ve "kurulu" ölçütü

> **Koşu notu (2026-08-12), iki düzeltme:**
> 1. Plan foto grubuna sabit bir dosya adı yazıyordu. O ad bizim değil — defterin kurduğu checkpoint
>    kullanıcının seçimi. Uydurulmuş bir ad, **çalışan bir kurulumu "kurulu değil"** gösterir ve
>    foto panelini kilitlerdi. Ölçüt ikiye ayrıldı: **grubu olan üretici dosyalarıyla, grubu olmayan
>    kendisiyle** cevaplanır (`list_producers(groups, files, producers, running)`).
> 2. Görev 5'in iki testi (buton kilidi, şerit noktası) koddan **sonra** yazıldı. Sırası kaçtı;
>    ikisi de eski kodda geçmezdi (`producer` prop'u yoktu), o yüzden kapsam gerçek — ama kırmızı
>    görülmedi.

**Dosyalar:**
- Oluştur: `.../producers/domain/model_groups.py`, `.../producers/data/__init__.py`,
  `.../producers/data/comfy_models.py`
- Değiştir: `.../producers/domain/usecases/list_producers.py`, `.../producers/domain/ports.py`
- Değiştir: `queen-editor/backend/config.py`, `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_producers.py`

**Arayüzler:**
- Üretir: `GROUPS = {kind: [{"folder", "name", "url"|None}]}`.
- Üretir: `ModelFiles` port'u — `exists(folder, name) -> bool`, `path(folder, name) -> str`,
  `remove(folder, name)`.
- Değişir: `list_producers(groups, files, running=None)` — üretici nesnesine değil **dosyalara**
  bakar; `running` o an koşan kurulumun durumudur.

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

`test_producers.py`'yi yeni ölçüte çevir; sahte dosya sistemi:

```python
class FakeFiles:
    def __init__(self, present=()):
        self.present = set(present)
        self.removed = []

    def exists(self, folder, name):
        return (folder, name) in self.present

    def path(self, folder, name):
        return f"/models/{folder}/{name}"

    def remove(self, folder, name):
        self.removed.append((folder, name))
        self.present.discard((folder, name))


GROUPS = {"photo": [{"folder": "checkpoints", "name": "nova.safetensors", "url": "u1"}],
          "video": [{"folder": "diffusion_models", "name": "wan.safetensors", "url": "u2"},
                    {"folder": "vae", "name": "wan_vae.safetensors", "url": "u3"}],
          "audio": []}


def test_a_producer_is_installed_when_every_file_of_its_group_is_here():
    rows = list_producers(GROUPS, FakeFiles(present=[("checkpoints", "nova.safetensors")]))

    assert rows[0]["installed"] is True


def test_one_missing_file_means_not_installed():
    files = FakeFiles(present=[("diffusion_models", "wan.safetensors")])

    rows = list_producers(GROUPS, files)

    assert rows[1]["installed"] is False


def test_the_running_install_is_reported_on_its_own_row():
    rows = list_producers(GROUPS, FakeFiles(),
                          running={"kind": "video", "done": 5, "total": 10, "file": "wan"})

    assert rows[1]["installing"] == {"done": 5, "total": 10, "file": "wan"}
    assert rows[0].get("installing") is None
```

Eski `FakeProducer` testleri silinir — ölçüt değişti.

- [ ] **Adım 2: Koş, kırmızıyı gör** · `python -m pytest queen-editor -q`

- [ ] **Adım 3: Grubu, port'u ve ölçütü yaz**

`model_groups.py`:

```python
"""What each producer needs on disk, and where.

Knowledge inherited from collab-toolbox, not a dependency on it: the names and addresses are copied
into our own file, so that folder can change without changing ours (CODE-STANDARD's independence
rule).

`url: None` means the file cannot be fetched without credentials -- the notebook installs it. The
installer stops there and says so rather than leaving a group half-installed in silence.
"""
HF_WAN22 = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files"
HF_WAN21 = "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files"

GROUPS = {
    # The photo group is what the notebook's setup cells already fetch; it is listed here so the
    # same question ("is this producer installed?") has one answer for all three.
    "photo": [
        {"folder": "checkpoints", "name": "nova3dcg.safetensors", "url": None},
    ],
    "video": [
        {"folder": "vae", "name": "wan_2.1_vae.safetensors",
         "url": f"{HF_WAN21}/vae/wan_2.1_vae.safetensors"},
        {"folder": "text_encoders", "name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
         "url": f"{HF_WAN21}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
         "url": f"{HF_WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"},
        {"folder": "loras", "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
         "url": f"{HF_WAN22}/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"},
        # SmoothMix I2V comes from Civitai and needs a token; the notebook fetches it.
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_High.safetensors", "url": None},
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_Low.safetensors", "url": None},
    ],
    "audio": [
        {"folder": "mmaudio", "name": "mmaudio_large_44k_v2.pth", "url": None},
    ],
}
```

`ports.py`'ye eklenir:

```python
class ModelFiles(Protocol):
    def exists(self, folder: str, name: str) -> bool:
        """Is this file already on this machine?"""

    def path(self, folder: str, name: str) -> str:
        """Where it goes -- created on demand by the writer."""

    def remove(self, folder: str, name: str) -> None:
        """Throw away a half-written file."""
```

`list_producers.py`:

```python
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(groups, files, running=None):
    """Three rows: a name, whether the group is here, and the install that is running on it."""
    rows = []
    for kind in ORDER:
        group = groups.get(kind, [])
        row = {"id": kind, "name": NAMES[kind],
               # An empty group would read as "installed", which is a lie about a producer nobody
               # has described yet.
               "installed": bool(group) and all(files.exists(f["folder"], f["name"])
                                                for f in group)}
        if running and running.get("kind") == kind:
            row["installing"] = {k: running[k] for k in ("done", "total", "file")}
        rows.append(row)
    return rows
```

`data/comfy_models.py`:

```python
"""ModelFiles over the ComfyUI folder -- the only place that knows that layout."""
import os


class ComfyModelFiles:
    def __init__(self, root):
        self._root = root

    def path(self, folder, name):
        return os.path.join(self._root, "models", folder, name)

    def exists(self, folder, name):
        return os.path.exists(self.path(folder, name))

    def remove(self, folder, name):
        try:
            os.remove(self.path(folder, name))
        except FileNotFoundError:
            pass
```

`config.py`:

```python
# ComfyUI's own folder on this machine -- where a producer's model group is installed. The notebook
# passes it in; the literal is only the fallback.
COMFY_ROOT = os.environ.get("QE_COMFY_ROOT", "/content/ComfyUI")
```

`main.py` bağlar: `_model_files = ComfyModelFiles(config.COMFY_ROOT)` ve
`partial(list_producers, GROUPS, _model_files)`.

- [ ] **Adım 4: Koş, yeşili gör** · `python -m pytest queen-editor -q`

---

### Görev 2: İndirme servisi

**Dosyalar:**
- Oluştur: `queen-editor/backend/services/download/__init__.py`,
  `queen-editor/backend/services/download/fetcher.py`
- Test: `queen-editor/backend/tests/test_fetcher.py`

**Arayüzler:**
- Üretir: `HttpFetcher(open_url).fetch(url, path, on_progress, cancelled) -> None` — parça parça
  yazar, her parçada `on_progress(done, total)` çağırır, `cancelled()` doğru dönerse
  `Cancelled` yükseltir.

- [ ] **Adım 1: Testi yaz (kırmızı test)**

```python
"""Streaming one file to disk: progress while it lands, and a way to stop it."""
import pytest

from backend.services.download.fetcher import Cancelled, HttpFetcher


class FakeResponse:
    def __init__(self, chunks, total=None):
        self.chunks = list(chunks)
        self.headers = {"Content-Length": str(total)} if total is not None else {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def iter(self, size):
        return iter(self.chunks)


def opener(response):
    return lambda url: response


def test_it_writes_the_whole_file_and_reports_as_it_goes(tmp_path):
    seen = []
    fetcher = HttpFetcher(opener(FakeResponse([b"ab", b"cd"], total=4)))
    target = tmp_path / "deep" / "model.safetensors"

    fetcher.fetch("http://x", str(target), on_progress=lambda d, t: seen.append((d, t)))

    assert target.read_bytes() == b"abcd"
    assert seen == [(2, 4), (4, 4)]


def test_a_server_that_gives_no_length_reports_an_unknown_total(tmp_path):
    seen = []
    fetcher = HttpFetcher(opener(FakeResponse([b"ab"])))

    fetcher.fetch("http://x", str(tmp_path / "m"), on_progress=lambda d, t: seen.append((d, t)))

    assert seen == [(2, None)]


def test_cancelling_stops_the_download_and_leaves_no_half_file(tmp_path):
    target = tmp_path / "m"
    fetcher = HttpFetcher(opener(FakeResponse([b"ab", b"cd"], total=4)))

    with pytest.raises(Cancelled):
        fetcher.fetch("http://x", str(target), cancelled=lambda: True)

    assert not target.exists()
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

- [ ] **Adım 3: Servisi yaz**

```python
"""One file, from a URL to a path, in pieces.

A service: it knows no producer, no model and no folder layout -- only how to move bytes and how to
be stopped. `open_url` is injected so tests never touch the network.

The file is written under a .part name and renamed at the end: a run that dies leaves no file that
looks finished, and "is it here?" stays a question about the real name.
"""
import os
import urllib.request

CHUNK = 1 << 20     # 1 MiB: big enough that progress is not a syscall storm, small enough to stop


class Cancelled(Exception):
    """The user asked for the download to stop (message is user-facing)."""


def _open(url):
    return urllib.request.urlopen(url)


class HttpFetcher:
    def __init__(self, open_url=None):
        self._open = open_url or _open

    def fetch(self, url, path, on_progress=None, cancelled=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        partial = f"{path}.part"
        done = 0
        try:
            with self._open(url) as response:
                total = self._length(response)
                with open(partial, "wb") as out:
                    for chunk in response.iter(CHUNK):
                        if cancelled and cancelled():
                            raise Cancelled("Kurulum iptal edildi.")
                        out.write(chunk)
                        done += len(chunk)
                        if on_progress:
                            on_progress(done, total)
            os.replace(partial, path)
        except BaseException:
            # Whatever went wrong -- cancel, network, disk -- the half file goes.
            if os.path.exists(partial):
                os.remove(partial)
            raise

    @staticmethod
    def _length(response):
        raw = response.headers.get("Content-Length")
        return int(raw) if raw else None
```

> `response.iter(size)` sahte ve gerçek yanıtın ortak yüzeyidir; `urlopen` sonucunda karşılığı
> `read` olduğu için `_open` gerçek hâlinde küçük bir sarmalayıcı döndürür (aşağıda).

`_open` gerçek hâli:

```python
class _Streamed:
    """urlopen's response with the one method the fetcher uses."""

    def __init__(self, response):
        self._response = response
        self.headers = response.headers

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._response.close()
        return False

    def iter(self, size):
        while True:
            chunk = self._response.read(size)
            if not chunk:
                return
            yield chunk


def _open(url):
    return _Streamed(urllib.request.urlopen(url))
```

- [ ] **Adım 4: Koş, yeşili gör**

---

### Görev 3: Kurulum koşusu ve uçları

**Dosyalar:**
- Oluştur: `.../producers/runner.py`, `.../producers/domain/usecases/install_producer.py`,
  `.../producers/domain/usecases/cancel_install.py`
- Değiştir: `.../producers/presentation/routes.py`, `main.py`
- Test: `queen-editor/backend/tests/test_producers.py`

**Arayüzler:**
- Üretir: `InstallRunner` — `status()`, `start(kind, job)`, `report(patch)`, `request_cancel()`,
  `cancelled()`, `reset()`. Foto koşucusunun kopyası; bağımlısı değil.
- Üretir: `install_producer(groups, files, fetcher, runner, kind) -> None`; ikinci çağrı `Busy`.
- Üretir: `cancel_install(runner) -> None`.

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

```python
class FakeFetcher:
    def __init__(self, fail=None):
        self.fetched = []
        self.fail = fail

    def fetch(self, url, path, on_progress=None, cancelled=None):
        if self.fail and url == self.fail:
            raise RuntimeError("bağlantı yok")
        self.fetched.append((url, path))
        if on_progress:
            on_progress(10, 10)


def sync_installer():
    return InstallRunner(spawn=lambda fn: fn())


def test_it_fetches_only_what_is_missing():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors")])
    fetcher = FakeFetcher()

    install_producer(GROUPS, files, fetcher, sync_installer(), "video")

    assert [url for url, _p in fetcher.fetched] == ["u2"]


def test_a_second_install_is_refused_while_one_runs():
    runner = InstallRunner(spawn=lambda fn: None)      # never finishes
    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, "video")

    with pytest.raises(Busy):
        install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, "photo")


def test_a_file_the_app_cannot_fetch_stops_the_install_and_says_why():
    runner = sync_installer()
    groups = {"video": [{"folder": "d", "name": "smooth.safetensors", "url": None}]}

    install_producer(groups, FakeFiles(), FakeFetcher(), runner, "video")

    assert runner.status()["status"] == "error"
    assert "defter" in runner.status()["error"]
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

- [ ] **Adım 3: Koşucuyu, senaryoyu ve uçları yaz**

`producers/runner.py` — `photo_generation/runner.py`'nin kopyası, adları kurulum diline çevrilmiş
(`project` yerine `kind`, `request_stop` yerine `request_cancel`). Kopyalanır, import edilmez: aynı
bakım kuralı.

`install_producer.py`:

```python
"""Fetch whatever of a producer's group is missing, in the background.

The rule is the same one the queue uses: work already done is not done again. A file that cannot be
fetched without credentials stops the run and says so -- a group half installed in silence would
read as installed the next time somebody looked.
"""
from backend.features.producers.domain.producers import NAMES


class Busy(Exception):
    """An install is already running (message is user-facing)."""


NEEDS_NOTEBOOK = ("{name} uygulamadan indirilemiyor — bu dosyayı defterin kurulum hücresi kurar.")


def install_producer(groups, files, fetcher, runner, kind):
    missing = [f for f in groups.get(kind, []) if not files.exists(f["folder"], f["name"])]

    def job():
        for spec in missing:
            if spec["url"] is None:
                return {"status": "error", "error": NEEDS_NOTEBOOK.format(name=spec["name"])}
            runner.report({"file": spec["name"], "done": 0, "total": None})
            fetcher.fetch(spec["url"], files.path(spec["folder"], spec["name"]),
                          on_progress=lambda done, total: runner.report({"done": done,
                                                                         "total": total}),
                          cancelled=runner.cancelled)
        return {"status": "done"}

    if not runner.start(kind, job):
        raise Busy(f"{NAMES[kind]} zaten kuruluyor.")
```

`cancel_install.py`:

```python
"""Ask the running install to stop. What it leaves behind is the fetcher's to clean."""


def cancel_install(runner):
    runner.request_cancel()
```

`routes.py`:

```python
    @bp.post("/api/producers/<kind>/install")
    def install(kind):
        try:
            install_producer(kind)
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify({"install": "running"}), 202

    @bp.post("/api/producers/<kind>/install/cancel")
    def cancel(kind):
        cancel_install()
        return "", 204
```

`GET /api/producers` koşan kurulumu da yayınlar: `list_producers()` çağrısı `running` olarak
`install_status()`'ü alır (composition root'ta bağlanır).

- [ ] **Adım 4: Koş, yeşili gör**

---

### Görev 4: Panel kurar, iptal eder, ilerlemeyi gösterir

**Dosyalar:**
- Değiştir: `frontend/src/shared/api.js`, `features/producers/useProducers.js`,
  `features/producers/ProducersPanel.jsx` (+ testi)
- Oluştur: `features/producers/InstallCard.jsx` (+ testi)

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

`ProducersPanel.test.jsx`'e:

```jsx
  it("asks before it starts a long download", () => {
    const onInstall = vi.fn();
    render(<ProducersPanel producers={THREE} error={null} onInstall={onInstall}
                           onCancel={() => {}} />);

    fireEvent.click(screen.getAllByText("Kur")[0]);

    expect(screen.getByText("Video üreticisi kurulsun mu?")).toBeTruthy();
    expect(onInstall).not.toHaveBeenCalled();

    fireEvent.click(screen.getByText("Kur", { selector: ".wf-btn--hl" }));
    expect(onInstall).toHaveBeenCalledWith("video");
  });

  it("shows how far the running install has got, and offers a way out", () => {
    const rows = THREE.map((p) => (p.id === "video"
      ? { ...p, installing: { done: 5, total: 10, file: "wan.safetensors" } }
      : p));
    render(<ProducersPanel producers={rows} error={null} onInstall={() => {}}
                           onCancel={() => {}} />);

    expect(screen.getByText("kuruluyor… bitince bu kart kaybolur")).toBeTruthy();
    expect(screen.getByText("İptal")).toBeTruthy();
  });

  it("asks before it throws away what has come down so far", () => {
    const onCancel = vi.fn();
    const rows = THREE.map((p) => (p.id === "video"
      ? { ...p, installing: { done: 5, total: 10, file: "wan.safetensors" } }
      : p));
    render(<ProducersPanel producers={rows} error={null} onInstall={() => {}}
                           onCancel={onCancel} />);

    fireEvent.click(screen.getByText("İptal"));

    expect(screen.getByText("Kurulum iptal edilsin mi?")).toBeTruthy();
  });
```

`InstallCard.test.jsx`:

```jsx
  it("names the producer and offers a Kur that asks nothing", () => {
    const onInstall = vi.fn();
    render(<InstallCard producer={{ id: "video", name: "Video üreticisi", installed: false }}
                        onInstall={onInstall} />);

    expect(screen.getByText("Video üreticisi kurulu değil.")).toBeTruthy();
    fireEvent.click(screen.getByText("Kur"));

    expect(onInstall).toHaveBeenCalledWith("video");
  });

  it("turns into progress while the download runs", () => {
    render(<InstallCard producer={{ id: "video", name: "Video üreticisi", installed: false,
                                    installing: { done: 5, total: 10, file: "wan" } }}
                        onInstall={() => {}} />);

    expect(screen.getByText("kuruluyor… bitince bu kart kaybolur")).toBeTruthy();
    expect(screen.queryByText("Kur")).toBeNull();
  });

  it("is nothing at all once the producer is installed", () => {
    const { container } = render(
      <InstallCard producer={{ id: "photo", name: "Fotoğraf üreticisi", installed: true }}
                   onInstall={() => {}} />);

    expect(container.firstChild).toBeNull();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

- [ ] **Adım 3: Yaz**

`api.js`: `installProducer(kind)` ve `cancelInstall(kind)`.

`useProducers.js`: kurulum sürerken 2 saniyede bir yoklar (üretim durumunun yoklandığı gibi) ve
`install(kind)` / `cancel(kind)` eylemlerini döndürür.

`InstallCard.jsx`: kurulu üreticide `null`; kurulu değilse mor çerçeveli kart + "Kur"; kurulum
sürerken çubuk + canlı nokta + "kuruluyor… bitince bu kart kaybolur".

`ProducersPanel.jsx`: satırın Kur'u `ConfirmModal` açar; kurulum sürerken çubuk ve ghost kırmızı
İptal, o da `ConfirmModal` açar.

- [ ] **Adım 4: Koş, yeşili gör**

---

### Görev 5: Üretim paneli ve şerit noktası

**Dosyalar:**
- Değiştir: `features/photo_generation/GeneratePanel.jsx` (+ testi),
  `features/photo_generation/SidePanel.jsx` (+ testi), `ProjectScreen.jsx`

- [ ] **Adım 1: Testleri yaz (kırmızı test)**

```jsx
  it("holds the queue button while the producer is missing", () => {
    renderPanel({ producer: { id: "photo", name: "Fotoğraf üreticisi", installed: false } });

    expect(screen.getByText("Fotoğraf üreticisi kurulu değil.")).toBeTruthy();
    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
  });
```

```jsx
  it("marks the rail while something is being installed", () => {
    renderColumn({ producers: { producers: [
      { id: "video", name: "Video üreticisi", installed: false,
        installing: { done: 1, total: 2, file: "x" } }], error: null } });

    expect(screen.getByLabelText("Üreticiler").querySelector(".qe-dot--alive")).toBeTruthy();
  });
```

- [ ] **Adım 2: Koş, kırmızıyı gör**

- [ ] **Adım 3: Yaz**

`GeneratePanel` `producer` prop'u alır, en üste `<InstallCard>` çizer ve
`disabled={… || (producer && !producer.installed)}` ekler. `ProjectScreen` foto satırını seçip
geçirir. `SidePanel` şerit düğmesine, herhangi bir üretici kuruluyorsa canlı nokta koyar.

- [ ] **Adım 4: Koş, yeşili gör**

---

### Görev 6: Kapanış

- [ ] İki takımı koş · derle · tek commit.

```bash
git add -A
git commit -F - <<'MSG'
feat(queen-editor): a producer can be installed from inside the app

Görev 11 asked which producers are here; this answers the follow-up nobody
could act on. A producer is its model group, so installing one is fetching the
files it is missing -- and the app now does that itself, in the background,
with a bar that counts bytes rather than files.

Two Kur buttons, on purpose. The one in the producers panel starts a long piece
of maintenance and says so first; the one inside a generation panel is the only
thing between the user and what they already asked for, so it asks nothing.

A file that needs credentials is not fetched and not faked: the run stops and
the card says the notebook installs that one. A group half installed in silence
would read as installed the next time anybody looked.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
MSG
```

## Öz denetim

**1. Spec kapsaması:** Karar 1 → Görev 1; karar 2 (token'lı dosya) → Görev 3'ün üçüncü testi;
karar 3 (tek ve arka planda) → Görev 3'ün ikinci testi ve kendi runner'ı; karar 4 (bayt) → Görev
2'nin ilerleme testleri; karar 5 (iki Kur) → Görev 4 ve 5; karar 6 (bitince açılır) → Görev 4'ün
yoklaması ve Görev 5'in pasiflik testi.

**2. Yer tutucu taraması:** Görev 3'ün `runner.py`'si "foto koşucusunun kopyası" diye anılıyor —
tarif değil talimat: dosya birebir kopyalanıp adları çevrilir.

**3. Tür tutarlılığı:** `installing` her yerde `{done, total, file}`; `kind` her yerde
`photo`/`video`/`audio`; `fetch(url, path, on_progress, cancelled)` imzası servis, senaryo ve
sahtelerde aynı.
