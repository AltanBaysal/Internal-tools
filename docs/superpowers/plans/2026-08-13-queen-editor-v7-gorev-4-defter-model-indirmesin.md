# Görev 4 — Defter model indirmeyi bıraksın (uygulama planı)

**Spec:** [Görev 4](../specs/2026-08-13-queen-editor-v7-gorev-4-defter-model-indirmesin-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 2

**Amaç:** Defterin model indirme işi tamamen kalksın; "bunu defter kurar" diyen her cümle ve her
kod parçası gitsin; iki yaşayan belge yeni gerçeği anlatsın.

## Global kısıtlar

- Kod, yorum, docstring ve test adları **İngilizce**; defterin markdown/print metni Türkçe.
- Ön yüz değişmiyor → `npm run build` gerekmez.
- Görev sonunda **tek commit**.

## Dosyalar

- **Oluştur:** `queen-editor/backend/tests/test_model_install_is_the_apps_job.py`
- **Değiştir:** `queen-editor/app.ipynb` (bir hücre silinir, dördü değişir)
- **Değiştir:** `queen-editor/backend/features/producers/domain/usecases/install_producer.py`
- **Değiştir:** `queen-editor/backend/features/producers/domain/model_groups.py`
- **Değiştir:** `queen-editor/backend/tests/test_producers.py`
- **Değiştir:** `queen-editor/FOUNDATION.md`
- **Değiştir:** `queen-editor/CODE-STANDARD.md`
- **Değiştir:** `queen-editor/README.md`

---

### Adım 1 — Testleri yaz

`queen-editor/backend/tests/test_model_install_is_the_apps_job.py`:

```python
"""Installing a model is the app's job; the notebook installs code only.

A leftover download cell is not a broken import -- it is a second way of installing the same
files, and the two only disagree when somebody is watching a fresh machine.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP_DIRS = {".git", "dist", "node_modules", "__pycache__"}
# This file names them on purpose; it is the one place they are allowed to appear.
SKIP_FILES = {os.path.basename(__file__)}
GONE = ("CIVITAI_MODELS", "OPEN_MODELS", "civitai_probe")


def _mentions():
    found = []
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name in SKIP_FILES or not name.endswith((".py", ".md", ".json", ".ipynb", ".jsx",
                                                        ".js", ".txt")):
                continue
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
            found += [(os.path.relpath(path, ROOT), word) for word in GONE if word in text]
    return found


def test_the_notebook_downloads_no_models():
    assert _mentions() == []
```

`test_producers.py` içinde iki testi yeni gerçeğe göre yaz:

```python
def test_a_producer_with_no_files_declared_cannot_be_installed():
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "photo")

    assert runner.status()["status"] == "error"
    assert "Fotoğraf üreticisi" in runner.status()["error"]
    assert "defter" not in runner.status()["error"]
```

ve `test_a_file_the_app_cannot_fetch_stops_the_install_and_says_why` ile fixture'daki
`"audio": [{... "url": None}]` satırını sil — o kavram kalkıyor. Fixture'ın ses grubu:

```python
    "audio": [{"folder": "mmaudio", "name": "mm.pth", "url": "u4"}],
```

### Adım 2 — Koş, kırmızı olduğunu gör

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **FAIL** — defter üç adı da taşıyor, hata metninde "defter" geçiyor.

### Adım 3 — Defterin model hücresini sil

`app.ipynb`, hücre `05c61d4d` (kod) tamamen silinir.

### Adım 4 — Model markdown'ı yerini bir nota bıraksın

`app.ipynb`, hücre `3ad9cb36`:

```markdown
## Modeller — burada inmez

Defter model indirmez: ComfyUI, custom node'lar ve MMAudio kütüphanesi kurulur, o kadar.
Modeller uygulama açıldıktan sonra **Üreticiler** panelinden kurulur — her üreticinin kendi
**Kur** düğmesi var, ve neyin kurulu olduğunu da orası söyler.

Civitai'den inen dosyalar için `CIVITAI_COOKIE` gerekiyor; defter onu uygulamaya geçiriyor.
```

### Adım 5 — Yalnız indirmeye hizmet eden yardımcılar gitsin

`app.ipynb`, hücre `df871d38`:

```python
# === Shared helpers — log + fail-loud run ===
# Used by the custom node and MMAudio cells; defined once (DRY).
import time, subprocess

# Neither cell below needs CONFIG (both install to hardcoded local paths, no Drive), so without
# this gate a failed CONFIG cell stays invisible until the app starts -- after a ~10 min install.
assert "COMFY_ROOT" in globals(), "❌ Önce 1) CONFIG hücresini çalıştır"

def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"{icons.get(level, '·')} [{time.strftime('%H:%M:%S')}] {msg}")

def run(cmd, label, cwd=None, timeout=3600):
    """Run a command; non-zero exit or timeout -> RuntimeError with the command's own stderr.

    The single gate for install failures: git and pip both exit non-zero and say why, and that
    sentence is what gets raised rather than a guess at what went wrong.
    """
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{label}: timeout ({timeout}s)")
    if r.returncode != 0:
        tail = "\n".join((r.stderr or r.stdout or "").strip().splitlines()[-5:])
        raise RuntimeError(f"{label}: exit {r.returncode}\n{tail}")
    return r.stdout

print("✓ Ortak yardımcılar hazır (log, run)")
```

### Adım 6 — Giriş metni ve CONFIG yorumu doğruyu söylesin

`app.ipynb`, hücre `34c9ff58`: kurulum zinciri "**ComfyUI'yi kurar** (19 custom node) →
**MMAudio** kütüphanesini kurar" olsun, "~7.5 GiB model" ifadesi kalksın, ve 3. adımdaki süre
"ilk kurulum ~5-10 dk (modeller uygulamadan kurulur)" olsun.

`app.ipynb`, hücre `8215086b`: GPU assert'inin üstündeki yorum artık indirmeden söz etmesin —
GPU olmadan ComfyUI kalkar ama her render düşer.

### Adım 7 — "Defter kurar" cümlesi ve `url: None` kavramı gitsin

`install_producer.py`:

```python
NO_FILES = "{name} için indirilecek dosya tanımlı değil."
# A row whose source wants a key, on a process that was given none. Named rather than skipped: a
# silently missing file reads as installed the next time anybody looks.
NO_KEY = "{name} indirilemiyor — {source} anahtarı yok."


def install_producer(groups, files, fetcher, runner, auth, kind):
    group = groups.get(kind) or []
    missing = [spec for spec in group if not files.exists(spec["folder"], spec["name"])]
    auth = auth or {}

    def job():
        if not group:
            return {"status": "error", "error": NO_FILES.format(name=NAMES[kind])}
        for spec in missing:
            source = spec.get("auth")
            if source and source not in auth:
                return {"status": "error",
                        "error": NO_KEY.format(name=spec["name"], source=source)}
            ...
```

Modül docstring'i: durduran iki şey kaldı — dosya listesi olmayan bir tür, ve anahtarı verilmemiş
bir kaynak.

`model_groups.py` docstring'i yine iki tür anlatsın (`url` olan, `url` + `auth` olan);
`url: None` maddesi kalkar.

### Adım 8 — İki yaşayan belge

`FOUNDATION.md`'ye 9. karar:

```markdown
**9. The app installs its own models; the notebook installs only code.**
The notebook brings up ComfyUI, its custom nodes and the sound library, and stops there: every
model file is installed from the app's own Üreticiler panel, per producer, after it opens. Why:
one place answers "is this producer ready?", and it is the same place that can fix the answer.
Two installers meant the notebook decided what was on disk while the panel reported it, and the
two only disagreed on a fresh machine, where nobody was looking. Consequence: a new machine opens
with nothing installed and that is the expected state, not a failure.
```

`CODE-STANDARD.md`, bağımsızlık tablosundaki kurulum hücreleri satırı:

| Inherited (knowledge) | Never (dependency) |
|---|---|
| Setup cells for **code** — custom nodes, headless ComfyUI — copied verbatim into `app.ipynb`, because that machinery is proven | Running or importing their cells, or reading a file they own. Model installation is inherited from nobody: it is the app's own, in the producers feature ([FOUNDATION 9](../../../queen-editor/FOUNDATION.md)) |

`README.md`: 3. adımdaki "downloads ~7.5 GiB of models (~10-15 min…)" cümlesi kalkar, yerine
kurulumun uygulamadan yapıldığı yazılır; 2. adımdaki çerez açıklamasında "model cell stops" yerine
kurulum ekranının söylediği yazılır.

### Adım 9 — Tam takım

Çalıştır: `python -m pytest queen-editor -q` ve
`npm test --prefix queen-editor/frontend -- --run`

Beklenen: ikisi de **PASS**.

### Adım 10 — Commit

```bash
git add queen-editor docs/superpowers
git commit -m "feat(queen-editor): the notebook installs code, the app installs models"
```
