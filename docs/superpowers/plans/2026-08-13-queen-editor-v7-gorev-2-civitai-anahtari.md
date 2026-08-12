# Görev 2 — Civitai anahtarı uygulamaya geçsin (uygulama planı)

**Spec:** [Görev 2](../specs/2026-08-13-queen-editor-v7-gorev-2-civitai-anahtari-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

**Amaç:** Kurulum ekranı Civitai'deki dört SmoothMix dosyasını kendi indirsin; anahtar defterin
Colab Secret'ından ortam değişkeniyle gelsin.

**Yaklaşım:** İçeriden dışarı — önce indirici başlık taşısın, sonra model listesi hangi satırın
kimlik istediğini söylesin, sonra kurulum ikisini birleştirsin, en sonda bileşim kökü ve defter.

## Global kısıtlar

- Kod, yorum, docstring ve test adları **İngilizce**; kullanıcıya görünen metin Türkçe.
- Servis hiçbir üretici/model tanımaz: indirici yalnız verilen başlığı gönderir.
- Sır domain'e girmez: satır kaynağın **adını** taşır, değeri `main.py` verir.
- Ön yüz değişmiyor → `npm run build` gerekmez.
- Görev sonunda **tek commit**.

## Dosyalar

- **Değiştir:** `queen-editor/backend/services/download/fetcher.py`
- **Değiştir:** `queen-editor/backend/tests/test_fetcher.py`
- **Değiştir:** `queen-editor/backend/features/producers/domain/model_groups.py`
- **Değiştir:** `queen-editor/backend/features/producers/domain/usecases/install_producer.py`
- **Değiştir:** `queen-editor/backend/tests/test_producers.py`
- **Değiştir:** `queen-editor/backend/config.py`
- **Değiştir:** `queen-editor/backend/main.py`
- **Değiştir:** `queen-editor/app.ipynb`

---

### Adım 1 — İndiricinin başlık testlerini yaz

`test_fetcher.py` içinde `opener` yardımcısını başlığı yakalayacak hale getir ve iki test ekle:

```python
def opener(response, seen=None):
    def open_url(url, headers):
        if seen is not None:
            seen.append(headers)
        return response
    return open_url


def test_it_sends_the_headers_it_was_given(tmp_path):
    seen = []
    fetcher = HttpFetcher(opener(FakeResponse([b"ab"]), seen))

    fetcher.fetch("http://x", str(tmp_path / "m"), headers={"Cookie": "k=v"})

    assert seen == [{"Cookie": "k=v"}]


def test_no_headers_means_none_are_added(tmp_path):
    seen = []
    fetcher = HttpFetcher(opener(FakeResponse([b"ab"]), seen))

    fetcher.fetch("http://x", str(tmp_path / "m"))

    assert seen == [{}]


def test_a_page_is_not_written_under_a_models_name(tmp_path):
    # A gated file can come back as a sign-in page: 200, HTML, a couple of kilobytes. Writing that
    # as the model would leave something that looks installed for good.
    page = FakeResponse([b"<html>"])
    page.headers = {"Content-Type": "text/html; charset=utf-8"}
    target = tmp_path / "model.safetensors"

    with pytest.raises(RuntimeError) as exc:
        HttpFetcher(opener(page)).fetch("http://x", str(target))

    assert "text/html" in str(exc.value)
    assert not target.exists() and not (tmp_path / "model.safetensors.part").exists()
```

### Adım 2 — Koş, kırmızı olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **FAIL** — mevcut `_open` tek argüman alıyor, HTML kontrolü de yok.

### Adım 3 — İndirici başlık taşısın ve sayfayı reddetsin

`fetcher.py`:

```python
def _open(url, headers):
    return _Streamed(urllib.request.urlopen(urllib.request.Request(url, headers=headers)))
```

```python
    def fetch(self, url, path, headers=None, on_progress=None, cancelled=None):
        """`headers` is sent as given. What they are and why is the caller's business: a service
        knows no producer, no model and no source."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        partial = f"{path}.part"
        done = 0
        try:
            with self._open(url, headers or {}) as response:
                self._refuse_a_page(response)
                total = self._length(response)
```

ve sınıfa:

```python
    @staticmethod
    def _refuse_a_page(response):
        """A file is expected; a page is not one. Reported with the server's own words rather than
        a guess at why it answered that way."""
        kind = (response.headers.get("Content-Type") or "").lower()
        if kind.startswith("text/html"):
            raise RuntimeError(f"İndirme dosya yerine sayfa döndü (Content-Type: {kind})")
```

### Adım 4 — Koş, indirici testleri yeşil olsun

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: indirici testleri **PASS**; başka bir şey kırılmamalı.

### Adım 5 — Model listesinin testlerini yaz

`test_producers.py` sonuna:

```python
def test_the_video_group_has_nothing_the_app_cannot_fetch():
    assert all(row["url"] for row in model_groups.GROUPS["video"])


def test_every_gated_row_says_which_source_it_needs():
    gated = [row for row in model_groups.GROUPS["video"] if row.get("auth")]

    assert len(gated) == 4                                   # the two SmoothMix pairs
    assert all(row["auth"] == model_groups.CIVITAI for row in gated)
    assert all(row["url"].startswith(model_groups.CIVITAI_DOWNLOAD) for row in gated)


def test_the_civitai_header_carries_the_cookie_under_its_own_name():
    assert model_groups.civitai_headers("abc") == {"Cookie": "__Secure-civ-token=abc"}
```

### Adım 6 — Koş, kırmızı olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **FAIL** — `CIVITAI` yok, dört satırın `url`'i hâlâ `None`.

### Adım 7 — Model listesi kaynağı tanısın

`model_groups.py` başına:

```python
# Civitai serves gated files by model version id, behind a login cookie. The address and the
# cookie's name live together: if the source changes, one file changes.
CIVITAI = "civitai"
CIVITAI_DOWNLOAD = "https://civitai.red/api/download/models"
CIVITAI_COOKIE_NAME = "__Secure-civ-token"


def civitai_headers(cookie):
    """What a Civitai download must carry. This file knows the cookie's name, never its value --
    the secret is the composition root's to supply."""
    return {"Cookie": f"{CIVITAI_COOKIE_NAME}={cookie}"}
```

Dört satır (yorumuyla birlikte):

```python
        # SmoothMix comes from Civitai behind a login cookie. The graph loads it twice over: the
        # checkpoint pair as diffusion models, and the Animations pair as loras the Power Lora
        # Loader has switched on.
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_High.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2513182", "auth": CIVITAI},
        {"folder": "diffusion_models", "name": "SmoothMix_I2V_v2_Low.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2513186", "auth": CIVITAI},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_High.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2376136", "auth": CIVITAI},
        {"folder": "loras", "name": "SmoothMix_Animations_XXX_Low.safetensors",
         "url": f"{CIVITAI_DOWNLOAD}/2376143", "auth": CIVITAI},
```

Dosyanın başındaki modül docstring'inde `url: None` anlatan paragraf duruyor — foto grubu boş
kaldığı sürece doğru; dokunma.

### Adım 8 — Kurulumun testlerini yaz

`test_producers.py` içinde `FakeFetcher.fetch` başlığı da yakalasın:

```python
    def fetch(self, url, path, headers=None, on_progress=None, cancelled=None):
        if self.fail and url == self.fail:
            raise RuntimeError("bağlantı yok")
        self.fetched.append((url, path))
        self.headers = headers
        if on_progress:
            on_progress(10, 10)
```

`FakeFetcher.__init__`'e `self.headers = None` satırını da ekle.

Kimlik isteyen bir satır fixture'da yok; video grubunun bir kopyasına eklenerek yazılır — kurulum
`NAMES`'te karşılığı olan bir tür istiyor, uydurma bir grup adı kullanılamaz:

```python
def gated_groups():
    """The shipped video group's shape: one row that needs a source's key."""
    return {**GROUPS, "video": GROUPS["video"] + [
        {"folder": "loras", "name": "smooth.safetensors", "url": "u3", "auth": "civitai"}]}


def test_a_gated_row_is_fetched_with_its_sources_headers():
    fetcher = FakeFetcher()

    install_producer(gated_groups(), FakeFiles(), fetcher, sync_installer(),
                     {"civitai": {"Cookie": "k=v"}}, "video")

    assert fetcher.headers == {"Cookie": "k=v"}


def test_a_gated_row_with_no_key_stops_the_install_and_names_the_source():
    runner = sync_installer()

    install_producer(gated_groups(), FakeFiles(), FakeFetcher(), runner, {}, "video")

    assert runner.status()["status"] == "error"
    assert "smooth.safetensors" in runner.status()["error"]
    assert "civitai" in runner.status()["error"]
```

Mevcut beş `install_producer(...)` çağrısına da `{}` argümanını ekle (satır 113, 120, 123, 129,
138).

### Adım 9 — Koş, kırmızı olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **FAIL** — `install_producer` beşinci argümanı tanımıyor.

### Adım 10 — Kurulum kimliği taşısın

`install_producer.py`:

```python
NOTEBOOK_OWNS = "{name} uygulamadan indirilemiyor — bunu defterin kurulum hücresi kurar."
# A row whose source needs a key, on a machine that was given none. Named rather than skipped: a
# silently missing file reads as installed the next time anybody looks.
NO_KEY = "{name} indirilemiyor — {source} anahtarı yok."


def install_producer(groups, files, fetcher, runner, auth, kind):
    group = groups.get(kind) or []
    missing = [spec for spec in group if not files.exists(spec["folder"], spec["name"])]
    auth = auth or {}

    def job():
        if not group:
            return {"status": "error", "error": NOTEBOOK_OWNS.format(name=NAMES[kind])}
        for spec in missing:
            if spec["url"] is None:
                return {"status": "error", "error": NOTEBOOK_OWNS.format(name=spec["name"])}
            source = spec.get("auth")
            if source and source not in auth:
                return {"status": "error",
                        "error": NO_KEY.format(name=spec["name"], source=source)}
            # Named before the bytes start so the card has something to say from the first tick.
            runner.report({"file": spec["name"], "done": 0, "total": None})
            fetcher.fetch(
                spec["url"], files.path(spec["folder"], spec["name"]),
                headers=auth.get(source),
                on_progress=lambda done, total: runner.report({"done": done, "total": total}),
                cancelled=runner.cancelled)
        return {"status": "done"}

    if not runner.start(kind, job):
        raise Busy(f"{NAMES[kind]} zaten kuruluyor.")
```

Docstring'in ikinci cümlesi de yeni gerçeği söylesin: kimliksiz indirilemeyen dosya **ve** anahtarı
verilmemiş kaynak, koşuyu durdurur.

### Adım 11 — Koş, yeşil olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **PASS**.

### Adım 12 — Ayar ve bileşim kökü

`config.py`, `XAI_API_KEY`'in hemen üstüne ya da altına:

```python
# Civitai's login cookie: the gated model files are behind it. Comes from Colab Secrets through the
# notebook, like the xAI key; empty means those installs stop and say which source they wanted.
CIVITAI_COOKIE = os.environ.get("QE_CIVITAI_COOKIE", "")
```

`main.py`:

```python
from backend.features.producers.domain.model_groups import (
    CIVITAI,
    GROUPS,
    audio_weights,
    civitai_headers,
)
```

```python
_fetcher = HttpFetcher()
_install_runner = InstallRunner()
# The keys the installer may need, by source. Built here because this is the only layer a secret
# belongs in; an empty map is a real answer -- the install stops at a gated row and says so.
_auth = {CIVITAI: civitai_headers(config.CIVITAI_COOKIE)} if config.CIVITAI_COOKIE else {}
_producers_bp = make_producers_blueprint(
    list_producers=lambda: list_producers(GROUPS, _model_files, _producers,
                                          running=_install_runner.status()),
    install_producer=partial(install_producer, GROUPS, _model_files, _fetcher, _install_runner,
                             _auth),
    cancel_install=partial(cancel_install, _install_runner),
)
```

### Adım 13 — Defter anahtarı sürece geçirsin

`app.ipynb`, Flask'ı başlatan hücrede `flask_env`:

```python
flask_env = {**os.environ, "QE_DRIVE_ROOT": DRIVE_ROOT, "QE_COMFY_URL": COMFYUI_URL,
             "QE_XAI_API_KEY": XAI_API_KEY or "",
             "QE_CIVITAI_COOKIE": COOKIE_VALUE or ""}
```

Üstündeki yorum "üçü de" diyorsa dördü olarak düzelt.

### Adım 14 — Tam takım

Çalıştır: `python -m pytest queen-editor -q` ve
`npm test --prefix queen-editor/frontend -- --run`

Beklenen: ikisi de **PASS**.

### Adım 15 — Commit

```bash
git add queen-editor docs/superpowers
git commit -m "feat(queen-editor): the app downloads what the key opens"
```
