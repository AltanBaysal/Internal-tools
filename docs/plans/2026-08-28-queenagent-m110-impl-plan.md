# Madde 110 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m110-kalite-uygulama-design.md](../specs/2026-08-28-queenagent-m110-kalite-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `build_prompts.py` — sabit, import'ların altına

```python
# The chain every prompt opens with. In code rather than in each structure file since Madde 110:
# it is the same in every scenario, and a model writing it meant a model copying it out of the
# schema example -- which is how a chain mixing two model families reached real files. A scenario
# that needs a different one writes quality in its own file and this steps aside.
DEFAULT_QUALITY = (
    "score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres"
)
```

## B. `build_prompts.py` — iki kullanım yeri

`build_prompts` içinde:

```python
        parts = [structure.get("quality") or DEFAULT_QUALITY, frame.get("people", "")]
```

`build_character_prompts` içinde:

```python
    quality = structure.get("quality") or DEFAULT_QUALITY
```

## C. `schema.py` — örnek

`'  "quality": "score_9_up, masterpiece, best quality, absurdres",\n'` satırı silinir.

## D. `schema.py` — düzyazı

`"Everything in this file is English"` cümlesinden önce yeni paragraf:

```python
    "The quality chain is not in this file: code puts it at the front of every prompt, the same "
    "way for every scenario. Write a quality field only when this one needs a different chain -- "
    "what is written there is used instead.\n"
    "\n"
```

## E. Doğrulama ve kapanış

1. İki suite; beş kırmızı yeşerir, defter çifti dışında kırmızı kalmaz.
2. `dist` derlenmez — ön yüz değişmiyor.
3. Commit: `build_prompts.py` + `schema.py` + bu turun iki belgesi.

## Bilerek yapılmayanlar

- **Kural defterinin 3. maddesi ellenmez.**
- **Kamera işi ellenmez** *(111)*.
- **Test dosyaları değişmez.**
