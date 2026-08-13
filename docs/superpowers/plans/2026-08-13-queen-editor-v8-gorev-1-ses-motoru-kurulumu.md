# v8 · Görev 1 — Ses motoru gerektiğinde kurulsun (uygulama planı)

> **Ajanlara:** bu plan adım adım uygulanır; her adım kendi testiyle başlar (full TDD).

**Spec:** [2026-08-13-queen-editor-v8-gorev-1-ses-motoru-kurulumu-design.md](../specs/2026-08-13-queen-editor-v8-gorev-1-ses-motoru-kurulumu-design.md)
**Amaç:** MMAudio kütüphanesi defterde değil, Üreticiler panelindeki "Kur"da kurulsun; panelin
"kurulu" cevabı onu saysın.

**Komutlar:** `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend -- --run`
· `npm run build --prefix queen-editor/frontend`

## Global kısıtlar

- Katman yönü `presentation → domain ← data → services`; somut sınıf yalnız `backend/main.py`'de
  bağlanır ([CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)).
- Kod, yorum, docstring ve test adları **İngilizce**; kullanıcıya görünen metin **Türkçe**.
- Hata mesajı aracın kendi çıktısını taşır; sebep uydurulmaz.
- Ön yüz değişirse `dist/` aynı commit'te yeniden derlenir.
- Görev tek commit; commit mesajında çift tırnak yok.

## Adım 1 — Kütüphane tablosu ve portu

**Dosyalar:** `backend/features/producers/domain/model_groups.py` (değişir),
`backend/features/producers/domain/ports.py` (yeni), `backend/tests/test_producers.py` (değişir)

- [ ] **1.1 Kırmızı test yaz** — `test_producers.py`'nin sonuna:

```python
def test_the_sound_producer_declares_the_engine_it_runs_in_this_process():
    rows = model_groups.LIBRARIES["audio"]

    assert len(rows) == 1, "Ses motoru tek kütüphane"
    assert rows[0]["module"] == "mmaudio"
    assert "hkchengrex/MMAudio" in rows[0]["repo"]


def test_the_graph_producers_need_no_library_of_their_own():
    """Photo and video run in ComfyUI, which the notebook still installs."""
    assert set(model_groups.LIBRARIES) == {"audio"}
```

- [ ] **1.2 Koş, kırmızıyı gör** — `python -m pytest queen-editor -q -k declares`
      Beklenen: `AttributeError: module ... has no attribute 'LIBRARIES'`

- [ ] **1.3 `LIBRARIES`'i yaz** — `model_groups.py`'de `GROUPS`'un altına:

```python
# Code the producer needs inside THIS process, as opposed to a model file on disk. Only sound has
# one: photo and video run in ComfyUI, which the notebook installs. The clone folder and the module
# are both named because they answer different questions -- where the source sits, and what the
# process imports.
LIBRARIES = {
    "audio": [{"module": "mmaudio", "name": "MMAudio kütüphanesi", "folder": "MMAudio",
               "repo": "https://github.com/hkchengrex/MMAudio.git"}],
}
```

- [ ] **1.4 Portu yaz** — yeni `backend/features/producers/domain/ports.py`:

```python
"""What this feature needs from the outside world, stated by the side that uses it.

Model files have their own port already (`ModelFiles`, implemented over ComfyUI's folder tree). A
library is the second kind of thing a producer can need: code that has to be inside this process
rather than a file on disk, which is why "is it here" is a different question with a different
answer.
"""
from typing import Protocol


class Libraries(Protocol):
    def present(self, module: str) -> bool:
        """Can this process import `module`? Asked on every panel poll, so it stays cheap and
        never runs the module."""

    def install(self, repo: str, folder: str, module: str) -> None:
        """Fetch the library and install it. Raises with the tool's own output on failure --
        the message is user-facing."""
```

- [ ] **1.5 Koş, yeşil** — `python -m pytest queen-editor -q -k "declares or graph_producers"`

## Adım 2 — Kurulum önce kütüphaneyi geçer

**Dosyalar:** `backend/features/producers/domain/usecases/install_producer.py`,
`backend/tests/test_producers.py`

- [ ] **2.1 Sahteleri hazırla** — `test_producers.py`'de `FakeFetcher`'a ortak günlük ekle ve
      `FakeLibs` ile `SpyRunner`'ı ekle:

```python
class FakeFetcher:
    def __init__(self, fail=None, log=None):
        self.fetched = []
        self.fail = fail
        self.headers = None
        self.log = log if log is not None else []

    def fetch(self, url, path, headers=None, on_progress=None, cancelled=None):
        if self.fail and url == self.fail:
            raise RuntimeError("bağlantı yok")
        self.fetched.append((url, path))
        self.log.append(f"file:{url}")
        self.headers = headers
        if on_progress:
            on_progress(10, 10)


class FakeLibs:
    """A library port that remembers what it was asked to do.

    `stays_missing` is the case the restart sentence exists for: the install succeeded but this
    process still cannot see the module.
    """

    def __init__(self, present=(), fail=None, stays_missing=(), log=None):
        self.have = set(present)
        self.installed = []
        self.fail = fail
        self.stays_missing = set(stays_missing)
        self.log = log if log is not None else []

    def present(self, module):
        return module in self.have

    def install(self, repo, folder, module):
        self.installed.append(module)
        self.log.append(f"lib:{module}")
        if self.fail == module:
            raise RuntimeError("pip: exit 1")
        if module not in self.stays_missing:
            self.have.add(module)


class SpyRunner:
    """Runs the job inline and keeps every progress report, so the order the screen sees is
    assertable -- the real runner only keeps the last one."""

    def __init__(self):
        self.reports = []
        self.state = {"status": "idle"}

    def start(self, kind, job):
        self.state = {"status": "running", "kind": kind}
        self.state = {**job(), "kind": kind}
        return True

    def report(self, patch):
        self.reports.append(patch)

    def cancelled(self):
        return False


LIBS = {"audio": [{"module": "mmaudio", "name": "MMAudio kütüphanesi", "folder": "MMAudio",
                   "repo": "https://github.com/hkchengrex/MMAudio.git"}]}
```

- [ ] **2.2 Kırmızı testleri yaz**:

```python
def test_the_library_is_installed_before_the_weights():
    steps = []
    libs = FakeLibs(log=steps)

    install_producer(GROUPS, FakeFiles(), FakeFetcher(log=steps), sync_installer(), {}, "audio",
                     libraries=LIBS, lib=libs)

    assert steps == ["lib:mmaudio", "file:u4"]


def test_a_library_that_is_already_here_is_not_installed_again():
    libs = FakeLibs(present=["mmaudio"])

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), sync_installer(), {}, "audio",
                     libraries=LIBS, lib=libs)

    assert libs.installed == []


def test_a_failed_library_install_stops_before_the_weights():
    runner, fetcher = sync_installer(), FakeFetcher()

    install_producer(GROUPS, FakeFiles(), fetcher, runner, {}, "audio",
                     libraries=LIBS, lib=FakeLibs(fail="mmaudio"))

    assert fetcher.fetched == []
    assert runner.status()["status"] == "error"
    assert "pip: exit 1" in runner.status()["error"]


def test_a_library_this_process_still_cannot_see_asks_for_a_restart():
    runner, fetcher = sync_installer(), FakeFetcher()

    install_producer(GROUPS, FakeFiles(), fetcher, runner, {}, "audio",
                     libraries=LIBS, lib=FakeLibs(stays_missing=["mmaudio"]))

    assert fetcher.fetched == []
    assert "yeniden başlat" in runner.status()["error"]


def test_the_library_step_is_named_before_it_starts():
    runner = SpyRunner()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "audio",
                     libraries=LIBS, lib=FakeLibs())

    assert runner.reports[0]["step"] == "MMAudio kütüphanesi"


def test_a_producer_with_neither_a_file_nor_a_library_cannot_be_installed():
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "photo",
                     libraries=LIBS, lib=FakeLibs())

    assert runner.status()["status"] == "error"
    assert "Fotoğraf üreticisi" in runner.status()["error"]
```

Ayrıca mevcut `test_the_running_install_is_reported_on_its_own_row` içindeki `"file"` anahtarını
`"step"` yap (hem `running=` sözlüğünde hem beklenen `installing` değerinde).

- [ ] **2.3 Koş, kırmızıyı gör** — `python -m pytest queen-editor -q -k library`
      Beklenen: `TypeError: install_producer() got an unexpected keyword argument 'libraries'`

- [ ] **2.4 `install_producer`'ı yaz**:

```python
# A library that installed but is still invisible here: pip put it on disk, this process did not
# pick it up. Named rather than swallowed -- the weights would land next and the panel would call
# the producer installed while no sound job could run.
NO_IMPORT = "{name} kuruldu ama bu süreçte görünmüyor — uygulamayı yeniden başlat."


def install_producer(groups, files, fetcher, runner, auth, kind, libraries=None, lib=None):
    group = groups.get(kind) or []
    libs = (libraries or {}).get(kind) or []
    missing = [spec for spec in group if not files.exists(spec["folder"], spec["name"])]
    auth = auth or {}

    def job():
        if not group and not libs:
            return {"status": "error", "error": NO_FILES.format(name=NAMES[kind])}
        # Libraries first: one is what makes the producer usable at all, and its failure is worth
        # seeing before minutes of downloading.
        for spec in libs:
            if lib.present(spec["module"]):
                continue
            runner.report({"step": spec["name"]})
            lib.install(spec["repo"], spec["folder"], spec["module"])
            if not lib.present(spec["module"]):
                return {"status": "error", "error": NO_IMPORT.format(name=spec["name"])}
        for spec in missing:
            ...   # unchanged, except the report's key:
            runner.report({"step": spec["name"], "done": 0, "total": None})
```

- [ ] **2.5 Koş, yeşil** — `python -m pytest queen-editor/backend/tests/test_producers.py -q`

## Adım 3 — "Kurulu mu" kütüphaneyi sayar

**Dosyalar:** `backend/features/producers/domain/usecases/list_producers.py`,
`backend/tests/test_producers.py`

- [ ] **3.1 Kırmızı test yaz**:

```python
def test_a_producer_whose_library_is_missing_is_not_installed():
    """The one case the panel used to lie about: the weights are here, the engine is not."""
    files = FakeFiles(present=[("mmaudio", "mm.pth")])

    rows = list_producers(GROUPS, files, libraries=LIBS, lib=FakeLibs())

    assert rows[2]["installed"] is False


def test_it_is_installed_when_both_the_library_and_the_weights_are_here():
    files = FakeFiles(present=[("mmaudio", "mm.pth")])

    rows = list_producers(GROUPS, files, libraries=LIBS, lib=FakeLibs(present=["mmaudio"]))

    assert rows[2]["installed"] is True
```

- [ ] **3.2 Koş, kırmızıyı gör** — `TypeError: unexpected keyword argument 'libraries'`

- [ ] **3.3 `list_producers`'ı yaz**:

```python
def list_producers(groups, files, running=None, libraries=None, lib=None):
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        libs = (libraries or {}).get(kind) or []
        installed = bool(group or libs) and all(
            files.exists(spec["folder"], spec["name"]) for spec in group) and all(
            lib.present(spec["module"]) for spec in libs)
        ...
                row["installing"] = {"step": running.get("step")}
```

Docstring'i de düzelt: kurulu olmak artık "declared model group is on this machine" değil,
"her dosyası diskte ve her kütüphanesi bu süreçte".

- [ ] **3.4 Koş, tam takım yeşil** — `python -m pytest queen-editor -q`

## Adım 4 — Gerçekten kuran sınıf ve bağlama

**Dosyalar:** `backend/features/producers/data/pip_libraries.py` (yeni), `backend/config.py`,
`backend/main.py`

- [ ] **4.1 `PipLibraries`'i yaz** — testi yok (dış dünya, spec'te yazılı):

```python
"""git + pip -- the notebook's own way of installing MMAudio, moved into the app.

No tests, like the ComfyUI client and the ffmpeg exporter: a fake subprocess would only be testing
the fake. Every decision above it (order, skipping, stopping, what the screen says) is domain and
is covered there.

The method is copied rather than improved: clone shallow, `pip install -e .`, then import it in a
separate process to prove the install. `-e` keeps the package where it was cloned, so updating it
is a `git pull`.
"""
import importlib.util
import os
import subprocess
import sys


class PipLibraries:
    def __init__(self, root):
        self._root = root

    def present(self, module):
        # No invalidate_caches() here: this is asked on every panel poll, and dropping the import
        # system's caches that often taxes every later import. The install does it once, right
        # after pip has written the package.
        return importlib.util.find_spec(module) is not None

    def install(self, repo, folder, module):
        path = os.path.join(self._root, folder)
        if not os.path.isdir(path) or not os.listdir(path):
            _run(["git", "clone", "--depth", "1", repo, path], timeout=180)
        _run([sys.executable, "-m", "pip", "install", "-q", "-e", "."], cwd=path, timeout=900)
        # A package written after this process started is invisible until the finders drop their
        # cached directory listings.
        importlib.invalidate_caches()
        # The notebook's fail-loud import, kept: a broken dependency says so now, in the tool's own
        # words, rather than forty minutes later inside a render. Its own process, so a half-loaded
        # module cannot poison this one.
        _run([sys.executable, "-c", f"import {module}"], timeout=600)


def _run(cmd, cwd=None, timeout=900):
    """Run it; a non-zero exit or a timeout raises with the command's own last lines."""
    try:
        done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{' '.join(cmd)}: timeout ({timeout}s)")
    if done.returncode != 0:
        tail = "\n".join((done.stderr or done.stdout or "").strip().splitlines()[-5:])
        raise RuntimeError(f"{' '.join(cmd)}: exit {done.returncode}\n{tail}")
```

- [ ] **4.2 `config.py`** — `COMFY_ROOT`'un altına:

```python
# Where a producer's library is cloned and installed from. Derived from the ComfyUI root rather
# than given its own setting: on Colab that is /content, which is where the notebook used to clone
# MMAudio, and a machine that moves one moves the other.
LIB_ROOT = os.path.dirname(COMFY_ROOT)
```

- [ ] **4.3 `main.py`** — `PipLibraries` ve `LIBRARIES`'i içe aktar, `_libraries` kur, iki
      kullanıma da `libraries=LIBRARIES, lib=_libraries` geçir.

- [ ] **4.4 Koş** — `python -m pytest queen-editor -q` (bağlama testleri de yeşil kalmalı)

## Adım 5 — Ekran adımı söyler

**Dosyalar:** `frontend/src/features/producers/InstallCard.jsx`, `ProducersPanel.jsx`,
`useProducers.js` ve üçünün testleri; gerekiyorsa `photo_generation/SidePanel.test.jsx` fixture'ı

- [ ] **5.1 Testleri `step`'e çevir** — `InstallCard.test.jsx` içindeki iki
      `installing: { file: "wan.safetensors" }` → `installing: { step: "wan.safetensors" }`,
      `ProducersPanel.test.jsx` içindeki bir tane, ve yeni bir test:

```jsx
  it("names the step, so a library install is not mistaken for a file", () => {
    render(<InstallCard producer={{ ...MISSING, installing: { step: "MMAudio kütüphanesi" } }}
                        onInstall={() => {}} />);

    expect(screen.getByText("kuruluyor… MMAudio kütüphanesi")).toBeTruthy();
  });
```

- [ ] **5.2 Koş, kırmızıyı gör** — `npm test --prefix queen-editor/frontend -- --run`

- [ ] **5.3 Bileşenleri çevir** — `Running({ step })`, iki çağrı yeri
      `<Running step={producer.installing.step} />`, `useProducers`'ın iyimser satırı
      `said(kind, { step: null })`. `Running`'in docstring'i de dosya değil **adım** demeli.

- [ ] **5.4 Koş, yeşil** — `npm test --prefix queen-editor/frontend -- --run`

- [ ] **5.5 Derle** — `npm run build --prefix queen-editor/frontend`

## Adım 6 — Kapanış

- [ ] **6.1 İki takımı da koş** — `python -m pytest queen-editor -q` ve
      `npm test --prefix queen-editor/frontend -- --run`
- [ ] **6.2 Commit** — kod + testler + `dist/` + spec + plan, tek commit'te.

## Kendi kontrolüm

- Spec'in her kararı bir adımda: tablo (1), sıra ve durma (2), kurulu mu (3), gerçek kurulum ve
  bağlama (4), ekran (5). ✓
- `install_producer`'ın imzasında `kind` altıncı sırada kaldı, `libraries`/`lib` ondan sonra —
  `main.py`'nin `partial(...)` + rota `install_producer(kind)` zinciri kırılmıyor, mevcut testlerin
  hepsi olduğu gibi geçiyor. ✓
- `step` adı üç yerde birden değişiyor (use case, list_producers, ön yüz) — birini unutmak paneli
  boş "kuruluyor…" bırakır, o yüzden 2.2'deki mevcut testin güncellenmesi listede. ✓
