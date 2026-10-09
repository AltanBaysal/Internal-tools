# Python bağımlılıkları dosyada durur · Tur 1 (test) — Plan

**Tasarım:** [2026-09-01-python-requirements-testler-design.md](../specs/2026-09-01-python-requirements-testler-design.md)
**Dal:** `feat/python-requirements` *(`main`'den)*
**Bu tur yalnız test dosyalarına dokunur.** `requirements.txt`'ler bu turda **değişmez** — değişse
kırmızı diye bir şey kalmazdı.
**Test komutları (değişmez, dördü de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `queen-agent/backend/tests/test_requirements.py` — yeni dosya, iki kırmızı.

```python
"""What the code needs to be installed is written where pip can read it.

Beside the backend's tests because `pytest queen-agent` collects them from here, but what it reads
is the repository's own manifest -- the same reason test_dist_is_committed.py and
test_frontend_toolchain.py live here.

The list is not written down twice. A test naming the packages would be a second copy of
requirements.txt, and the copy would drift; this one parses the source and asks whether the file
already says what the source needs.

Only module level imports count -- `tree.body`, nothing nested. An import inside a function says
"needed if this path is taken"; an import at the top says "nothing here runs without it", and only
the second belongs in a file whose job is to make a fresh checkout work. queen-editor leans on that
distinction: torch is imported inside MMAudioSampler.render, which is why its suite runs on a
machine with no GPU and no torch at all.
"""
import ast
import os
import sys

TOOL = os.path.dirname(          # queen-agent
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
BACKEND = os.path.join(TOOL, "backend")
REQUIREMENTS = os.path.join(BACKEND, "requirements.txt")

# The package this repo's own code lives under, which pip is never asked for.
LOCAL = {"backend"}


def _module_level_imports(path):
    """The top level names a file imports, and only those.

    Walks tree.body rather than ast.walk on purpose: a lazy import sits inside a FunctionDef and
    is deliberately not counted, and so is one guarded by try/except ImportError or TYPE_CHECKING.
    """
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def _needed():
    """Every third-party package the backend imports without being asked twice."""
    found = set()
    for folder, _, files in os.walk(BACKEND):
        for name in files:
            if name.endswith(".py"):
                found |= _module_level_imports(os.path.join(folder, name))
    return found - set(sys.stdlib_module_names) - LOCAL


def _declared():
    """The package names requirements.txt lists, without their version ranges."""
    with open(REQUIREMENTS, encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    return {
        line.split("#")[0].strip().split(">=")[0].split("==")[0].split("<")[0].strip().lower()
        for line in lines
        if not line.startswith("#")
    }


def test_the_tool_says_what_to_install():
    assert os.path.exists(REQUIREMENTS), (
        f"{REQUIREMENTS} yok -- kurulumun neye ihtiyacı olduğunu pip okuyamıyor"
    )


def test_every_import_the_code_makes_is_declared():
    missing = sorted(name for name in _needed() if name.lower() not in _declared())
    assert missing == [], (
        f"Kod bunları içe aktarıyor ama requirements.txt saymıyor: {missing}"
    )
```

Bugün **ikisi de kırmızı**: dosya hiç yok, ve ilki düştüğü için ikincisi de `FileNotFoundError`
verir. Uygulama turu dosyayı yaratınca ikisi birden yeşile döner.

## B. `queen-editor/backend/tests/test_requirements.py` — aynı dosya, bir kırmızı.

Birebir aynı içerik; `TOOL` `__file__`'dan türediği için **metin de aynı kalıyor**. Kopya bilerek,
`test_frontend_toolchain.py`'deki gerekçeyle: iki araç ayrı `pytest` koşusu.

Burada `test_the_tool_says_what_to_install` **yeşil** *(dosya var)* ve
`test_every_import_the_code_makes_is_declared` **kırmızı** — `requests` eksik.

## C. Koşuldu: **3 kırmızı**, tam planlanan üçü.

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-agent -q` | **2 kırmızı**, 656 yeşil |
| `python -m pytest queen-editor -q` | **1 kırmızı**, 719 yeşil |
| `npm test --prefix queen-agent/frontend` | 568 yeşil |
| `npm test --prefix queen-editor/frontend` | 584 yeşil |

queen-agent'ın ikisi dosyanın yokluğunu gösteriyor: biri `AssertionError` ile adres vererek, öteki
`FileNotFoundError` ile. queen-editor'de `test_the_tool_says_what_to_install` **yeşil** *(dosya
var)*, ve 719 sayısı 718'e o yeşili ekliyor.

### Testin kendisi de ölçüldü, ve geçti

Planın kontrolü şuydu: queen-editor'ün kırmızısı yalnız `['requests']` demeli. Dediği tam olarak bu:

```
Kod bunları içe aktarıyor ama requirements.txt saymıyor: ['requests']
```

**`torch` listede yok**, ve olmaması tesadüf değil — `mmaudio_sampler.py` onu `render()`'ın içinde
içe aktarıyor, ve `tree.body` taraması oraya bakmıyor. Tasarımın kalbindeki ayrım bu turda kanıtını
verdi: her içe aktarımı sayan bir test burada `torch`, `torchaudio` ve `mmaudio` isterdi.

## D. Kırmızı commit.

## Bilerek yapılmayanlar

`skip`/`xfail` yok. `requirements.txt`'ler ellenmez. Ön yüz, `dist`, `package.json` ellenmez.
