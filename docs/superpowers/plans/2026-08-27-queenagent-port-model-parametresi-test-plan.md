# `Engine` portundaki ölü `model` parametresi · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-port-model-parametresi-testler-design.md](../specs/2026-08-27-queenagent-port-model-parametresi-testler-design.md)
**Bu turda kod yazılmaz.** Üç test kırmızıya döner.
**Komut:** `python -m pytest queen-agent -q`

---

## Tek dosya: `backend/tests/test_ports.py` — yeni

```python
import inspect

import pytest

from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.domain.ports import Engine


@pytest.mark.parametrize("method", ["complete", "stream"])
def test_the_engine_port_asks_for_what_its_adapter_takes(method):
    # A Protocol has no body, so nothing running catches it drifting from the thing that answers it.
    # Its signature can still be read, and that is the measure: what the port promises the domain
    # against what the adapter actually takes. Measured on the real adapter rather than on a fake --
    # the fakes are written to whatever the caller passes, so they would agree with either side.
    promised = list(inspect.signature(getattr(Engine, method)).parameters)
    given = list(inspect.signature(getattr(XaiEngine, method)).parameters)
    assert promised == given


def test_the_port_no_longer_hands_a_model_to_the_call():
    # Madde 82 settled it: one model, named once in config.py. The signature test does not reach
    # this -- a parameter can go while the sentence explaining it stays, and then the file says
    # something that is no longer true. Watched rather than simply deleted, so it cannot come back.
    assert "travels with the call" not in inspect.getdoc(Engine.complete)
```

## Beklenen kırmızı

| Test | Neden |
|---|---|
| `..._asks_for_what_its_adapter_takes[complete]` | port `['self', 'messages', 'tools', 'model']`, adaptör `['self', 'messages', 'tools']` |
| `..._asks_for_what_its_adapter_takes[stream]` | port `[..., 'model', 'on_open']`, adaptör `[..., 'on_open']` |
| `..._no_longer_hands_a_model_to_the_call` | cümle `complete`'in docstring'inde duruyor |

**Üç.** Sayı koşarak değil bugünkü iki dosyadan türetiliyor:
[`ports.py:44-58`](../../../queen-agent/backend/features/workspace/domain/ports.py#L44-L58) ve
[`xai_engine.py:13-17`](../../../queen-agent/backend/features/workspace/data/xai_engine.py#L13-L17).

**İki kırmızı bu işin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `ports.py` bu turda açılmaz.
- **`Stops`, `FileStore`, `ChatStore`, `ProjectStore` sınanmaz** — bu iş `Engine`'in artığını
  temizliyor, portlara toptan bir bekçi kurmuyor. Öteki üçünün adaptörlerinde bilinen bir sürüklenme
  yok, ve olmayan bir soruna test yazmak testi kuralın kendisi sanmaktır.
- **`complete` silinmez** — spec'te kapsam dışı olarak kaydedildi.
- **Ön yüz açılmaz, `dist` derlenmez.**
